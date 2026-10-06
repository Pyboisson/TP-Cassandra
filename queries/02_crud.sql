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
