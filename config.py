# config.py
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'sql123$$',
    'database': 'ecommerce_db',
    'port':     3306
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None