-- REQ-02: Héros avec un total de PV (total_hp) supérieur ou égal à 600
-- Utile pour identifier des héros robustes pour des objectifs spécifiques
SELECT hero_key, name, role, total_hp
FROM overwatch.heroes
WHERE total_hp >= 600 ALLOW FILTERING;
