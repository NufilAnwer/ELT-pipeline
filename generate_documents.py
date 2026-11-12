import os
import subprocess
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.abspath(".")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DOCX_OUT = os.path.join(BASE_DIR, "ETL_Pipeline_Report.docx")
PDF_OUT = os.path.join(BASE_DIR, "ETL_Pipeline_Report.pdf")
HTML_OUT = os.path.join(BASE_DIR, "report_printable.html")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
TEMP_USER_DATA = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "edge_pdf_temp")

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_docx():
    print("Generating Word Document (DOCX)...")
    doc = Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("AIRFLOW ETL PIPELINE REPORT")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    run_sub = p_sub.add_run("Daily Currency Exchange Rates Integration into MongoDB via Astro CLI")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Metadata table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Author / Student:", "Nufil Anwer (l230532@lhr.nu.edu.pk)"),
        ("GitHub Repository:", "https://github.com/NufilAnwer/ELT-pipeline/tree/main"),
        ("DagsHub Repository:", "https://dagshub.com/NufilAnwer/ELT-pipeline"),
        ("Date & Status:", "November 12, 2026 | Verified & Production Ready")
    ]
    for i, (label, val) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(30, 41, 59)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(val)
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(14, 116, 144) if "http" in val else RGBColor(51, 65, 85)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(3)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 41, 59)
        return h

    def add_body_p(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_screenshot(filename, caption):
        img_path = os.path.join(SCREENSHOTS_DIR, filename)
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            doc.add_picture(img_path, width=Inches(6.4))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            r_cap = p_cap.add_run(f"Figure: {caption}")
            r_cap.font.name = "Calibri"
            r_cap.font.size = Pt(9.5)
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(100, 116, 139)

    # 1. Executive Summary
    add_heading_1("1. Executive Summary")
    add_body_p(
        "This project implements an enterprise-grade automated ETL (Extract, Transform, Load) "
        "data pipeline developed with Astronomer's Astro CLI and Apache Airflow. The objective is "
        "to regularly ingest foreign exchange rate metrics from the public Frankfurter API, "
        "normalize and validate data structures according to rigorous business specifications, "
        "and persist the transformed records into MongoDB. A web-based graphical interface "
        "(Mongo Express) is integrated alongside Airflow services over a custom Docker bridge network "
        "with persistent storage."
    )

    # 2. Public API Integration
    add_heading_1("2. Public API Architecture (Frankfurter API)")
    add_body_p(
        "The extraction phase consumes the public Frankfurter currency exchange API (https://frankfurter.dev). "
        "Specifically, the endpoint 'https://api.frankfurter.dev/v2/rates?base=EUR&quotes=USD,GBP,JPY' "
        "is queried to retrieve base EUR rates against USD, GBP, and JPY in real time."
    )
    add_screenshot("01_api_request_response.png", "Frankfurter API v2 Request & JSON Response Payload")

    # 3. Multi-Service Container Architecture
    add_heading_1("3. Multi-Service Docker Architecture & Configuration")
    add_body_p(
        "The architecture configures MongoDB as the core operational database and Mongo Express as "
        "the administration interface via 'docker-compose.override.yml'. The deployment fulfills all "
        "required container metadata:"
    )
    add_body_p(
        "• Docker Networking: MongoDB, Mongo Express, Airflow Scheduler, and API Server are connected "
        "to a custom bridge network ('airflow'), enabling secure inter-container communication using DNS names.\n"
        "• Persistent Storage: A named Docker volume 'mongo_data' is mounted to '/data/db' inside MongoDB, "
        "guaranteeing full state persistence across container recycles."
    )
    add_screenshot("02_docker_compose_override.png", "docker-compose.override.yml Service & Network Definitions")
    add_screenshot("06_docker_services_running.png", "Active Docker Containers Stack (docker ps Output)")

    # 4. Airflow DAG Implementation & Three Core Tasks
    add_heading_1("4. Airflow DAG Implementation & Three Core Tasks")
    add_body_p(
        "The pipeline is encapsulated in DAG 'currency_exchange_etl' running on a daily schedule. "
        "The workflow enforces strict sequential execution: Extract >> Transform >> Load. "
        "Inter-task communication is achieved using explicit Airflow Named XComs."
    )
    
    add_heading_2("4.1 Task 1: Extract Currency Exchange Rates")
    add_body_p(
        "Performs an HTTP GET request to the Frankfurter API, validates HTTP 200 OK status, "
        "and pushes the raw rate payload into Named XCom key 'raw_exchange_rates'."
    )
    add_screenshot("03_dag_code_extract.png", "Task 1: extract_currency_rates Code with Named XCom Push")

    add_heading_2("4.2 Task 2: Transform Exchange Rate Data")
    add_body_p(
        "Pulls raw data from Named XCom key 'raw_exchange_rates', validates the structure, and maps "
        "each rate into the target schema: base_currency, target_currency, exchange_rate, rate_date, "
        "source, and retrieved_at (ISO 8601 UTC timestamp). Transformed records are pushed to Named XCom "
        "key 'transformed_exchange_rates'."
    )
    add_screenshot("04_dag_code_transform.png", "Task 2: transform_currency_rates Code with Schema Normalization")

    add_heading_2("4.3 Task 3: Load Data into MongoDB")
    add_body_p(
        "Pulls transformed records from Named XCom key 'transformed_exchange_rates', establishes a "
        "connection to MongoDB (database 'currency_exchange', collection 'exchange_rates'), and executes "
        "idempotent bulk upsert operations. A summary of modified/upserted counts is pushed to Named XCom "
        "key 'mongodb_load_summary'."
    )
    add_screenshot("05_dag_code_load.png", "Task 3: load_currency_rates_to_mongodb Code with Bulk Upsert")

    # 5. Airflow Execution & Named XCom Verification
    add_heading_1("5. Airflow Execution & Named XCom Verification")
    add_body_p(
        "The DAG was triggered and verified in the containerized Airflow environment. "
        "All three tasks executed successfully with zero failures."
    )
    add_screenshot("07_airflow_task_execution.png", "Airflow CLI: Task Run States Confirmed SUCCESS")
    add_body_p(
        "To verify Named XCom usage, the Airflow PostgreSQL metadata table 'xcom' was queried directly. "
        "The output confirms all three named keys are registered and passed between tasks."
    )
    add_screenshot("08_named_xcom_inspection.png", "PostgreSQL Metadata Query: Verified Named XCom Keys")

    # 6. MongoDB Persistence & Mongo Express UI
    add_heading_1("6. MongoDB Persistence & Mongo Express Administration")
    add_body_p(
        "Direct inspection of the MongoDB database collection 'currency_exchange.exchange_rates' "
        "via 'mongosh' confirms that records were correctly normalized and stored."
    )
    add_screenshot("09_mongodb_persisted_data.png", "MongoDB mongosh Query: Persisted Documents in exchange_rates")
    
    add_body_p(
        "The Mongo Express administrative web interface (accessible on port 8081) was validated. "
        "The dashboard displays server connectivity, active database statistics, and collection contents."
    )
    add_screenshot("10_mongo_express_dashboard.png", "Mongo Express Web UI: Server Dashboard & Database List")
    add_screenshot("11_mongo_express_documents.png", "Mongo Express Web UI: Viewing Documents in exchange_rates Collection")

    # 7. Unit Tests & Version Control
    add_heading_1("7. Quality Assurance & Git Repository Evidence")
    add_body_p(
        "Automated DAG integrity and configuration tests were executed using Astro CLI's test suite "
        "('astro dev pytest'). All 3 tests passed without import or parsing errors."
    )
    add_screenshot("12_unit_tests_pytest.png", "Astro Dev Pytest Execution: 3 Passed")

    add_body_p(
        "All pipeline assets, configuration files, and documentation were version-controlled and pushed "
        "to both GitHub and DagsHub repositories."
    )
    add_screenshot("13_git_push_evidence.png", "Git Log, Remotes, and Push Verification")

    # 8. Summary Table
    add_heading_1("8. Requirements Compliance Checklist")
    comp_table = doc.add_table(rows=8, cols=3)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    checklist = [
        ("Requirement", "Implementation Detail", "Status"),
        ("Astro CLI Integration", "Astro Runtime initialized, configured, and tested", "COMPLIANT"),
        ("Frankfurter Public API", "Ingestion from https://api.frankfurter.dev/v2/rates", "COMPLIANT"),
        ("MongoDB & Mongo Express", "Services configured in docker-compose.override.yml", "COMPLIANT"),
        ("Docker Networking & Storage", "Bridge network 'airflow' & persistent volume 'mongo_data'", "COMPLIANT"),
        ("Three Airflow Tasks", "Extract, Transform, and Load tasks with sequential workflow", "COMPLIANT"),
        ("Airflow Named XComs", "raw_exchange_rates, transformed_exchange_rates, mongodb_load_summary", "COMPLIANT"),
        ("GitHub & DagsHub Push", "Code pushed to https://github.com/NufilAnwer/ELT-pipeline/tree/main", "COMPLIANT"),
    ]
    for i, (col0, col1, col2) in enumerate(checklist):
        row = comp_table.rows[i]
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width = Inches(2.2)
        c1.width = Inches(3.5)
        c2.width = Inches(1.2)
        
        bg = "1E293B" if i == 0 else ("F8FAFC" if i % 2 == 1 else "FFFFFF")
        text_color = RGBColor(255, 255, 255) if i == 0 else RGBColor(30, 41, 59)
        status_color = RGBColor(255, 255, 255) if i == 0 else RGBColor(16, 185, 129)
        
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(col0)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = text_color
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(col1)
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = text_color
        
        p2 = c2.paragraphs[0]
        r2 = p2.add_run(col2)
        r2.font.bold = True
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = status_color

    doc.save(DOCX_OUT)
    print(f"Generated DOCX: {DOCX_OUT} ({os.path.getsize(DOCX_OUT)} bytes)")

def create_html_and_pdf():
    print("Generating HTML for PDF compilation...")
    
    # We will build an HTML report with CSS print styles and base64 embedded images
    import base64
    def b64_img(filename):
        path = os.path.join(SCREENSHOTS_DIR, filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        return ""

    img_api = b64_img("01_api_request_response.png")
    img_override = b64_img("02_docker_compose_override.png")
    img_t1 = b64_img("03_dag_code_extract.png")
    img_t2 = b64_img("04_dag_code_transform.png")
    img_t3 = b64_img("05_dag_code_load.png")
    img_ps = b64_img("06_docker_services_running.png")
    img_tasks = b64_img("07_airflow_task_execution.png")
    img_xcom = b64_img("08_named_xcom_inspection.png")
    img_mongo = b64_img("09_mongodb_persisted_data.png")
    img_me_dash = b64_img("10_mongo_express_dashboard.png")
    img_me_docs = b64_img("11_mongo_express_documents.png")
    img_pytest = b64_img("12_unit_tests_pytest.png")
    img_git = b64_img("13_git_push_evidence.png")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Airflow ETL Pipeline Technical Report</title>
<style>
    @page {{
        size: A4;
        margin: 18mm 15mm 18mm 15mm;
        @bottom-right {{
            content: counter(page);
        }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        line-height: 1.5;
        font-size: 11pt;
        margin: 0;
        padding: 0;
    }}
    .header-box {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 24px;
    }}
    h1 {{
        font-size: 20pt;
        margin: 0 0 6px 0;
        color: #38bdf8;
        font-weight: 700;
    }}
    .subtitle {{
        font-size: 12pt;
        color: #94a3b8;
        margin: 0 0 16px 0;
    }}
    .meta-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        font-size: 9.5pt;
        background: rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 6px;
    }}
    .meta-grid a {{
        color: #38bdf8;
        text-decoration: none;
    }}
    h2 {{
        font-size: 14pt;
        color: #0f172a;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 4px;
        margin-top: 24px;
        margin-bottom: 12px;
        page-break-after: avoid;
    }}
    h3 {{
        font-size: 11pt;
        color: #334155;
        margin-top: 16px;
        margin-bottom: 8px;
        page-break-after: avoid;
    }}
    p {{
        margin: 0 0 10px 0;
        text-align: justify;
    }}
    .img-card {{
        margin: 14px 0 18px 0;
        page-break-inside: avoid;
        text-align: center;
    }}
    .img-card img {{
        max-width: 100%;
        border-radius: 6px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #cbd5e1;
    }}
    .caption {{
        font-size: 9pt;
        font-style: italic;
        color: #64748b;
        margin-top: 6px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }}
    th, td {{
        border: 1px solid #cbd5e1;
        padding: 8px 12px;
        text-align: left;
    }}
    th {{
        background-color: #0f172a;
        color: #ffffff;
    }}
    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}
    .badge {{
        background: #10b981;
        color: #ffffff;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 8.5pt;
    }}
    .page-break {{
        page-break-before: always;
    }}
