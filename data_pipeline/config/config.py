from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import os



ENV = os.environ.get('ENV', 'DEV')


# BASE_DIRECTORIES
RAW_DIR = Path('raw')  # Stores original downloaded data
CLEAN_DIR = Path('clean')  # Stores cleaned and validated data
PROCESSED_DIR = Path('processed')  # Stores final processed data (e.g., database files)

# URL CONFIGURATION
DATA_URL = f'https://cryptics.georgeho.org/data/clues.json?_next200&_shape=array'

# FILE PATHS
RAW_FILE = RAW_DIR / 'cryptics_raw.json'
CLEAN_FILE = CLEAN_DIR / 'cryptics_clean.json' # Sets the file name for the clean json data
DB_FILE = PROCESSED_DIR / 'cryptics.db'

# DATABASE CONFIGURATIONS
USE_SECRETS = os.getenv('USE_SECRETS', 'true').lower() == 'true'

if USE_SECRETS:

    DB_CONFIG = {
        'secret_name': 'crossword-app-mysql-creds',
        'region_name': 'us-east-1',
        'use_secrets': True
    }
else:
    # Local MySQL
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'CROSSWORD_DB'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'use_secrets': False
    }


# DATA CLEANING CONFIG
DB_NAME = ('CROSSWORD_DB')
TABLE_NAME = ('CROSSWORD_TABLE')
