import pandas as pd
import mysql.connector
from datetime import datetime
import sys
from getpass import getpass
import numpy as np

# ===============================
# DB CONNECTION
# ===============================
password = getpass("Enter MySQL password: ")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="team2_firmhub"
)

cursor = conn.cursor(dictionary=True)

# ===============================
# LOAD EXCEL
# ===============================
file_path = "../data/panel_2020_2024.xlsx"

df = pd.read_excel(file_path)

df.columns = df.columns.str.strip().str.lower()

# convert NaN -> None
df = df.replace({np.nan: None})
df.replace("NULL", None, inplace=True)

print(f"Loaded {len(df)} rows")


# ===============================
# HELPER FUNCTIONS
# ===============================

def get_firm_id(ticker):
    sql = """
        SELECT firm_id
        FROM dim_firm
        WHERE ticker = %s
    """
    cursor.execute(sql, (ticker,))
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"Ticker not found: {ticker}")

    return result["firm_id"]


def get_snapshot_id(fiscal_year, source_id):
    sql = """
        SELECT snapshot_id
        FROM fact_data_snapshot
        WHERE fiscal_year = %s
        AND source_id = %s
    """
    cursor.execute(sql, (fiscal_year, source_id))
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"Snapshot not found: year={fiscal_year}, source={source_id}")

    return result["snapshot_id"]


# ===============================
# IMPORT LOOP
# ===============================

row_count = 0
error_count = 0

try:
    for idx, row in df.iterrows():
        try:
            ticker = row["ticker"]
            fiscal_year = row["fiscal_year"]

            firm_id = get_firm_id(ticker)

            # snapshot ids theo source
            snapshot_ownership = get_snapshot_id(fiscal_year, 1)
            snapshot_financial = get_snapshot_id(fiscal_year, 2)
            snapshot_market = get_snapshot_id(fiscal_year, 3)
            snapshot_text = get_snapshot_id(fiscal_year, 4)

            # ===============================
            # OWNERSHIP
            # ===============================
            sql = """
            INSERT INTO fact_ownership_year
            (firm_id,fiscal_year,snapshot_id,
            managerial_inside_own,state_own,
            institutional_own,foreign_own,
            note,created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (
                firm_id,
                fiscal_year,
                snapshot_ownership,
                row["managerial_inside_own"],
                row["state_own"],
                row["institutional_own"],
                row["foreign_own"],
                "seed",
                datetime.now()
            ))

            # ===============================
            # FINANCIAL
            # ===============================
            sql = """
            INSERT INTO fact_financial_year
            (firm_id,fiscal_year,snapshot_id,
            unit_scale,currency_code,
            net_sales,total_assets,
            selling_expenses,general_admin_expenses,
            intangible_assets_net,
            manufacturing_overhead,
            net_operating_income,
            raw_material_consumption,
            merchandise_purchase_year,
            wip_goods_purchase,
            outside_manufacturing_expenses,
            production_cost,
            rnd_expenses,
            net_income,
            total_equity,total_liabilities,
            cash_and_equivalents,
            long_term_debt,
            current_assets,current_liabilities,
            growth_ratio,
            inventory,
            net_ppe,
            created_at)
            VALUES (%s,%s,%s,
            %s,%s,
            %s,%s,
            %s,%s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,%s,
            %s,
            %s,
            %s,%s,
            %s,
            %s,
            %s,
            %s)
            """

            cursor.execute(sql, (
                firm_id,
                fiscal_year,
                snapshot_financial,
                1000000000,
                "VND",
                row["net_sales"],
                row["total_assets"],
                row["selling_expenses"],
                row["general_admin_expenses"],
                row["intangible_assets_net"],
                row["manufacturing_overhead"],
                row["net_operating_income"],
                row["raw_material_consumption"],
                row["merchandise_purchase_year"],
                row["wip_goods_purchase"],
                row["outside_manufacturing_expenses"],
                row["production_cost"],
                row["rnd_expenses"],
                row["net_income"],
                row["total_equity"],
                row["total_liabilities"],
                row["cash_and_equivalents"],
                row["long_term_debt"],
                row["current_assets"],
                row["current_liabilities"],
                row["growth_ratio"],
                row["inventory"],
                row["net_ppe"],
                datetime.now()
            ))

            # ===============================
            # CASHFLOW
            # ===============================
            sql = """
            INSERT INTO fact_cashflow_year
            (firm_id,fiscal_year,snapshot_id,
            unit_scale,currency_code,
            net_cfo,capex,net_cfi,
            created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (
                firm_id,
                fiscal_year,
                snapshot_financial,
                1000000000,
                "VND",
                row["net_cfo"],
                row["capex"],
                row["net_cfi"],
                datetime.now()
            ))

            # ===============================
            # MARKET
            # ===============================
            sql = """
            INSERT INTO fact_market_year
            (firm_id,fiscal_year,snapshot_id,
            shares_outstanding,
            price_reference,
            share_price,
            market_value_equity,
            dividend_cash_paid,
            eps_basic,
            currency_code,
            created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (
                firm_id,
                fiscal_year,
                snapshot_market,
                row["shares_outstanding"],
                "close_year_end",
                row["share_price"],
                row["market_value_equity"],
                row["dividend_cash_paid"],
                row["eps_basic"],
                "VND",
                datetime.now()
            ))

            # ===============================
            # INNOVATION
            # ===============================
            sql = """
            INSERT INTO fact_innovation_year
            (firm_id,fiscal_year,snapshot_id,
            product_innovation,
            process_innovation,
            evidence_source_id,
            evidence_note,
            created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (
                firm_id,
                fiscal_year,
                snapshot_text,
                row["product_innovation"],
                row["process_innovation"],
                4,
                row["evidence_note"],
                datetime.now()
            ))

            # ===============================
            # FIRM META
            # ===============================
            sql = """
            INSERT INTO fact_firm_year_meta
            (firm_id,fiscal_year,snapshot_id,
            employees_count,firm_age,
            created_at)
            VALUES (%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (
                firm_id,
                fiscal_year,
                snapshot_text,
                row["employees_count"],
                row["firm_age"],
                datetime.now()
            ))

            row_count += 1

        except Exception as e:
            error_count += 1
            print(f"❌ Error at row {idx+1} ({ticker} {fiscal_year}): {e}")
            continue

    # ===============================
    # COMMIT
    # ===============================

    conn.commit()

    print("=================================")
    print(f"Imported rows: {row_count}")
    print(f"Errors: {error_count}")
    print("Panel import completed ✅")

except Exception as e:
    conn.rollback()
    print(f"❌ Fatal error: {e}")
    print("All changes rolled back.")

finally:
    cursor.close()
    conn.close()