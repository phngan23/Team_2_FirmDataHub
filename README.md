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
1. Run sql/schema_and_seed.sql
2. Run etl/import_firms.py
3. Run etl/create_snapshot.py
4. Run etl/import_panel.py
5. Run etl/qc_checks.py
6. Run etl/export_panel.py
