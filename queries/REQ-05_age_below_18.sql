-- Hypothèse: la colonne age est de type int
 
SELECT hero_key, name, role, age
FROM overwatch.heroes_by_age_bucket
WHERE age_bucket = 'all' AND age < 18;
