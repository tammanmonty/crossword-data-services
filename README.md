# Crossword Data Pipeline

An ETL (Extract, Transform, Load) pipeline that downloads cryptic crossword clues from an online API, cleans and validates the data, and loads it into a MySQL database.

## Overview

This pipeline automates the process of:
1. **Extracting** crossword clue data from the Cryptics API
2. **Transforming** the data through cleaning, normalization, and validation
3. **Loading** the processed data into a MySQL database

## Features

- Downloads cryptic crossword clues with answers and definitions
- Normalizes answers and clues (uppercase conversion, punctuation removal)
- Validates data quality (filters invalid entries, removes duplicates)
- Supports both local MySQL and AWS RDS deployments
- Containerized with Docker for easy deployment
- Environment-based configuration (LOCAL, DEVELOPMENT, PRODUCTION)

## Project Structure

```
crossword-data-services/
├── data_pipeline/
│   ├── config/              # Configuration management
│   ├── raw/                 # Raw downloaded data
│   ├── clean/               # Cleaned and validated data
│   ├── processed/           # Final processed data
│   ├── download_crossword_data.py  # Data extraction and cleaning
│   ├── db_mysql_initialize.py      # Database initialization
│   ├── db_upload_mysql.py          # Data loading to MySQL
│   └── main.py              # Pipeline orchestration
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Prerequisites

- Python 3.10+
- MySQL 5.7+ (local) or AWS RDS MySQL
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd crossword-data-services
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Configuration

Edit `.env` file with your settings:

```env
ENV=LOCAL                    # LOCAL, DEVELOPMENT, or PRODUCTION
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=CROSSWORD_DB
DB_PORT=3306
```

For AWS RDS deployments, set `ENV=PRODUCTION` and configure AWS Secrets Manager.

## Usage

### Local Execution

```bash
python data_pipeline/main.py
```

### Docker Execution

```bash
# Build the image
docker build -t crossword-pipeline .

# Run the container
docker run --env-file .env crossword-pipeline
```

## Pipeline Stages

### 1. Extract
Downloads raw crossword clue data from the Cryptics API and saves to `raw/cryptics_raw.json`.

### 2. Transform
- Converts answers to uppercase
- Removes punctuation and special characters
- Validates answer length (minimum 2 characters)
- Validates definitions exist
- Removes duplicate entries
- Saves cleaned data to `clean/cryptics_clean.json`

### 3. Load
- Initializes MySQL database and tables if needed. It is recommended to use an administrator account and do this step manually. You can utilize the initialize script if you have admin privileges.
- Uploads cleaned data to `CROSSWORD_CLUES` table
- Handles duplicate entries gracefully

## Database Schema

```sql
CREATE DATABASE IF NOT EXISTS CROSSWORD_DB;
```
```sql
CREATE TABLE IF NOT EXISTS CROSSWORD_CLUES (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clue TEXT NOT NULL,
    answer VARCHAR(255) NOT NULL,
    definition TEXT NOT NULL,
    UNIQUE KEY unique_clue_answer (answer, clue(255))
);
```

## Data Source

Data is fetched from the [Cryptics API](https://cryptics.georgeho.org/data/clues.json), which provides cryptic crossword clues from various publications including The Times.

## Dependencies

Key packages:
- `mysql-connector-python` - MySQL database connectivity
- `pandas` - Data manipulation and cleaning
- `requests` - API data fetching
- `boto3` - AWS services integration (for production)
- `python-dotenv` - Environment configuration

## Environment Support

- **LOCAL**: Uses local MySQL instance with credentials from `.env`
- **DEVELOPMENT/PRODUCTION**: Uses AWS RDS MySQL with AWS Secrets Manager

## Logging

The pipeline uses Python's logging module with configurable log levels. Set `LOG_LEVEL` in `.env`:
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages

## Error Handling

The pipeline includes comprehensive error handling for:
- Network timeouts and connection errors
- Invalid or malformed data
- Database connection issues
- File system errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Author

Tamman Montanaro