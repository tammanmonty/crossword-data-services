from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from enum import Enum
import logging
import os

class Environment(Enum):
    """Supported environment variables."""
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    LOCAL = "LOCAL"

# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

logger = logging.getLogger(__name__)

def get_env() -> Environment:
    """
    Get the current environment from ENV variables.

    :return:
        Environment enum value

    """
    logger.debug("Retrieving environment from ENV variables")
    env_str = os.getenv('ENV', 'LOCAL').upper()

    try:
        return Environment[env_str]
    except KeyError:
        valid_envs = [e.value for e in Environment]
        raise ValueError(f"Invalid ENV value: {env_str}. Must be one of {valid_envs}")


ENV = get_env()

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# Base directory - root of the data_pipeline module
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
RAW_DIR = BASE_DIR / 'raw' # Stores original downloaded data
CLEAN_DIR = BASE_DIR / 'clean' # Stores cleaned and validated data
PROCESSED_DIR = BASE_DIR / 'processed' # Stores final processed data (e.g., database files)
LOG_DIR = BASE_DIR / '..' / 'logs'

# Ensure directories exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATA_URL = os.getenv("DATA_URL", f"https://cryptics.georgeho.org/data/clues.json?_next=100&_shape=array")

# FILE PATHS
RAW_FILE = RAW_DIR / 'cryptics_raw.json'
CLEAN_FILE = CLEAN_DIR / 'cryptics_clean.json' # Sets the file name for the clean json data
DB_FILE = PROCESSED_DIR / 'cryptics.db'
LOG_FILE = LOG_DIR / 'crossword_data_pipeline.log'

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

if ENV == Environment.LOCAL:
    # Local MySQL
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'local_password'),
        'database': os.getenv('DB_NAME', 'CROSSWORD_DB'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'use_secrets': False
    }
else:
    # AWS RDS MySQL
    DB_CONFIG = {
        'secret_name': os.getenv('SECRET_NAME'),
        'region_name': os.getenv('DB_REGION_NAME', 'us-east-1'),
        'use_secrets': True
    }


# DATA CLEANING CONFIG
DB_NAME = ('CROSSWORD_DB')
TABLE_NAME = ('CROSSWORD_TABLE')


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Log format
LOG_FORMAT = os.getenv(
    'LOG_FORMAT',
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)