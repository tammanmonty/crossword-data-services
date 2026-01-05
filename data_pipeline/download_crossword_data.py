import re
import requests
import pandas as pd
from pathlib import Path

# API endpoint for cryptic crossword clues dataset
DATA_URL = f'https://cryptics.georgeho.org/data/clues.json?_next100&_shape=array'

# Define directory structure for data pipeline stages
RAW_DIR = Path('raw')  # Stores original downloaded data
CLEAN_DIR = Path('clean')  # Stores cleaned and validated data
PROCESSED_DIR = Path('processed')  # Stores final processed data (e.g., database files)

# Create all required directories if they don't exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Define file paths for each pipeline stage
RAW_FILE = RAW_DIR / 'cryptics_raw.json'
CLEAN_FILE = CLEAN_DIR / 'cryptics_clean.json'
DB_FILE = PROCESSED_DIR / 'cryptics.db'

''' 1. Download the Dataset '''


def download_cryptics_dataset():
    """
    Downloads the cryptic crossword clues dataset from the API.
    Saves the raw JSON response to the raw directory without any modifications.
    """
    print('Downloading cryptics dataset')

    # Make HTTP GET request with 20 second timeout
    r = requests.get(DATA_URL, timeout=20)

    # Raise an exception if the request failed (status code 4xx or 5xx)
    r.raise_for_status()

    # Write raw binary content directly to file
    RAW_FILE.write_bytes(r.content)
    print('Download Raw Dataset Complete')


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
    if definition is None:
        return False
    return True


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
    print('Reading raw dataset...')

    # Load raw JSON file into pandas DataFrame
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        df = pd.read_json(f)

    # Select only the columns we need for the crossword application
    # rowid: unique identifier, clue: puzzle clue, answer: solution, definition: hint
    df_clean = df[['rowid', 'clue', 'answer', 'definition']]

    print('Cleaning dataset...')

    # Filter out rows with missing or too-short answers (less than 2 characters)
    df_clean = df_clean[df_clean["answer"].notnull() & (df_clean["answer"].str.len() >= 2)]

    # Filter out rows with invalid definitions using our validation function
    df_clean = df_clean[df_clean["definition"].apply(is_valid_definition)]

    # Apply normalization functions to standardize all text fields
    df_clean["answer"] = df_clean["answer"].apply(normalize_answer)
    df_clean["clue"] = df_clean["clue"].apply(normalize_clue)
    df_clean["definition"] = df_clean["definition"].apply(normalize_definition)

    # Remove any duplicate entries to ensure data quality
    df_clean = df_clean.drop_duplicates()

    # Save cleaned data as formatted JSON (with indentation for readability)
    df_clean.to_json(CLEAN_FILE, orient='records', indent=1)

    print(f"Saved clean dataset to: {CLEAN_FILE}")

# Entry point when script is run directly (currently commented out)
# if __name__ == '__main__':
#     download_cryptics_dataset()
#     cleaning_cryptic_data()