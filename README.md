# Daily Currency Exchange Rates ETL Pipeline (Astro CLI + Airflow + MongoDB)

An automated production-ready **ETL (Extract, Transform, Load)** pipeline built using the **Astronomer Astro CLI** and **Apache Airflow**. The pipeline extracts daily currency exchange rates from the **Frankfurter API**, normalizes and validates the records, and integrates them into **MongoDB** with web administration via **Mongo Express**.

---

## Repository Links

- **GitHub Repository**: [https://github.com/NufilAnwer/ELT-pipeline/tree/main](https://github.com/NufilAnwer/ELT-pipeline/tree/main)
- **DagsHub Repository**: [https://dagshub.com/NufilAnwer/ELT-pipeline](https://dagshub.com/NufilAnwer/ELT-pipeline)

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Frankfurter Public API    |
                      |   (EUR -> USD, GBP, JPY)    |
                      +--------------+--------------+
                                     |
                                     v
                 +---------------------------------------+
                 |  Task 1: extract_currency_rates       |
                 |  - HTTP GET Frankfurter API           |
                 |  - Push to Named XCom:                |
                 |    'raw_exchange_rates'               |
                 +-------------------+-------------------+
                                     | (Named XCom)
                                     v
                 +---------------------------------------+
                 |  Task 2: transform_currency_rates     |
                 |  - Pull from 'raw_exchange_rates'     |
                 |  - Standardize schema & types         |
                 |  - Push to Named XCom:                |
                 |    'transformed_exchange_rates'       |
                 +-------------------+-------------------+
                                     | (Named XCom)
                                     v
                 +---------------------------------------+
                 |  Task 3: load_currency_rates_to_mongo |
                 |  - Pull from                          |
                 |    'transformed_exchange_rates'       |
                 |  - Upsert records to MongoDB          |
                 |  - Push to Named XCom:                |
                 |    'mongodb_load_summary'             |
                 +-------------------+-------------------+
                                     |
                                     v
    +--------------------------------+--------------------------------+
    |                                                                 |
    v                                                                 v
+-------------------------------+                     +-------------------------------+
|       MongoDB Service         |                     |     Mongo Express Service     |
|   Database: currency_exchange | <=================> |   Web-based UI Interface      |
|   Collection: exchange_rates  |                     |   Port: 8081                  |
|   Persistent Volume:          |                     |                               |
|   mongo_data:/data/db         |                     |                               |
+-------------------------------+                     +-------------------------------+
```

---

## Key Features & Requirements Addressed

1. **Astro CLI Integration**:
   - Initialized and orchestrated using the official Astronomer Astro CLI.
   - Containerized runtime with automatic dependency management via `requirements.txt`.

2. **Public API Ingestion**:
   - Source: [Frankfurter API](https://frankfurter.dev/)
   - Endpoint: `https://api.frankfurter.dev/v2/rates?base=EUR&quotes=USD,GBP,JPY`
   - Ingests EUR rates for USD, GBP, and JPY.

3. **Multi-Service Docker Architecture**:
   - **MongoDB**: Primary database storing transformed rate documents.
   - **Mongo Express**: Interactive administrative web dashboard running on port `8081`.
   - **Docker Networking**: Both services communicate over the custom bridge network (`airflow`) alongside Airflow scheduler and worker containers.
   - **Persistent Storage**: MongoDB uses a named volume (`mongo_data:/data/db`) ensuring full data persistence across container recycles.

4. **Three Core Airflow Tasks**:
   - `extract_currency_rates`: Retrieves raw rate payloads from the external API.
   - `transform_currency_rates`: Normalizes the schema with UTC timestamp and metadata.
   - `load_currency_rates_to_mongodb`: Performs idempotent bulk upserts into MongoDB collection `exchange_rates`.

5. **Named Airflow XComs**:
   - Explicit named XCom keys are utilized for inter-task communication:
     - `raw_exchange_rates` (Task 1 -> Task 2)
     - `transformed_exchange_rates` (Task 2 -> Task 3)
     - `mongodb_load_summary` (Task 3 metadata)

---

## Data Schema

### Transformed Document Schema

Each document persisted in MongoDB follows this exact specification:

```json
{
  "_id": "6af5b56f602d34a4492a2aea",
  "base_currency": "EUR",
  "target_currency": "USD",
  "exchange_rate": 1.1141,
  "rate_date": "2026-11-12",
  "source": "Frankfurter API",
  "retrieved_at": "2026-11-12T12:47:45"
}
```

---

## Project Structure

```
elt/
├── .astro/
│   ├── config.yaml
│   └── test_dag_integrity_default.py
├── dags/
│   └── currency_exchange_etl.py       # Core ETL DAG definition with 3 tasks & Named XComs
├── .dockerignore
├── .env                               # Environment configurations (MONGO_URI, Airflow flags)
├── .gitignore
├── Dockerfile                         # Astronomer Runtime Dockerfile
├── docker-compose.override.yml        # MongoDB & Mongo Express services, networks & volumes
├── packages.txt                       # System dependencies
├── README.md                          # Pipeline documentation
└── requirements.txt                   # Python packages: pymongo, requests
```

---

## Docker Compose Configuration (`docker-compose.override.yml`)

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

---

## Getting Started & Execution

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- [Astronomer Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).

### Step 1: Start the Local Pipeline
Run the following command in the project root:
```bash
astro dev start
```

### Step 2: Access the User Interfaces
- **Airflow Web UI**: `http://localhost:8080` (or the dynamic port assigned by Astro CLI)
- **Mongo Express UI**: `http://localhost:8081`

### Step 3: Trigger the DAG
Trigger the pipeline manually or let the scheduler run it daily:
```bash
docker exec elt_58a7c7-scheduler-1 airflow dags trigger currency_exchange_etl
```

### Step 4: Verify MongoDB Contents
Verify records directly using `mongosh`:
```bash
docker exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin --eval "console.log(JSON.stringify(db.getSiblingDB('currency_exchange').exchange_rates.find().toArray(), null, 2))"
```

---

## Verification & Execution Evidence

### 1. Task Execution Status
```
dag_id                | task_id                        | state   | duration
======================+================================+=========+==========
currency_exchange_etl | extract_currency_rates         | success | ~0.8s
currency_exchange_etl | transform_currency_rates       | success | ~0.3s
currency_exchange_etl | load_currency_rates_to_mongodb | success | ~0.3s
```

### 2. Airflow Named XCom Records
Querying the metadata database confirms the named keys:
```sql
SELECT key, task_id, dag_id FROM xcom WHERE dag_id='currency_exchange_etl';
```
| Key | Task ID | DAG ID |
|---|---|---|
| `raw_exchange_rates` | `extract_currency_rates` | `currency_exchange_etl` |
| `transformed_exchange_rates` | `transform_currency_rates` | `currency_exchange_etl` |
| `mongodb_load_summary` | `load_currency_rates_to_mongodb` | `currency_exchange_etl` |
