# Team_2_FirmDataHub (2020–2024)

## 1. Project Overview
This project implements a Firm Data Hub for Vietnamese listed companies, including data storage, versioning, quality checks, and panel export.

## 2. Team member
- Nguyễn Phương Ngân
- Tạ Ngọc Ánh
- Vũ Thị Thúy Hằng
- Lê Phạm Khánh Linh

## 3. Project Structure
```text
TEAM_2_FirmDataHub/
│
├── README.md
│
├── sql/  # Database schema and views
│   └── schema_and_seed.sql
│
├── etl/  # Python ETL scripts
│   ├── __init__.py
│   ├── import_firms.py
│   ├── create_snapshot.py
│   ├── import_panel.py
│   ├── qc_checks.py
│   └── export_panel.py
│
├── data/  # Input data files
│   ├── team_tickers.csv
│   ├── firms.xlsx
│   └── panel_2020_2024.xlsx
│
├── outputs/  # Generated outputs
│   ├── qc_report.csv
│   └── panel_latest.csv
│
├── docs/  # Documentation and diagrams
│   ├── erd.png
│   └── data_dictionary.md
│
├── scripts/
│   └── run_pipeline.sh   (hoặc .bat nếu dùng Windows)
│
└── .gitignore
```

## 4. How to Run
### Requirements
Before running the project, install the following:
- Python 3.10+
- MySQL 8+
- pip packages

### Step 1: Clone the Repository
```bash
git clone https://github.com/phngan23/Team_2_FirmDataHub.git
cd Team_2_FirmDataHub
```

### Step 2: Create and Activate Virtual Environment (run step-by-step)
Windows:
```bash
python -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned # run if error
.venv\Scripts\activate
```
Mac:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Project Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create the Database
Open PowerShell or Terminal in VS Code (Window):
```bash
cd "C:\Program Files\MySQL\MySQL Server 8.4\bin" # hoặc tìm trong Program Files (x86)
.\mysql -u root -p
```
Then enter your password to connect MySQL.
If you see 
```text
<mysql>
```
then run:
```bash
source sql/schema_and_seed.sql;
# if error, run:
source "path";
# path là đường dẫn đúng đến file schema_and_seed.sql trong máy, lưu ý đổi dấu \ thành /
# note: đường dẫn đầy đủ không được chứa ký tự tiếng việt, không chứa khoảng trắng
```

### Step 5: Import Firm Data
Firm information is stored in: data/firms.xlsx

Open Terminal and run:
```bash
cd etl
python import_firms.py
```
Enter your MySQL password to run. Then open MySQL and run the following query:
```sql
USE team2_firmhub;
SELECT COUNT(*) FROM dim_firm;
```
Expected result: 20

You can also preview the data:
```sql
SELECT * FROM dim_firm;
```

### Step 6: Create snapshot
Snapshots represent the firm-year observation structure used for panel data.

The script below creates 20 initial snapshots (one per firm).

Run:
```bash
python etl/init_snapshots.py
```
Expected output: === DONE INITIALIZING SNAPSHOTS ===

Then open MySQL and check the snapshot table:
```sql
SELECT * FROM fact_data_snapshot;
```

#### Create additional snapshots
If new firm-year data needs to be added later, run:
```bash
python etl/create_snapshot.py
```
This script generates new snapshot rows for additional years or new firms.

### Step 7: Import Panel Data
Panel financial data is stored in: data/panel_2020_2024.xlsx
Run the following script:
```bash
python etl/import_panel.py
```
Enter your MySQL password to run, and then expected output: 
```text
Imported rows: 100
Panel import completed ✅
```
Open MySQL and check:
```sql
SELECT COUNT(*) FROM fact_financial_year;
```
Expected output: 100

This confirms that the panel dataset has been successfully imported.
