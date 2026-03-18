"""
create_snapshot.py

Purpose:
Create a new snapshot record in fact_data_snapshot table.

"""

import mysql.connector
import argparse
from datetime import datetime
import sys
from getpass import getpass
import os

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': None,   # sẽ set động
    'database': 'team2_firmhub'
}

# ============================================================
# DATABASE CONNECTION FUNCTION
# ============================================================

def get_connection(password):
    try:
        config = DB_CONFIG.copy()
        config['password'] = password
        return mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        print(f"❌ Connection failed: {err}")
        sys.exit(1)

# ============================================================
# LOOKUP SOURCE_ID FROM dim_data_source
# ============================================================

def get_source_id(cursor, source_name):
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

def create_snapshot(conn, source_name, fiscal_year, snapshot_date, version_tag):

    cursor = conn.cursor()

    try:
        # 1️⃣ Validate date
        try:
            datetime.strptime(snapshot_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("snapshot_date must be in format YYYY-MM-DD")

        # 2️⃣ Get source_id
        source_id = get_source_id(cursor, source_name)

        # 3️⃣ Insert
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
            "system"
        ))

        snapshot_id = cursor.lastrowid

        # 4️⃣ Commit 
        conn.commit()

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
        raise  

    finally:
        cursor.close()

# ============================================================
# COMMAND LINE INTERFACE (chạy riêng lẻ vẫn OK)
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Create snapshot for firm-year data"
    )

    parser.add_argument("--source", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--version", required=True)

    args = parser.parse_args()

    password = os.getenv("MYSQL_PASSWORD") or getpass("Enter MySQL password: ")

    conn = get_connection(password)

    try:
        create_snapshot(
            conn,
            source_name=args.source,
            fiscal_year=args.year,
            snapshot_date=args.date,
            version_tag=args.version
        )
    finally:
        conn.close()