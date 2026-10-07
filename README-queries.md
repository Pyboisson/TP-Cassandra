# Requêtes et scripts OverFast x Cassandra

Ce dossier contient:
- Des requêtes CQL illustrant des besoins métier courants via des tables orientées requêtes (sans ALLOW FILTERING).
- Des scripts CQL utilitaires (mise à jour, suppression, réinsertion) pour la démonstration.

Modèle (rappel):
- Table source: `overwatch.heroes` (clé primaire: `hero_key`)
- Tables de lecture dédiées:
  - `overwatch.heroes_by_role ((role), hero_key)`
  - `overwatch.heroes_by_hp_bucket ((hp_bucket), total_hp, hero_key)`
  - `overwatch.heroes_by_armor_bucket ((armor_bucket), armor, hero_key)`
  - `overwatch.heroes_by_location ((location), hero_key)`
  - `overwatch.heroes_by_age_bucket ((age_bucket), age, hero_key)`

---

## REQ-01 — Tous les personnages tank

Besoin métier:
- Lister tous les héros jouant le rôle « tank » pour constituer une frontline.

Fichier: `queries/REQ-01_tank_heroes.sql`

Requête CQL:
```sql
SELECT hero_key, name, 'tank' AS role
FROM overwatch.heroes_by_role
WHERE role = 'tank';
```

Clé de partition utilisée:
- Aucune (filtrage secondaire sur `role`).

Justification:
- Le modèle est single-table avec partition par `hero_key`. Sans table secondaire par rôle, on doit filtrer avec `ALLOW FILTERING`.

---

## REQ-02 — Héros à forte endurance (total_hp >= 600)

Besoin métier:
- Identifier des héros robustes pour des objectifs spécifiques (push, point contest, etc.).

Fichier: `queries/REQ-02_high_hp_heroes.sql`

Requête CQL:
```sql
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes_by_hp_bucket
WHERE hp_bucket = 'all' AND total_hp >= 600;
```

Clé de partition utilisée:
- Aucune (filtrage numérique sur `total_hp`).

Justification:
- Tri/filtrage sur une colonne non clé: nécessite `ALLOW FILTERING` avec ce modèle.

---

## REQ-03 — Héros disposant d'armure (armor > 0)

Besoin métier:
- Lister les héros qui possèdent de l'armure pour évaluer la résistance additionnelle.

Fichier: `queries/REQ-03_heroes_with_armor.sql`

Requête CQL:
```sql
SELECT hero_key, name, role, armor
FROM overwatch.heroes_by_armor_bucket
WHERE armor_bucket = 'all' AND armor > 0;
```

Clé de partition utilisée:
- Aucune (filtrage numérique sur `armor`).

---

## REQ-04 — Héros localisés en France (location = 'France')

Besoin métier:
- Retrouver les héros dont la localisation déclarée est « France ».

Fichier: `queries/REQ-04_location_equals_france.sql`

Requête CQL:
```sql
SELECT hero_key, name, role, location
FROM overwatch.heroes_by_location
WHERE location = 'France';
```

Clé de partition utilisée:
- Aucune (filtrage texte sur `location`).

---

## REQ-05 — Héros de moins de 18 ans (age < 18)

Besoin métier:
- Identifier les héros mineurs.

Fichier: `queries/REQ-05_age_below_18.sql`

Requête CQL:
```sql
SELECT hero_key, name, role, age
FROM overwatch.heroes_by_age_bucket
WHERE age_bucket = 'all' AND age < 18;
```

Clé de partition utilisée:
- Aucune (filtrage numérique sur `age`).

---

## Scripts utilitaires (démonstration DML autour de Winston)

- `queries/01_update_winston.sql`
  - Met à jour Winston pour lui attribuer un total de 10000 PV.
  - Extrait:
    ```sql
    UPDATE overwatch.heroes
    SET health = 10000,
        armor = 0,
        shields = 0,
        total_hp = 10000
    WHERE hero_key = 'winston';
    ```

- `queries/02_delete_winston.sql`
  - Supprime la ligne correspondant à Winston.
  - Extrait:
    ```sql
    DELETE FROM overwatch.heroes WHERE hero_key = 'winston';
    ```

- `queries/03_reinsert_winston_defaults.sql`
  - Réinsère Winston avec des valeurs par défaut (cohérentes avec l’import initial).
  - Le script fournit toutes les colonnes nécessaires à l’insertion.

---

## Notes
- Les tables de lecture sont alimentées automatiquement par le script `script/get_overwatch.py` lors de l’ingestion (writes en éventail).
- Limiter `ALLOW FILTERING` aux démos.faible volumétrie. Ici, il n’est plus utilisé pour les 5 requêtes métier.
