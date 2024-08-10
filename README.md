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

La base de données MySQL est structurée en plusieurs tables, représentant les différentes entités du projet. Le diagramme ERD suivant montre la relation entre ces entités :

![ERD](erd.png)


### Tables principales

- **customers** : Informations sur les clients (ID, nom, segment).
- **products** : Informations sur les produits (ID, nom, catégorie, sous-catégorie).
- **sales_reps** : Informations sur les représentants commerciaux (ID, équipe, manager).
- **locations** : Détails des emplacements (ID, ville, état, code postal, région).
- **orders** : Informations sur les commandes (ID, date de commande, date d'expédition, mode d'expédition).
- **order_details** : Détails de chaque commande (ID, produit, client, représentant commercial, emplacement, ventes, quantité, remise, profit).

## Pipeline ETL

Le pipeline ETL est géré par Airflow et est défini dans le fichier `superstore_etl.py`. Le processus complet est organisé en quatre tâches principales :

1. **create_tables** : Cette tâche crée les tables nécessaires dans la base de données MySQL.
2. **extract** : Cette tâche extrait les données brutes du fichier CSV `SuperStoreRawData.csv` et les enregistre dans un fichier temporaire.
3. **transform** : Cette tâche nettoie et transforme les données extraites, en supprimant les doublons, en gérant les valeurs manquantes, et en normalisant les formats de données.
4. **load** : Cette tâche charge les données transformées dans les tables MySQL.

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
