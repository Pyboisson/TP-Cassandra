-- 03_requetes_metier.sql
-- Requêtes métier principales (tables orientées requêtes — sans ALLOW FILTERING)
-- Pour chaque besoin: CREATE TABLE (modèle) puis SELECT (requête)

-- ============================================================================
-- Besoin 1: lister les héros par rôle (ex: tous les tanks)
-- Modèle (clé de partition = role):
CREATE TABLE IF NOT EXISTS overwatch.heroes_by_role (
  role text,
  hero_key text,
  name text,
  total_hp int,
  armor int,
  location text,
  age int,
  PRIMARY KEY ((role), hero_key)
);

-- Requête:
SELECT hero_key, name, 'tank' AS role
FROM overwatch.heroes_by_role
WHERE role = 'tank';

-- ============================================================================
-- Besoin 2: lister les héros avec total_hp >= 600
-- Modèle (clé de partition = hp_bucket, plage sur total_hp):
CREATE TABLE IF NOT EXISTS overwatch.heroes_by_hp_bucket (
  hp_bucket text,
  total_hp int,
  hero_key text,
  name text,
  role text,
  armor int,
  location text,
  age int,
  PRIMARY KEY ((hp_bucket), total_hp, hero_key)
) WITH CLUSTERING ORDER BY (total_hp DESC, hero_key ASC);

-- Requête:
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes_by_hp_bucket
WHERE hp_bucket = 'all' AND total_hp >= 600;

-- ============================================================================
-- Besoin 3: lister les héros avec armure (armor > 0)
-- Modèle (clé de partition = armor_bucket, plage sur armor):
CREATE TABLE IF NOT EXISTS overwatch.heroes_by_armor_bucket (
  armor_bucket text,
  armor int,
  hero_key text,
  name text,
  role text,
  total_hp int,
  location text,
  age int,
  PRIMARY KEY ((armor_bucket), armor, hero_key)
) WITH CLUSTERING ORDER BY (armor DESC, hero_key ASC);

-- Requête:
SELECT hero_key, name, role, armor
FROM overwatch.heroes_by_armor_bucket
WHERE armor_bucket = 'all' AND armor > 0;

-- ============================================================================
-- Besoin 4: lister les héros localisés en France
-- Modèle (clé de partition = location):
CREATE TABLE IF NOT EXISTS overwatch.heroes_by_location (
  location text,
  hero_key text,
  name text,
  role text,
  total_hp int,
  armor int,
  age int,
  PRIMARY KEY ((location), hero_key)
);

-- Requête:
SELECT hero_key, name, role, location
FROM overwatch.heroes_by_location
WHERE location = 'France';

-- ============================================================================
-- Besoin 5: lister les héros de moins de 18 ans
-- Modèle (clé de partition = age_bucket, plage sur age):
CREATE TABLE IF NOT EXISTS overwatch.heroes_by_age_bucket (
  age_bucket text,
  age int,
  hero_key text,
  name text,
  role text,
  total_hp int,
  armor int,
  location text,
  PRIMARY KEY ((age_bucket), age, hero_key)
) WITH CLUSTERING ORDER BY (age ASC, hero_key ASC);

-- Requête:
SELECT hero_key, name, role, age
FROM overwatch.heroes_by_age_bucket
WHERE age_bucket = 'all' AND age < 18;
