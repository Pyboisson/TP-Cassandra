-- 01_verification.sql
-- Objectif: vérifier rapidement le keyspace, la table et un échantillon des données

-- Nombre total de héros importés
SELECT count(*) FROM overwatch.heroes;

-- Échantillon des héros (limite à 10)
SELECT hero_key, name, role, total_hp FROM overwatch.heroes LIMIT 10;

-- Format JSON (utile pour auditer la structure brute)
SELECT JSON hero_key, name, role, total_hp FROM overwatch.heroes LIMIT 5;
