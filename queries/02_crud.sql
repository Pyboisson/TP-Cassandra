-- 02_crud.sql
-- Exemples d'opérations CRUD sur la table overwatch.heroes

-- CREATE / INSERT: insérer (ou réinsérer) un héros minimal
INSERT INTO overwatch.heroes (hero_key, name, role, total_hp)
VALUES ('test_hero', 'Test Hero', 'damage', 200);

-- READ: lecture par clé primaire
SELECT hero_key, name, role, total_hp FROM overwatch.heroes WHERE hero_key = 'test_hero';

-- UPDATE: modifier des attributs
UPDATE overwatch.heroes
SET health = 150, armor = 25, shields = 25, total_hp = 200
WHERE hero_key = 'test_hero';

-- DELETE: supprimer un héros par clé
DELETE FROM overwatch.heroes WHERE hero_key = 'test_hero';

-- NOTE IMPORTANTE
-- Ces opérations modifient uniquement la table source overwatch.heroes.
-- Dans ce TP, les tables de lecture (heroes_by_role, heroes_by_hp_bucket, ...)
-- sont alimentées/maintenues à l’écriture par le script d’ingestion (writes en éventail).
-- Si vous insérez/éditez/supprimez directement dans overwatch.heroes,
-- pensez que les tables de lecture ne seront pas mises à jour automatiquement par ces scripts CQL.
