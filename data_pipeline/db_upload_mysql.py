import json
import mysql.connector
from pathlib import Path

# Define path to cleaned data file
CLEAN_DIR = Path('clean')
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_FILE = CLEAN_DIR / 'cryptics_clean.json'


def get_mysql_connection():
    """
    Establishes connection to the CROSSWORD_DB database.

    Returns:
        MySQL connection object connected to CROSSWORD_DB

    Note: Database credentials should be stored in environment variables in production
    """
    return mysql.connector.connect(
        host="localhost",  # MySQL server location
        user="root",  # Database user
        passwd="local_password",  # User password (SECURITY: Use env vars in production)
        database="CROSSWORD_DB",  # Connect directly to the crossword database
    )


def insert_crossword_clue(cursor, clue_data):
    """
    Inserts a single crossword clue record into the CROSSWORD_CLUES table.

    Args:
        cursor: Active MySQL cursor for executing queries
        clue_data: Dictionary containing 'clue', 'answer', and 'definition' keys

    Uses parameterized query (%s placeholders) to prevent SQL injection attacks.
    """
    # Parameterized SQL query - %s placeholders are safely replaced by mysql.connector
    sql_query = '''INSERT INTO CROSSWORD_CLUES (clue, answer, definition) \
                   VALUES (%s, %s, %s);'''

    # Extract values from dictionary in the order expected by the query
    values = (
        clue_data['clue'],
        clue_data['answer'],
        clue_data['definition']
    )

    # Execute the insert with parameterized values
    cursor.execute(sql_query, values)


def upload_dataset_mysql(dataset):
    """
    Uploads an entire dataset of crossword clues to the MySQL database.

    Args:
        dataset: List of dictionaries, each containing clue data

    Process:
    1. Establishes database connection
    2. Iterates through dataset and inserts each record
    3. Commits all changes as a single transaction
    4. Handles errors and ensures proper cleanup
    """
    try:
        # Establish connection to MySQL database
        mysql_db = get_mysql_connection()
        cursor = mysql_db.cursor()

        # Insert each clue from the dataset
        for item in dataset:
            insert_crossword_clue(cursor, item)

        # Commit all inserts as a single transaction for better performance and data integrity
        mysql_db.commit()
        print(f"Inserted {len(dataset)} rows into MYSQL database successfully")

    except mysql.connector.Error as err:
        # Handle any MySQL-specific errors (connection issues, constraint violations, etc.)
        print("Error: %s" % err)

    finally:
        # Always clean up database resources, even if errors occurred
        if mysql_db.is_connected():
            cursor.close()
            mysql_db.close()

# Entry point when script is run directly (currently commented out)
# if __name__ == "__main__":
#     # Load cleaned data from JSON file
#     with open(CLEAN_FILE) as json_file:
#         values = json.load(json_file)
#     # Upload to database
#     upload_dataset_mysql(values)