#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from cassandra.cluster import Cluster


# Configuration
API_BASE_URL = os.getenv("OVERFAST_BASE_URL", "http://localhost:8080").rstrip("/")
PUBLIC_API_BASE_URL = os.getenv("OVERFAST_PUBLIC_BASE_URL", "https://overfast-api.tekrop.fr").rstrip("/")
CASSANDRA_CONTACT_POINTS = [h for h in os.getenv("CASSANDRA_HOSTS", os.getenv("CASSANDRA_HOST", "127.0.0.1")).split(",") if h]
KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "overwatch")
TABLE = os.getenv("CASSANDRA_TABLE", "heroes")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "15"))
FALLBACK_TO_PUBLIC = os.getenv("OVERFAST_FALLBACK_PUBLIC", "1") not in ("0", "false", "False")
HERO_LIMIT_ENV = os.getenv("OVERFAST_LIMIT")
HERO_LIMIT = int(HERO_LIMIT_ENV) if HERO_LIMIT_ENV and HERO_LIMIT_ENV.isdigit() else None


def http_get_json(path: str, base_url: Optional[str] = None) -> Any:
    base = (base_url or API_BASE_URL).rstrip("/")
    url = f"{base}{path}"
    resp = requests.get(url, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def fetch_heroes_list(base_url: Optional[str] = None) -> List[Dict[str, Any]]:
    # /heroes returns a list of HeroShort items
    data = http_get_json("/heroes", base_url=base_url)
    if isinstance(data, dict) and "results" in data:
        return data.get("results", [])
    if isinstance(data, list):
        return data
    # Fallback: try to read HeroKey enum from openapi.json
    spec = http_get_json("/openapi.json", base_url=base_url)
    try:
        keys = spec["components"]["schemas"]["HeroKey"]["enum"]
        return [{"key": k} for k in keys]
    except Exception:
        raise ValueError("Unexpected /heroes response format and couldn't parse HeroKey enum from openapi.json")


def fetch_hero_detail(hero_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
    # /heroes/{hero_key} returns a Hero object (detailed)
    return http_get_json(f"/heroes/{hero_key}", base_url=base_url)


def ensure_schema(session) -> None:
    # Create keyspace/table if not exists (idempotent)
    session.execute(
        f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
        """
    )
    session.set_keyspace(KEYSPACE)
    session.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            hero_key text PRIMARY KEY,
            name text,
            description text,
            portrait text,
            role text,
            subrole text,
            location text,
            age text,
            birthday text,
            health int,
            armor int,
            shields int,
            total_hp int,
            abilities list<text>,
            backgrounds list<text>,
            perks_json text,
            story text,
            raw_json text,
            last_update timestamp
        )
        """
    )
    # Tables orientées requêtes métier (lecture) — sans ALLOW FILTERING
    # 1) Par rôle
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS heroes_by_role (
            role text,
            hero_key text,
            name text,
            total_hp int,
            armor int,
            location text,
            age int,
            PRIMARY KEY ((role), hero_key)
        )
        """
    )
    # 2) Par HP (bucket unique 'all' + plage sur total_hp)
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS heroes_by_hp_bucket (
            hp_bucket text,
            total_hp int,
            hero_key text,
            name text,
            role text,
            armor int,
            location text,
            age int,
            PRIMARY KEY ((hp_bucket), total_hp, hero_key)
        ) WITH CLUSTERING ORDER BY (total_hp DESC, hero_key ASC)
        """
    )
    # 3) Par armor (bucket unique 'all' + plage sur armor)
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS heroes_by_armor_bucket (
            armor_bucket text,
            armor int,
            hero_key text,
            name text,
            role text,
            total_hp int,
            location text,
            age int,
            PRIMARY KEY ((armor_bucket), armor, hero_key)
        ) WITH CLUSTERING ORDER BY (armor DESC, hero_key ASC)
        """
    )
    # 4) Par localisation
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS heroes_by_location (
            location text,
            hero_key text,
            name text,
            role text,
            total_hp int,
            armor int,
            age int,
            PRIMARY KEY ((location), hero_key)
        )
        """
    )
    # 5) Par âge (bucket unique 'all' + plage sur age)
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS heroes_by_age_bucket (
            age_bucket text,
            age int,
            hero_key text,
            name text,
            role text,
            total_hp int,
            armor int,
            location text,
            PRIMARY KEY ((age_bucket), age, hero_key)
        ) WITH CLUSTERING ORDER BY (age ASC, hero_key ASC)
        """
    )


def _to_int(x: Any) -> Optional[int]:
    try:
        return int(x) if x is not None else None
    except Exception:
        return None


def map_hero_row(hero_detail: Dict[str, Any], hero_key: str) -> Dict[str, Any]:
    def _t(x: Any) -> Optional[str]:
        return None if x is None else str(x)

    hit = hero_detail.get("hitpoints") or {}
    # Extract abilities names if present
    abilities: List[str] = []
    for a in (hero_detail.get("abilities", []) or []):
        if isinstance(a, dict):
            name = a.get("name") or a.get("title") or a.get("key")
            if name:
                abilities.append(str(name))
        elif isinstance(a, str):
            abilities.append(a)

    # Extract background image URLs if present
    backgrounds: List[str] = []
    for b in (hero_detail.get("backgrounds", []) or []):
        if isinstance(b, dict) and b.get("url"):
            backgrounds.append(str(b.get("url")))
        elif isinstance(b, str):
            backgrounds.append(b)

    story_val = hero_detail.get("story")
    if isinstance(story_val, dict):
        story_text = story_val.get("summary")
    else:
        story_text = story_val

    row = {
        "hero_key": hero_key,
        "name": _t(hero_detail.get("name")),
        "description": _t(hero_detail.get("description")),
        "portrait": _t(hero_detail.get("portrait")),
        "role": _t(hero_detail.get("role")),
        "subrole": _t(hero_detail.get("subrole")),
        "location": _t(hero_detail.get("location")),
        "age": _t(hero_detail.get("age")),
        "birthday": _t(hero_detail.get("birthday")),
        "health": _to_int((hit or {}).get("health")),
        "armor": _to_int((hit or {}).get("armor")),
        "shields": _to_int((hit or {}).get("shields")),
        "total_hp": _to_int((hit or {}).get("total")),
        "abilities": abilities,
        "backgrounds": backgrounds,
        "perks_json": json.dumps(hero_detail.get("perks") or {}, ensure_ascii=False),
        "story": _t(story_text),
        "raw_json": json.dumps(hero_detail, ensure_ascii=False),
        "last_update": datetime.utcnow(),
    }
    return row


def main() -> int:
    print(f"Base API préférée: {API_BASE_URL}")
    active_base = API_BASE_URL
    try:
        heroes = fetch_heroes_list(base_url=active_base)
    except Exception as e:
        print("Échec de la récupération de la liste des héros sur la base préférée:", e, file=sys.stderr)
        if FALLBACK_TO_PUBLIC:
            print(f"Basculement sur l'API publique: {PUBLIC_API_BASE_URL}")
            active_base = PUBLIC_API_BASE_URL
            try:
                heroes = fetch_heroes_list(base_url=active_base)
            except Exception as e2:
                print("Échec de la récupération de la liste des héros sur l'API publique:", e2, file=sys.stderr)
                return 1
        else:
            return 1

    # Determine hero keys from the listing
    hero_keys: List[str] = []
    for h in heroes:
        if isinstance(h, dict):
            k = h.get("key") or h.get("hero_key") or h.get("id")
            if k:
                hero_keys.append(str(k))
    hero_keys = list(dict.fromkeys(hero_keys))  # unique order-preserving
    print(f"{len(hero_keys)} héros trouvés.")
    if not hero_keys:
        print("Aucun héros à importer (liste vide).")
        return 0
    if HERO_LIMIT is not None and HERO_LIMIT >= 0:
        hero_keys = hero_keys[:HERO_LIMIT]
        print(f"Limitation activée: on importe seulement les {len(hero_keys)} premiers héros.")

    cluster = Cluster(contact_points=CASSANDRA_CONTACT_POINTS)
    session = cluster.connect()
    try:
        ensure_schema(session)
        insert_cql = (
            f"INSERT INTO {TABLE} ("
            "hero_key, name, description, portrait, role, subrole, "
            "location, age, birthday, health, armor, shields, total_hp, "
            "abilities, backgrounds, perks_json, story, raw_json, last_update"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        prepared = session.prepare(insert_cql)
        # Prepared statements pour les tables de lecture
        p_ins_role = session.prepare(
            """
            INSERT INTO heroes_by_role (role, hero_key, name, total_hp, armor, location, age)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        )
        p_ins_hp = session.prepare(
            """
            INSERT INTO heroes_by_hp_bucket (hp_bucket, total_hp, hero_key, name, role, armor, location, age)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
        p_ins_armor = session.prepare(
            """
            INSERT INTO heroes_by_armor_bucket (armor_bucket, armor, hero_key, name, role, total_hp, location, age)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
        p_ins_loc = session.prepare(
            """
            INSERT INTO heroes_by_location (location, hero_key, name, role, total_hp, armor, age)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        )
        p_ins_age = session.prepare(
            """
            INSERT INTO heroes_by_age_bucket (age_bucket, age, hero_key, name, role, total_hp, armor, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        )

        inserted = 0
        errors = 0
        for key in hero_keys:
            try:
                # Try on active base; if it fails and public fallback allowed, retry on public
                try:
                    detail = fetch_hero_detail(key, base_url=active_base)
                except Exception as e_det:
                    if FALLBACK_TO_PUBLIC and active_base != PUBLIC_API_BASE_URL:
                        detail = fetch_hero_detail(key, base_url=PUBLIC_API_BASE_URL)
                    else:
                        raise e_det
                row = map_hero_row(detail, key)
                params = (
                    row["hero_key"],
                    row["name"],
                    row["description"],
                    row["portrait"],
                    row["role"],
                    row["subrole"],
                    row["location"],
                    row["age"],
                    row["birthday"],
                    row["health"],
                    row["armor"],
                    row["shields"],
                    row["total_hp"],
                    row["abilities"],
                    row["backgrounds"],
                    row["perks_json"],
                    row["story"],
                    row["raw_json"],
                    row["last_update"],
                )
                session.execute(prepared, params)
                # Alimentation des tables de lecture
                role = row.get("role")
                hero_key = row.get("hero_key")
                name = row.get("name")
                location = row.get("location")
                total_hp = _to_int(row.get("total_hp"))
                armor = _to_int(row.get("armor"))
                age_int = _to_int(row.get("age"))

                # 1) Par rôle (role, hero_key)
                if role and hero_key:
                    session.execute(p_ins_role, (
                        role, hero_key, name, total_hp, armor, location, age_int
                    ))
                # 2) Par HP bucket
                if total_hp is not None and hero_key:
                    session.execute(p_ins_hp, (
                        'all', total_hp, hero_key, name, role, armor, location, age_int
                    ))
                # 3) Par armor bucket
                if armor is not None and hero_key:
                    session.execute(p_ins_armor, (
                        'all', armor, hero_key, name, role, total_hp, location, age_int
                    ))
                # 4) Par localisation
                if location and hero_key:
                    session.execute(p_ins_loc, (
                        location, hero_key, name, role, total_hp, armor, age_int
                    ))
                # 5) Par âge bucket
                if age_int is not None and hero_key:
                    session.execute(p_ins_age, (
                        'all', age_int, hero_key, name, role, total_hp, armor, location
                    ))
                inserted += 1
                print(f"Inséré: {key} - {row['name']}")
            except Exception as e:
                errors += 1
                print(f"Erreur pour {key}: {e}", file=sys.stderr)

        print(f"Import terminé. Succès: {inserted}, Erreurs: {errors}")
    finally:
        try:
            session.shutdown()
        except Exception:
            pass
        try:
            cluster.shutdown()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
