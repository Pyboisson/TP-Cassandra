-- 03_requetes_metier.sql
-- Requêtes métier principales (tables orientées requêtes — sans ALLOW FILTERING)

-- 1) Tous les tanks
SELECT hero_key, name, 'tank' AS role
FROM overwatch.heroes_by_role
WHERE role = 'tank';

-- 2) Héros total_hp >= 600
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes_by_hp_bucket
WHERE hp_bucket = 'all' AND total_hp >= 600;

-- 3) Héros avec armure > 0
SELECT hero_key, name, role, armor
FROM overwatch.heroes_by_armor_bucket
WHERE armor_bucket = 'all' AND armor > 0;

-- 4) Héros dont la location est France
SELECT hero_key, name, role, location
FROM overwatch.heroes_by_location
WHERE location = 'France';

-- 5) Héros de moins de 18 ans
SELECT hero_key, name, role, age
FROM overwatch.heroes_by_age_bucket
WHERE age_bucket = 'all' AND age < 18;
