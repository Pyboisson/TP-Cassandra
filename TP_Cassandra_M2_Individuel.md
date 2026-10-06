# TP — Concevoir et exploiter un cluster Cassandra

**Module :** Données distribuées — M2 Big Data & IA  
**Niveau :** Master 2  
**Travail :** Individuel  
**Technologies :** Apache Cassandra · Docker · Docker Compose · CQL · Python  
**Sujet :** même sujet de données que celui choisi au TP1

---

## 1. Objectif

Après le TP1, vous passez d'une simulation de système distribué à un **véritable cluster Cassandra**.

Vous allez progressivement :

- construire un cluster Cassandra à 3 nœuds ;
- comprendre `cluster`, `datacenter`, `rack` et `node` ;
- créer un keyspace et des tables ;
- importer les données de votre TP1 ;
- comprendre partitionnement, tokens et réplication ;
- tester la cohérence et la panne d'un nœud.

> **Important :** reprenez obligatoirement le même sujet que dans le TP1 : Vélib', météo, transport, films, sport, finance, e-commerce, etc.

---

# 2. Architecture cible

```text
                    Cluster tp2-cluster
                           │
                          dc1
             ┌─────────────┼─────────────┐
             │             │             │
           rack1         rack2         rack3
             │             │             │
           cass1         cass2         cass3
```

Les nœuds sont démarrés progressivement :

```text
cass1
  ↓
cass1 + cass2
  ↓
cass1 + cass2 + cass3
```

---

# 3. Créer le projet

```bash
mkdir TP-Cassandra-Cluster
cd TP-Cassandra-Cluster
nano docker-compose.yml
```

Copiez-collez :

```yaml
services:

  cass1:
    image: cassandra:4.1
    container_name: cass1
    hostname: cass1

    networks:
      - cass-net

    ports:
      - "9042:9042"

    environment:
      CASSANDRA_CLUSTER_NAME: tp2-cluster
      CASSANDRA_SEEDS: cass1
      CASSANDRA_DC: dc1
      CASSANDRA_RACK: rack1
      CASSANDRA_ENDPOINT_SNITCH: GossipingPropertyFileSnitch
      CASSANDRA_NUM_TOKENS: 16
      MAX_HEAP_SIZE: 512M
      HEAP_NEWSIZE: 128M

    volumes:
      - cass1_data:/var/lib/cassandra


  cass2:
    image: cassandra:4.1
    container_name: cass2
    hostname: cass2

    networks:
      - cass-net

    environment:
      CASSANDRA_CLUSTER_NAME: tp2-cluster
      CASSANDRA_SEEDS: cass1
      CASSANDRA_DC: dc1
      CASSANDRA_RACK: rack2
      CASSANDRA_ENDPOINT_SNITCH: GossipingPropertyFileSnitch
      CASSANDRA_NUM_TOKENS: 16
      MAX_HEAP_SIZE: 512M
      HEAP_NEWSIZE: 128M

    volumes:
      - cass2_data:/var/lib/cassandra


  cass3:
    image: cassandra:4.1
    container_name: cass3
    hostname: cass3

    networks:
      - cass-net

    environment:
      CASSANDRA_CLUSTER_NAME: tp2-cluster
      CASSANDRA_SEEDS: cass1
      CASSANDRA_DC: dc1
      CASSANDRA_RACK: rack3
      CASSANDRA_ENDPOINT_SNITCH: GossipingPropertyFileSnitch
      CASSANDRA_NUM_TOKENS: 16
      MAX_HEAP_SIZE: 512M
      HEAP_NEWSIZE: 128M

    volumes:
      - cass3_data:/var/lib/cassandra


networks:

  cass-net:
    name: cass-net


volumes:

  cass1_data:
  cass2_data:
  cass3_data:
```

---

# 4. Construire le cluster

## 4.1 Démarrer `cass1`

```bash
docker compose up -d cass1
```

Vérifier :

```bash
docker ps
```

Puis :

```bash
docker exec -it cass1 nodetool status
```

Vous devez obtenir un nœud :

```text
UN ... rack1
```

À retenir :

- `U` = Up
- `N` = Normal
- `UN` = nœud actif et opérationnel
- `dc1` = datacenter
- `rack1` = rack

### Question 1

Expliquez brièvement ce que signifie `UN` et le rôle de `dc1` et `rack1`.

---

## 4.2 Ajouter `cass2`

Lorsque `cass1` est `UN` :

```bash
docker compose up -d cass2
```

Puis :

```bash
docker exec -it cass1 nodetool status
```

Vous devez obtenir deux nœuds `UN`.