</style>
</head>
<body>

<div class="header-box">
    <h1>AIRFLOW ETL PIPELINE REPORT</h1>
    <div class="subtitle">Daily Currency Exchange Rates Integration into MongoDB via Astro CLI</div>
    <div class="meta-grid">
        <div><strong>Author:</strong> Nufil Anwer (l230532@lhr.nu.edu.pk)</div>
        <div><strong>Date:</strong> November 12, 2026</div>
        <div><strong>GitHub:</strong> <a href="https://github.com/NufilAnwer/ELT-pipeline/tree/main">github.com/NufilAnwer/ELT-pipeline</a></div>
        <div><strong>DagsHub:</strong> <a href="https://dagshub.com/NufilAnwer/ELT-pipeline">dagshub.com/NufilAnwer/ELT-pipeline</a></div>
    </div>
</div>

<h2>1. Executive Summary</h2>
<p>
    This report documents the architecture, implementation, and successful verification of an automated
    ETL data pipeline orchestrated with Astronomer's <strong>Astro CLI</strong> and <strong>Apache Airflow</strong>.
    The pipeline ingests foreign exchange rates from the public <strong>Frankfurter API</strong>, performs normalization
    and strict JSON schema enforcement, and securely loads the transformed documents into a containerized 
    <strong>MongoDB</strong> database instance. Web administration is provided by <strong>Mongo Express</strong>.
    All data exchanges between pipeline tasks are governed via <strong>Airflow Named XComs</strong>.
