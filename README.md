# SuperStore ETL Docker Airflow Project

## Objectif du projet

L'objectif de ce projet est de construire un pipeline ETL (Extraction, Transformation, Chargement) pour traiter les données de vente d'un magasin SuperStore. Ce projet utilise Docker pour orchestrer plusieurs services, dont Airflow pour la gestion du pipeline ETL, MySQL pour le stockage des données, et Jupyter pour l'analyse des données. Les données brutes sont extraites d'un fichier CSV, nettoyées et transformées, puis chargées dans une base de données MySQL pour une analyse ultérieure.

## Structure du projet

La structure du projet est organisée comme suit :

```
superstore-etl-docker-airflow-project/
├── docker-compose.yml
├── .env
├── airflow/
│   ├── dags/
│   │   └── superstore_etl.py
│   ├── logs/
│   ├── plugins/
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│    └── SuperStoreRawData.csv
├── jupyter/
│    └── Dockerfile
│    └── requirements.txt
├── mysql/
│    ├── init.sql
│    └── my.cnf
└── notebooks/
    └── analysis.ipynb
```

### Détails des dossiers et fichiers

- **docker-compose.yml** : Fichier de configuration Docker Compose qui orchestre tous les services nécessaires (MySQL, Airflow, Jupyter, Adminer).
- **.env** : Fichier de variables d'environnement pour configurer les mots de passe, les noms de base de données, et autres paramètres nécessaires aux services.
- **airflow/** :
  - **dags/** : Contient le script Airflow `superstore_etl.py` qui définit le pipeline ETL.
  - **logs/** : Répertoire pour les logs générés par Airflow.
  - **plugins/** : Répertoire pour ajouter des plugins Airflow personnalisés.
  - **Dockerfile** : Fichier Docker pour créer une image Airflow personnalisée avec les dépendances spécifiées dans `requirements.txt`.
  - **requirements.txt** : Fichier contenant les dépendances Python nécessaires à Airflow, comme `mysql-connector-python`.
- **data/** :
  - **SuperStoreRawData.csv** : Fichier de données brutes à traiter par le pipeline ETL.
- **jupyter/** :
  - **Dockerfile** : Fichier Docker pour créer une image Jupyter personnalisée capable de se connecter à la base de données MySQL.
  - **requirements.txt** : Fichier contenant les packages Python nécessaires à Jupyter, comme `mysql-connector-python`, `SQLAlchemy`, ...
- **mysql/** :
  - **init.sql** : Script SQL pour initialiser la base de données (non utilisé directement dans le pipeline mais disponible si nécessaire).
  - **my.cnf** : Fichier de configuration MySQL personnalisé.
- **notebooks/** :
  - **analysis.ipynb** : Notebook Jupyter pour l'analyse exploratoire des données chargées dans MySQL.

## Fichier `.env`

Créez un fichier `.env` à la racine du projet avec le contenu suivant comme exemple :

```env
# MySQL environment variables for Airflow
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=airflow_db
MYSQL_HOST=mysql
MYSQL_USER=airflow
MYSQL_PASSWORD=123

# MySQL environment variables for SuperStore
SUPERSTORE_MYSQL_DATABASE=superstore
DATA_FILE_PATH=/data/SuperStoreRawData.csv
```

Le fichier `.env` contient des variables d'environnement qui sont utilisées pour configurer les services MySQL et les chemins de fichiers dans votre projet. Voici les variables définies :

- **MYSQL_ROOT_PASSWORD** : Mot de passe pour l'utilisateur root de MySQL.
- **MYSQL_DATABASE** : Nom de la base de données utilisée par Airflow.
- **MYSQL_HOST** : Hôte de la base de données MySQL (nom du service dans Docker Compose).
- **MYSQL_USER** : Nom d'utilisateur pour MySQL (utilisé par Airflow et pour l'ETL).
- **MYSQL_PASSWORD** : Mot de passe pour l'utilisateur MySQL.
- **SUPERSTORE_MYSQL_DATABASE** : Nom de la base de données spécifique pour les données SuperStore.
- **DATA_FILE_PATH** : Chemin du fichier CSV contenant les données SuperStore, monté dans le conteneur Docker.

## Modélisation ERD

La base de données MySQL pour ce projet est structurée selon un schéma relationnel classique, où les données sont organisées en plusieurs tables interconnectées. Chaque table représente une entité clé du modèle de données SuperStore, avec des relations bien définies entre elles via des clés primaires et étrangères. Le diagramme ERD ci-dessous illustre la structure et les relations entre ces tables :

![ERD](erd.png)

### Détails des tables

#### 1. **customers** (Clients)
- **Description** : Cette table stocke les informations sur les clients.
- **Colonnes** :
  - `customer_id` (PRIMARY KEY) : Identifiant unique pour chaque client.
  - `customer_name` : Nom du client.
  - `segment` : Segment de marché auquel appartient le client (par exemple, "Consommateur", "Entreprise").
  
#### 2. **products** (Produits)
- **Description** : Cette table contient des informations sur les produits vendus par le SuperStore.
- **Colonnes** :
  - `product_id` (PRIMARY KEY) : Identifiant unique pour chaque produit.
  - `product_name` : Nom du produit.
  - `category` : Catégorie du produit (par exemple, "Mobilier", "Fournitures de bureau").
  - `sub_category` : Sous-catégorie du produit (par exemple, "Chaises", "Accessoires de bureau").
  
#### 3. **sales_reps** (Représentants des ventes)
- **Description** : Cette table garde une trace des représentants des ventes et de leurs équipes.
- **Colonnes** :
  - `sales_rep` (PRIMARY KEY) : Identifiant unique ou nom du représentant commercial.
  - `sales_team` : Nom de l'équipe de vente à laquelle appartient le représentant.
  - `sales_team_manager` : Nom du manager de l'équipe de vente.
  
#### 4. **locations** (Emplacements)
- **Description** : Cette table stocke les informations relatives aux emplacements (villes, états) où les ventes ont lieu.
- **Colonnes** :
  - `location_id` (PRIMARY KEY) : Identifiant unique pour chaque emplacement (peut être une combinaison du code postal et de la ville).
  - `city` : Nom de la ville.
  - `state` : État ou région.
  - `postal_code` : Code postal.
  - `region` : Région géographique (par exemple, "Nord", "Sud").

#### 5. **orders** (Commandes)
- **Description** : Cette table contient des informations de haut niveau sur les commandes passées par les clients.
- **Colonnes** :
  - `order_id` (PRIMARY KEY) : Identifiant unique pour chaque commande.
  - `order_date` : Date à laquelle la commande a été passée.
  - `ship_date` : Date d'expédition de la commande.
  - `ship_mode` : Mode d'expédition utilisé (par exemple, "Classe standard", "Seconde classe").

#### 6. **order_details** (Détails des commandes)
- **Description** : Cette table enregistre les détails spécifiques pour chaque commande, y compris les produits commandés, les quantités, et les ventes.
- **Colonnes** :
  - `order_detail_id` (PRIMARY KEY, AUTO_INCREMENT) : Identifiant unique pour chaque enregistrement de détail de commande.
  - `order_id` (FOREIGN KEY) : Fait référence à `order_id` dans la table `orders`.
  - `product_id` (FOREIGN KEY) : Fait référence à `product_id` dans la table `products`.
  - `customer_id` (FOREIGN KEY) : Fait référence à `customer_id` dans la table `customers`.
  - `sales_rep` (FOREIGN KEY) : Fait référence à `sales_rep` dans la table `sales_reps`.
  - `location_id` (FOREIGN KEY) : Fait référence à `location_id` dans la table `locations`.
  - `sales` : Montant des ventes pour cet enregistrement.
  - `quantity` : Quantité de produit commandée.
  - `discount` : Remise appliquée à cet enregistrement.
  - `profit` : Bénéfice réalisé sur cet enregistrement.

### Relations entre les tables

Les relations entre les tables sont établies via des clés étrangères (`FOREIGN KEY`), assurant l'intégrité des données à travers la base de données :

- **orders** ↔ **order_details** : La table `orders` est liée à `order_details` via la clé primaire `order_id`, permettant de regrouper tous les détails associés à une commande spécifique.
- **products** ↔ **order_details** : La table `products` est liée à `order_details` via la clé primaire `product_id`, associant chaque produit à ses détails de commande respectifs.
- **customers** ↔ **order_details** : La table `customers` est liée à `order_details` via la clé primaire `customer_id`, permettant de relier chaque détail de commande à un client spécifique.
- **sales_reps** ↔ **order_details** : La table `sales_reps` est liée à `order_details` via la clé primaire `sales_rep`, associant chaque vente à un représentant commercial.
- **locations** ↔ **order_details** : La table `locations` est liée à `order_details` via la clé primaire `location_id`, liant chaque commande à un emplacement spécifique.

Ces relations permettent de structurer les données de manière à garantir leur cohérence et à faciliter les requêtes complexes pour des analyses approfondies.

## Pipeline ETL

Le pipeline ETL est géré par Apache Airflow et est défini dans le fichier `superstore_etl.py`. Le processus complet est organisé en quatre tâches principales :

1. **create_tables** : Cette tâche crée les tables nécessaires dans la base de données MySQL conformément à la modélisation ERD (Entity-Relationship Diagram) définie pour le projet. Chaque table est créée avec des colonnes spécifiques, des clés primaires et des clés étrangères pour garantir l'intégrité et la structure des données. La création des tables suit strictement le schéma relationnel, en veillant à établir les relations entre les entités telles que `customers`, `products`, `orders`, `order_details`, etc.

2. **extract** : Cette tâche extrait les données brutes du fichier CSV `SuperStoreRawData.csv` et les enregistre dans un fichier temporaire sur le système de fichiers local. Ces données brutes constituent la matière première pour les étapes de transformation suivantes.

3. **transform** : Cette tâche nettoie et transforme les données extraites pour qu'elles soient prêtes à être chargées dans la base de données MySQL. Les étapes de transformation incluent :
   - **Gestion des valeurs manquantes** : Les lignes contenant des valeurs nulles ou manquantes sont supprimées pour garantir la qualité des données.
   - **Suppression des duplicatas** : Les doublons sont supprimés afin d'éviter toute redondance dans la base de données.
   - **Traitement des valeurs aberrantes** : Les valeurs de la colonne `sales` qui sont considérées comme aberrantes (trop faibles ou trop élevées) par rapport à l'écart interquartile (IQR) sont filtrées.
   - **Uniformisation des formats de données** : Les dates sont normalisées au format `YYYY-MM-DD` pour assurer la cohérence dans la base de données.
   - **Correction des valeurs incorrectes** : Les valeurs négatives dans la colonne `quantity` sont corrigées en utilisant la valeur absolue.
   - Les données transformées sont ensuite enregistrées dans un fichier temporaire pour être prêtes à être chargées.

4. **load** : Cette tâche charge les données transformées dans les tables MySQL. Pour chaque ligne du fichier de données transformées :
   - Les données sont insérées dans les tables correspondantes (`customers`, `products`, `sales_reps`, `locations`, `orders`, `order_details`).
   - Les opérations `INSERT` utilisent la clause `ON DUPLICATE KEY UPDATE` pour s'assurer que les enregistrements existants sont mis à jour sans créer de doublons. Cela garantit que les dernières informations sont correctement enregistrées dans la base de données.
   - Les relations définies par les clés étrangères sont respectées lors de l'insertion des données, assurant ainsi l'intégrité référentielle entre les tables.

### Utilisation du pipeline ETL

Pour exécuter le pipeline ETL, suivez ces étapes :

1. **Démarrer les services** :
   - Assurez-vous que Docker et Docker Compose sont installés sur votre machine.
   - Lancez tous les services en exécutant la commande suivante dans le répertoire du projet :
     ```bash
     docker-compose up -d
     ```

2. **Accéder à l'interface Airflow** :
   - Airflow est accessible via votre navigateur à l'adresse `http://localhost:8080`.
   - Utilisez les identifiants par défaut (nom d'utilisateur : `admin`, mot de passe : `admin`) pour vous connecter.
   
3. **Accéder à Adminer** :
   - Adminer, un outil de gestion de base de données, est accessible via votre navigateur à l'adresse `http://localhost:8081`.
   - Utilisez les mêmes informations de connexion que celles définies dans le fichier `.env` pour accéder à votre base de données MySQL.

4. **Exécuter le DAG** :
   - Activez le DAG `superstore_etl` dans l'interface Airflow pour commencer à traiter les données.

## Analyse des données avec Jupyter

Une fois les données chargées dans MySQL, vous pouvez les analyser en utilisant le notebook Jupyter fourni (`analysis.ipynb`).

### Utilisation de Jupyter

1. **Accéder à Jupyter** :
   - Jupyter est accessible via votre navigateur à l'adresse `http://localhost:8887`.
   - Aucune authentification n'est nécessaire.

2. **Exécuter le Notebook** :
   - Ouvrez et exécutez le notebook `analysis.ipynb` pour charger et visualiser les données de la table `order_details` dans un DataFrame pandas.

## Conclusion

Ce projet met en place un pipeline ETL complet en utilisant Airflow, MySQL et Jupyter, et démontre comment orchestrer ces outils efficacement dans un environnement Docker. Vous pouvez étendre ce projet pour inclure des analyses plus approfondies, des visualisations de données ou même des modèles prédictifs basés sur les données SuperStore.

Si vous avez des questions ou des suggestions, n'hésitez pas à contribuer au projet ou à ouvrir une issue.
