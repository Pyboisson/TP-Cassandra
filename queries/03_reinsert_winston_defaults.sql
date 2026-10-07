-- Réinsérer Winston avec ses valeurs de base (retour aux données par défaut)
-- Si la ligne existe déjà, vous pouvez au préalable exécuter DELETE (voir 02_delete_winston.sql)

-- Nouveau modèle KISS (10 colonnes) — cette requête ne met à jour que la table source.
-- Attention: dans le modèle orienté requêtes, les tables de lecture (heroes_by_*)
-- sont normalement maintenues à l’ingestion (fan-out) via le script Python.
INSERT INTO overwatch.heroes (
  hero_key, name, role, subrole, location, age,
  health, shields, armor, total_hp
) VALUES (
  'winston',
  'Winston',
  'tank',
  'initiator',
  'Horizon Lunar Colony (formerly), Watchpoint: Gibraltar',
  31,
  425,
  0,
  200,
  625
);
