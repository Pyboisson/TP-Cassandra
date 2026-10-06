-- REQ-01: Lister tous les héros tank (pour composer une frontline)
SELECT hero_key, name, role
FROM overwatch.heroes
WHERE role = 'tank' ALLOW FILTERING;