</p>

<h2>2. Public API Architecture (Frankfurter API)</h2>
<p>
    The extraction phase queries the public Frankfurter API endpoint 
    <code>https://api.frankfurter.dev/v2/rates?base=EUR&quotes=USD,GBP,JPY</code>.
    The response delivers real-time exchange rates for EUR against USD, GBP, and JPY.
</p>
<div class="img-card">
    <img src="{img_api}" alt="Frankfurter API Request and Response">
    <div class="caption">Figure 1: Frankfurter API v2 Request & Output JSON Payload</div>
</div>

<h2>3. Multi-Service Container Architecture & Docker Configuration</h2>
<p>
    MongoDB and Mongo Express are orchestrated as complementary services alongside Airflow in 
    <code>docker-compose.override.yml</code>.
</p>
<p>
    • <strong>Docker Networking:</strong> All containers reside on the custom bridge network (<code>airflow</code>),
    enabling internal service discovery and secure communication via hostnames (<code>mongodb:27017</code>).<br>
    • <strong>Persistent Storage:</strong> A named volume (<code>mongo_data</code>) is attached to <code>/data/db</code>,
    guaranteeing zero data loss across container teardown or host reboot.
</p>
<div class="img-card">
    <img src="{img_override}" alt="Docker Compose Configuration">
    <div class="caption">Figure 2: docker-compose.override.yml Specification (MongoDB & Mongo Express)</div>
