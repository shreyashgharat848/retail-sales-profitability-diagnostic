"""Step 4: Holt-Winters exponential smoothing -> 4-quarter sales projection.

1. Aggregate sales to monthly totals (48 months: Jan-2014 .. Dec-2017).
2. Back-test: train on 2014-2016, predict 2017, compare with a seasonal-naive benchmark.
3. Refit on all data and project the next 12 months (= 4 quarters of 2018) with an 80% simulation interval.
"""
import sqlite3
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from config import DB_PATH, TABLES, CHARTS, POWERBI, FORECAST_MONTHS, RANDOM_STATE, BLUE, ORANGE, GREY

warnings.filterwarnings("ignore")
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

with sqlite3.connect(DB_PATH) as con:
    m = pd.read_sql_query("SELECT order_month, ROUND(SUM(sales),2) AS sales FROM orders "
                          "GROUP BY order_month ORDER BY order_month", con)
y = pd.Series(m.sales.values, index=pd.PeriodIndex(m.order_month, freq="M").to_timestamp(how="start"))
y.index.freq = "MS"
assert len(y) == 48

def mape(a, f): return float(np.mean(np.abs((a - f) / a)) * 100)

# ---- 1) back-test on 2017 ---------------------------------------------------
train, test = y[:"2016-12-01"], y["2017-01-01":]
configs = {
    "HW additive trend + multiplicative season": dict(trend="add", seasonal="mul"),
    "HW damped trend + multiplicative season":   dict(trend="add", damped_trend=True, seasonal="mul"),
    "HW additive trend + additive season":       dict(trend="add", seasonal="add"),
    "HW no trend + multiplicative season":       dict(trend=None, seasonal="mul"),
}
rows = []
for name, kw in configs.items():
    fit = ExponentialSmoothing(train, seasonal_periods=12, initialization_method="estimated", **kw).fit()
    rows.append((name, mape(test.values, fit.forecast(12).values)))
snaive = train.iloc[-12:].values                      # seasonal naive: repeat last year
rows.append(("Seasonal naive (benchmark)", mape(test.values, snaive)))
bt = pd.DataFrame(rows, columns=["model", "MAPE_2017_pct"]).sort_values("MAPE_2017_pct").round(2)
bt.to_csv(TABLES / "forecast_backtest.csv", index=False)
print("\nBack-test on 2017 (lower MAPE = better):"); print(bt.to_string(index=False))

best_name = bt[bt.model.str.startswith("HW")].iloc[0].model
best_kw = configs[best_name]
print(f"\nSelected model: {best_name}")

# ---- 2) final fit on all 48 months and forecast 12 months -----------------
final = ExponentialSmoothing(y, seasonal_periods=12, initialization_method="estimated", **best_kw).fit()
fc = final.forecast(FORECAST_MONTHS)
sims = final.simulate(FORECAST_MONTHS, repetitions=2000, error="mul" if best_kw.get("seasonal") == "mul" else "add",
                      random_state=RANDOM_STATE)
lo, hi = np.percentile(sims, 10, axis=1), np.percentile(sims, 90, axis=1)
fdf = pd.DataFrame({"month": fc.index, "forecast": fc.values, "lower_80": lo, "upper_80": hi})
fdf["quarter"] = fdf.month.dt.to_period("Q").astype(str)
fdf.round(0).to_csv(TABLES / "forecast_monthly_2018.csv", index=False)

q = fdf.groupby("quarter").forecast.sum().to_frame("forecast")
# quarterly interval: sum each simulated path within the quarter, THEN take percentiles
qid = fdf.month.dt.to_period("Q").astype(str).values
sim_q = pd.DataFrame(np.asarray(sims)).groupby(qid).sum()
q["lower_80"] = np.percentile(sim_q.values, 10, axis=1)
q["upper_80"] = np.percentile(sim_q.values, 90, axis=1)
q = q.round(0)
# last four actual quarters for comparison
act = y.resample("QS").sum()
act.index = act.index.to_period("Q").astype(str)
q["same_quarter_2017_actual"] = [act.get(p.replace("2018", "2017")) for p in q.index]
q["growth_vs_2017_pct"] = ((q.forecast / q.same_quarter_2017_actual - 1) * 100).round(1)
q.to_csv(TABLES / "forecast_quarterly_2018.csv")
print("\nQuarterly projection for 2018:"); print(q.to_string())
print(f"\nFY2018 projection: ${q.forecast.sum():,.0f} vs FY2017 actual ${act['2017Q1':'2017Q4'].sum():,.0f}")

# ---- Power BI table (actual + forecast) -----------------------------------
hist = pd.DataFrame({"month": y.index, "actual": y.values, "forecast": np.nan, "lower_80": np.nan, "upper_80": np.nan})
pb = pd.concat([hist, fdf[["month", "forecast", "lower_80", "upper_80"]]], ignore_index=True)
pb["type"] = np.where(pb.actual.notna(), "Actual", "Forecast")
pb.round(2).to_csv(POWERBI / "sales_forecast.csv", index=False)
q.reset_index().to_csv(POWERBI / "forecast_quarterly.csv", index=False)

# ---- chart ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(y.index, y.values / 1000, color=BLUE, marker="o", ms=3, label="Actual monthly sales")
ax.plot(fdf.month, fdf.forecast / 1000, color=ORANGE, marker="o", ms=3, label="Holt-Winters forecast")
ax.fill_between(fdf.month, fdf.lower_80 / 1000, fdf.upper_80 / 1000, color=ORANGE, alpha=.2, label="80% interval")
ax.axvline(pd.Timestamp("2017-12-15"), ls="--", c=GREY)
ax.set_ylabel("Sales ($ thousand)"); ax.set_title(f"Monthly sales and 2018 projection ({best_name})")
ax.legend(frameon=False, loc="upper left"); fig.tight_layout()
fig.savefig(CHARTS / "08_sales_forecast.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 4))
w = .38; xs = np.arange(4)
ax.bar(xs - w / 2, q.same_quarter_2017_actual / 1000, w, color=GREY, label="2017 actual")
ax.bar(xs + w / 2, q.forecast / 1000, w, color=ORANGE, label="2018 forecast")
ax.set_xticks(xs); ax.set_xticklabels(["Q1", "Q2", "Q3", "Q4"]); ax.set_ylabel("Sales ($ thousand)")
ax.set_title("Quarterly sales: 2017 actual vs 2018 projection"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(CHARTS / "09_quarterly_projection.png", dpi=150); plt.close(fig)
