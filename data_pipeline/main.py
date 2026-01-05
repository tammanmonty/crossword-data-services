from download_crossword_data import *
from db_mysql_initialize import *
from db_upload_mysql import *


if __name__ == '__main__':
    # EXTRACT THE DATA FROM THE CROSSWORD CLUES AND ANSWERS SITE
    # CLEAN THE DATA FOR ONLY WHAT IS NEEDED
    download_cryptics_dataset()
    cleaning_cryptic_data()

    # INITIALIZE THE MYSQL DATABASE SCHEMA AND TABLES
    initialize_mysql()

    # UPLOAD THE CLEANED DATA
    with open(CLEAN_FILE) as json_file:
        values = json.load(json_file)
    upload_dataset_mysql(values)