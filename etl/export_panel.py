"""
export_panel.py

Purpose
-------
Export vw_firm_panel_latest to CSV for analysis.

Output
------
- outputs/panel_latest.csv

Output Format
-------------
- 100 rows (20 firms × 5 years)
- 42 columns (ticker, company_name, fiscal_year, firm_id + 38 variables)
- Sorted by ticker, fiscal_year
- UTF-8 encoding
"""

import os
import mysql.connector
from getpass import getpass
import pandas as pd
from pathlib import Path

# ─── CONFIGURATION ───────────────────────────────────────────────

# Output directory - parent of etl/ (i.e., ../outputs/)
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "panel_latest.csv"

# ─── MAIN EXECUTION ──────────────────────────────────────────────

def export_panel():
    """Export vw_firm_panel_latest to CSV."""
    
    print("=" * 70)
    print("EXPORT PANEL LATEST - team2_firmhub")
    print("=" * 70)
    print()
    
    # Connect to database
    print("Connecting to database...")
    password = os.getenv("MYSQL_PASSWORD") or getpass("Enter MySQL password: ")

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=password,
        database='team2_firmhub'
    )
    print("✓ Connected\n")
    
    # Check view exists
    print("Checking view vw_firm_panel_latest...")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.VIEWS 
        WHERE TABLE_SCHEMA = 'team2_firmhub' 
          AND TABLE_NAME = 'vw_firm_panel_latest'
    """)
    view_exists = cursor.fetchone()[0]
    
    if not view_exists:
        print("❌ Error: View vw_firm_panel_latest does not exist!")
        print("   Please run: mysql -u root -p team2_firmhub < sql/views.sql")
        conn.close()
        return
    
    print("✓ View exists\n")
    
    # Query view
    print("Querying view...")
    query = "SELECT * FROM vw_firm_panel_latest ORDER BY ticker, fiscal_year"
    
    df = pd.read_sql(query, conn)
    
    print(f"✓ Retrieved {len(df)} rows × {len(df.columns)} columns\n")
    
    # Close connection
    conn.close()
    
    # Verify data
    print("Data validation:")
    print("-" * 70)
    
    # Check row count
    if len(df) != 100:
        print(f"⚠ Warning: Expected 100 rows, got {len(df)}")
    else:
        print(f"✓ Row count: {len(df)} (expected 100)")
    
    # Check column count
    if len(df.columns) != 42:
        print(f"⚠ Warning: Expected 42 columns, got {len(df.columns)}")
    else:
        print(f"✓ Column count: {len(df.columns)} (expected 42)")
    
    # Check unique firms
    unique_tickers = df['ticker'].nunique()
    print(f"✓ Unique tickers: {unique_tickers} (expected 20)")
    
    # Check years
    unique_years = sorted(df['fiscal_year'].unique())
    print(f"✓ Years: {unique_years}")
    
    print("-" * 70)
    print()
    
    # Missing data summary
    print("Missing data summary:")
    print("-" * 70)
    
    total_cells = len(df) * len(df.columns)
    non_null_cells = df.notna().sum().sum()
    null_cells = total_cells - non_null_cells
    
    print(f"Total cells: {total_cells:,}")
    print(f"Non-null cells: {non_null_cells:,} ({non_null_cells/total_cells*100:.1f}%)")
    print(f"Null cells: {null_cells:,} ({null_cells/total_cells*100:.1f}%)")
    print()
    
    # Top fields with missing data
    missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    top_missing = missing_pct[missing_pct > 0].head(10)
    
    if len(top_missing) > 0:
        print("Top 10 fields with missing data:")
        for field, pct in top_missing.items():
            missing_count = int(df[field].isnull().sum())
            print(f"  {field}: {missing_count} missing ({pct:.1f}%)")
    else:
        print("✓ No missing data")
    
    print("-" * 70)
    print()
    
    # Export to CSV
    print("Exporting to CSV...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"✓ Exported to: {OUTPUT_FILE}")
    
    print()
    print("=" * 70)
    print("✓ EXPORT COMPLETED!")
    print("=" * 70)

# ─── ENTRY POINT ─────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        export_panel()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()