"""
run_pipeline.py

Purpose
-------
Master pipeline script to run entire ETL workflow in correct order.

Workflow
--------
1. Initialize data snapshots (20 snapshots)
2. Import firm master data (20 firms)
3. Import panel data (100 observations)
4. Run QC checks
5. Create analytical views
6. Export final panel dataset

Usage
-----
python run_pipeline.py
"""

from getpass import getpass
import mysql.connector
import sys
from pathlib import Path
import subprocess
import os

# ─── CONFIGURATION ───────────────────────────────────────────────

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'database': 'team2_firmhub'
}

# ─── HELPER FUNCTIONS ────────────────────────────────────────────

def run_python_script(script_name, password, description):
    """Run a Python script in the etl/ directory."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}\n")
    
    script_path = Path(__file__).parent / "etl" / script_name
    
    if not script_path.exists():
        print(f"❌ Error: Script not found: {script_path}")
        sys.exit(1)
    
    try:
        # Set environment variable for password
        env = os.environ.copy()
        env['MYSQL_PASSWORD'] = password
        
        # Run script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            env=env,
            capture_output=False,  # Show output in real-time
            text=True,
            check=True
        )
        
        print(f"\n✅ {description} completed\n")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {script_name}")
        print(f"Return code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

def create_views(password):
    """Create SQL views from view.sql file."""
    print(f"\n{'='*70}")
    print("STEP 5: Creating SQL Views")
    print(f"{'='*70}\n")
    
    try:
        config = DB_CONFIG.copy()
        config["password"] = password
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Path to view.sql
        sql_path = Path(__file__).parent / "sql" / "view.sql"
        
        if not sql_path.exists():
            print(f"❌ Error: SQL file not found: {sql_path}")
            sys.exit(1)
        
        print(f"Reading SQL from: {sql_path}")
        
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        print("Executing SQL statements...")
        
        # Split by semicolons and execute each statement
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for stmt in statements:
            if stmt:
                cursor.execute(stmt)
                # If there are results, fetch and print them
                try:
                    if cursor.with_rows:
                        for row in cursor.fetchall():
                            print(row)
                except:
                    pass
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Views created successfully\n")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating views: {e}")
        sys.exit(1)

def verify_outputs():
    """Verify all expected outputs exist."""
    print(f"\n{'='*70}")
    print("VERIFICATION: Checking Outputs")
    print(f"{'='*70}\n")
    
    outputs_dir = Path(__file__).parent / "outputs"
    
    expected_files = [
        "qc_report.csv",
        "panel_latest.csv"
    ]
    
    all_exist = True
    
    for filename in expected_files:
        filepath = outputs_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"✅ {filename} exists ({size:,} bytes)")
        else:
            print(f"❌ {filename} NOT FOUND")
            all_exist = False
    
    print()
    
    if not all_exist:
        print("⚠ Warning: Some output files are missing")
    else:
        print("✅ All output files present")
    
    return all_exist

def verify_database(password):
    """Verify database row counts."""
    print(f"\n{'='*70}")
    print("DATABASE VERIFICATION")
    print(f"{'='*70}\n")
    
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=password,
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        tables = [
            ('dim_firm', 20),
            ('fact_data_snapshot', 20),
            ('fact_ownership_year', 100),
            ('fact_financial_year', 100),
            ('fact_cashflow_year', 100),
            ('fact_market_year', 100),
            ('fact_innovation_year', 100),
            ('fact_firm_year_meta', 100),
        ]
        
        all_correct = True
        
        for table_name, expected_count in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            actual_count = cursor.fetchone()[0]
            
            if actual_count == expected_count:
                print(f"✅ {table_name}: {actual_count} rows (expected {expected_count})")
            else:
                print(f"❌ {table_name}: {actual_count} rows (expected {expected_count})")
                all_correct = False
        
        # Check view
        cursor.execute("SELECT COUNT(*) FROM vw_firm_panel_latest")
        view_count = cursor.fetchone()[0]
        
        if view_count == 100:
            print(f"✅ vw_firm_panel_latest: {view_count} rows (expected 100)")
        else:
            print(f"❌ vw_firm_panel_latest: {view_count} rows (expected 100)")
            all_correct = False
        
        cursor.close()
        conn.close()
        
        print()
        
        if all_correct:
            print("✅ All database counts correct")
        else:
            print("⚠ Warning: Some row counts are incorrect")
        
        return all_correct
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return False

# ─── MAIN PIPELINE ───────────────────────────────────────────────

def main():
    """Run complete ETL pipeline."""
    
    print("=" * 70)
    print("TEAM 2 FIRM DATA HUB - COMPLETE ETL PIPELINE")
    print("=" * 70)
    print()
    
    # Get password once
    password = getpass("Enter MySQL password: ")
    
    # Test connection first
    print("Testing database connection...")
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=password,
            database=DB_CONFIG['database']
        )
        conn.close()
        print("✅ Database connection successful\n")
    except mysql.connector.Error as e:
        print(f"❌ Cannot connect to database: {e}")
        print("\nPlease check:")
        print("  - MySQL is running")
        print("  - Database 'team2_firmhub' exists")
        print("  - Password is correct")
        sys.exit(1)
    
    # Run pipeline steps
    try:
        # Step 1: Initialize snapshots (using init_snapshots.py)
        run_python_script(
            "init_snapshots.py",
            password,
            "STEP 1: Initializing Data Snapshots (20 snapshots)"
        )
        
        # Step 2: Import firms
        run_python_script(
            "import_firms.py",
            password,
            "STEP 2: Importing Firm Master Data (20 firms)"
        )
        
        # Step 3: Import panel
        run_python_script(
            "import_panel.py",
            password,
            "STEP 3: Importing Panel Data (100 observations)"
        )
        
        # Step 4: QC checks
        run_python_script(
            "qc_checks.py",
            password,
            "STEP 4: Running QC Checks"
        )
        
        # Step 5: Create views (from SQL file)
        create_views(password)
        
        # Step 6: Export panel
        run_python_script(
            "export_panel.py",
            password,
            "STEP 6: Exporting Panel Dataset"
        )
        
        # Verify database
        verify_database(password)
        
        # Verify outputs
        verify_outputs()
        
        # Success
        print("=" * 70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ─── ENTRY POINT ─────────────────────────────────────────────────

if __name__ == "__main__":
    main()