</div>

<div class="img-card">
    <img src="{img_ps}" alt="Running Docker Containers">
    <div class="caption">Figure 3: Active Containers Stack (docker ps Output)</div>
</div>

<div class="page-break"></div>

<h2>4. Airflow DAG Implementation & Three Core Tasks</h2>
<p>
    The DAG <code>currency_exchange_etl</code> defines three sequential tasks: 
    <code>extract_currency_rates >> transform_currency_rates >> load_currency_rates_to_mongodb</code>.
</p>

<h3>4.1 Task 1: Extract Currency Exchange Rates</h3>
<p>
    Queries the Frankfurter API, validates HTTP 200 OK status, and pushes raw JSON into Named XCom 
    <code>raw_exchange_rates</code>.
</p>
<div class="img-card">
    <img src="{img_t1}" alt="Task 1 Extract Code">
    <div class="caption">Figure 4: Task 1 (Extract) Implementation with Named XCom Push</div>
</div>

<h3>4.2 Task 2: Transform Exchange Rate Data</h3>
<p>
    Pulls from Named XCom <code>raw_exchange_rates</code> and normalizes each record to the required specification,
    appending the UTC retrieval timestamp. The transformed records are pushed to Named XCom <code>transformed_exchange_rates</code>.
</p>
<div class="img-card">
    <img src="{img_t2}" alt="Task 2 Transform Code">
    <div class="caption">Figure 5: Task 2 (Transform) Implementation with Schema Normalization</div>
</div>

<h3>4.3 Task 3: Load Data into MongoDB</h3>
<p>
    Pulls from Named XCom <code>transformed_exchange_rates</code>, connects to MongoDB database 
    <code>currency_exchange</code>, collection <code>exchange_rates</code>, and applies bulk upserts based on
    <code>(base_currency, target_currency, rate_date)</code> to ensure complete idempotency.
</p>
<div class="img-card">
    <img src="{img_t3}" alt="Task 3 Load Code">
    <div class="caption">Figure 6: Task 3 (Load) Implementation with Bulk Upsert</div>
</div>

<div class="page-break"></div>

<h2>5. Execution Evidence & Named XCom Verification</h2>
<p>
    The DAG was executed in the Astro Airflow environment. Verification confirmed that all tasks achieved 
    <strong>SUCCESS</strong> state.
