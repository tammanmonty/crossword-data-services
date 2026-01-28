import re
import requests
import pandas as pd
import logging
from requests.exceptions import HTTPError, ConnectionError, Timeout
from pathlib import Path

from requests import RequestException

from config.config import DATA_URL, RAW_DIR, CLEAN_DIR, PROCESSED_DIR, RAW_FILE, CLEAN_FILE, DB_FILE

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

''' 1. Download the Dataset '''
def download_cryptics_dataset():
    logger.info('Downloading cryptics dataset')
    try:
        """
        Downloads the cryptic crossword clues dataset from the API.
        Saves the raw JSON response to the raw directory without any modifications.
        """

        logger.debug('Making HTTP GET request with 20 second timeout')
        r = requests.get(DATA_URL, timeout=20)

        # Raise an exception if the request failed (status code 4xx or 5xx)
        r.raise_for_status()

        # Write raw binary content directly to file
        RAW_FILE.write_bytes(r.content)
        logger.info('Download Raw Dataset Complete')
    except Timeout as e:
        logger.error(f'Timeout Error: {e}')
        raise
    except ConnectionError as e:
        logger.error(f'Connection Error: {e}')
        raise
    except HTTPError as e:
        logger.error(f'HTTP error when making HTTP GET request: {e}')
        raise
    except Exception as e:
        logger.error(f'Unexpected error during data download: {e}')
        raise


''' 2. Cleaning Utilities '''
def normalize_answer(answer: str) -> str:
    """
    Standardizes crossword answers by:
    - Converting to uppercase (crossword convention)
    - Removing all non-alphanumeric characters except spaces

    Example: "Mary's-Day" -> "MARYS DAY"
    """
    answer = answer.upper()
    # Remove punctuation, special characters, keeping only letters, numbers, and spaces
    answer = re.sub(r"[^A-Za-z0-9\s]", "", answer)
    return answer


def normalize_clue(clue: str) -> str:
    """
    Cleans up clue text by removing leading/trailing whitespace.
    """
    return clue.strip()


def is_valid_definition(definition: str) -> bool:
    """
    Validates that a definition exists (is not None).
    Definitions are required for the dataset quality.
    """
    return definition is not None


def normalize_definition(definition: str) -> str:
    """
    Cleans up definition text by removing leading/trailing whitespace.
    """
    return definition.strip()


def is_valid_answer(answer: str) -> bool:
    """
    Validates answer quality by checking:
    - Not None or empty
    - Length greater than 1 (single letters excluded)
    - Contains only alphabetic characters (no numbers/special chars)

    This ensures we only keep meaningful crossword answers.
    """
    if answer is None or len(answer) <= 1:
        return False
    if not answer.isalpha():
        return False
    return True


''' 3. Clean the Dataset '''


def cleaning_cryptic_data():
    """
    Performs comprehensive data cleaning:
    1. Loads raw JSON data
    2. Selects only required columns
    3. Filters out invalid entries
    4. Normalizes all text fields
    5. Removes duplicates
    6. Saves cleaned data to JSON file
    """
    logger.info('Cleaning Cryptic Dataset')

    logger.debug(f'Load raw JSON file {RAW_FILE} into pandas DataFrame')
    try:
        with open(RAW_FILE, "r", encoding="utf-8") as f:
            df = pd.read_json(f)

        # Select only the columns we need for the crossword application
        initial_count = len(df)

        logger.debug('rowid: unique identifier, clue: puzzle clue, answer: solution, definition: hint')
        df_clean = df[['rowid', 'clue', 'answer', 'definition']]

        logger.info('Cleaning dataset...')

        # Filter out rows with missing or too-short answers (less than 2 characters)
        df_clean = df_clean[df_clean["answer"].notnull() & (df_clean["answer"].str.len() >= 2)]
        after_answer_filter = len(df_clean)
        removed_ans = initial_count - after_answer_filter
        logger.info(f'Filtered answers: removed {removed_ans} invalid entries')

        # Filter out rows with invalid definitions using our validation function
        df_clean = df_clean[df_clean["definition"].apply(is_valid_definition)]
        after_def_filter = len(df_clean)
        removed_def = after_answer_filter - after_def_filter
        logger.info(f'Filtered definitions: removed {removed_def} invalid entries')

        # Apply normalization functions to standardize all text fields
        logger.debug('Applying normalization...')
        df_clean["answer"] = df_clean["answer"].apply(normalize_answer)
        df_clean["clue"] = df_clean["clue"].apply(normalize_clue)
        df_clean["definition"] = df_clean["definition"].apply(normalize_definition)

        # Remove any duplicate entries to ensure data quality
        logger.debug('Removing duplicate entries')
        before_dedup = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        after_dedup = len(df_clean)
        rem_dedup = before_dedup - after_dedup
        logger.info(f'Removed {rem_dedup} duplicate entries')

        # Save cleaned data as formatted JSON (with indentation for readability)
        df_clean.to_json(CLEAN_FILE, orient='records', indent=1)

        logger.info(f'Data cleaning complete: {after_dedup}/{initial_count} records retained')
        logger.info(f'Saved clean dataset to: {CLEAN_FILE}')
    except FileNotFoundError as e:
        logger.error(f'Raw data file not found: {e}')
        raise
    except Exception as e:
        logger.error(f'Unexpected error during data cleaning: {e}')
        raise

# Entry point when script is run directly (currently commented out)
# if __name__ == '__main__':
#     download_cryptics_dataset()
#     cleaning_cryptic_data()