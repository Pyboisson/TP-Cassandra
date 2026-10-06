# Requêtes et scripts OverFast x Cassandra

Ce dossier contient:
- Des requêtes CQL illustrant des besoins métier courants sur la table unique `overwatch.heroes`.
- Des scripts CQL utilitaires (mise à jour, suppression, réinsertion) pour la démonstration.

Modèle (rappel):
- Table: `overwatch.heroes`
- Clé primaire: `hero_key` (clé de partition)
- Colonnes notables: `name`, `role`, `total_hp`, `abilities` (list<text>), `backgrounds` (list<text>), etc.

Note: Le modèle est centré sur la lecture par identifiant. Les requêtes analytiques ou par attribut secondaire (role, HP, etc.) nécessitent `ALLOW FILTERING` et ne sont pas optimales à grande échelle. Pour un usage production, prévoir des tables de lecture dédiées (ex: `heroes_by_role`) ou du matériel dérivé.

---

## REQ-01 — Tous les personnages tank

Besoin métier:
- Lister tous les héros jouant le rôle « tank » pour constituer une frontline.

Fichier: `queries/REQ-01_tank_heroes.sql`

Requête CQL:
```sql
SELECT hero_key, name, role
FROM overwatch.heroes
WHERE role = 'tank' ALLOW FILTERING;
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
FROM overwatch.heroes
WHERE total_hp >= 600 ALLOW FILTERING;
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
FROM overwatch.heroes
WHERE armor > 0 ALLOW FILTERING;
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
FROM overwatch.heroes
WHERE location = 'France' ALLOW FILTERING;
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
FROM overwatch.heroes
WHERE age < 18 ALLOW FILTERING;
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

## Conseils d’optimisation (hors périmètre « une seule table »)
- Créer des tables de lecture par attribut d’accès: `heroes_by_role (role, hero_key, name, ...)`, `tanks_by_hp (role, total_hp, hero_key, ...)`.
- Maintenir ces vues via l’ingestion applicative (writes en éventail) ou un pipeline ETL.
- Limiter `ALLOW FILTERING` aux démos/faible volumétrie.
