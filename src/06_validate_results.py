"""Step 6: assert that every headline number quoted in the README / resume is reproduced by the data."""
import sqlite3
import pandas as pd
from config import DB_PATH, TABLES

con = sqlite3.connect(DB_PATH)
one = lambda sql: con.execute(sql).fetchone()[0]
checks = []

def check(name, actual, expected, tol=0.01):
    ok = abs(actual - expected) <= tol
    checks.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {actual} (expected {expected})")

check("order lines", one("SELECT COUNT(*) FROM orders"), 9994, 0)
check("unique customers", one("SELECT COUNT(DISTINCT customer_id) FROM orders"), 793, 0)
check("margin, no discount (%)", round(one("SELECT 100.0*SUM(profit)/SUM(sales) FROM orders WHERE discount=0"), 1), 29.5, 0.05)
check("margin, 20-40% discount (%)", round(one("SELECT 100.0*SUM(profit)/SUM(sales) FROM orders WHERE discount>0.20 AND discount<=0.40"), 1), -15.3, 0.05)
check("margin, ALL >20% discount (%)", round(one("SELECT 100.0*SUM(profit)/SUM(sales) FROM orders WHERE discount>0.20"), 1), -37.3, 0.05)
loss = [r[0] for r in con.execute("SELECT sub_category FROM orders GROUP BY sub_category HAVING SUM(profit)<0 ORDER BY SUM(profit)")]
check("loss-making sub-categories", len(loss), 3, 0)
print("   loss-making:", loss)

seg = pd.read_csv(TABLES / "rfm_customers.csv")
check("RFM segments", seg.rfm_segment.nunique(), 4, 0)
check("RFM customers", len(seg), 793, 0)
fq = pd.read_csv(TABLES / "forecast_quarterly_2018.csv")
check("forecast quarters", len(fq), 4, 0)

assert all(checks), "One or more validation checks FAILED"
print("\nAll validation checks passed.")
