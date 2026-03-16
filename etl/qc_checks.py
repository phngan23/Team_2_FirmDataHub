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
import mysql.connector
from getpass import getpass
import pandas as pd
from pathlib import Path
from decimal import Decimal

# ─── CONFIGURATION ───────────────────────────────────────────────
password = getpass("Enter MySQL password: ")

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': password,
    'database': 'team2_firmhub'
}

# QC Thresholds (configurable)
MIN_GROWTH = -0.95
MAX_GROWTH = 5.0
MARKET_VALUE_TOLERANCE = 0.05  # 5%

OUTPUT_DIR = Path("outputs")
OUTPUT_FILE = OUTPUT_DIR / "qc_report.csv"

# ─── DATABASE CONNECTION ─────────────────────────────────────────
def get_db_connection():
    """Establish MySQL connection with password prompt."""
    password = getpass("Enter MySQL password: ")
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=password
    )
    return conn

# ─── QC RULE FUNCTIONS ───────────────────────────────────────────

def rule1_ownership_ratios(conn):
    """
    Rule 1: Ownership Ratios trong [0, 1]
    Validate: managerial_inside_own, state_own, institutional_own, foreign_own
    """
    errors = []
    fields = ['managerial_inside_own', 'state_own', 'institutional_own', 'foreign_own']
    
    query = """
        SELECT 
            f.ticker,
            oy.fiscal_year,
            oy.managerial_inside_own,
            oy.state_own,
            oy.institutional_own,
            oy.foreign_own
        FROM fact_ownership_year oy
        JOIN dim_firm f ON oy.firm_id = f.firm_id
    """
    
    df = pd.read_sql(query, conn)
    
    for field in fields:
        mask = df[field].notna() & ((df[field] < 0) | (df[field] > 1))
        invalid = df[mask]
        
        for _, row in invalid.iterrows():
            errors.append({
                'ticker': row['ticker'],
                'fiscal_year': row['fiscal_year'],
                'field_name': field,
                'error_type': 'OUT_OF_RANGE',
                'message': f"Ownership ratio {row[field]:.4f} out of range [0, 1]"
            })
    
    return errors

def rule2_shares_outstanding(conn):
    """
    Rule 2: Shares Outstanding > 0
    """
    errors = []
    
    query = """
        SELECT 
            f.ticker,
            m.fiscal_year,
            m.shares_outstanding
        FROM fact_market_year m
        JOIN dim_firm f ON m.firm_id = f.firm_id
        WHERE m.shares_outstanding IS NOT NULL
          AND m.shares_outstanding <= 0
    """
    
    df = pd.read_sql(query, conn)
    
    for _, row in df.iterrows():
        errors.append({
            'ticker': row['ticker'],
            'fiscal_year': row['fiscal_year'],
            'field_name': 'shares_outstanding',
            'error_type': 'INVALID_VALUE',
            'message': f"Shares outstanding {row['shares_outstanding']} must be positive"
        })
    
    return errors

def rule3_total_assets(conn):
    """
    Rule 3: Total Assets ≥ 0
    """
    errors = []
    
    query = """
        SELECT 
            f.ticker,
            fin.fiscal_year,
            fin.total_assets
        FROM fact_financial_year fin
        JOIN dim_firm f ON fin.firm_id = f.firm_id
        WHERE fin.total_assets IS NOT NULL
          AND fin.total_assets < 0
    """
    
    df = pd.read_sql(query, conn)
    
    for _, row in df.iterrows():
        errors.append({
            'ticker': row['ticker'],
            'fiscal_year': row['fiscal_year'],
            'field_name': 'total_assets',
            'error_type': 'INVALID_VALUE',
            'message': f"Total assets {row['total_assets']:.2f} must be non-negative"
        })
    
    return errors

def rule4_current_liabilities(conn):
    """
    Rule 4: Current Liabilities ≥ 0
    """
    errors = []
    
    query = """
        SELECT 
            f.ticker,
            fin.fiscal_year,
            fin.current_liabilities
        FROM fact_financial_year fin
        JOIN dim_firm f ON fin.firm_id = f.firm_id
        WHERE fin.current_liabilities IS NOT NULL
          AND fin.current_liabilities < 0
    """
    
    df = pd.read_sql(query, conn)
    
    for _, row in df.iterrows():
        errors.append({
            'ticker': row['ticker'],
            'fiscal_year': row['fiscal_year'],
            'field_name': 'current_liabilities',
            'error_type': 'INVALID_VALUE',
            'message': f"Current liabilities {row['current_liabilities']:.2f} must be non-negative"
        })
    
    return errors

def rule5_growth_ratio(conn):
    """
    Rule 5: Growth Ratio trong [-0.95, 5.0]
    """
    errors = []
    
    query = """
        SELECT 
            f.ticker,
            fin.fiscal_year,
            fin.growth_ratio
        FROM fact_financial_year fin
        JOIN dim_firm f ON fin.firm_id = f.firm_id
        WHERE fin.growth_ratio IS NOT NULL
          AND (fin.growth_ratio < %s OR fin.growth_ratio > %s)
    """
    
    df = pd.read_sql(query, conn, params=(MIN_GROWTH, MAX_GROWTH))
    
    for _, row in df.iterrows():
        errors.append({
            'ticker': row['ticker'],
            'fiscal_year': row['fiscal_year'],
            'field_name': 'growth_ratio',
            'error_type': 'OUT_OF_RANGE',
            'message': f"Growth ratio {row['growth_ratio']:.4f} out of range [{MIN_GROWTH}, {MAX_GROWTH}]"
        })
    
    return errors

