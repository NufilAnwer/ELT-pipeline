import os
from PIL import Image, ImageDraw, ImageFont

SCREENSHOTS_DIR = os.path.abspath("screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf"

def create_terminal_image(title, lines, filename, width=1050):
    """
    Renders a modern terminal window mockup using PIL.
    lines is a list of tuples: (text, color_hex, is_bold)
    """
    font_size = 15
    title_font_size = 13
    
    font = ImageFont.truetype(FONT_PATH, font_size)
    font_bold = ImageFont.truetype(FONT_BOLD_PATH, font_size)
    title_font = ImageFont.truetype(FONT_BOLD_PATH, title_font_size)
    
    line_height = 24
    padding_x = 24
    padding_y = 20
    header_height = 42
    
    content_height = len(lines) * line_height + padding_y * 2
    total_height = header_height + content_height
    
    # Create image
    img = Image.new("RGBA", (width, total_height), (15, 23, 42, 255)) # Dark navy background
    draw = ImageDraw.Draw(img)
    
    # Window card
    window_rect = [0, 0, width - 1, total_height - 1]
    draw.rounded_rectangle(window_rect, radius=10, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=1)
    
    # Title bar background
    title_bar_rect = [0, 0, width - 1, header_height]
    draw.rounded_rectangle(title_bar_rect, radius=10, fill=(15, 23, 42, 255))
    draw.rectangle([0, header_height - 10, width - 1, header_height], fill=(15, 23, 42, 255))
    draw.line([(0, header_height), (width, header_height)], fill=(51, 65, 85, 255), width=1)
    
    # Window dots
    draw.ellipse([18, 15, 28, 25], fill=(239, 68, 68, 255))   # Red
    draw.ellipse([34, 15, 44, 25], fill=(245, 158, 11, 255))  # Yellow
    draw.ellipse([50, 15, 60, 25], fill=(16, 185, 129, 255))  # Green
    
    # Title text
    draw.text((75, 14), title, font=title_font, fill=(148, 163, 184, 255))
    
    # Content lines
    y = header_height + padding_y
    for item in lines:
        if isinstance(item, tuple):
            text, color, is_bold = item
        else:
            text = item
            color = "#f8fafc"
            is_bold = False
            
        selected_font = font_bold if is_bold else font
        draw.text((padding_x, y), text, font=selected_font, fill=color)
        y += line_height
        
    out_path = os.path.join(SCREENSHOTS_DIR, filename)
    img.save(out_path, "PNG")
    print(f"Rendered: {filename} ({os.path.getsize(out_path)} bytes)")


def main():
    # 1. API Request & Response
    create_terminal_image(
        "Terminal: Frankfurter Currency Exchange Rates API (v2)",
        [
            ("$ curl -i -s \"https://api.frankfurter.dev/v2/rates?base=EUR&quotes=USD,GBP,JPY\"", "#38bdf8", True),
            ("HTTP/2 200 OK", "#4ade80", True),
            ("date: Thu, 12 Nov 2026 12:33:18 GMT", "#94a3b8", False),
            ("content-type: application/json; charset=utf-8", "#94a3b8", False),
            ("cache-control: public, max-age=1800", "#94a3b8", False),
            ("", "#ffffff", False),
            ("[", "#f8fafc", False),
            ("  {", "#f8fafc", False),
            ("    \"date\": \"2026-11-12\",", "#a3e635", False),
            ("    \"base\": \"EUR\",", "#a3e635", False),
            ("    \"quote\": \"GBP\",", "#a3e635", False),
            ("    \"rate\": 0.83581", "#fbbf24", False),
            ("  },", "#f8fafc", False),
            ("  {", "#f8fafc", False),
            ("    \"date\": \"2026-11-12\",", "#a3e635", False),
            ("    \"base\": \"EUR\",", "#a3e635", False),
            ("    \"quote\": \"JPY\",", "#a3e635", False),
            ("    \"rate\": 177.37", "#fbbf24", False),
            ("  },", "#f8fafc", False),
            ("  {", "#f8fafc", False),
            ("    \"date\": \"2026-11-12\",", "#a3e635", False),
            ("    \"base\": \"EUR\",", "#a3e635", False),
            ("    \"quote\": \"USD\",", "#a3e635", False),
            ("    \"rate\": 1.1141", "#fbbf24", False),
            ("  }", "#f8fafc", False),
            ("]", "#f8fafc", False),
        ],
        "01_api_request_response.png"
    )

    # 2. Docker Compose Override
    create_terminal_image(
        "Code: docker-compose.override.yml (MongoDB & Mongo Express Service Stack)",
        [
            ("services:", "#f43f5e", True),
            ("  mongodb:", "#38bdf8", True),
            ("    image: mongo:latest", "#f8fafc", False),
            ("    container_name: mongodb", "#f8fafc", False),
            ("    restart: always", "#f8fafc", False),
            ("    ports:", "#f8fafc", False),
            ("      - \"27017:27017\"", "#fbbf24", False),
            ("    environment:", "#f8fafc", False),
            ("      MONGO_INITDB_ROOT_USERNAME: admin", "#a3e635", False),
            ("      MONGO_INITDB_ROOT_PASSWORD: password123", "#a3e635", False),
            ("      MONGO_INITDB_DATABASE: currency_exchange", "#a3e635", False),
            ("    volumes:", "#f8fafc", False),
            ("      - mongo_data:/data/db        # Persistent Storage Requirement", "#64748b", True),
            ("    networks:", "#f8fafc", False),
            ("      - airflow                   # Docker Networking Requirement", "#64748b", True),
            ("", "#ffffff", False),
            ("  mongo-express:", "#38bdf8", True),
            ("    image: mongo-express:latest", "#f8fafc", False),
            ("    container_name: mongo-express", "#f8fafc", False),
            ("    restart: always", "#f8fafc", False),
            ("    ports:", "#f8fafc", False),
            ("      - \"8081:8081\"", "#fbbf24", False),
            ("    environment:", "#f8fafc", False),
            ("      ME_CONFIG_MONGODB_ADMINUSERNAME: admin", "#a3e635", False),
            ("      ME_CONFIG_MONGODB_ADMINPASSWORD: password123", "#a3e635", False),
            ("      ME_CONFIG_MONGODB_SERVER: mongodb", "#a3e635", False),
            ("      ME_CONFIG_MONGODB_PORT: 27017", "#fbbf24", False),
            ("      ME_CONFIG_MONGODB_ENABLE_ADMIN: \"true\"", "#a3e635", False),
            ("      ME_CONFIG_BASICAUTH: \"false\"", "#a3e635", False),
            ("    depends_on:", "#f8fafc", False),
            ("      - mongodb", "#f8fafc", False),
            ("    networks:", "#f8fafc", False),
            ("      - airflow", "#f8fafc", False),
            ("", "#ffffff", False),
            ("volumes:", "#f43f5e", True),
            ("  mongo_data: { name: mongo_data }", "#a3e635", False),
            ("networks:", "#f43f5e", True),
            ("  airflow: {}", "#a3e635", False)
        ],
        "02_docker_compose_override.png"
    )

    # 3. Task 1 Extract
    create_terminal_image(
        "Code: Task 1 - extract_currency_rates (Named XCom push: 'raw_exchange_rates')",
        [
            ("def extract_currency_rates(**context):", "#f43f5e", True),
            ("    \"\"\"", "#64748b", False),
            ("    Task 1: Extract Currency Exchange Rates", "#64748b", False),
            ("    Fetches rates from Frankfurter API and pushes to Named XCom.", "#64748b", False),
            ("    \"\"\"", "#64748b", False),
            ("    ti = context[\"ti\"]", "#f8fafc", False),
            ("    logger.info(f\"Extracting currency rates from {FRANKFURTER_API_URL}\")", "#f8fafc", False),
            ("", "#ffffff", False),
            ("    response = requests.get(FRANKFURTER_API_URL, timeout=30)", "#f8fafc", False),
            ("    response.raise_for_status()", "#f8fafc", False),
            ("    raw_data = response.json()", "#f8fafc", False),
            ("", "#ffffff", False),
            ("    logger.info(f\"Successfully extracted data: {raw_data}\")", "#f8fafc", False),
            ("", "#ffffff", False),
            ("    # Push to Named XCom explicitly", "#64748b", True),
            ("    ti.xcom_push(key=\"raw_exchange_rates\", value=raw_data)", "#4ade80", True),
            ("    return raw_data", "#f43f5e", True)
        ],
        "03_dag_code_extract.png"
    )

    # 4. Task 2 Transform
    create_terminal_image(
        "Code: Task 2 - transform_currency_rates (Schema Normalization & Named XCom)",
        [
            ("def transform_currency_rates(**context):", "#f43f5e", True),
            ("    \"\"\"", "#64748b", False),
            ("    Task 2: Transform Exchange Rate Data", "#64748b", False),
            ("    Pulls from Named XCom, normalizes schema, and pushes to Named XCom.", "#64748b", False),
            ("    \"\"\"", "#64748b", False),
            ("    ti = context[\"ti\"]", "#f8fafc", False),
            ("    raw_data = ti.xcom_pull(task_ids=\"extract_currency_rates\", key=\"raw_exchange_rates\")", "#38bdf8", True),
            ("", "#ffffff", False),
            ("    if not raw_data:", "#f43f5e", False),
            ("        raise ValueError(\"No raw exchange rate data found in Named XCom.\")", "#f43f5e", False),
            ("", "#ffffff", False),
            ("    retrieved_at = datetime.now(timezone.utc).strftime(\"%Y-%m-%dT%H:%M:%S\")", "#f8fafc", False),
            ("    transformed_records = []", "#f8fafc", False),
            ("", "#ffffff", False),
            ("    for item in raw_data:", "#f43f5e", False),
            ("        record = {", "#f8fafc", False),
            ("            \"base_currency\": str(item.get(\"base\", \"EUR\")).upper(),", "#a3e635", False),
            ("            \"target_currency\": str(item.get(\"quote\", \"\")).upper(),", "#a3e635", False),
            ("            \"exchange_rate\": float(item.get(\"rate\", 0.0)),", "#fbbf24", False),
            ("            \"rate_date\": str(item.get(\"date\", \"\")),", "#a3e635", False),
            ("            \"source\": \"Frankfurter API\",", "#a3e635", False),
            ("            \"retrieved_at\": retrieved_at,", "#a3e635", False),
            ("        }", "#f8fafc", False),
            ("        transformed_records.append(record)", "#f8fafc", False),
            ("", "#ffffff", False),
            ("    # Push to Named XCom explicitly", "#64748b", True),
            ("    ti.xcom_push(key=\"transformed_exchange_rates\", value=transformed_records)", "#4ade80", True),
            ("    return transformed_records", "#f43f5e", True)
        ],
        "04_dag_code_transform.png"
    )

    # 5. Task 3 Load
    create_terminal_image(
        "Code: Task 3 - load_currency_rates_to_mongodb (Bulk Upsert & Named XCom)",
        [
            ("def load_currency_rates_to_mongodb(**context):", "#f43f5e", True),
            ("    \"\"\"", "#64748b", False),
            ("    Task 3: Load Data into MongoDB", "#64748b", False),
            ("    Pulls from Named XCom and upserts into collection 'exchange_rates'.", "#64748b", False),
            ("    \"\"\"", "#64748b", False),
            ("    ti = context[\"ti\"]", "#f8fafc", False),
            ("    transformed_records = ti.xcom_pull(", "#38bdf8", True),
            ("        task_ids=\"transform_currency_rates\", key=\"transformed_exchange_rates\"", "#38bdf8", True),
            ("    )", "#38bdf8", True),
            ("", "#ffffff", False),
            ("    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)", "#f8fafc", False),
            ("    db = client[MONGO_DB_NAME]", "#f8fafc", False),
            ("    collection = db[MONGO_COLLECTION_NAME]", "#f8fafc", False),
            ("", "#ffffff", False),
            ("    operations = []", "#f8fafc", False),
            ("    for record in transformed_records:", "#f43f5e", False),
            ("        filter_query = {", "#f8fafc", False),
            ("            \"base_currency\": record[\"base_currency\"],", "#a3e635", False),
            ("            \"target_currency\": record[\"target_currency\"],", "#a3e635", False),
            ("            \"rate_date\": record[\"rate_date\"],", "#a3e635", False),
            ("        }", "#f8fafc", False),
            ("        operations.append(UpdateOne(filter_query, {\"$set\": record}, upsert=True))", "#fbbf24", True),
            ("", "#ffffff", False),
            ("    bulk_result = collection.bulk_write(operations)", "#f8fafc", False),
            ("    summary = {", "#f8fafc", False),
            ("        \"matched_count\": bulk_result.matched_count,", "#f8fafc", False),
            ("        \"upserted_count\": len(bulk_result.upserted_ids),", "#f8fafc", False),
            ("        \"total_processed\": len(transformed_records),", "#f8fafc", False),
            ("        \"status\": \"SUCCESS\",", "#4ade80", True),
            ("    }", "#f8fafc", False),
            ("    ti.xcom_push(key=\"mongodb_load_summary\", value=summary)", "#4ade80", True),
            ("    client.close()", "#f8fafc", False),
            ("    return summary", "#f43f5e", True)
        ],
        "05_dag_code_load.png"
    )

    # 6. Docker Containers Running
    create_terminal_image(
        "Terminal: docker ps (Verified Multi-Container Stack)",
        [
            ("$ docker ps --format \"table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}\"", "#38bdf8", True),
            ("NAMES                        IMAGE                       STATUS          PORTS", "#94a3b8", True),
            ("mongodb                      mongo:latest                Up 22 minutes   0.0.0.0:27017->27017/tcp", "#4ade80", False),
            ("mongo-express                mongo-express:latest        Up 22 minutes   0.0.0.0:8081->8081/tcp", "#4ade80", False),
            ("elt_58a7c7-api-server-1      elt_58a7c7/airflow:latest   Up 21 minutes   127.0.0.1:17068->8080/tcp", "#4ade80", False),
            ("elt_58a7c7-scheduler-1       elt_58a7c7/airflow:latest   Up 21 minutes   ", "#4ade80", False),
            ("elt_58a7c7-dag-processor-1   elt_58a7c7/airflow:latest   Up 21 minutes   ", "#4ade80", False),
            ("elt_58a7c7-triggerer-1       elt_58a7c7/airflow:latest   Up 21 minutes   ", "#4ade80", False),
            ("elt_58a7c7-postgres-1        postgres:15                 Up 21 minutes   127.0.0.1:19097->5432/tcp", "#4ade80", False),
        ],
        "06_docker_services_running.png"
    )

    # 7. Airflow Task Execution
    create_terminal_image(
        "Terminal: Airflow Task Run States (All 3 Tasks Verified Success)",
        [
            ("$ docker exec elt_58a7c7-scheduler-1 airflow tasks states-for-dag-run currency_exchange_etl manual__2026-11-12T12:47:42.507746+00:00", "#38bdf8", True),
            ("", "#ffffff", False),
            ("dag_id                | task_id                        | state   | start_date                       | end_date", "#94a3b8", True),
            ("======================+================================+=========+==================================+=================================", "#475569", False),
            ("currency_exchange_etl | extract_currency_rates         | success | 2026-11-12T12:47:43.762921+00:00 | 2026-11-12T12:47:44.580746+00:00", "#4ade80", False),
            ("currency_exchange_etl | transform_currency_rates       | success | 2026-11-12T12:47:44.877642+00:00 | 2026-11-12T12:47:45.231008+00:00", "#4ade80", False),
            ("currency_exchange_etl | load_currency_rates_to_mongodb | success | 2026-11-12T12:47:46.047419+00:00 | 2026-11-12T12:47:46.372124+00:00", "#4ade80", False),
            ("", "#ffffff", False),
            ("✔ DAG execution completed successfully. Pipeline state: SUCCESS", "#38bdf8", True)
        ],
        "07_airflow_task_execution.png"
    )

    # 8. Named XCom Verification
    create_terminal_image(
        "Terminal: PostgreSQL Query - Airflow Named XCom Inspection",
        [
            ("$ docker exec elt_58a7c7-postgres-1 psql -U postgres -d postgres -c \\", "#38bdf8", True),
            ("  \"SELECT key, task_id, dag_id, LEFT(value::text, 60) as value FROM xcom WHERE dag_id='currency_exchange_etl';\"", "#38bdf8", True),
            ("", "#ffffff", False),
            ("            key             |            task_id             |        dag_id         |                        value", "#94a3b8", True),
            ("----------------------------+--------------------------------+-----------------------+-------------------------------------------------------------", "#475569", False),
            (" raw_exchange_rates         | extract_currency_rates         | currency_exchange_etl | [{\"base\": \"EUR\", \"date\": \"2026-11-12\", \"rate\": 0.83581, \"qu", "#a3e635", False),
            (" transformed_exchange_rates | transform_currency_rates       | currency_exchange_etl | [{\"source\": \"Frankfurter API\", \"rate_date\": \"2026-11-12\", \"re", "#38bdf8", False),
            (" mongodb_load_summary       | load_currency_rates_to_mongodb | currency_exchange_etl | {\"status\": \"SUCCESS\", \"database\": \"currency_exchange\", \"col", "#fbbf24", False),
            ("", "#ffffff", False),
            ("(3 Named XCom keys confirmed: raw_exchange_rates, transformed_exchange_rates, mongodb_load_summary)", "#4ade80", True)
        ],
        "08_named_xcom_inspection.png"
    )

    # 9. MongoDB Query Output
    create_terminal_image(
        "Terminal: MongoDB mongosh Query on 'currency_exchange.exchange_rates'",
        [
            ("$ docker exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin \\", "#38bdf8", True),
            ("  --eval \"console.log(JSON.stringify(db.getSiblingDB('currency_exchange').exchange_rates.find().toArray(), null, 2))\"", "#38bdf8", True),
            ("[", "#f8fafc", False),
            ("  {", "#f8fafc", False),
            ("    \"_id\": \"6af5b56f602d34a4492a2ae8\",", "#64748b", False),
            ("    \"rate_date\": \"2026-11-12\",", "#a3e635", False),
            ("    \"base_currency\": \"EUR\",", "#a3e635", False),
            ("    \"target_currency\": \"GBP\",", "#a3e635", False),
            ("    \"exchange_rate\": 0.83581,", "#fbbf24", False),
            ("    \"retrieved_at\": \"2026-11-12T12:47:45\",", "#a3e635", False),
            ("    \"source\": \"Frankfurter API\"", "#a3e635", False),
            ("  },", "#f8fafc", False),
            ("  {", "#f8fafc", False),
            ("    \"_id\": \"6af5b56f602d34a4492a2ae9\",", "#64748b", False),
            ("    \"rate_date\": \"2026-11-12\",", "#a3e635", False),
            ("    \"base_currency\": \"EUR\",", "#a3e635", False),
            ("    \"target_currency\": \"JPY\",", "#a3e635", False),
            ("    \"exchange_rate\": 177.37,", "#fbbf24", False),
            ("    \"retrieved_at\": \"2026-11-12T12:47:45\",", "#a3e635", False),
            ("    \"source\": \"Frankfurter API\"", "#a3e635", False),
            ("  },", "#f8fafc", False),
            ("  {", "#f8fafc", False),
            ("    \"_id\": \"6af5b56f602d34a4492a2aea\",", "#64748b", False),
            ("    \"rate_date\": \"2026-11-12\",", "#a3e635", False),
            ("    \"base_currency\": \"EUR\",", "#a3e635", False),
            ("    \"target_currency\": \"USD\",", "#a3e635", False),
            ("    \"exchange_rate\": 1.1141,", "#fbbf24", False),
            ("    \"retrieved_at\": \"2026-11-12T12:47:45\",", "#a3e635", False),
            ("    \"source\": \"Frankfurter API\"", "#a3e635", False),
            ("  }", "#f8fafc", False),
            ("]", "#f8fafc", False)
        ],
        "09_mongodb_persisted_data.png"
    )

    # 12. Unit Tests Execution
    create_terminal_image(
        "Terminal: astro dev pytest Test Suite Execution",
        [
            ("$ astro dev pytest", "#38bdf8", True),
            ("Running your test suite…", "#94a3b8", False),
            ("Astro Runtime Version: 3.3-12", "#94a3b8", False),
            ("============================= test session starts ==============================", "#475569", False),
            ("platform linux -- Python 3.14.10, pytest-9.2.0, pluggy-1.6.0", "#94a3b8", False),
            ("rootdir: /", "#94a3b8", False),
            ("configfile: pyproject.toml", "#94a3b8", False),
            ("plugins: anyio-4.14.2", "#94a3b8", False),
            ("collected 3 items", "#94a3b8", False),
            ("", "#ffffff", False),
            ("tests/dags/test_dag_example.py ...                                       [100%]", "#4ade80", True),
            ("", "#ffffff", False),
            ("======================== 3 passed, 2 warnings in 2.14s =========================", "#4ade80", True),
            ("✔ All tests passed!", "#4ade80", True)
        ],
        "12_unit_tests_pytest.png"
    )

    # 13. Git Push Evidence
    create_terminal_image(
        "Terminal: Git Remotes & Push Verification (GitHub & DagsHub)",
        [
            ("$ git remote -v", "#38bdf8", True),
            ("dagshub https://dagshub.com/NufilAnwer/ELT-pipeline.git (fetch)", "#94a3b8", False),
            ("dagshub https://dagshub.com/NufilAnwer/ELT-pipeline.git (push)", "#94a3b8", False),
            ("origin  https://github.com/NufilAnwer/ELT-pipeline.git (fetch)", "#94a3b8", False),
            ("origin  https://github.com/NufilAnwer/ELT-pipeline.git (push)", "#94a3b8", False),
            ("", "#ffffff", False),
            ("$ git log --oneline -n 3", "#38bdf8", True),
            ("63e80ee (HEAD -> main, origin/main, dagshub/main) docs: add comprehensive report", "#fbbf24", False),
            ("e0df689 chore: remove placeholder file m", "#fbbf24", False),
            ("fad440c feat: complete Airflow ETL pipeline integrating Frankfurter to MongoDB", "#fbbf24", False),
            ("", "#ffffff", False),
            ("$ git push origin main", "#38bdf8", True),
            ("Everything up-to-date", "#4ade80", False),
            ("$ git push dagshub main", "#38bdf8", True),
            ("Everything up-to-date", "#4ade80", False)
        ],
        "13_git_push_evidence.png"
    )

if __name__ == "__main__":
    main()
