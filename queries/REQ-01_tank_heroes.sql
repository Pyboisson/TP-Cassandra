-- REQ-01: Lister tous les héros tank (pour composer une frontline)
SELECT hero_key, name, 'tank' AS role
FROM overwatch.heroes_by_role
WHERE role = 'tank';