</p>
<div class="img-card">
    <img src="{img_tasks}" alt="Airflow Task Run States">
    <div class="caption">Figure 7: Airflow CLI Task Instance States Confirmed SUCCESS</div>
</div>

<p>
    Inspection of the Airflow metadata database (PostgreSQL <code>xcom</code> table) confirms that explicit 
    Named XCom keys transferred payloads between tasks:
</p>
<div class="img-card">
    <img src="{img_xcom}" alt="Named XCom Verification">
    <div class="caption">Figure 8: PostgreSQL Metadata Table (xcom) Inspection</div>
</div>

<h2>6. MongoDB Data Persistence & Mongo Express Administration</h2>
<p>
    Querying MongoDB directly via <code>mongosh</code> confirms that documents were persisted with exact field specifications:
</p>
<div class="img-card">
    <img src="{img_mongo}" alt="MongoDB Persisted Documents">
    <div class="caption">Figure 9: Persisted Documents in MongoDB Collection exchange_rates</div>
</div>

<p>
    The web administration interface Mongo Express (running at <code>http://localhost:8081</code>) was validated:
</p>
<div class="img-card">
    <img src="{img_me_dash}" alt="Mongo Express Dashboard">
    <div class="caption">Figure 10: Mongo Express Web Dashboard Showing Databases & Server Status</div>
</div>

<div class="img-card">
    <img src="{img_me_docs}" alt="Mongo Express Documents View">
    <div class="caption">Figure 11: Mongo Express Web UI Viewing exchange_rates Documents</div>
</div>

<div class="page-break"></div>

<h2>7. Automated Testing & Version Control Evidence</h2>
<p>
    DAG integrity and configuration tests were validated via Astro CLI test suite:
</p>
<div class="img-card">
    <img src="{img_pytest}" alt="Astro Dev Pytest Execution">
    <div class="caption">Figure 12: Astro Dev Pytest Test Results (3 Passed)</div>
</div>

<p>
    All code and assets are synchronized with remote repositories:
</p>
<div class="img-card">
    <img src="{img_git}" alt="Git Push Verification">
    <div class="caption">Figure 13: Git Remote Repositories & Push Status</div>
</div>

<h2>8. Requirements Compliance Checklist</h2>
<table>
    <tr>
        <th>Requirement</th>
        <th>Implementation Detail</th>
        <th>Verification Status</th>
    </tr>
    <tr>
        <td><strong>Astro CLI Integration</strong></td>
        <td>Project initialized and operated via Astronomer Astro CLI</td>
        <td><span class="badge">COMPLIANT</span></td>
    </tr>
    <tr>
        <td><strong>Frankfurter Public API</strong></td>
        <td>HTTP GET to https://api.frankfurter.dev/v2/rates (EUR -> USD, GBP, JPY)</td>
        <td><span class="badge">COMPLIANT</span></td>
    </tr>
    <tr>
        <td><strong>MongoDB & Mongo Express</strong></td>
        <td>Configured as Docker services in docker-compose.override.yml</td>
        <td><span class="badge">COMPLIANT</span></td>
    </tr>
    <tr>
        <td><strong>Docker Networking & Storage</strong></td>
        <td>Bridge network 'airflow' & persistent volume 'mongo_data'</td>
        <td><span class="badge">COMPLIANT</span></td>
    </tr>
    <tr>
        <td><strong>Three Airflow Tasks</strong></td>
        <td>Extract, Transform, and Load tasks with sequential dependency</td>
        <td><span class="badge">COMPLIANT</span></td>
    </tr>
    <tr>
        <td><strong>Airflow Named XComs</strong></td>
        <td>raw_exchange_rates, transformed_exchange_rates, mongodb_load_summary</td>
        <td><span class="badge">COMPLIANT</span></td>
    </tr>
    <tr>
        <td><strong>Repository Push</strong></td>
        <td>Pushed to GitHub and DagsHub repositories</td>
        <td><span class="badge">COMPLIANT</span></td>
    </tr>
</table>

</body>
</html>
"""

    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated HTML: {HTML_OUT}")

    # Convert HTML to PDF using Edge headless
    print("Compiling PDF with Edge headless...")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        f"--user-data-dir={TEMP_USER_DATA}",
        f"--print-to-pdf={PDF_OUT}",
        f"file:///{HTML_OUT.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(PDF_OUT):
        print(f"Generated PDF: {PDF_OUT} ({os.path.getsize(PDF_OUT)} bytes)")
    else:
        print("Failed to generate PDF.")

if __name__ == "__main__":
    create_docx()
    create_html_and_pdf()
