"""
import_firms.py

Purpose
-------
Import and maintain the firm master data (DIM tables) for the Firm Data Hub.

Main Responsibilities
---------------------
- Read firm metadata from Excel input file
- Normalize firm attributes:
    + ticker
    + company_name
    + exchange (HOSE/HNX)
    + industry_l2
- Populate and maintain the following dimension tables:
    + dim_firm
    + dim_exchange
    + dim_industry_l2
- Apply upsert logic:
    + Insert new firms if ticker does not exist
    + Update existing records if firm information changes

Input
-----
- data/firms.xlsx

Output
------
- Updated DIM tables in MySQL database
- No file-based output

Constraints
-----------
- Ticker must be unique in dim_firm
- Exchange and industry must exist or be created before firm insertion
"""
