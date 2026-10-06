Plan
- Fournir une documentation complète en français prête à copier/coller dans un fichier .md.
- La documentation couvrira : but du script, prérequis, variables de configuration, description détaillée des fonctions, déroulement d’exécution, sortie attendue, et dépannage.
- Le texte sera autonome et clair pour un étudiant qui colle dans Installation_Cassandra.md ou README.md.

Documentation (copiez/collez tout ce qui suit dans votre .md)

# getapi.py — Documentation

## Objectif
Ce script Python récupère les métadonnées des stations Vélib’ depuis l’API publique de la ville de Paris, normalise la réponse et insère chaque station dans une table Cassandra. Il crée le keyspace et la table si nécessaire.

Il affiche des messages pendant l’import pour indiquer la progression, par exemple :
Récupération des données Vélib'...
20 stations récupérées.
Station importée : 10115 - Granges aux Belles
...
Import terminé.

## Emplacement attendu
script/getapi.py

## Pré-requis
- Python 3.x installé.
- Un nœud Cassandra accessible (par défaut sur 127.0.0.1:9042).
- Les paquets Python suivants :
  - requests
  - cassandra-driver

Installation des dépendances :
pip install requests cassandra-driver

Remarque : sur certaines plateformes, `cassandra-driver` peut nécessiter des paquets systèmes supplémentaires. Si l’installation échoue, copiez l’erreur et je vous aiderai.

## Variables de configuration (dans le script)
- API_URL : URL de l’API Vélib’ utilisée (par défaut : limit=20).
- CASSANDRA_CONTACT_POINTS : liste des points de contact pour Cassandra (par défaut ["127.0.0.1"]).
- KEYSPACE : nom du keyspace Cassandra (par défaut "velib").
- TABLE : nom de la table (par défaut "stations").

Adaptez ces variables en haut du fichier si nécessaire (par exemple pour changer l’adresse Cassandra, le nombre de stations récupérées, ou le nom du keyspace/table).

## Schéma Cassandra utilisé
Le script crée (si nécessaire) la table avec la structure suivante :

CREATE TABLE IF NOT EXISTS stations (
  station_id text PRIMARY KEY,
  name text,
  capacity int,
  latitude double,
  longitude double,
  opening_hours text
);

Le keyspace est créé avec SimpleStrategy et replication_factor = 1 :
CREATE KEYSPACE IF NOT EXISTS velib WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }

## Flux global
1. Récupération des données depuis l’API (GET).
2. Normalisation des résultats (prise en charge de deux formats courants : liste d’objets station ou liste d’objets contenant un champ `fields`).
3. Connexion au cluster Cassandra.
4. Création du keyspace / de la table si nécessaire.
5. Préparation d’une requête d’insertion et insertion de chaque station.
6. Affichage d’un message pour chaque station insérée.
7. Fermeture des connexions.

## Description détaillée des fonctions

- fetch_stations(url)
  - Envoie une requête GET à l’URL `url`.
  - Vérifie le code HTTP et convertit la réponse en JSON.
  - Extrait la liste utile via `results` ou `records`.
  - Normalise la liste : si chaque élément est un objet contenant `fields`, on retourne directement ces `fields`.
  - Retourne une liste d’objets stations (dictionnaires).

- ensure_schema(session)
  - Crée le keyspace si nécessaire (IF NOT EXISTS).
  - Sélectionne le keyspace (`session.set_keyspace(KEYSPACE)`).
  - Crée la table `stations` si nécessaire (IF NOT EXISTS) avec les colonnes listées dans le schéma.

- insert_station(session, prepared, item)
  - Extrait les champs nécessaires depuis l’objet `item` :
    - stationcode → station_id,
    - name → name,
    - capacity → capacity,
    - coordonnees_geo.lat → latitude,
    - coordonnees_geo.lon → longitude,
    - station_opening_hours → opening_hours.
  - Gère quelques variantes de noms de champs (p.ex. station_id, stationCode) et la possibilité où `coordonnees_geo` est absent (essaye lat/lon à la racine).
  - Vérifie que `station_id` est présent ; si absent, lève une exception.
  - Exécute la requête préparée d’insertion.
  - Affiche : Station importée : {station_id} - {name}

