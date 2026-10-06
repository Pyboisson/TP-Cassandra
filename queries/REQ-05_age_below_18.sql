-- REQ-05: Héros dont l'âge est strictement inférieur à 18 ans
-- Hypothèse: la colonne age est de type int
-- Remarque: nécessite ALLOW FILTERING avec le modèle single-table actuel

SELECT hero_key, name, role, age
FROM overwatch.heroes
WHERE age < 18 ALLOW FILTERING;
