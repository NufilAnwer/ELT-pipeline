"""
Currency Exchange Rates ETL Pipeline DAG
========================================
Integrates daily currency exchange rates from the Frankfurter API into MongoDB.
Features:
- Three distinct tasks: Extract, Transform, Load.
- Named XComs for task-to-task communication.
- Containerized MongoDB and Mongo Express with Docker networking & persistent storage.
"""

from datetime import datetime, timedelta, timezone
import logging
import os
import requests
from pymongo import MongoClient, UpdateOne

from airflow import DAG
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

logger = logging.getLogger("airflow.task")

# API Configuration
FRANKFURTER_API_URL = "https://api.frankfurter.dev/v2/rates?base=EUR&quotes=USD,GBP,JPY"
SOURCE_NAME = "Frankfurter API"

# MongoDB Configuration
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://admin:password123@mongodb:27017/?authSource=admin"
)
MONGO_DB_NAME = "currency_exchange"
MONGO_COLLECTION_NAME = "exchange_rates"

# Named XCom Keys
XCOM_RAW_RATES_KEY = "raw_exchange_rates"
XCOM_TRANSFORMED_RATES_KEY = "transformed_exchange_rates"
XCOM_LOAD_SUMMARY_KEY = "mongodb_load_summary"


def extract_currency_rates(**context):
    """
    Task 1: Extract Currency Exchange Rates
    Fetches exchange rates from Frankfurter API and pushes the raw payload
    into Airflow Named XCom ('raw_exchange_rates').
    """
    ti = context["ti"]
    logger.info(f"Extracting currency rates from {FRANKFURTER_API_URL}")

    response = requests.get(FRANKFURTER_API_URL, timeout=30)
    response.raise_for_status()
    raw_data = response.json()

    logger.info(f"Successfully extracted data: {raw_data}")

    # Push to Named XCom
    ti.xcom_push(key=XCOM_RAW_RATES_KEY, value=raw_data)
    return raw_data


def transform_currency_rates(**context):
    """
    Task 2: Transform Exchange Rate Data
    Pulls raw exchange rates from Named XCom ('raw_exchange_rates'),
    normalizes records to the required target schema, and pushes transformed
    records to Named XCom ('transformed_exchange_rates').
    
    Target Schema:
    {
        "base_currency": "EUR",
        "target_currency": "USD",
        "exchange_rate": 1.15,
        "rate_date": "2026-11-04",
        "source": "Frankfurter API",
        "retrieved_at": "2026-11-05T07:15:00"
    }
    """
    ti = context["ti"]
    raw_data = ti.xcom_pull(
        task_ids="extract_currency_rates",
        key=XCOM_RAW_RATES_KEY
    )

    if not raw_data:
        raise ValueError("No raw exchange rate data found in Named XCom.")

    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    transformed_records = []

    # Handle API response format: v2 returns list of objects [{date, base, quote, rate}]
    if isinstance(raw_data, list):
        for item in raw_data:
            record = {
                "base_currency": str(item.get("base", "EUR")).upper(),
                "target_currency": str(item.get("quote", "")).upper(),
                "exchange_rate": float(item.get("rate", 0.0)),
                "rate_date": str(item.get("date", "")),
                "source": SOURCE_NAME,
                "retrieved_at": retrieved_at,
            }
            transformed_records.append(record)
    # Handle dictionary format (e.g. v1 or wrapped formats)
    elif isinstance(raw_data, dict):
        base_curr = raw_data.get("base", "EUR")
        rate_date = raw_data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        rates = raw_data.get("rates", {})
        for target_curr, rate_val in rates.items():
            record = {
                "base_currency": str(base_curr).upper(),
                "target_currency": str(target_curr).upper(),
                "exchange_rate": float(rate_val),
                "rate_date": str(rate_date),
                "source": SOURCE_NAME,
                "retrieved_at": retrieved_at,
            }
            transformed_records.append(record)
    else:
        raise ValueError(f"Unexpected raw data format: {type(raw_data)}")

    logger.info(f"Transformed {len(transformed_records)} records: {transformed_records}")

    # Push to Named XCom
    ti.xcom_push(key=XCOM_TRANSFORMED_RATES_KEY, value=transformed_records)
    return transformed_records


def load_currency_rates_to_mongodb(**context):
    """
    Task 3: Load Data into MongoDB
    Pulls transformed records from Named XCom ('transformed_exchange_rates')
    and upserts/inserts them into MongoDB database 'currency_exchange',
    collection 'exchange_rates'. Pushes load summary to Named XCom.
    """
    ti = context["ti"]
    transformed_records = ti.xcom_pull(
        task_ids="transform_currency_rates",
        key=XCOM_TRANSFORMED_RATES_KEY
    )

    if not transformed_records:
        raise ValueError("No transformed records found in Named XCom.")

    logger.info(f"Connecting to MongoDB at: {MONGO_URI}")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    # Use upsert by (base_currency, target_currency, rate_date) to prevent duplicates on DAG re-runs
    operations = []
    for record in transformed_records:
        filter_query = {
            "base_currency": record["base_currency"],
            "target_currency": record["target_currency"],
            "rate_date": record["rate_date"],
        }
        operations.append(UpdateOne(filter_query, {"$set": record}, upsert=True))

    bulk_result = collection.bulk_write(operations)
    summary = {
        "matched_count": bulk_result.matched_count,
        "modified_count": bulk_result.modified_count,
        "upserted_count": len(bulk_result.upserted_ids),
        "total_processed": len(transformed_records),
        "database": MONGO_DB_NAME,
        "collection": MONGO_COLLECTION_NAME,
        "status": "SUCCESS",
    }

    logger.info(f"MongoDB Load Summary: {summary}")

    # Push to Named XCom
    ti.xcom_push(key=XCOM_LOAD_SUMMARY_KEY, value=summary)
    client.close()
    return summary


with DAG(
    dag_id="currency_exchange_etl",
    default_args=default_args,
    description="ETL pipeline integrating Frankfurter daily exchange rates into MongoDB",
    schedule="@daily",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    tags=["etl", "currency", "mongodb", "frankfurter"],
) as dag:

    # Task 1: Extract
    extract_task = PythonOperator(
        task_id="extract_currency_rates",
        python_callable=extract_currency_rates,
    )

    # Task 2: Transform
    transform_task = PythonOperator(
        task_id="transform_currency_rates",
        python_callable=transform_currency_rates,
    )

    # Task 3: Load
    load_task = PythonOperator(
        task_id="load_currency_rates_to_mongodb",
        python_callable=load_currency_rates_to_mongodb,
    )

    # Task Dependencies
    extract_task >> transform_task >> load_task
