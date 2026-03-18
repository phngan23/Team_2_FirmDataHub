# Team 2 FirmDataHub (2020–2024)

## 1. Project Overview
This project implements a Firm Data Hub for Vietnamese listed companies, including data storage, versioning, quality checks, and panel export.

**Dataset:** 20 Vietnamese listed firms × 5 years (2020-2024) = 100 observations with 38 variables

## 2. Team Members
- Nguyễn Phương Ngân
- Tạ Ngọc Ánh
- Vũ Thị Thúy Hằng
- Lê Phạm Khánh Linh
**| Name | Student ID | Role & Responsibilities | Contribution |***
|------|------------|-------------------------|--------------|
| **Nguyen Phuong Ngan** | 11245914 | **Team Leader:** Led the project, built the database schema, developed core ETL scripts (import, snapshot, export), and integrated the full pipeline. Also handled data collection for firms 1–5. | % |
| **Vu Thi Thuy Hang** | 11245873 | **Data Quality Analyst:** Collected data for firms 6–10, validated ownership and market data, and implemented QC checks. | 25% |
| **Ta Ngoc Anh** | 11245844 | **Data & Documentation:** Collected data for firms 11–15, gathered innovation data (10 firms), and prepared the data dictionary, and reviewed the entire project after completion. | % |
| **Le Pham Khanh Linh** | 11245892 | **Database Design:** Collected data for firms 16–20, gathered innovation data (10 firms), and designed the ERD and relational schema, and reviewed the entire project after completion. | % |

## 3. Project Structure
```text
Team_2_FirmDataHub/
│
├── README.md
├── run_pipeline.py          # Master pipeline script (RUN THIS!)
│
├── sql/                     # Database schema and views
│   ├── schema_and_seed.sql
│   └── view.sql
│
├── etl/                     # ETL scripts (executed by run_pipeline.py)
│   ├── init_snapshots.py
│   ├── create_snapshot.py
│   ├── import_firms.py
│   ├── import_panel.py
│   ├── qc_checks.py
│   └── export_panel.py
│
├── data/                    # Input data files
│   ├── team_tickers.csv
│   ├── firms.xlsx
│   └── panel_2020_2024.xlsx
│
├── outputs/                 # Generated outputs
│   ├── qc_report.csv
│   └── panel_latest.csv
│
└── docs/                    # Documentation
    ├── erd.png
    └── data_dictionary.md
```

## 4. Quick Start Guide

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone https://github.com/phngan23/Team_2_FirmDataHub.git
cd Team_2_FirmDataHub
```

### Step 2: Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate

# If you get an execution policy error, run:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Database Schema

**Option A: Using PowerShell (Windows)**
```bash
Get-Content sql\schema_and_seed.sql | mysql -u root -p
```

**Option B: Using MySQL CLI**
```bash
mysql -u root -p

# Inside MySQL, run:
source sql/schema_and_seed.sql;

# If error, use full path (replace backslashes with forward slashes):
source D:/Path/To/Team_2_FirmDataHub/sql/schema_and_seed.sql;

# Exit MySQL
EXIT;
```

**Important:** The full path must NOT contain:
- Vietnamese characters (ú, ê, ô, etc.)
- Spaces

**Verify database creation:**
```sql
mysql -u root -p

USE team2_firmhub;
SHOW TABLES;
# Should show 11 tables

EXIT;
```

### Step 5: Run Complete Pipeline

**This single script runs everything:**
```bash
python run_pipeline.py
```

Enter your MySQL password when prompted.

**The pipeline will automatically:**
1. Create 20 data snapshots
2. Import 20 firms
3. Import 100 panel observations
4. Run QC checks (6 validation rules)
5. Create analytical views
6. Export final panel dataset

**Expected output:**
```text
======================================================================
TEAM 2 FIRM DATA HUB - COMPLETE ETL PIPELINE
======================================================================

Enter MySQL password: ****
Testing database connection...
✅ Database connection successful

======================================================================
STEP 1: Initializing Data Snapshots (20 snapshots)
======================================================================
[... progress messages ...]
✅ STEP 1 completed

======================================================================
STEP 2: Importing Firm Master Data (20 firms)
======================================================================
Loaded 20 firms
Inserted: 20
✅ STEP 2 completed

======================================================================
STEP 3: Importing Panel Data (100 observations)
======================================================================
Loaded 100 rows
Imported rows: 100
✅ STEP 3 completed

======================================================================
STEP 4: Running QC Checks
======================================================================
Total errors found: 3
Errors by ticker:
  CII: 3
✅ STEP 4 completed

======================================================================
STEP 5: Creating SQL Views
======================================================================
✅ Views created successfully

======================================================================
STEP 6: Exporting Panel Dataset
======================================================================
✓ Retrieved 100 rows × 42 columns
✅ STEP 6 completed

======================================================================
DATABASE VERIFICATION
======================================================================
✅ dim_firm: 20 rows
✅ fact_data_snapshot: 20 rows
✅ All fact tables: 100 rows each
✅ vw_firm_panel_latest: 100 rows

======================================================================
VERIFICATION: Checking Outputs
======================================================================
✅ qc_report.csv exists
✅ panel_latest.csv exists

