# Modélisation Cassandra — OverFast / Overwatch Heroes

Ce document présente la (dé)normalisation choisie pour le TP, les tables, les clés, ainsi que 5 besoins métier et leurs requêtes.

## Tables et clés

Table principale: `overwatch.heroes`
- Clé primaire: `hero_key` (text) — clé de partition
- Colonnes principales:
  - `name` (text) — nom du héros
  - `description` (text)
  - `portrait` (text)
  - `role` (text) — tank / damage / support
  - `subrole` (text)
  - `location` (text)
  - `age` (int)
  - `health` (int), `armor` (int), `shields` (int), `total_hp` (int)
  - `abilities` (list<text>) — noms des capacités
  - `backgrounds` (list<text>) — URLs d’images
  - `perks_json` (text), `story` (text), `raw_json` (text)
  - `last_update` (timestamp)

Justification du modèle:
- Approche « single-table » pour simplifier l’ingestion et les lectures par identifiant (hero_key).
- Les besoins analytiques/filtrages secondaires reposent sur `ALLOW FILTERING` dans ce TP (pédagogique, faible volumétrie).
- Pour une production à plus forte volumétrie, prévoir des tables de lecture dédiées par attribut d’accès (par ex. `heroes_by_role`, `heroes_by_hp`, etc.).

## Choix de modélisation
- Dé-normalisation poussée: toutes les informations utiles d’un héros sont stockées dans la même table `overwatch.heroes`.
- Les champs texte complexes (perks_json, raw_json) sont conservés en l’état pour permettre une évolution du schéma applicatif sans migration coûteuse.
- Les champs de collection (abilities, backgrounds) offrent des usages simples (ex: affichage, filtres pédagogiques), avec la contrepartie d’un filtrage sous-optimal sans index spécialisés.

## 5 besoins métier et leurs requêtes

1) Lister tous les tanks
```sql
SELECT hero_key, name, role
FROM overwatch.heroes
WHERE role = 'tank' ALLOW FILTERING;
```

2) Identifier les héros Total HP >= 600
```sql
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes
WHERE total_hp >= 600 ALLOW FILTERING;
```

3) Lister les héros avec armure (armor > 0)
```sql
SELECT hero_key, name, role, armor
FROM overwatch.heroes
WHERE armor > 0 ALLOW FILTERING;
```

4) Retrouver les héros localisés en France
```sql
SELECT hero_key, name, role, location
FROM overwatch.heroes
WHERE location = 'France' ALLOW FILTERING;
```

5) Identifier les héros de moins de 18 ans
```sql
SELECT hero_key, name, role, age
FROM overwatch.heroes
WHERE age < 18 ALLOW FILTERING;
```

## Améliorations possibles (hors périmètre TP)
- Tables de lecture dédiées: `heroes_by_role (role, hero_key, name, total_hp, ...)`, `heroes_by_hp (total_hp, hero_key, name, role, ...)`.
- Index SAI/SASI pour recherches textuelles si la distribution le permet et si besoin de LIKE sans tables dérivées.
- Pipelines ETL pour maintenir des vues matérialisées applicatives.
