from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
from typing import AnyStr
from config.config import DB_NAME, DB_CONFIG, ENV, Environment
from botocore.exceptions import ClientError
import boto3
import json
import logging
import mysql.connector

logger = logging.getLogger(__name__)
logging.getLogger('mysql.connector').setLevel(logging.WARNING)

def get_rdsmysql_secret() -> AnyStr:
    secret_name = DB_CONFIG['secret_name']
    region_name = DB_CONFIG['region_name']

    # Create a Secrets Manager Client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = json.loads(get_secret_value_response['SecretString'])
        return secret
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/lates/apireference/API_GetSecretValue.html
        raise e



def get_mysql_connection():
    """
    Creates a connection to MySQL server depending on the DB_CONFIG variable set in the config. The environment file determines whether or not LOCAL configurations
    or established DEV / PROD configurations are used. This is crucial for determining the type of Database connection established. LOCAL configurations uses a
    local MySQL database connections. Alternatively, the DEV and PROD configurations connect to an AWS MySQL Instance.

    Returns:
        MySQL connection object
    """
    try:
        logger.debug(f"Connecting to MySQL DB: {DB_CONFIG}")
        if DB_CONFIG.get('use_secrets', True):
            logger.info("AWS MySQL Connection Created")

            secret = get_rdsmysql_secret()

            return mysql.connector.connect(
                host=secret['host'],
                user=secret['username'],
                password=secret['password'],
                port=secret.get('port', 3306),
                database=secret['dbname']
            )
        else:
            logger.info("Local MySQL Connection Created")
            return mysql.connector.connect(
                host=DB_CONFIG['host'],  # MySQL server running on local machine
                user=DB_CONFIG['user'],  # MySQL root user
                password=DB_CONFIG['password'], # Root user password (NOTE: Should use env variables in production)
                port=DB_CONFIG['port'], # Port
                database=DB_CONFIG['database']  # MySQL Database
            )
        logger.info("MySQL connection established successfully")
        return mysql_connection
    except ClientError as e:
        logger.error(F"MySQL Client Error: {e}")
        raise
    except mysql.connector.Error as e:
        logger.error(F"MySQL Database Error: {e}")
        raise
    except KeyError as e:
        logger.error(F"Missing Configuration Key: {e}")
        logger.error(F"DB_Config Contents: {DB_CONFIG}")
        raise
    except Exception as e:
        logger.error(F"Unexpected MySQL Connection: {e}")
        raise

def get_db_connection():
    """
    Creates a connection to MySQL server and selects the CROSSWORD_DB database.
    Used for operations that need to work within the specific database.

    Returns:
        MySQL connection object with CROSSWORD_DB selected
    """
    conn = get_mysql_connection()
    cursor = conn.cursor()

    # Switch to use the CROSSWORD_DB database
    cursor.execute(f"USE {DB_NAME}")

    # Commit the USE command (though not strictly necessary)
    conn.commit()
    cursor.close()

    return conn


def initialize_db():
    """
    Creates the CROSSWORD_DB database if it doesn't already exist.
    This is the first step in setting up the database infrastructure.
    """
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()

        print("Initializing DB")

        # Create database only if it doesn't exist (IF NOT EXISTS prevents errors on reruns)
        create_db_query = '''CREATE \
        DATABASE IF NOT EXISTS CROSSWORD_DB;'''
        cursor.execute(create_db_query)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error Initializing DB: {err}")
    finally:
        # Clean up database resources
        cursor.close()
        conn.close()


def initialize_tables(conn):
    """
    Creates the CROSSWORD_CLUES table within the database.
    Table schema:
    - id: Auto-incrementing primary key for unique identification
    - clue: Full text of the crossword clue (TEXT allows long content)
    - answer: The solution word/phrase (VARCHAR limited to 255 chars)
    - definition: The hint or definition part of the clue (TEXT)

    Args:
        conn: Active MySQL connection to the CROSSWORD_DB database
    """
    cursor = conn.cursor()

    print("Initializing tables")

    # Create table with IF NOT EXISTS to allow safe re-running of script
    create_table_query = '''CREATE TABLE IF NOT EXISTS CROSSWORD_CLUES \
    ( \
        id INT AUTO_INCREMENT PRIMARY KEY, \
        clue TEXT NOT NULL, \
        answer VARCHAR(255) NOT NULL,
        definition TEXT NOT NULL,
        UNIQUE KEY unique_clue_answer (answer, clue(255))
        )'''

    cursor.execute(create_table_query)
    conn.commit()

    # Clean up database resources
    cursor.close()
    conn.close()

# Entry point when script is run directly
if __name__ == "__main__":
    """
    Complete MySQL database initialization process:
    1. Creates the database
    2. Connects to it
    3. Creates required tables

    This is the main entry point for database setup.
    """
    # Step 1: Create the database
    initialize_db()

    # Step 2: Get connection to the newly created database
    conn = get_db_connection()

    # Step 3: Create tables within the database
    initialize_tables(conn)