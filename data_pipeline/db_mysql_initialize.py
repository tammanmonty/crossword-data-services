import mysql.connector

# Database name to be created and used for storing crossword data
DB_NAME = ('CROSSWORD_DB')


def get_mysql_connection():
    """
    Creates a connection to MySQL server without selecting a specific database.
    Used for initial database creation operations.

    Returns:
        MySQL connection object
    """
    return mysql.connector.connect(
        host="localhost",  # MySQL server running on local machine
        user="root",  # MySQL root user
        passwd="local_password",  # Root user password (NOTE: Should use env variables in production)
    )


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
    conn = get_mysql_connection()
    cursor = conn.cursor()

    print("Initializing DB")

    # Create database only if it doesn't exist (IF NOT EXISTS prevents errors on reruns)
    create_db_query = '''CREATE \
    DATABASE IF NOT EXISTS CROSSWORD_DB;'''
    cursor.execute(create_db_query)
    conn.commit()

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
        id \
        int \
        AUTO_INCREMENT \
        PRIMARY \
        KEY,  -- Unique identifier, auto-generated \
        clue \
        text \
        NOT \
        NULL, -- Required: the crossword clue text \
        answer \
        varchar \
                            ( \
        255 \
                            ) NOT NULL, -- Required: the answer (max 255 chars)
        definition text NOT NULL -- Required: the definition/hint
        )'''

    cursor.execute(create_table_query)
    conn.commit()

    # Clean up database resources
    cursor.close()
    conn.close()


def initialize_mysql():
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

# Entry point when script is run directly (currently commented out)
# if __name__ == "__main__":
#     initialize_mysql()