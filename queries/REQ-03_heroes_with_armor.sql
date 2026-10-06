-- REQ-03: Héros disposant d'armure (armor > 0)
-- Objectif: lister les héros qui possèdent une valeur d'armure strictement positive
-- Remarque: nécessite ALLOW FILTERING avec le modèle single-table actuel

SELECT hero_key, name, role, armor
FROM overwatch.heroes
WHERE armor > 0 ALLOW FILTERING;
