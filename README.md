# Team_2_FirmDataHub

# Firm Data Hub (2020–2024)

## Project Overview
This project implements a Firm Data Hub for Vietnamese listed companies, including data storage, versioning, quality checks, and panel export.

## Team member
- Nguyễn Phương Ngân
- Tạ Ngọc Ánh
- Vũ Thị Thúy Hằng
- Lê Phạm Khánh Linh

## Folder Structure
- sql/: Database schema and views
- etl/: Python ETL scripts
- data/: Input data files
- outputs/: Generated outputs
- docs/: Documentation and diagrams

## How to Run
1. Run sql/schema_and_seed.sql
2. Run etl/import_firms.py
3. Run etl/create_snapshot.py
4. Run etl/import_panel.py
5. Run etl/qc_checks.py
6. Run etl/export_panel.py