def rule6_market_value_consistency(conn):
    """
    Rule 6: Market Value ≈ Shares × Price
    Formula: shares × price / 1 billion = market_value_equity
    Tolerance: 5%
    """
    errors = []
    
    query = """
        SELECT 
            f.ticker,
            m.fiscal_year,
            m.shares_outstanding,
            m.share_price,
            m.market_value_equity
        FROM fact_market_year m
        JOIN dim_firm f ON m.firm_id = f.firm_id
        WHERE m.shares_outstanding IS NOT NULL
          AND m.share_price IS NOT NULL
          AND m.market_value_equity IS NOT NULL
          AND m.shares_outstanding > 0
          AND m.share_price > 0
    """
    
    df = pd.read_sql(query, conn)
    
    for _, row in df.iterrows():
        # Calculate expected market value
        # shares_outstanding (số cổ phiếu) × share_price (VND/CP) = market_value_equity (VND)
        expected_mve = (row['shares_outstanding'] * float(row['share_price'])) 
        actual_mve = float(row['market_value_equity'])
        
        # Check tolerance
        if expected_mve > 0:
            diff_pct = abs(actual_mve - expected_mve) / expected_mve
            
            if diff_pct > MARKET_VALUE_TOLERANCE:
                errors.append({
                    'ticker': row['ticker'],
                    'fiscal_year': row['fiscal_year'],
                    'field_name': 'market_value_equity',
                    'error_type': 'INCONSISTENT',
                    'message': (
                        f"Market value {actual_mve:.2f} inconsistent with "
                        f"shares {row['shares_outstanding']:,.0f} × price {float(row['share_price']):.2f} "
                        f"(expected {expected_mve:.2f}, diff {diff_pct*100:.1f}%)"
                    )
                })
    
    return errors

# ─── MAIN EXECUTION ──────────────────────────────────────────────

def run_qc_checks():
    """Run all QC checks and generate report."""
    
    print("=" * 60)
    print("QC CHECKS - team2_firmhub")
    print("=" * 60)
    print()
    
    # Connect to database
    print("Connecting to database...")
    conn = get_db_connection()
    print("✓ Connected\n")
    
    # Run all checks
    all_errors = []
    
    print("Running QC checks...")
    print("-" * 60)
    
    rules = [
        ("Rule 1: Ownership Ratios [0,1]", rule1_ownership_ratios),
        ("Rule 2: Shares Outstanding > 0", rule2_shares_outstanding),
        ("Rule 3: Total Assets ≥ 0", rule3_total_assets),
        ("Rule 4: Current Liabilities ≥ 0", rule4_current_liabilities),
        ("Rule 5: Growth Ratio in range", rule5_growth_ratio),
        ("Rule 6: Market Value consistency", rule6_market_value_consistency),
    ]
    
    for rule_name, rule_func in rules:
        print(f"• {rule_name}...", end=" ")
        errors = rule_func(conn)
        all_errors.extend(errors)
        print(f"{len(errors)} errors")
    
    print("-" * 60)
    print()
    
    # Close connection
    conn.close()
    
    # Convert to DataFrame
    if all_errors:
        df_errors = pd.DataFrame(all_errors)
        
        # Sort by ticker, fiscal_year, field_name
        df_errors = df_errors.sort_values(['ticker', 'fiscal_year', 'field_name'])
        
        # Count total records (estimate)
        total_records = count_total_records(DB_CONFIG, getpass("Enter MySQL password again to count records: "))
        
        # Print summary
        print_summary(df_errors, total_records)
        
        # Save to CSV
        OUTPUT_DIR.mkdir(exist_ok=True)
        df_errors.to_csv(OUTPUT_FILE, index=False)
        print(f"\n✓ QC report saved to: {OUTPUT_FILE}")
        
    else:
        print("=" * 60)
        print("QC CHECKS SUMMARY")
        print("=" * 60)
        print("✓ NO ERRORS FOUND - All checks passed!")
        print("=" * 60)

def count_total_records(db_config, password):
    """Count approximate total records checked."""
    conn = mysql.connector.connect(
        host=db_config['host'],
        database=db_config['database'],
        user=db_config['user'],
        password=password
    )
    cursor = conn.cursor()
    
    # Count records in fact tables
    tables = ['fact_ownership_year', 'fact_financial_year', 'fact_market_year']
    total = 0
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total += count
    
    conn.close()
    return total

def print_summary(df_errors, total_records):
    """Print QC summary to console."""
    print("=" * 60)
    print("QC CHECKS SUMMARY")
    print("=" * 60)
    print(f"Total records checked: {total_records}")
    print(f"Total errors found: {len(df_errors)}")
    print()
    
    # Errors by type
    print("Errors by type:")
    error_type_counts = df_errors['error_type'].value_counts()
    for error_type, count in error_type_counts.items():
        print(f"  {error_type}: {count}")
    print()
    
    # Errors by field
    print("Errors by field:")
    field_counts = df_errors['field_name'].value_counts()
    for field, count in field_counts.items():
        print(f"  {field}: {count}")
    print()
    
    # Errors by ticker (top 10)
    print("Errors by ticker (top 10):")
    ticker_counts = df_errors['ticker'].value_counts().head(10)
    for ticker, count in ticker_counts.items():
        print(f"  {ticker}: {count}")
    print("=" * 60)

# ─── ENTRY POINT ─────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        run_qc_checks()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()