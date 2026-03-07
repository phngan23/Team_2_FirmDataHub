"""
create_snapshot.py

Purpose:
Create a new snapshot record in fact_data_snapshot table.

Usage example:
python create_snapshot.py --source BCTC_Audited --year 2022 --date 2023-03-31 --version v1_raw

This script:
1. Connects to MySQL database
2. Looks up source_id from dim_data_source
3. Inserts a new snapshot
4. Returns snapshot_id
"""

import mysql.connector
import argparse
from datetime import datetime
import sys

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

# ⚠️ Update password if needed
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'team2_firmhub'
}

# ============================================================
# DATABASE CONNECTION FUNCTION
# ============================================================

def get_connection():
    """
    Create and return a MySQL connection.
    Exit program if connection fails.
    """
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"❌ Connection failed: {err}")
        sys.exit(1)

# ============================================================
# LOOKUP SOURCE_ID FROM dim_data_source
# ============================================================

def get_source_id(cursor, source_name):
    """
    Convert source_name (e.g. 'BCTC_Audited')
    into source_id from dim_data_source table.
    """

    cursor.execute("""
        SELECT source_id
        FROM dim_data_source
        WHERE source_name = %s
    """, (source_name,))
    
    result = cursor.fetchone()
    
    if not result:
        raise ValueError(f"Source not found in dim_data_source: {source_name}")
    
    return result[0]

# ============================================================
# CREATE SNAPSHOT FUNCTION
# ============================================================

def create_snapshot(source_name, fiscal_year, snapshot_date, version_tag):
    """
    Insert a new snapshot into fact_data_snapshot.

    Parameters:
        source_name  : Name of source (must exist in dim_data_source)
        fiscal_year  : Year of data (2020–2024)
        snapshot_date: Date when snapshot is created
        version_tag  : Version label (e.g., v1_raw, v2_after_qc)

    Returns:
        snapshot_id (auto-generated primary key)
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # --------------------------------------------------------
        # 1️⃣ Validate snapshot_date format (YYYY-MM-DD)
        # --------------------------------------------------------
        try:
            datetime.strptime(snapshot_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("snapshot_date must be in format YYYY-MM-DD")

        # --------------------------------------------------------
        # 2️⃣ Get source_id from dim_data_source
        # --------------------------------------------------------
        source_id = get_source_id(cursor, source_name)

        # --------------------------------------------------------
        # 3️⃣ Insert new snapshot record
        # --------------------------------------------------------
        insert_sql = """
        INSERT INTO fact_data_snapshot
        (snapshot_date, fiscal_year, source_id, version_tag, created_by)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(insert_sql, (
            snapshot_date,
            fiscal_year,
            source_id,
            version_tag,
            "system"   # default created_by
        ))

        # --------------------------------------------------------
        # 4️⃣ Get auto-generated snapshot_id
        # --------------------------------------------------------
        snapshot_id = cursor.lastrowid

        # --------------------------------------------------------
        # 5️⃣ Commit transaction
        # --------------------------------------------------------
        conn.commit()

        # --------------------------------------------------------
        # 6️⃣ Print confirmation
        # --------------------------------------------------------
        print("=================================")
        print("✅ Snapshot created successfully")
        print(f"snapshot_id : {snapshot_id}")
        print(f"source      : {source_name}")
        print(f"year        : {fiscal_year}")
        print(f"version     : {version_tag}")
        print("=================================")

        return snapshot_id

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        sys.exit(1)

    finally:
        cursor.close()
        conn.close()

# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

if __name__ == "__main__":

    # Define expected command line arguments
    parser = argparse.ArgumentParser(
        description="Create snapshot for firm-year data"
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Source name (must exist in dim_data_source)"
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Fiscal year (e.g., 2022)"
    )

    parser.add_argument(
        "--date",
        required=True,
        help="Snapshot date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--version",
        required=True,
        help="Version tag (e.g., v1_raw, v2_after_qc)"
    )

    args = parser.parse_args()

    # Call main function
    create_snapshot(
        source_name=args.source,
        fiscal_year=args.year,
        snapshot_date=args.date,
        version_tag=args.version
    )