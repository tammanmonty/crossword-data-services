import os
import re
from zlib import DEF_BUF_SIZE

import requests
import pandas as pd
import json
import sqlite3
from pathlib import Path


DATA_URL = f'https://cryptics.georgeho.org/data/clues.json?_next&_shape=array'
RAW_DIR = Path('raw')
CLEAN_DIR = Path('clean')
PROCESSED_DIR = Path('processed')


RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = RAW_DIR / 'cryptics_raw.csv'
CLEAN_FILE = CLEAN_DIR / 'cryptics_clean.csv'
DB_FILE = PROCESSED_DIR / 'cryptics.db'



''' 1. Download the Dataset '''
def download_cryptics_dataset():
    print('Downloading cryptics dataset')
    r = requests.get(DATA_URL, timeout=20)
    r.raise_for_status()

    RAW_FILE.write_bytes(r.content)
    print('Download Raw Dataset Complete')


''' 2. Cleaning Utilies '''
def normalize_answer(answer: str) -> str:
    #Only uppercase answers
    answer = answer.upper()
    answer = re.sub(r"[^A-Za-z0-9\s]", "", answer)
    return answer

def normalize_clue(clue: str) -> str:
    return clue.strip()

def is_valid_definition(definition: str) -> bool:
    if definition is None:
        return False
    return True

def normalize_definition(definition: str) -> str:
    return definition.strip()

def is_valid_answer(answer: str) -> bool:
    if answer is None or len(answer) <= 1:
        return False
    if not answer.isalpha():
        return False
    return True

''' 3. Clean the Dataset '''
def cleaning_cryptic_data():
    print('Reading raw dataset...')

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df_subset = df[['rowid', 'clue', 'answer', 'definition']]

    print('Cleaning dataset...')
    # Filter Invalid Answers and Definitions
    df_subset = df_subset[df_subset["answer"].notnull() & (df_subset["answer"].str.len() >= 2)]
    df_subset = df_subset[df_subset["definition"].apply(is_valid_definition)]

    # Cleaning Values
    df_subset["answer"] = df_subset["answer"].apply(normalize_answer)
    df_subset["clue"] = df_subset["clue"].apply(normalize_clue)
    df_subset["definition"] = df_subset["definition"].apply(normalize_definition)

    # Remove duplicaties
    df_subset = df_subset.drop_duplicates()

    df_subset.to_json(CLEAN_FILE, orient='records', lines=True)

    print(f"Saved clean dataset to: {CLEAN_FILE}")


if __name__ == '__main__':
    download_cryptics_dataset()
    cleaning_cryptic_data()
