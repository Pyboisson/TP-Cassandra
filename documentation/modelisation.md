# Modélisation Cassandra — OverFast / Overwatch Heroes

Ce document présente la (dé)normalisation choisie pour le TP, les tables, les clés, ainsi que 5 besoins métier et leurs requêtes.

## Tables et clés

Table source (KISS): `overwatch.heroes`
- Clé primaire: `hero_key` (text) — clé de partition unique
- Colonnes: `name` (text), `role` (text), `subrole` (text), `location` (text), `age` (int), `health` (int), `shields` (int), `armor` (int), `total_hp` (int)

Tables de lecture dédiées (orientées requêtes)
- `overwatch.heroes_by_role ((role), hero_key)` — lecture par rôle
- `overwatch.heroes_by_hp_bucket ((hp_bucket), total_hp, hero_key)` — lecture par plage de HP, avec bucket applicatif
- `overwatch.heroes_by_armor_bucket ((armor_bucket), armor, hero_key)` — lecture par plage d’armure
- `overwatch.heroes_by_location ((location), hero_key)` — lecture par localisation exacte
- `overwatch.heroes_by_age_bucket ((age_bucket), age, hero_key)` — lecture par plage d’âge

## Choix de modélisation
- Modèle centré sur les requêtes: chaque besoin métier dispose d’une table dédiée pour éviter `ALLOW FILTERING`.
- Writes en éventail: à l’ingestion, les données d’un héros sont insérées dans la table source et dans les tables de lecture nécessaires.
- Colonnes numériques pour le range: les tables par plage utilisent la colonne de clustering adéquate (ex: `total_hp`, `armor`, `age`).
- Schéma minimaliste: on ne conserve que 10 colonnes utiles au TP pour simplifier la maintenance et la lisibilité.

## 5 besoins métier et leurs requêtes

1) Lister tous les tanks
```sql
SELECT hero_key, name, 'tank' AS role
FROM overwatch.heroes_by_role
WHERE role = 'tank';
```

2) Identifier les héros Total HP >= 600
```sql
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes_by_hp_bucket
WHERE hp_bucket = 'all' AND total_hp >= 600;
```

3) Lister les héros avec armure (armor > 0)
```sql
SELECT hero_key, name, role, armor
FROM overwatch.heroes_by_armor_bucket
WHERE armor_bucket = 'all' AND armor > 0;
```

4) Retrouver les héros localisés en France
```sql
SELECT hero_key, name, role, location
FROM overwatch.heroes_by_location
WHERE location = 'France';
```

5) Identifier les héros de moins de 18 ans
```sql
SELECT hero_key, name, role, age
FROM overwatch.heroes_by_age_bucket
WHERE age_bucket = 'all' AND age < 18;
```

## Améliorations possibles
- Tables de lecture additionnelles (ex: par sous-rôle, par capacité) si de nouveaux besoins apparaissent.
- Index SAI/SASI pour recherches textuelles si besoin (selon la distribution Cassandra utilisée).
- Pipelines ETL pour alimenter des vues ou exports analytiques.