### Question 2

Expliquez la différence entre les états :

```text
UJ
UN
```

---

## 4.3 Ajouter `cass3`

Lorsque `cass1` et `cass2` sont opérationnels :

```bash
docker compose up -d cass3
```

Puis :

```bash
docker exec -it cass1 nodetool status
```

Résultat attendu :

```text
UN ... rack1
UN ... rack2
UN ... rack3
```

Observez également :

```bash
docker exec -it cass1 nodetool describecluster
```

### Question 3

Présentez brièvement votre architecture finale :

- cluster ;
- datacenter ;
- nœuds ;
- racks ;
- tokens.

---

# 5. Créer le Keyspace

Entrer dans Cassandra :

```bash
docker exec -it cass1 cqlsh
```

Exemple avec Vélib' :

```sql
CREATE KEYSPACE velib
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};
```

Puis :

```sql
USE velib;
```

Vérifier :

```sql
DESCRIBE KEYSPACE velib;
```

### Question 4

Expliquez simplement :

```text
NetworkTopologyStrategy
dc1
RF = 3
```

Dans un cluster de trois nœuds, que signifie RF=3 pour une partition ?

---

# 6. Créer les tables

Reprenez le modèle défini à partir de votre sujet du TP1.

Exemple Vélib' :

```sql
CREATE TABLE stations (
    station_id text PRIMARY KEY,
    name text,
    capacity int,
    latitude double,
    longitude double,
    opening_hours text
);
```

Vérifier :

```sql
DESCRIBE TABLE stations;
```

Exemple avec une clustering key :

```sql
CREATE TABLE station_availability (
    station_id text,
    timestamp timestamp,
    available_bikes int,
    available_bases int,
    PRIMARY KEY (station_id, timestamp)
);
```

Dans cet exemple :

```text
station_id → Partition Key
timestamp  → Clustering Key
```

### Question 5

Pour votre modèle, indiquez :

- la partition key ;
- la clustering key éventuelle ;
- pourquoi ces clés correspondent à vos requêtes métier.

---

# 7. Importer les données du TP1

Utilisez la même source que dans votre TP1 :

```text
API
JSON
CSV
Open Data
Dataset
```

Pour Vélib' :

```text
https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records?limit=20
```

Installer les dépendances :

```bash
pip3 install requests cassandra-driver
```

Connexion Python :

```python
from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
session = cluster.connect("velib")
```

Le flux attendu est :

```text
Source
  ↓
Python
  ↓
Transformation
  ↓
Cassandra
```

Pour Vélib' :

```text
stationcode            → station_id
name                   → name
capacity               → capacity
coordonnees_geo.lat    → latitude
coordonnees_geo.lon    → longitude
station_opening_hours  → opening_hours
```

Utilisez de préférence une requête préparée pour les insertions.

Vérifier ensuite :

```sql
SELECT COUNT(*) FROM stations;
```

Puis :

```sql
SELECT * FROM stations LIMIT 10;
```

### Question 6

Indiquez :

- la source utilisée ;
- le nombre de données importées ;
- le mapping réalisé ;
- la preuve que les données sont présentes.

---

# 8. Partitionnement et tokens

Observer le cluster :

```bash
docker exec -it cass1 nodetool status
```

Observer les statistiques :

```bash
docker exec -it cass1 nodetool tablestats velib
```

Le chemin logique est :

```text
Partition Key
      ↓
Hash
      ↓
Token
      ↓
Nœud responsable
```

Avec :

```yaml
CASSANDRA_NUM_TOKENS: 16
```

chaque nœud possède plusieurs positions dans l'espace des tokens.

### Question 7

Expliquez ce mécanisme avec une partition de votre projet :

- quelle est votre partition key ?
- comment devient-elle un token ?
- comment Cassandra utilise-t-elle ce token pour distribuer les données ?

---

# 9. Tester la cohérence

Dans `cqlsh` :

```sql
CONSISTENCY ONE;
```

Faites une lecture avec votre partition key.

Puis :

```sql
CONSISTENCY QUORUM;
```

Refaites la même lecture.

Enfin :

```sql
CONSISTENCY ALL;
```

Refaites la même lecture.

Pour RF=3 :

| Niveau | Réplicas nécessaires |
|---|---:|
| ONE | 1 |
| QUORUM | 2 |
| ALL | 3 |

### Question 8

Expliquez en quelques lignes la différence entre `ONE`, `QUORUM` et `ALL`, notamment en matière de disponibilité et de tolérance à la panne.

---

# 10. Simuler une panne

