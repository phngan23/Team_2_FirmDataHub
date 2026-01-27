"""
qc_checks.py

Purpose
-------
Perform data quality checks (QC) on firm-year panel data.

Main Responsibilities
---------------------
- Validate numerical constraints:
    + Ownership ratios within [0, 1]
    + Shares outstanding > 0
    + Total assets >= 0
    + Current liabilities >= 0
- Detect abnormal growth rates
- Check market value consistency:
    market_value_equity ≈ shares_outstanding × share_price
- Generate a structured QC report

Output
------
- outputs/qc_report.csv

QC Report Columns
-----------------
- ticker
- fiscal_year
- field_name
- error_type
- message

Notes
-----
- QC rules are configurable
- QC results do not modify data automatically
"""
