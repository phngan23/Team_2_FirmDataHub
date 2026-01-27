#!/bin/bash
# run_pipeline.sh
#
# Purpose
# -------
# Execute the full ETL pipeline for the Firm Data Hub.
#
# Steps
# -----
# 1. Import firm master data
# 2. Create a new snapshot
# 3. Import firm-year panel data
# 4. Run data quality checks
# 5. Export the latest clean panel dataset
#
# Usage
# -----
# bash scripts/run_pipeline.sh
