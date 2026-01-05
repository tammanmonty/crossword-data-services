from download_crossword_data import *
from db_mysql_initialize import *
from db_upload_mysql import *

if __name__ == '__main__':
    """
    Main execution pipeline for the crossword data processing system.

    Pipeline stages:
    1. EXTRACT: Download raw data from API
    2. TRANSFORM: Clean and validate the data
    3. LOAD: Initialize database and upload cleaned data

    This ETL (Extract, Transform, Load) pipeline ensures data flows from
    source to database in a structured, repeatable manner.
    """

    # ========== STAGE 1: EXTRACT & TRANSFORM ==========
    # Download raw crossword clues and answers from the online source
    download_cryptics_dataset()

    # Clean the data: normalize text, filter invalid entries, remove duplicates
    cleaning_cryptic_data()

    # ========== STAGE 2: LOAD - DATABASE SETUP ==========
    # Create MySQL database and required tables if they don't exist
    initialize_mysql()

    # ========== STAGE 3: LOAD - DATA UPLOAD ==========
    # Read the cleaned JSON data
    with open(CLEAN_FILE) as json_file:
        values = json.load(json_file)

    # Upload all cleaned records to the MySQL database
    upload_dataset_mysql(values)