-- Objectif: lister les héros qui possèdent une valeur d'armure strictement positive
-- Requête sans ALLOW FILTERING via table orientée requête
SELECT hero_key, name, role, armor
FROM overwatch.heroes_by_armor_bucket
WHERE armor_bucket = 'all' AND armor > 0;
