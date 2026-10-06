-- Mettre les PV (total) de Winston à 10000
-- On place toute la vie dans "health" et on remet armor/shields à 0 pour garder total_hp cohérent
UPDATE overwatch.heroes
SET health = 10000,
    armor = 0,
    shields = 0,
    total_hp = 10000
WHERE hero_key = 'winston';