- main()
  - Orchestration générale :
    - appelle `fetch_stations`,
    - vérifie le nombre de stations et affiche "{n} stations récupérées.",
    - se connecte à Cassandra (Cluster(contact_points=CASSANDRA_CONTACT_POINTS)),
    - appelle `ensure_schema`,
    - prépare l’INSERT et appelle `insert_station` pour chaque élément,
    - gère et affiche les erreurs d’insertion pour chaque item,
    - ferme proprement session et cluster,
    - renvoie un code de sortie (0 = succès, 1 = erreur récupération API).

## Exécution
Depuis la racine du projet :
python script/getapi.py
ou
python3 script/getapi.py

Si vous exécutez depuis un environnement virtuel, activez-le avant d’installer les dépendances et d’exécuter le script.

## Sortie attendue
- Log en console montrant la récupération puis chaque station importée, par exemple :
Récupération des données Vélib'...
20 stations récupérées.
Station importée : 10115 - Granges aux Belles
Station importée : 12128 - Pyramide - Ecole du Breuil
...
Import terminé.

## Points de vigilance / dépannage
- Erreur de connexion à Cassandra :
  - Vérifiez que Cassandra tourne et que le port 9042 est exposé.
  - Vérifiez la valeur de CASSANDRA_CONTACT_POINTS (mettre l’IP/hostname correct).
  - Test rapide : depuis la machine, `cqlsh 127.0.0.1 9042` pour vérifier la connectivité.

- Erreur d’installation du driver cassandra-driver :
  - Sur Windows ou certaines distributions Linux, il peut manquer des dépendances (compilateur C, bibliothèques). Utilisez les wheel/binaries fournis par pip ou installez les paquets système requis. Si vous copiez l’erreur ici, je vous aiderai.

- L’API Vélib’ peut renvoyer des structures différentes (ex. `records` vs `results`, objets encapsulés dans `fields`) — le script gère les cas les plus usuels. Si vous avez un format inattendu, collez ici un extrait JSON et je l’adapte.

- Si `station_id` est absent pour un élément, le script lèvera une erreur pour cet élément et l’affichera. Généralement la donnée `stationcode` est toujours présente.

## Extentions et améliorations possibles
- Paginer l’API pour importer toutes les stations (augmenter `limit` ou suivre la pagination de l’API).
- Ajouter un paramètre en ligne de commande pour définir le nombre de stations à récupérer ou l’URL.
- Implémenter des insertions en batch pour améliorer les performances.
- Gérer la mise à jour (upsert) suivant un critère de version ou timestamp.
- Ajouter des logs plus structurés (module logging) et niveaux (INFO/ERROR/DEBUG).
- Vérifier les doublons avant insertion si besoin et ajouter des tests unitaires.

## Correspondance API → colonnes Cassandra
- API `stationcode` → Cassandra `station_id`
- API `name` → `name`
- API `capacity` → `capacity`
- API `coordonnees_geo.lat` → `latitude`
- API `coordonnees_geo.lon` → `longitude`
- API `station_opening_hours` → `opening_hours`

## Exemples de problèmes courants et solutions rapides
- Problème : script se termine immédiatement sans rien faire.
  - Vérifier la valeur de API_URL (peut renvoyer une liste vide si limit trop petit ou si l’API ne répond pas).
  - Afficher la réponse brute JSON pour debug (ajouter `print(resp.text)` dans fetch_stations).
- Problème : insertion échoue pour champ latitude/longitude non-numérique.
  - Vérifier le format des coordonnées renvoyées par l’API ; ajouter une conversion `float()` et gestion d’exception si nécessaire.

---

Fin de la documentation.  
Si vous voulez, je peux aussi :
- Générer une version en anglais,
- Ajouter un exemple de commande pour importer toutes les stations via pagination,
- Ajouter une section "FAQ" spécifique à votre environnement (Windows, WSL, Docker).