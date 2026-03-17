import pandas as pd
import mysql.connector
from datetime import datetime
from getpass import getpass

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
file_path = "../data/firms.xlsx"

df = pd.read_excel(file_path)

df.columns = df.columns.str.strip().str.lower()

print(f"Loaded {len(df)} firms")

# ===============================
# HELPER FUNCTIONS
# ===============================

def get_exchange_id(exchange_code):
    sql = """
        SELECT exchange_id
        FROM dim_exchange
        WHERE exchange_code = %s
    """
    cursor.execute(sql, (exchange_code,))
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"Exchange not found: {exchange_code}")

    return result["exchange_id"]


def get_or_create_industry(industry_name):

    # check tồn tại
    sql = """
        SELECT industry_l2_id
        FROM dim_industry_l2
        WHERE industry_l2_name = %s
    """

    cursor.execute(sql, (industry_name,))
    result = cursor.fetchone()

    if result:
        return result["industry_l2_id"]

    # nếu chưa có → insert
    insert_sql = """
        INSERT INTO dim_industry_l2 (industry_l2_name)
        VALUES (%s)
    """

    cursor.execute(insert_sql, (industry_name,))
    conn.commit()

    return cursor.lastrowid


def firm_exists(ticker):
    sql = """
        SELECT firm_id
        FROM dim_firm
        WHERE ticker = %s
    """
    cursor.execute(sql, (ticker,))
    return cursor.fetchone()


# ===============================
# IMPORT LOOP
# ===============================

insert_count = 0
update_count = 0
error_count = 0

try:
    for idx, row in df.iterrows():
        try:
            ticker = row["ticker"]

            exchange_id = get_exchange_id(row["exchange_code"])
            industry_id = get_or_create_industry(row["industry_l2_name"])

            existing = firm_exists(ticker)

            if existing:
                # -------- UPDATE --------
                update_sql = """
                    UPDATE dim_firm
                    SET
                        company_name = %s,
                        exchange_id = %s,
                        industry_l2_id = %s,
                        founded_year = %s,
                        listed_year = %s,
                        updated_at = %s
                    WHERE ticker = %s
                """

                cursor.execute(update_sql, (
                    row["company_name"],
                    exchange_id,
                    industry_id,
                    row["founded_year"],
                    row["listed_year"],
                    datetime.now(),
                    ticker
                ))

                update_count += 1

            else:
                # -------- INSERT --------
                insert_sql = """
                    INSERT INTO dim_firm (
                        firm_id,
                        ticker,
                        company_name,
                        exchange_id,
                        industry_l2_id,
                        founded_year,
                        listed_year,
                        status,
                        created_at,
                        updated_at
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """

                cursor.execute(insert_sql, (
                    row["firm_id"],
                    ticker,
                    row["company_name"],
                    exchange_id,
                    industry_id,
                    row["founded_year"],
                    row["listed_year"],
                    "active",
                    datetime.now(),
                    datetime.now()
                ))

                insert_count += 1

        except Exception as e:
            error_count += 1
            print(f"❌ Error at row {idx+1} ({ticker}): {e}")
            continue

    # ===============================
    # COMMIT
    # ===============================
    conn.commit()

    print("=================================")
    print(f"Inserted: {insert_count}")
    print(f"Updated : {update_count}")
    print(f"Errors  : {error_count}")
    print("Import completed ✅")

except Exception as e:
    conn.rollback()
    print(f"❌ Fatal error: {e}")
    print("All changes rolled back.")

finally:
    cursor.close()
    conn.close()