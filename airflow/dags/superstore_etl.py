from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os

# Arguments par défaut pour les tâches
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
dag = DAG(
    'superstore_etl',
    default_args=default_args,
    description='ETL process to extract, transform and load SuperStore data from a csv file',
    schedule_interval=timedelta(minutes=60),  # Planifie le DAG pour s'exécuter toutes les 60 minutes
    start_date=datetime(2024, 8, 9),
    catchup=False,
)

# Function to try parsing a date with multiple formats
def try_parsing_date(text):
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'):
        try:
            return pd.to_datetime(text, format=fmt)
        except (ValueError, TypeError):
            pass
    return pd.to_datetime(text, errors='coerce')  # Fallback to automatic parsing

# Fonction pour créer les tables appropriées dans MySQL
def create_tables(**kwargs):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('SUPERSTORE_MYSQL_DATABASE')
        )
        if connection.is_connected():
            cursor = connection.cursor()

            # Supprimer les tables existantes
            cursor.execute("DROP TABLE IF EXISTS order_details;")
            cursor.execute("DROP TABLE IF EXISTS orders;")
            cursor.execute("DROP TABLE IF EXISTS customers;")
            cursor.execute("DROP TABLE IF EXISTS products;")
            cursor.execute("DROP TABLE IF EXISTS sales_reps;")
            cursor.execute("DROP TABLE IF EXISTS locations;")
            
            # Créer la table customers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id VARCHAR(50) PRIMARY KEY,
                    customer_name VARCHAR(100),
                    segment VARCHAR(50)
                );
                """
            )
            
            # Créer la table products
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id VARCHAR(50) PRIMARY KEY,
                    product_name VARCHAR(150),
                    category VARCHAR(50),
                    sub_category VARCHAR(50)
                );
                """
            )
            
            # Créer la table sales_reps
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sales_reps (
                    sales_rep VARCHAR(100) PRIMARY KEY,
                    sales_team VARCHAR(50),
                    sales_team_manager VARCHAR(50)
                );
                """
            )
            
            # Créer la table locations
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS locations (
                    location_id VARCHAR(50) PRIMARY KEY,
                    city VARCHAR(100),
                    state VARCHAR(50),
                    postal_code INT,
                    region VARCHAR(50)
                );
                """
            )
            
            # Créer la table orders
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    order_date DATE,
                    ship_date DATE,
                    ship_mode VARCHAR(50)
                );
                """
            )
            
            # Créer la table order_details
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS order_details (
                    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id VARCHAR(50),
                    product_id VARCHAR(50),
                    customer_id VARCHAR(50),
                    sales_rep VARCHAR(100),
                    location_id VARCHAR(50),
                    sales DECIMAL(10, 2),
                    quantity INT,
                    discount DECIMAL(10, 2),
                    profit DECIMAL(10, 2),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY (sales_rep) REFERENCES sales_reps(sales_rep),
                    FOREIGN KEY (location_id) REFERENCES locations(location_id)
                );
                """
            )

            connection.commit()
            cursor.close()
            print("Tables created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

# Fonction pour extraire les données
def extract():
    data_file_path = os.getenv('DATA_FILE_PATH')
    df = pd.read_csv(data_file_path)
    df.to_csv('/tmp/superstore_data_clean.csv', index=False)

def transform():
    df = pd.read_csv('/tmp/superstore_data_clean.csv')

    # 1. Gérer les valeurs manquantes
    # Supprimer les lignes avec des valeurs manquantes
    df = df.dropna()
    
    # 2. Supprimer les duplicata
    df = df.drop_duplicates()
    
    # 3. Traiter les valeurs aberrantes
    Q1 = df['sales'].quantile(0.25)
    Q3 = df['sales'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df['sales'] < (Q1 - 1.5 * IQR)) | (df['sales'] > (Q3 + 1.5 * IQR)))]
    
    # 4. Uniformiser les formats de données
    # Apply the parsing function to each date column
    for col in ['order_date', 'ship_date']:
        df[col] = df[col].apply(try_parsing_date).dt.strftime('%Y-%m-%d')
    
    # 5. Corriger les valeurs incorrectes
    df['quantity'] = df['quantity'].abs()

    # Enregistrer les données nettoyées
    df.to_csv('/tmp/superstore_data_transformed.csv', index=False)

def load():
    # Connexion à la base de données
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('SUPERSTORE_MYSQL_DATABASE')
    )
    
    cursor = conn.cursor()
    
    df = pd.read_csv('/tmp/superstore_data_transformed.csv')
    
    # Insérer les données dans les tables respectives
    for index, row in df.iterrows():
        
        # Insérer dans la table customers
        cursor.execute("""
            INSERT INTO customers (customer_id, customer_name, segment)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            customer_name=VALUES(customer_name), segment=VALUES(segment)
        """, (row['customer_id'], row['customer_name'], row['segment']))
        
        # Insérer dans la table products
        cursor.execute("""
            INSERT INTO products (product_id, product_name, category, sub_category)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            product_name=VALUES(product_name), category=VALUES(category), sub_category=VALUES(sub_category)
        """, (row['product_id'], row['product_name'], row['category'], row['sub_category']))
        
        # Insérer dans la table sales_reps
        cursor.execute("""
            INSERT INTO sales_reps (sales_rep, sales_team, sales_team_manager)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            sales_team=VALUES(sales_team), sales_team_manager=VALUES(sales_team_manager)
        """, (row['sales_rep'], row['sales_team'], row['sales_team_manager']))
        
        # Insérer dans la table locations
        cursor.execute("""
            INSERT INTO locations (location_id, city, state, postal_code, region)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            city=VALUES(city), state=VALUES(state), postal_code=VALUES(postal_code), region=VALUES(region)
        """, (row['location_id'], row['city'], row['state'], row['postal_code'], row['region']))
        
        # Insérer dans la table orders
        cursor.execute("""
            INSERT INTO orders (order_id, order_date, ship_date, ship_mode)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            order_date=VALUES(order_date), ship_date=VALUES(ship_date), ship_mode=VALUES(ship_mode)
        """, (row['order_id'], row['order_date'], row['ship_date'], row['ship_mode']))
        
        # Insérer dans la table order_details
        cursor.execute("""
            INSERT INTO order_details (order_id, product_id, customer_id, sales_rep, location_id, sales, quantity, discount, profit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (row['order_id'], row['product_id'], row['customer_id'], row['sales_rep'], row['location_id'], row['sales'], row['quantity'], row['discount'], row['profit']))

    # Valider les transactions
    conn.commit()

    # Fermer le curseur et la connexion
    cursor.close()
    conn.close()

# Définition des tâches du DAG
create_tables_task = PythonOperator(
    task_id='create_tables',
    python_callable=create_tables,
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag,
)

# Définition de la séquence des tâches
create_tables_task >> extract_task >> transform_task >> load_task
