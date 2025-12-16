import json
import sys

import mysql.connector
from pathlib import Path


CLEAN_DIR = Path('clean')
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_FILE = CLEAN_DIR / 'cryptics_clean.json'


def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="local_password",
        database="CROSSWORD_DB",
    )

def insert_crossword_clue(cursor, clue_data):
    sql_query = '''INSERT INTO CROSSWORD_CLUES (clue, answer, definition) VALUES (%s, %s, %s);'''
    values = (
        clue_data['clue'],
        clue_data['answer'],
        clue_data['definition']
    )
    cursor.execute(sql_query, values)

def upload_dataset_mysql(dataset):
    try:
        mysql_db = get_mysql_connection()
        cursor = mysql_db.cursor()

        for item in dataset:
            insert_crossword_clue(cursor, item)

        mysql_db.commit()
        print(f"Inserted {len(dataset)} rows into MYSQL database successfully")

    except mysql.connector.Error as err:
        print("Error: %s" % err)


    finally:
        if mysql_db.is_connected():
            cursor.close()
            mysql_db.close()


if __name__ == "__main__":
    with open(CLEAN_FILE) as json_file:
        values = json.load(json_file)
    upload_dataset_mysql(values)