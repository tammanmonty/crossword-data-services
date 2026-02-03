import json
import mysql.connector
from config.config import CLEAN_DIR, CLEAN_FILE, DB_CONFIG
from db_mysql_initialize import get_mysql_connection
import logging

# Create the Parent Clean Directory if it doesn't already exist
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

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
    if not dataset:
        raise ValueError("Dataset must not be empty")
    try:
        # Establish connection to MySQL database
        logger.info(f"Establishing database connection")
        mysql_db = get_mysql_connection()
        cursor = mysql_db.cursor()

        # Parameterized SQL query - %s placeholders are safely replaced by mysql.connector
        sql_query = '''INSERT \
        IGNORE INTO CROSSWORD_CLUES (clue, answer, definition) \
                       VALUES ( %s, %s, %s );'''

        # Prepare batch values
        values = [
            (item['clue'], item['answer'], item['definition'])
            for item in dataset
        ]

        cursor.executemany(sql_query, values)

        inserted_count = cursor.rowcount
        skipped_count = len(dataset) - inserted_count
        # Commit all inserts as a single transaction for better performance and data integrity
        mysql_db.commit()
        logger.info(f"Inserted {inserted_count} rows into MYSQL database successfully")
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} duplicate rows")

    except mysql.connector.Error as err:
        # Handle any MySQL-specific errors (connection issues, constraint violations, etc.)
        logger.error("Error: %s" % err)

    finally:
        # Always clean up database resources, even if errors occurred
        if mysql_db.is_connected():
            cursor.close()
            mysql_db.close()
            logger.info("MySQL database connection closed")

# Entry point when script is run directly (currently commented out)
# if __name__ == "__main__":
#     # Load cleaned data from JSON file
#     with open(CLEAN_FILE) as json_file:
#         values = json.load(json_file)
#     # Upload to database
#     upload_dataset_mysql(values)