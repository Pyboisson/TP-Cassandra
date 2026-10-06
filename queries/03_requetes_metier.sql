-- 03_requetes_metier.sql
-- Requêtes métier principales (extraits)

-- 1) Tous les tanks
SELECT hero_key, name, role
FROM overwatch.heroes
WHERE role = 'tank' ALLOW FILTERING;

-- 2) Héros total_hp >= 600
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes
WHERE total_hp >= 600 ALLOW FILTERING;

-- 3) Héros avec armure > 0
SELECT hero_key, name, role, armor
FROM overwatch.heroes
WHERE armor > 0 ALLOW FILTERING;

-- 4) Héros dont la location est France
SELECT hero_key, name, role, location
FROM overwatch.heroes
WHERE location = 'France' ALLOW FILTERING;

-- 5) Héros de moins de 18 ans
SELECT hero_key, name, role, age
FROM overwatch.heroes
WHERE age < 18 ALLOW FILTERING;
