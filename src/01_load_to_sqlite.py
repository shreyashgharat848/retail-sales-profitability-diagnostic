"""Step 1: clean the raw Superstore CSV and load it into a SQLite database.

Output: data/superstore.db  (table `orders`, one row per order line)
"""
import sqlite3
import pandas as pd
from config import RAW_CSV, DB_PATH

# The public Superstore file is Latin-1 encoded (some product names contain accents)
df = pd.read_csv(RAW_CSV, encoding="latin-1")

# ---- tidy column names -------------------------------------------------
df.columns = (df.columns.str.strip().str.lower()
              .str.replace("-", "_").str.replace(" ", "_"))

# ---- parse dates to ISO text (SQLite has no native date type) -----------
for c in ("order_date", "ship_date"):
    df[c] = pd.to_datetime(df[c], format="%m/%d/%Y")

# ---- derived columns used in SQL / BI ----------------------------------
df["order_year"] = df.order_date.dt.year
df["order_month"] = df.order_date.dt.to_period("M").astype(str)
df["profit_margin_pct"] = df.profit / df.sales * 100
df["is_loss_line"] = (df.profit < 0).astype(int)
df["discount_band"] = pd.cut(
    df.discount, bins=[-0.001, 0.0, 0.20, 0.40, 1.0],
    labels=["0% (none)", "0-20%", "20-40%", ">40%"]).astype(str)

# ---- data-quality checks (fail loudly if the data is not what we expect) --
assert len(df) == 9994, f"expected 9,994 rows, got {len(df)}"
assert df.row_id.is_unique, "row_id must be unique"
assert df.isna().sum().sum() == 0, "unexpected missing values"
assert df.customer_id.nunique() == 793, "expected 793 unique customers"
print(f"Rows: {len(df):,} | Customers: {df.customer_id.nunique()} | "
      f"Orders: {df.order_id.nunique():,} | "
      f"Dates: {df.order_date.min().date()} to {df.order_date.max().date()}")

# ---- write to SQLite ---------------------------------------------------
for c in ("order_date", "ship_date"):
    df[c] = df[c].dt.strftime("%Y-%m-%d")

DB_PATH.parent.mkdir(exist_ok=True)
if DB_PATH.exists():
    DB_PATH.unlink()
with sqlite3.connect(DB_PATH) as con:
    df.to_sql("orders", con, index=False)
    con.executescript("""
        CREATE INDEX idx_orders_customer ON orders(customer_id);
        CREATE INDEX idx_orders_date     ON orders(order_date);
        CREATE INDEX idx_orders_subcat   ON orders(sub_category);
    """)
    n = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
print(f"Loaded {n:,} rows into {DB_PATH.name}")
