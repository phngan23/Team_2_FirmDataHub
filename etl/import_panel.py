import pandas as pd
import mysql.connector
from mysql.connector import Error

# ==============================
# 1. LOAD EXCEL
# ==============================

df = pd.read_excel("../data/panel_2020_2024.xlsx")

# Rename identifier columns
df = df.rename(columns={
    "Ticker": "ticker",
    "YearEnd": "fiscal_year"
})

# Rename variables theo schema DB
rename_dict = {
    "Managerial/Inside ownership": "managerial_inside_own",
    "State ownership": "state_own",
    "Institutional ownership": "institutional_own",
    "Foreign ownership": "foreign_own",
    "Total share outstanding": "shares_outstanding",
    "Share_price": "share_price",
    "Market value of equity": "market_value_equity",
    "Divident payment": "dividend_cash_paid",
    "EPS": "eps_basic",
    "Net sales revenue": "net_sales",
    "Net operating income": "net_operating_income",
    "Net Income": "net_income",
    "Selling expenses": "selling_expenses",
    "General and administrative expenditure": "general_admin_expenses",
    "Manufacturing overhead (Indirect cost)": "manufacturing_overhead",
    "Consumption of raw material": "raw_material_consumption",
    "Merchandise purchase of the year": "merchandise_purchase_year",
    "Work-in-progess goods purchase": "wip_goods_purchase",
    "Outside manufacturing expenses": "outside_manufacturing_expenses",
    "Production cost": "production_cost",
    "Total assets": "total_assets",
    "Total shareholders' equity": "total_equity",
    "Total liabilities": "total_liabilities",
    "Value of intangible assets": "intangible_assets_net",
    "Long-term debt": "long_term_debt",
    "Current assets": "current_assets",
    "Current liabiltiies": "current_liabilities",
    "Total inventory": "inventory",
    "Net plant, property and equipment": "net_ppe",
    "Net cash from operating activities": "net_cfo",
    "Cash flows from investing activities": "net_cfi",
    "Capital expenditure": "capex",
    "Cash and cash equivalent": "cash_and_equivalents",
    "R&D expenditure": "rnd_expesnses",
    "Product innovation": "product_innovation",
    "Process innovation": "process_innovation",
    "Number of employees": "employess_count",
    "Growth ratio": "growth_ratio",
    "Firm age": "firm_age"
}

df = df.rename(columns=rename_dict)

# Replace NaN/NULL → None 
# Chuyển ô trống/NULL về None
df = df.where(pd.notnull(df), None)
df.replace("NULL", None, inplace=True)

# Check duplicate firm-year
duplicates = df.duplicated(subset=["ticker", "fiscal_year"]).sum()
if duplicates > 0:
    raise ValueError("Duplicate firm-year detected in Excel.")

print("Data loaded and cleaned successfully.")


# ==============================
# 2. CONNECT DATABASE
# ==============================

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="etl_user",
        password="123456", # nhập password của mình
        database="vn_firm"
    )

    cursor = conn.cursor()

    print("Connected to database.")

    # ======================================
    # 3. LOOP THROUGH DATA
    # ======================================

    for _, row in df.iterrows():

        ticker = row["ticker"]
        year = row["fiscal_year"]

        # Get firm_id
        cursor.execute(
            "SELECT firm_id FROM dim_firm WHERE ticker=%s",
            (ticker,)
        )
        result = cursor.fetchone()

        if result is None:
            raise ValueError(f"{ticker} not found in dim_firm")

        firm_id = result[0]

        # -------- GET SNAPSHOTS BY SOURCE --------

        def get_snapshot(year, source_id):
            cursor.execute("""
                SELECT snapshot_id
                FROM fact_data_snapshot
                WHERE fiscal_year=%s AND source_id=%s
            """, (year, source_id))
            snap = cursor.fetchone()
            if snap is None:
                raise ValueError(f"No snapshot for year {year}, source {source_id}")
            return snap[0]

        snapshot_ownership = get_snapshot(year, 1)
        snapshot_financial = get_snapshot(year, 2)
        snapshot_market = get_snapshot(year, 3)
        snapshot_text = get_snapshot(year, 4)

        # -------- OWNERSHIP --------
        cursor.execute("""
            INSERT INTO fact_ownership_year
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            firm_id, year, snapshot_ownership,
            row["managerial_inside_own"],
            row["state_own"],
            row["institutional_own"],
            row["foreign_own"]
        ))

        # -------- MARKET --------
        cursor.execute("""
            INSERT INTO fact_market_year
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            firm_id, year, snapshot_market,
            row["shares_outstanding"],
            row["share_price"],
            row["market_value_equity"],
            row["dividend_cash_paid"],
            row["eps_basic"]
        ))

        # -------- FINANCIAL --------
        cursor.execute("""
            INSERT INTO fact_financial_year
            VALUES (%s,%s,%s,
                    %s,%s,%s,
                    %s,%s,
                    %s,%s,
                    %s,%s,
                    %s,%s,
                    %s,%s,%s,
                    %s,%s,
                    %s,%s,
                    %s,%s,%s,%s)
        """, (
            firm_id, year, snapshot_financial,
            row["net_sales"], row["net_operating_income"], row["net_income"],
            row["selling_expenses"], row["general_admin_expenses"],
            row["manufacturing_overhead"], row["raw_material_consumption"],
            row["merchandise_purchase_year"], row["wip_goods_purchase"],
            row["outside_manufacturing_expenses"], row["production_cost"],
            row["total_assets"], row["total_equity"], row["total_liabilities"],
            row["intangible_assets_net"], row["long_term_debt"],
            row["current_assets"], row["current_liabilities"],
            row["inventory"], row["net_ppe"],
            row["rnd_expesnses"], row["growth_ratio"]
        ))

        # -------- CASHFLOW --------
        cursor.execute("""
            INSERT INTO fact_cashflow_year
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            firm_id, year, snapshot_financial,
            row["net_cfo"], row["net_cfi"],
            row["capex"], row["cash_and_equivalents"]
        ))

        # -------- INNOVATION --------
        cursor.execute("""
            INSERT INTO fact_innovation_year
            VALUES (%s,%s,%s,%s,%s)
        """, (
            firm_id, year, snapshot_text,
            row["product_innovation"],
            row["process_innovation"]
        ))

        # -------- META --------
        cursor.execute("""
            INSERT INTO fact_firm_year_meta
            VALUES (%s,%s,%s,%s,%s)
        """, (
            firm_id, year, snapshot_text,
            row["employess_count"],
            row["firm_age"]
        ))

    conn.commit()
    print("Import completed successfully.")

except Error as e:
    print("Database Error:", e)
    conn.rollback()

except Exception as e:
    print("Error:", e)

finally:
    cursor.close()
    conn.close()