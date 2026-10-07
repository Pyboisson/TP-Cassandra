# TP Cassandra — OverFast / Overwatch Heroes

Ce dépôt présente un TP autour de Cassandra en s’appuyant sur l’API OverFast (héros d’Overwatch).

Contenu du dépôt
- queries/: scripts CQL de vérification, CRUD et requêtes métier
- documentation/: modélisation de la table et des besoins

Sujet
- Importer des héros Overwatch à partir d’une API compatible OverFast et manipuler les données dans Cassandra.

API
- API locale (si lancée) via OVERFAST_BASE_URL, ou API publique de secours.
- Le script d’ingestion (hors périmètre de ce README) écrit dans la table `overwatch.heroes` et maintient les tables de lecture (fan-out) à l’écriture.

Données
- Une ligne par héros dans la table source minimaliste (10 colonnes utiles au TP): `hero_key, name, role, subrole, location, age, health, shields, armor, total_hp`.

Modèle Cassandra (résumé)
- Keyspace: `overwatch`
- Table source minimaliste (KISS):
  - `heroes (hero_key text PRIMARY KEY, name text, role text, subrole text, location text, age int, health int, shields int, armor int, total_hp int)`
- Tables orientées requêtes (lectures efficaces sans ALLOW FILTERING):
  - `heroes_by_role ((role), hero_key)`
  - `heroes_by_hp_bucket ((hp_bucket), total_hp, hero_key)`
  - `heroes_by_armor_bucket ((armor_bucket), armor, hero_key)`
  - `heroes_by_location ((location), hero_key)`
  - `heroes_by_age_bucket ((age_bucket), age, hero_key)`

Principales requêtes métier (extraits, sans ALLOW FILTERING)
- Tous les tanks:
  ```sql
  SELECT hero_key, name, 'tank' AS role
  FROM overwatch.heroes_by_role
  WHERE role = 'tank';
  ```
- Héros total_hp >= 600:
  ```sql
  SELECT hero_key, name, role, total_hp
  FROM overwatch.heroes_by_hp_bucket
  WHERE hp_bucket = 'all' AND total_hp >= 600;
  ```
- Héros avec armure > 0:
  ```sql
  SELECT hero_key, name, role, armor
  FROM overwatch.heroes_by_armor_bucket
  WHERE armor_bucket = 'all' AND armor > 0;
  ```
- Location = 'France':
  ```sql
  SELECT hero_key, name, role, location
  FROM overwatch.heroes_by_location
  WHERE location = 'France';
  ```
- Âge < 18:
  ```sql
  SELECT hero_key, name, role, age
  FROM overwatch.heroes_by_age_bucket
  WHERE age_bucket = 'all' AND age < 18;
  ```

Organisation attendue
```
TP-Cassandra/
│
├── README.md
│
├── queries/
│   ├── 01_verification.sql
│   ├── 02_crud.sql
│   ├── 03_requetes_metier.sql
│   └── ...
│
└── documentation/
    └── modelisation.md
```