Arrêter `cass3` :

```bash
docker stop cass3
```

Observer :

```bash
docker exec -it cass1 nodetool status
```

Tester à nouveau :

```sql
CONSISTENCY ONE;
```

```sql
CONSISTENCY QUORUM;
```

```sql
CONSISTENCY ALL;
```

### Question 9

Analysez vos résultats :

- quelles lectures fonctionnent ?
- lesquelles échouent éventuellement ?
- pourquoi ?
- quel rôle joue RF=3 ?

Remettre `cass3` en service :

```bash
docker start cass3
```

Puis vérifier son retour à :

```text
UN
```

---

# 11. Analyser une mauvaise partition key

Proposez une partition key qui serait mauvaise pour votre domaine.

Exemples possibles :

```text
country
city
category
type
```

si une seule valeur concentre trop de données.

### Question 10

Pour votre sujet :

1. proposez une mauvaise partition key ;
2. expliquez le risque de **hot partition** ;
3. expliquez le risque de **data skew** ;
4. proposez une meilleure stratégie.

---

# 12. Synthèse finale

Expliquez le chemin suivant avec **une requête réelle de votre projet** :

```text
Requête métier
      ↓
Partition Key
      ↓
Hash
      ↓
Token
      ↓
Nœuds responsables
      ↓
Replicas
      ↓
Consistency Level
```

### Question 11

En quelques lignes, expliquez comment Cassandra traite cette requête et comment le cluster permet de résister à la panne d'un nœud.

---

# 13. Reproduire le TP avec les données de votre TP1

Jusqu'ici, les exemples et les manipulations ont été réalisés avec **Vélib'** afin de fournir un jeu de données concret et commun à tous.

Vous devez maintenant refaire la partie ingestion avec **le sujet que vous avez choisi au TP1**.

Reprenez les mêmes données que dans votre TP1 :

```text
Votre source du TP1
        ↓
Python
        ↓
Transformation / mapping
        ↓
Cassandra
```

### Travail demandé

1. Reprendre la source de données utilisée dans votre TP1.
2. Adapter le modèle Cassandra à votre domaine.
3. Définir votre partition key et, si nécessaire, votre clustering key.
4. Créer votre keyspace et vos tables.
5. Écrire un script Python d'import.
6. Importer vos données dans Cassandra.
7. Vérifier que les données sont présentes.
8. Refaire les tests de lecture avec `ONE`, `QUORUM` et `ALL`.
9. Refaire le test de panne avec `cass3`.

### Exemple

Si votre TP1 porte sur :

```text
Météo
Transport
Films
Sport
Finance
E-commerce
```

vous devez remplacer le modèle Vélib' par **votre propre modèle de données**.

L'objectif final est d'obtenir la même chaîne de traitement que dans les exemples Vélib' :

```text
Données du TP1
      ↓
Modèle Cassandra
      ↓
Partition Key
      ↓
Token
      ↓
Distribution
      ↓
Réplication
      ↓
Consistency Level
      ↓
Test de panne
```

---

# 13. Livrable individuel

Structure minimale :

```text
TP-Cassandra-Cluster/
├── docker-compose.yml
├── README.md
├── python/
│   └── import_data.py
└── docs/
    └── compte-rendu.md
```

Le compte rendu doit contenir :

- sujet du TP1 ;
- architecture Cassandra ;
- modèle de données ;
- partition key / clustering key ;
- keyspace et tables ;
- script d'import ;
- preuve d'import ;
- RF ;
- tests `ONE`, `QUORUM`, `ALL` ;
- test de panne ;
- analyse de la partition key.

### Captures minimales

```text
1. nodetool status avec 3 nœuds
2. création du keyspace
3. création des tables
4. données importées
5. test de cohérence
6. panne de cass3
7. retour de cass3
```

Chaque capture doit être accompagnée d'une courte explication.

---

# 14. Nettoyage

Arrêter le cluster :

```bash
docker compose down
```

Pour supprimer également les volumes de ce projet :

```bash
docker compose down -v
```

> `docker compose down -v` supprime les données Cassandra stockées dans les volumes de ce projet.

---

## Conclusion

L'objectif n'est pas seulement d'obtenir trois conteneurs Cassandra fonctionnels.

Vous devez comprendre la chaîne :

```text
Requête
  ↓
Partition Key
  ↓
Token
  ↓
Distribution
  ↓
Réplication
  ↓
Cohérence
  ↓
Tolérance aux pannes
```

Le niveau attendu est celui d'un **Master 2** : les commandes doivent être accompagnées d'un raisonnement simple et justifié.
