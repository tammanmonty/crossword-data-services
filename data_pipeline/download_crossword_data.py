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

RAW_FILE = RAW_DIR / 'cryptics_raw.json'
CLEAN_FILE = CLEAN_DIR / 'cryptics_clean.json'
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
        df = pd.read_json(f)

    # df = pd.DataFrame(data)
    df_clean = df[['rowid', 'clue', 'answer', 'definition']]

    print('Cleaning dataset...')
    # Filter Invalid Answers and Definitions
    df_clean = df_clean[df_clean["answer"].notnull() & (df_clean["answer"].str.len() >= 2)]
    df_clean = df_clean[df_clean["definition"].apply(is_valid_definition)]

    # Cleaning Values
    df_clean["answer"] = df_clean["answer"].apply(normalize_answer)
    df_clean["clue"] = df_clean["clue"].apply(normalize_clue)
    df_clean["definition"] = df_clean["definition"].apply(normalize_definition)

    # Remove duplicaties
    df_clean = df_clean.drop_duplicates()

    df_clean.to_json(CLEAN_FILE, orient='records', indent=1)

    print(f"Saved clean dataset to: {CLEAN_FILE}")


if __name__ == '__main__':
    download_cryptics_dataset()
    cleaning_cryptic_data()
