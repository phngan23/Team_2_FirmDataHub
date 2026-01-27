"""
export_panel.py

Purpose
-------
Export the latest clean firm-year panel dataset for analysis.

Main Responsibilities
---------------------
- Select the most recent snapshot per firm-year
- Join all FACT tables into a unified panel dataset
- Output a clean, analysis-ready CSV file

Output
------
- outputs/panel_latest.csv

Notes
-----
- Latest snapshot is determined by snapshot_date or snapshot_id
- Output is used for downstream analytics and modeling
"""
