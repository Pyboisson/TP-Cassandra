-- Supprimer Winston de la table
DELETE FROM overwatch.heroes WHERE hero_key = 'winston';

-- NOTE: Cette suppression ne met à jour que la table source.
-- Les tables de lecture (heroes_by_*) peuvent contenir encore des lignes pour 'winston'
-- si elles ont été alimentées précédemment. Le modèle prévu est de gérer ces tables
-- à l’ingestion via le script Python (writes en éventail), pas par des CRUD manuels.
