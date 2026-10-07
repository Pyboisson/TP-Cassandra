-- Utile pour identifier des héros robustes pour des objectifs spécifiques
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes_by_hp_bucket
WHERE hp_bucket = 'all' AND total_hp >= 600;
