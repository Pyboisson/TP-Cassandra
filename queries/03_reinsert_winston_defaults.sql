-- Réinsérer Winston avec ses valeurs de base (retour aux données par défaut)
-- Si la ligne existe déjà, vous pouvez au préalable exécuter DELETE (voir 02_delete_winston.sql)

INSERT INTO overwatch.heroes (
  hero_key, name, description, portrait, role, subrole, location, age, birthday,
  health, armor, shields, total_hp, abilities, backgrounds, perks_json, story, raw_json, last_update
) VALUES (
  'winston',
  'Winston',
  'A super-intelligent, genetically engineered gorilla, Winston is a brilliant scientist and a champion for humanity’s potential.',
  'https://d15f34w2p8l1cc.cloudfront.net/overwatch/46a10db3aa908c590ddc4e7606376a88143d1f1306ecfbea043263040f9529a5.png',
  'tank',
  'initiator',
  'Horizon Lunar Colony (formerly), Watchpoint: Gibraltar',
  '31',
  'Jun 6',
  425,
  200,
  0,
  625,
  [ 'Tesla Cannon', 'Jump Pack', 'Barrier Projector', 'Primal Rage' ],
  [
    'https://blz-contentstack-images.akamaized.net/v3/assets/blt2477dcaf4ebd440c/blt393ab319cd413b01/638810d775e4d50e88ea3b30/winston-00.jpg',
    'https://blz-contentstack-images.akamaized.net/v3/assets/blt2477dcaf4ebd440c/blt8b22e773484e0ecf/638810d73ae72d1147f2401a/winston-01.jpg'
  ],
  '{}',
  null,
  null,
  toTimestamp(now())
);
