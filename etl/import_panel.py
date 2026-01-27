"""
import_panel.py

Purpose
-------
Import firm-year panel data (38 variables) into FACT tables.

Main Responsibilities
---------------------
- Read panel data from Excel file
- Validate firm existence against dim_firm
- Insert firm-year data into corresponding FACT tables:
    + fact_ownership_year
    + fact_financial_year
    + fact_cashflow_year
    + fact_market_year
    + fact_innovation_year
    + fact_firm_year_meta
- Associate all records with a snapshot_id

Input
-----
- data/panel_2020_2024.xlsx
- snapshot_id

Output
------
- Records inserted into FACT tables

Error Handling
--------------
- Reject and log any ticker not found in dim_firm
- Abort import if required keys are missing
"""
