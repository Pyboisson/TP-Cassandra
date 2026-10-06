#!/usr/bin/env python3
import sys
import requests
from cassandra.cluster import Cluster

API_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records?limit=20"
CASSANDRA_CONTACT_POINTS = ["127.0.0.1"]
KEYSPACE = "velib"
TABLE = "stations"

def fetch_stations(url):
    print("Récupération des données Vélib'...")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    # La doc du TP montre une clé "results" contenant les objets station.
    # Certaines API renvoient "records" ou des objets encapsulés dans "fields".
    results = data.get("results") or data.get("records") or []
    # Normaliser : si c'est une liste de records avec {"fields": {...}}, on retourne les fields.
    normalized = []
    for r in results:
        if isinstance(r, dict) and "fields" in r and isinstance(r["fields"], dict):
            normalized.append(r["fields"])
        else:
            normalized.append(r)
    return normalized

def ensure_schema(session):
    # Créer keyspace si nécessaire
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
    """)
    session.set_keyspace(KEYSPACE)
    # Créer table si nécessaire
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            station_id text PRIMARY KEY,
            name text,
            capacity int,
            latitude double,
            longitude double,
            opening_hours text
        )
    """)

def insert_station(session, prepared, item):
    # Extraire champs en gérant l'absence possible
    station_id = item.get("stationcode") or item.get("station_id") or item.get("stationCode")
    name = item.get("name")
    capacity = item.get("capacity")
    coord = item.get("coordonnees_geo") or item.get("coordonnees_geo") or item.get("coord")
    if coord is None:
        # certains objets peuvent avoir 'coordonnees_geo' absent ; essayer lon/lat racine
        latitude = item.get("lat") or item.get("latitude")
        longitude = item.get("lon") or item.get("longitude")
    else:
        latitude = coord.get("lat")
        longitude = coord.get("lon")
    opening_hours = item.get("station_opening_hours") or item.get("opening_hours")

    # S'assurer que station_id n'est pas None (skip sinon)
    if not station_id:
        raise ValueError("station_id absent dans l'item, impossible d'insérer")

    session.execute(prepared, (station_id, name, capacity, latitude, longitude, opening_hours))
    print(f"Station importée : {station_id} - {name}")

def main():
    try:
        stations = fetch_stations(API_URL)
    except Exception as e:
        print("Échec de la récupération de l'API :", e, file=sys.stderr)
        return 1

    print(f"{len(stations)} stations récupérées.")
    if len(stations) == 0:
        print("Aucune station à importer.")
        return 0

    cluster = Cluster(contact_points=CASSANDRA_CONTACT_POINTS)
    session = cluster.connect()
    try:
        ensure_schema(session)
        insert_cql = f"INSERT INTO {TABLE} (station_id, name, capacity, latitude, longitude, opening_hours) VALUES (?, ?, ?, ?, ?, ?)"
        prepared = session.prepare(insert_cql)
        for item in stations:
            try:
                insert_station(session, prepared, item)
            except Exception as e:
                print(f"Erreur insertion pour un item: {e}", file=sys.stderr)
        print("Import terminé.")
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
