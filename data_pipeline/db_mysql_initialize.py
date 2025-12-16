import mysql.connector

DB_NAME = ('CROSSWORD_DB')

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="local_password",
    )

def get_db_connection():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute(f"USE {DB_NAME}")

    conn.commit()
    cursor.close()

    return conn

def initialize_db():
    conn = get_mysql_connection()

    cursor = conn.cursor()
    create_db_query = '''CREATE DATABASE IF NOT EXISTS CROSSWORD_DB;'''
    cursor.execute(create_db_query)
    conn.commit()

    cursor.close()
    conn.close()

def initilize_tables(conn):
    cursor = conn.cursor()

    create_table_query = '''CREATE TABLE IF NOT EXISTS CROSSWORD_CLUES (
    id int AUTO_INCREMENT PRIMARY KEY,
    clue text NOT NULL,
    answer varchar(255) NOT NULL,
    definition text NOT NULL
    )'''

    cursor.execute(create_table_query)
    conn.commit()

    cursor.close()
    conn.close()

def initialize_mysql():
    initialize_db()
    conn = get_db_connection()
    initilize_tables(conn)


if __name__ == "__main__":
    initialize_mysql()