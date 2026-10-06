# TP Cassandra — OverFast / Overwatch Heroes

Ce dépôt présente un TP autour de Cassandra en s’appuyant sur l’API OverFast (héros d’Overwatch).

Contenu du dépôt
- queries/: scripts CQL de vérification, CRUD et requêtes métier
- documentation/: modélisation de la table et des besoins

Sujet
- Importer des héros Overwatch à partir d’une API compatible OverFast et manipuler les données dans Cassandra.

API
- API locale (si lancée) via OVERFAST_BASE_URL, ou API publique de secours.
- Le script d’ingestion (hors périmètre de ce README) écrit dans la table `overwatch.heroes`.

Données
- Une ligne par héros, incluant les attributs de base (name, role, HP, etc.) et du JSON brut pour l’extensibilité.

Modèle Cassandra (résumé)
- Keyspace: `overwatch`
- Table: `heroes (hero_key text PRIMARY KEY, name text, description text, portrait text, role text, subrole text, location text, age int, health int, armor int, shields int, total_hp int, abilities list<text>, backgrounds list<text>, perks_json text, story text, raw_json text, last_update timestamp)`
- Partitionnement: par `hero_key` (lecture/écriture par identifiant efficaces)

Principales requêtes métier (extraits)
- Tous les tanks:
  ```sql
  SELECT hero_key, name, role FROM overwatch.heroes WHERE role = 'tank' ALLOW FILTERING;
  ```
- Héros total_hp >= 600:
  ```sql
  SELECT hero_key, name, role, total_hp FROM overwatch.heroes WHERE total_hp >= 600 ALLOW FILTERING;
  ```
- Héros avec armure > 0:
  ```sql
  SELECT hero_key, name, role, armor FROM overwatch.heroes WHERE armor > 0 ALLOW FILTERING;
  ```
- Location = 'France':
  ```sql
  SELECT hero_key, name, role, location FROM overwatch.heroes WHERE location = 'France' ALLOW FILTERING;
  ```
- Âge < 18:
  ```sql
  SELECT hero_key, name, role, age FROM overwatch.heroes WHERE age < 18 ALLOW FILTERING;
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
