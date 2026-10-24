"""Step 2: run every diagnostic SQL query, save result tables and draw charts."""
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import DB_PATH, SQL_DIR, TABLES, CHARTS, GREEN, RED, BLUE, GREY, ORANGE

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
con = sqlite3.connect(DB_PATH)


def q(name):
    """Run sql/<name>.sql and save the result as outputs/tables/<name>.csv"""
    df = pd.read_sql_query((SQL_DIR / f"{name}.sql").read_text(), con)
    df.to_csv(TABLES / f"{name}.csv", index=False)
    return df


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=150)
    plt.close(fig)


kpi = q("01_overview_kpis")
bands = q("02_discount_bands")
thresh = q("03_discount_threshold")
sub = q("04_subcategory_profitability")
loss_split = q("05_loss_makers_discount_split")
reg = q("06_region_segment")
yearly = q("07_yearly_trend")
toploss = q("08_top_loss_products")

print("\n=== OVERVIEW ===");               print(kpi.T.to_string(header=False))
print("\n=== DISCOUNT BANDS ===");         print(bands.to_string(index=False))
print("\n=== DISCOUNT THRESHOLD ===");     print(thresh.to_string(index=False))
print("\n=== SUB-CATEGORIES ===");         print(sub[["sub_category", "profit", "profit_margin_pct", "status"]].to_string(index=False))
print("\n=== LOSS-MAKERS: DISCOUNT SPLIT ==="); print(loss_split.to_string(index=False))
print("\n=== YEARLY ===");                 print(yearly.to_string(index=False))

# ---- Chart 1: margin by discount band (the headline finding) -------------
fig, ax = plt.subplots(figsize=(8, 4.5))
colors = [GREEN if m > 0 else RED for m in bands.profit_margin_pct]
b = ax.bar(bands.discount_band, bands.profit_margin_pct, color=colors)
ax.axhline(0, color="black", lw=.8)
for rect, m, n in zip(b, bands.profit_margin_pct, bands.order_lines):
    ax.text(rect.get_x() + rect.get_width() / 2, m + (1.5 if m > 0 else -1.5),
            f"{m:+.1f}%\n(n={n:,})", ha="center", va="bottom" if m > 0 else "top", fontsize=9)
ax.set_ylabel("Profit margin (% of sales)"); ax.set_xlabel("Discount band")
ax.set_title("Profit margin collapses as discounts rise")
ax.set_ylim(min(bands.profit_margin_pct) - 12, max(bands.profit_margin_pct) + 10)
save(fig, "01_margin_by_discount_band.png")

# ---- Chart 2: sub-category profit, loss-makers highlighted ---------------
s = sub.sort_values("profit")
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(s.sub_category, s.profit / 1000, color=[RED if p < 0 else BLUE for p in s.profit])
ax.axvline(0, color="black", lw=.8)
ax.set_xlabel("Total profit ($ thousand)"); ax.set_title("Profit by sub-category (loss-makers in red)")
save(fig, "02_subcategory_profit.png")

# ---- Chart 3: discount level vs margin by sub-category -------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(sub.avg_discount_pct, sub.profit_margin_pct,
           s=sub.sales / 1500, c=[RED if p < 0 else BLUE for p in sub.profit], alpha=.7)
for _, r in sub.iterrows():
    ax.annotate(r.sub_category, (r.avg_discount_pct, r.profit_margin_pct), fontsize=8,
                xytext=(4, 4), textcoords="offset points")
ax.axhline(0, color="black", lw=.8)
ax.set_xlabel("Average discount (%)"); ax.set_ylabel("Profit margin (%)")
ax.set_title("Higher average discount, lower margin (bubble = sales)")
save(fig, "03_discount_vs_margin_subcategory.png")

# ---- Chart 4: yearly trend -----------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
x = yearly.order_year.astype(str)
ax.bar(x, yearly.sales / 1000, color=BLUE, alpha=.85, label="Sales")
ax.bar(x, yearly.profit / 1000, color=GREEN, label="Profit")
ax2 = ax.twinx(); ax2.plot(x, yearly.profit_margin_pct, color=ORANGE, marker="o", label="Margin %")
ax2.set_ylabel("Margin %"); ax.set_ylabel("$ thousand"); ax.set_title("Sales, profit and margin by year")
ax2.spines["top"].set_visible(False)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
save(fig, "04_yearly_trend.png")

# ---- Chart 5: loss-making sub-categories split by discount group -----------
p = loss_split.pivot(index="sub_category", columns="discount_group", values="profit")
fig, ax = plt.subplots(figsize=(7, 4.5))
p.plot(kind="bar", ax=ax, color=[GREEN, RED], rot=0)
ax.axhline(0, color="black", lw=.8); ax.set_ylabel("Profit ($)"); ax.set_xlabel("")
ax.set_title("Loss-making sub-categories: profit by discount group\n(Tables and Bookcases lose money only on >20% discount lines)")
ax.legend(title="", frameon=False)
save(fig, "05_loss_makers_discount_split.png")
con.close()
