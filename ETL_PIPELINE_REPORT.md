# Airflow ETL Pipeline Technical Report
## Integrating Frankfurter Currency Exchange Rates to MongoDB via Astro CLI

**Author:** Nufil Anwer  
**Repository Links:**
- **GitHub Repository**: [https://github.com/NufilAnwer/ELT-pipeline/tree/main](https://github.com/NufilAnwer/ELT-pipeline/tree/main)
- **DagsHub Repository**: [https://dagshub.com/NufilAnwer/ELT-pipeline](https://dagshub.com/NufilAnwer/ELT-pipeline)
**Date:** November 12, 2026  
**Pipeline Orchestrator:** Astronomer Astro CLI (Airflow Runtime 3.3-12)  
**Database:** MongoDB 9.0.8 & Mongo Express Web Administration  

---

## 1. Executive Summary

This report documents the end-to-end design, implementation, and successful verification of a production-grade **ETL (Extract, Transform, Load)** pipeline built using the **Astronomer Astro CLI** and **Apache Airflow**.

The pipeline ingests real-time foreign exchange data from the **Frankfurter Public API**, performs data normalization into a strictly defined JSON document schema, and persists the data into a containerized **MongoDB** instance. The database is administered using **Mongo Express** running alongside Airflow on a shared Docker bridge network with a persistent Docker volume.

All task-to-task data transfers are conducted using **Airflow Named XComs**, ensuring transparent data lineage and modular task boundaries.

---

## 2. Pipeline Architecture & Data Flow

```mermaid
flowchart TD
    API["🌐 Frankfurter Public API<br/>(/v2/rates?base=EUR&quotes=USD,GBP,JPY)"]
    
    subgraph AirflowDAG["🚀 Airflow DAG: currency_exchange_etl"]
        direction TB
        T1["📥 Task 1: extract_currency_rates<br/>HTTP GET to API"]
        X1[("🔑 Named XCom:<br/>'raw_exchange_rates'")]
        T2["⚙️ Task 2: transform_currency_rates<br/>Schema normalization & typing"]
        X2[("🔑 Named XCom:<br/>'transformed_exchange_rates'")]
        T3["📤 Task 3: load_currency_rates_to_mongodb<br/>Idempotent bulk upsert"]
        X3[("🔑 Named XCom:<br/>'mongodb_load_summary'")]
        
        T1 -->|Push| X1
        X1 -->|Pull| T2
        T2 -->|Push| X2
        X2 -->|Pull| T3
        T3 -->|Push| X3
    end

    subgraph DockerEnv["🐳 Docker Bridge Network: airflow"]
        direction LR
        Mongo[("🍃 MongoDB Service<br/>Container: mongodb<br/>Port: 27017<br/>DB: currency_exchange")]
        MongoExp["🖥️ Mongo Express UI<br/>Container: mongo-express<br/>Port: 8081"]
        Vol[("💾 Named Volume:<br/>mongo_data -> /data/db")]
        
        Mongo <-->|Admin connection| MongoExp
        Vol -->|Persistent Storage| Mongo
    end

    API -->|Fetch Rates| T1
    T3 -->|Upsert Documents| Mongo
```

---

## 3. Docker Infrastructure & Configuration

### a) Docker Networking
All containers (Airflow API server, scheduler, triggerer, DAG processor, Postgres, MongoDB, and Mongo Express) operate on a custom Docker bridge network (`airflow`). Containers communicate securely using service hostnames:
- Airflow workers connect to MongoDB at: `mongodb://admin:password123@mongodb:27017/?authSource=admin`
- Mongo Express connects to MongoDB at: `mongodb:27017`

### b) Persistent Storage
A dedicated named Docker volume `mongo_data` is mounted to `/data/db` on the MongoDB service container, guaranteeing that all currency rate documents are preserved across container lifecycles and host reboots.

### Docker Compose Service Definition (`docker-compose.override.yml`)
```yaml
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: currency_exchange
    volumes:
      - mongo_data:/data/db
    networks:
      - airflow

  mongo-express:
    image: mongo-express:latest
    container_name: mongo-express
    restart: always
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: admin
      ME_CONFIG_MONGODB_ADMINPASSWORD: password123
      ME_CONFIG_MONGODB_SERVER: mongodb
      ME_CONFIG_MONGODB_PORT: 27017
      ME_CONFIG_MONGODB_ENABLE_ADMIN: "true"
      ME_CONFIG_MONGODB_AUTH_DATABASE: admin
      ME_CONFIG_BASICAUTH: "false"
    depends_on:
      - mongodb
    networks:
      - airflow

volumes:
  mongo_data:
    name: mongo_data

networks:
  airflow:
```

### Docker Verification Outputs

**Inspecting Docker Network (`elt_58a7c7_airflow`):**
```json
[
  {
    "Name": "elt_58a7c7_airflow",
    "Driver": "bridge",
    "Containers": {
      "mongodb": { "IPv4Address": "172.19.0.3/16" },
      "mongo-express": { "IPv4Address": "172.19.0.4/16" },
      "elt_58a7c7-scheduler-1": { "IPv4Address": "172.19.0.8/16" },
      "elt_58a7c7-api-server-1": { "IPv4Address": "172.19.0.9/16" }
    }
  }
]
```

**Inspecting Persistent Volume (`mongo_data`):**
```json
[
  {
    "Name": "mongo_data",
    "Driver": "local",
    "Mountpoint": "/var/lib/docker/volumes/mongo_data/_data"
  }
]
```

---

## 4. Airflow DAG Implementation (`dags/currency_exchange_etl.py`)

The pipeline defines three modular tasks connected sequentially (`extract_task >> transform_task >> load_task`).

```python
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

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

logger = logging.getLogger("airflow.task")

FRANKFURTER_API_URL = "https://api.frankfurter.dev/v2/rates?base=EUR&quotes=USD,GBP,JPY"
SOURCE_NAME = "Frankfurter API"

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
    """Task 1: Extract Currency Exchange Rates and push to Named XCom."""
    ti = context["ti"]
    logger.info(f"Extracting currency rates from {FRANKFURTER_API_URL}")

    response = requests.get(FRANKFURTER_API_URL, timeout=30)
    response.raise_for_status()
    raw_data = response.json()

    logger.info(f"Successfully extracted data: {raw_data}")
    ti.xcom_push(key=XCOM_RAW_RATES_KEY, value=raw_data)
    return raw_data


def transform_currency_rates(**context):
    """Task 2: Pull from Named XCom, transform schema, and push to Named XCom."""
    ti = context["ti"]
    raw_data = ti.xcom_pull(
        task_ids="extract_currency_rates",
        key=XCOM_RAW_RATES_KEY
    )

    if not raw_data:
        raise ValueError("No raw exchange rate data found in Named XCom.")

    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    transformed_records = []

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

    logger.info(f"Transformed {len(transformed_records)} records")
    ti.xcom_push(key=XCOM_TRANSFORMED_RATES_KEY, value=transformed_records)
    return transformed_records


def load_currency_rates_to_mongodb(**context):
    """Task 3: Pull from Named XCom and upsert into MongoDB."""
    ti = context["ti"]
    transformed_records = ti.xcom_pull(
        task_ids="transform_currency_rates",
        key=XCOM_TRANSFORMED_RATES_KEY
    )

    if not transformed_records:
        raise ValueError("No transformed records found in Named XCom.")

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

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

    extract_task = PythonOperator(
        task_id="extract_currency_rates",
        python_callable=extract_currency_rates,
    )

    transform_task = PythonOperator(
        task_id="transform_currency_rates",
        python_callable=transform_currency_rates,
    )

    load_task = PythonOperator(
        task_id="load_currency_rates_to_mongodb",
        python_callable=load_currency_rates_to_mongodb,
    )

    extract_task >> transform_task >> load_task
```

---

## 5. Execution Evidence & Outputs

### 5.1 DAG & Task Run Execution Results

Execution verified via Airflow CLI inside the running scheduler container:
```text
dag_id                | task_id                        | state   | start_date                       | end_date                        
======================+================================+=========+==================================+=================================
currency_exchange_etl | extract_currency_rates         | success | 2026-11-12T12:47:43.762921+00:00 | 2026-11-12T12:47:44.580746+00:00
currency_exchange_etl | transform_currency_rates       | success | 2026-11-12T12:47:44.877642+00:00 | 2026-11-12T12:47:45.231008+00:00
currency_exchange_etl | load_currency_rates_to_mongodb | success | 2026-11-12T12:47:46.047419+00:00 | 2026-11-12T12:47:46.372124+00:00
```

### 5.2 Named XCom Verification (PostgreSQL Metadata Inspection)

Query executed against Airflow metadata database:
```sql
SELECT key, task_id, dag_id, LEFT(value::text, 65) as sample_val
FROM xcom
WHERE dag_id='currency_exchange_etl';
```

**Output:**
```text
            key             |            task_id             |        dag_id         |                            sample_val                            
----------------------------+--------------------------------+-----------------------+------------------------------------------------------------------
 raw_exchange_rates         | extract_currency_rates         | currency_exchange_etl | [{"base": "EUR", "date": "2026-11-12", "rate": 0.83581, "quote":
 transformed_exchange_rates | transform_currency_rates       | currency_exchange_etl | [{"source": "Frankfurter API", "rate_date": "2026-11-12", "retri
 mongodb_load_summary       | load_currency_rates_to_mongodb | currency_exchange_etl | {"status": "SUCCESS", "database": "currency_exchange", "collecti
```

### 5.3 MongoDB Transformed Data Output

Direct query to MongoDB collection `currency_exchange.exchange_rates`:
```bash
docker exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin \
  --eval "console.log(JSON.stringify(db.getSiblingDB('currency_exchange').exchange_rates.find().toArray(), null, 2))"
```

**Persisted Documents:**
```json
[
  {
    "_id": "6af5b56f602d34a4492a2ae8",
    "rate_date": "2026-11-12",
    "base_currency": "EUR",
    "target_currency": "GBP",
    "exchange_rate": 0.83581,
    "retrieved_at": "2026-11-12T12:47:45",
    "source": "Frankfurter API"
  },
  {
    "_id": "6af5b56f602d34a4492a2ae9",
    "rate_date": "2026-11-12",
    "base_currency": "EUR",
    "target_currency": "JPY",
    "exchange_rate": 177.37,
    "retrieved_at": "2026-11-12T12:47:45",
    "source": "Frankfurter API"
  },
  {
    "_id": "6af5b56f602d34a4492a2aea",
    "rate_date": "2026-11-12",
    "base_currency": "EUR",
    "target_currency": "USD",
    "exchange_rate": 1.1141,
    "retrieved_at": "2026-11-12T12:47:45",
    "source": "Frankfurter API"
  }
]
```

### 5.4 Mongo Express Web UI Verification

Mongo Express is accessible on port `8081` (`http://localhost:8081`). Server status checks confirm active connectivity:
- **Server Version**: MongoDB 9.0.8
- **Node Engine**: 18.20.3
- **Active Databases**: `currency_exchange`, `admin`, `config`, `local`
- **Active Collections**: `exchange_rates` (3 documents)

### 5.5 Unit Test Suite Results (`astro dev pytest`)

```text
============================= test session starts ==============================
platform linux -- Python 3.14.10, pytest-9.2.0, pluggy-1.6.0
rootdir: /
plugins: anyio-4.14.2
collected 3 items

tests/dags/test_dag_example.py ...                                       [100%]

======================== 3 passed, 2 warnings in 2.14s =========================
✔ All tests passed!
```

---

## 6. Conclusion

All requirements stipulated in the prompt have been fulfilled:
- ✅ Astro CLI utilized to build and operate the Airflow environment.
- ✅ Frankfurter API successfully integrated for EUR -> USD, GBP, JPY.
- ✅ MongoDB configured as the primary data store with Mongo Express web administration.
- ✅ Docker Networking (`airflow` bridge network) and Persistent Storage (`mongo_data` volume) properly configured.
- ✅ Three distinct tasks (Extract, Transform, Load) created with strict schema conformance.
- ✅ Airflow Named XComs (`raw_exchange_rates`, `transformed_exchange_rates`, `mongodb_load_summary`) actively transferring data between tasks.
- ✅ Code versioned and pushed to GitHub and DagsHub repositories.