======================================================================
✅ PIPELINE COMPLETED SUCCESSFULLY!
======================================================================
```

## 5. QC Report Notes

The QC checks validate 6 data quality rules. After running the pipeline, you will see:

**File:** `outputs/qc_report.csv`

**Expected errors:** 3 errors for CII (all related to market_value_equity)

### Why CII has errors?

**Reason:** CII's `market_value_equity` values are obtained directly from annual reports (actual market capitalization), NOT calculated from the formula `shares_outstanding × share_price`.

**Formula-based calculation:**
```
market_value = shares_outstanding × share_price / 1,000,000,000
```

**CII's actual values differ by >5% from this calculation because:**
- Official market cap data is more accurate than simple calculation
- Different timing: year-end closing price vs average market price
- Share count differences: outstanding shares vs diluted shares

**Resolution:** Data kept as-is (no corrections applied). CII values represent actual reported market capitalization from official sources.

**For other firms:** Market values are consistent with the formula (within 5% tolerance).

## 6. Output Files

After successful pipeline execution:

### `outputs/qc_report.csv`
- Data quality check results
- 3 rows (CII market value inconsistencies)
- Columns: ticker, fiscal_year, field_name, error_type, message

### `outputs/panel_latest.csv`
- Final panel dataset
- 100 rows (20 firms × 5 years)
- 42 columns (ticker, company_name, fiscal_year, firm_id + 38 variables)
- Ready for analysis

## 7. Database Schema

**Dimension Tables:**
- `dim_firm` - Firm master data (20 firms)
- `dim_exchange` - Stock exchanges (HOSE, HNX)
- `dim_industry_l2` - Industry classifications
- `dim_data_source` - Data sources (FiinPro, BCTC, Vietstock, Annual Reports)

**Fact Tables:**
- `fact_data_snapshot` - Data versioning (20 snapshots)
- `fact_ownership_year` - Ownership structure (100 observations)
- `fact_financial_year` - Financial statements (100 observations)
- `fact_cashflow_year` - Cash flow statements (100 observations)
- `fact_market_year` - Market data (100 observations)
- `fact_innovation_year` - Innovation indicators (100 observations)
- `fact_firm_year_meta` - Firm metadata (100 observations)

**Views:**
- `vw_firm_panel_latest` - Latest panel data (100 rows × 42 columns)

## 8. Data Variables (38 variables)

### Ownership (4 variables)
- managerial_inside_own, state_own, institutional_own, foreign_own

### Financial (23 variables)
- net_sales, total_assets, selling_expenses, general_admin_expenses
- intangible_assets_net, manufacturing_overhead, net_operating_income
- raw_material_consumption, merchandise_purchase_year, wip_goods_purchase
- outside_manufacturing_expenses, production_cost, rnd_expenses
- net_income, total_equity, total_liabilities, cash_and_equivalents
- long_term_debt, current_assets, current_liabilities, growth_ratio
- inventory, net_ppe

### Cashflow (3 variables)
- net_cfo, capex, net_cfi

### Market (4 variables)
- shares_outstanding, market_value_equity, dividend_cash_paid, eps_basic

### Innovation (2 variables)
- product_innovation, process_innovation

### Metadata (2 variables)
- employees_count, firm_age

## 9. Running Individual Scripts (Optional)

If you need to run scripts individually instead of using `run_pipeline.py`:

```bash
cd etl

# Step 1: Create snapshots
python init_snapshots.py

# Step 2: Import firms
python import_firms.py

# Step 3: Import panel
python import_panel.py

# Step 4: QC checks
python qc_checks.py

# Step 5: Create views (run SQL file instead)
mysql -u root -p team2_firmhub < ../sql/view.sql

# Step 6: Export panel
python export_panel.py
```

## 10. Troubleshooting

### Issue: Database not found
```
Error: Unknown database 'team2_firmhub'
```
**Solution:** Run Step 4 again to create the database schema.

### Issue: File not found error
```
FileNotFoundError: ../data/firms.xlsx
```
**Solution:** Make sure you run `run_pipeline.py` from the root directory (`Team_2_FirmDataHub/`), not from `etl/` or other subdirectories.

### Issue: Permission denied
```
Access denied for user 'root'
```
**Solution:** Check your MySQL password or verify MySQL is running.

### Issue: Path contains spaces or Vietnamese characters
**Solution:** Move the project folder to a path without spaces or special characters.
Example:
- ❌ Bad: `C:\Học tập\Đồ án\Team_2_FirmDataHub`
- ✅ Good: `C:\Projects\Team_2_FirmDataHub`

## 11. Data Sources

- **FiinPro:** Ownership data
- **BCTC Audited:** Financial statements and cash flow
- **Vietstock:** Market data
- **Annual Reports:** Innovation indicators and firm metadata

## 12. Version Control

The database implements snapshot-based versioning:
- Each firm-year observation can have multiple snapshots
- Views always return the latest snapshot (MAX snapshot_id)
- Historical data is preserved for audit trails

## 13. Contact

For questions, issues, or collaboration inquiries, please contact the team leader.

Team Leader: Nguyen Phuong Ngan
- Email: phngan3613@gmail.com
- Github: phngan23
- Phone: 0987836218

Project Repository: https://github.com/phngan23/Team_2_FirmDataHub
---
