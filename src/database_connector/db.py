import os
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error
from typing import Dict, Any, Optional

load_dotenv(find_dotenv(), override=True)

def connect_db(config: Dict[str, str] = None) -> Optional[mysql.connector.MySQLConnection]:
    """
    Create a database connection using the provided configuration.
    
    Args:
        config (Dict[str, str], optional): Database configuration dictionary containing
            host, user, password, and database name. If None, will use environment variables.
    
    Returns:
        Optional[mysql.connector.MySQLConnection]: Database connection if successful,
            None otherwise.
    """
    try:
        if config is None:
            config = {
                'host': os.getenv('DB_HOST'),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'database': os.getenv('DB_NAME')
            }
            
        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return None

def execute_query(connection: mysql.connector.MySQLConnection, query: str, params: tuple = None) -> Optional[Any]:
    """
    Execute a database query.
    
    Args:
        connection (mysql.connector.MySQLConnection): Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters
    
    Returns:
        Optional[Any]: Query result if successful, None otherwise
    """
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.rowcount
        
        cursor.close()
        return result
    except Error as e:
        print(f"Error executing query: {e}")
        return None