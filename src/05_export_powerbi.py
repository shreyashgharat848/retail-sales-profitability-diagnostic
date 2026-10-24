"""Step 5: export clean, model-ready CSV extracts for the Power BI dashboard."""
import sqlite3
import pandas as pd
from config import DB_PATH, POWERBI, TABLES

with sqlite3.connect(DB_PATH) as con:
    fact = pd.read_sql_query("SELECT * FROM orders", con, parse_dates=["order_date", "ship_date"])

seg = pd.read_csv(TABLES / "rfm_customers.csv")[["customer_id", "rfm_segment"]]
fact = fact.merge(seg, on="customer_id", how="left")
assert fact.rfm_segment.notna().all()
fact["discount_over_20"] = (fact.discount > 0.20).map({True: "Over 20%", False: "Up to 20%"})
fact.to_csv(POWERBI / "fact_orders.csv", index=False, date_format="%Y-%m-%d")

# ---- date dimension (continuous calendar, required for time intelligence DAX) ----
dates = pd.date_range(f"{fact.order_date.dt.year.min()}-01-01", f"{fact.order_date.dt.year.max()}-12-31")
dim = pd.DataFrame({"date": dates})
dim["year"] = dim.date.dt.year
dim["quarter"] = "Q" + dim.date.dt.quarter.astype(str)
dim["year_quarter"] = dim.year.astype(str) + "-" + dim.quarter
dim["month_num"] = dim.date.dt.month
dim["month_name"] = dim.date.dt.strftime("%b")
dim["year_month"] = dim.date.dt.strftime("%Y-%m")
dim.to_csv(POWERBI / "dim_date.csv", index=False, date_format="%Y-%m-%d")

# ---- small summary tables for quick visuals ------------------------------------
for name in ("02_discount_bands", "04_subcategory_profitability", "rfm_segment_summary"):
    pd.read_csv(TABLES / f"{name}.csv").to_csv(POWERBI / f"{name}.csv", index=False)

print("Power BI extracts written to powerbi/data/:")
for f in sorted(POWERBI.glob("*.csv")):
    print(f"  {f.name:40s} {sum(1 for _ in open(f, encoding='utf-8')) - 1:>7,} rows")
