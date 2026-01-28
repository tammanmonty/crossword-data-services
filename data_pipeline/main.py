import sys
import logging
from download_crossword_data import download_cryptics_dataset, cleaning_cryptic_data
from db_mysql_initialize import initialize_db, get_db_connection, initialize_tables
from db_upload_mysql import upload_dataset_mysql
from config.config import CLEAN_FILE, ENV
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """
    Main execution pipeline for the crossword data processing system.

    Pipeline stages:
    1. EXTRACT: Download raw data from API
    2. TRANSFORM: Clean and validate the data
    3. LOAD: Initialize database and upload cleaned data

    This ETL (Extract, Transform, Load) pipeline ensures data flows from
    source to database in a structured, repeatable manner.
    """
    try:
        logger.info(f'Starting data processing pipeline for {ENV} environment')
        # ========== STAGE 1: EXTRACT ==========
        # Download raw crossword clues and answers from the online source
        logger.info('Stage 1: Extracting data from Crossword Clues API')
        download_cryptics_dataset()

        # ========== STAGE 2: CLEAN AND TRANSFORM ==========
        # Clean the data: normalize text, filter invalid entries, remove duplicates
        logger.info('Stage 2: Clean and transform the data')
        cleaning_cryptic_data()

        if not CLEAN_FILE.exists():
            raise FileNotFoundError(f'File {CLEAN_FILE} does not exist')

        # Read the cleaned JSON data
        with open(CLEAN_FILE, encoding='utf-8') as json_file:
            values = json.load(json_file)

        if not values:
            raise ValueError('Cleaned dataset is empty')
        logger.info(f'Loaded {len(values)} records from cleaned data')

        # ========== STAGE 3: LOAD - DATA UPLOAD ==========
        logger.info(f'Stage 3: Loading the data to database instance')
        # Upload all cleaned records to the MySQL database
        upload_dataset_mysql(values)


    except FileNotFoundError as f:
        logger.error(f'File not found: {f}')
        return 1
    except ValueError as v:
        logger.error(f'Cleaned file is empty: {v}')
        return 1
    except ConnectionError as ce:
        logger.error(f'Connection error: {ce}')
        return 1
    except Exception as e:
        logger.error(f'Unexpected error pipeline: {e}')
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)