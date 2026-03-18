"""
init_snapshots.py
"""

from create_snapshot import create_snapshot, get_connection
from getpass import getpass
import os

years = [2020, 2021, 2022, 2023, 2024]

sources = {
    "FiinPro": "01-20",
    "BCTC_Audited": "03-31",
    "Vietstock": "01-05",
    "AnnualReport": "04-15"
}

def main():
    print("=== INITIALIZING SNAPSHOTS ===\n")

    password = os.getenv("MYSQL_PASSWORD") or getpass("Enter MySQL password: ")

    conn = get_connection(password)

    try:
        for year in years:
            for source, date_suffix in sources.items():

                snapshot_date = f"{year+1}-{date_suffix}"

                print(f"Creating snapshot: {source} - {year}")

                try:
                    create_snapshot(
                        conn,
                        source_name=source,
                        fiscal_year=year,
                        snapshot_date=snapshot_date,
                        version_tag="v1_raw"
                    )
                    print("✅ Success\n")

                except Exception as e:
                    print(f"❌ Error: {e}")
                    print("Continuing...\n")

    finally:
        conn.close()

    print("=== DONE INITIALIZING SNAPSHOTS ===")

if __name__ == "__main__":
    main()