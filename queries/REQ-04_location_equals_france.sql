-- REQ-04: Héros dont la location est "France"

SELECT hero_key, name, role, location
FROM overwatch.heroes
WHERE location = 'France' ALLOW FILTERING;
