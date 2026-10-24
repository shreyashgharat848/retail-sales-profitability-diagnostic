"""Step 3: RFM customer segmentation with K-Means (793 customers -> 4 segments)."""
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from config import DB_PATH, SQL_DIR, TABLES, CHARTS, RANDOM_STATE, N_CLUSTERS, POWERBI

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

with sqlite3.connect(DB_PATH) as con:
    rfm = pd.read_sql_query((SQL_DIR / "09_rfm_base.sql").read_text(), con)
assert len(rfm) == 793

# ---- feature engineering: log-transform skewed variables, then standardise ----
X = np.log1p(rfm[["recency_days", "frequency", "monetary"]])
Xs = StandardScaler().fit_transform(X)

# ---- how many clusters? show the evidence (elbow + silhouette) -------------
ks = range(2, 9)
inertia, sil = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE).fit(Xs)
    inertia.append(km.inertia_); sil.append(silhouette_score(Xs, km.labels_))
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(list(ks), inertia, marker="o"); ax[0].set_title("Elbow (inertia)"); ax[0].set_xlabel("k")
ax[1].plot(list(ks), sil, marker="o", color="#EF6C00"); ax[1].set_title("Silhouette score"); ax[1].set_xlabel("k")
for a in ax: a.axvline(N_CLUSTERS, ls="--", c="grey")
fig.suptitle(f"Choosing k (dashed line = k={N_CLUSTERS}, chosen for interpretable business segments)")
fig.tight_layout(); fig.savefig(CHARTS / "06_kmeans_k_selection.png", dpi=150); plt.close(fig)
pd.DataFrame({"k": list(ks), "inertia": inertia, "silhouette": sil}).to_csv(TABLES / "kmeans_k_selection.csv", index=False)

# ---- final model --------------------------------------------------------
km = KMeans(n_clusters=N_CLUSTERS, n_init=50, random_state=RANDOM_STATE).fit(Xs)
rfm["cluster"] = km.labels_
sil_final = silhouette_score(Xs, km.labels_)

# ---- name the clusters from their profile (rank of recency / frequency / monetary) ----
prof = rfm.groupby("cluster")[["recency_days", "frequency", "monetary"]].mean()
score = (prof.frequency.rank() + prof.monetary.rank() + (-prof.recency_days).rank())  # higher = better customer
order = score.sort_values(ascending=False).index.tolist()
names = {}
names[order[0]] = "Champions"                 # recent, frequent, high spend
names[order[-1]] = "Lost / Low value"         # long inactive, low spend
mid = order[1:-1]
# among the two middle clusters: the more recent one is "Recent buyers", the other "At risk"
mid_sorted = prof.loc[mid].sort_values("recency_days").index.tolist()
names[mid_sorted[0]] = "Recent buyers"
names[mid_sorted[1]] = "At risk"
rfm["rfm_segment"] = rfm.cluster.map(names)

summary = (rfm.groupby("rfm_segment")
           .agg(customers=("customer_id", "count"),
                avg_recency_days=("recency_days", "mean"),
                avg_orders=("frequency", "mean"),
                avg_spend=("monetary", "mean"),
                total_sales=("monetary", "sum"),
                total_profit=("total_profit", "sum"))
           .assign(pct_customers=lambda d: d.customers / d.customers.sum() * 100,
                   pct_sales=lambda d: d.total_sales / d.total_sales.sum() * 100,
                   profit_margin_pct=lambda d: d.total_profit / d.total_sales * 100)
           .sort_values("total_sales", ascending=False).round(1))
summary.to_csv(TABLES / "rfm_segment_summary.csv")
rfm.drop(columns="cluster").to_csv(TABLES / "rfm_customers.csv", index=False)
rfm.drop(columns="cluster").to_csv(POWERBI / "rfm_segments.csv", index=False)

print(f"k={N_CLUSTERS} | silhouette = {sil_final:.3f} | customers = {len(rfm)}")
print(summary.to_string())

# ---- charts ---------------------------------------------------------------
palette = {"Champions": "#2E7D32", "Recent buyers": "#1565C0", "At risk": "#EF6C00", "Lost / Low value": "#C62828"}
fig, ax = plt.subplots(1, 3, figsize=(13, 4.2))
for seg, g in rfm.groupby("rfm_segment"):
    ax[0].scatter(g.frequency, g.monetary, s=12, alpha=.6, label=seg, c=palette[seg])
    ax[1].scatter(g.recency_days, g.monetary, s=12, alpha=.6, c=palette[seg])
ax[0].set_xlabel("Frequency (orders)"); ax[0].set_ylabel("Monetary ($ sales)"); ax[0].legend(frameon=False, fontsize=8)
ax[1].set_xlabel("Recency (days since last order)"); ax[1].set_ylabel("Monetary ($ sales)")
for a in ax[:2]: a.set_yscale("log")
s2 = summary.reindex(["Champions", "Recent buyers", "At risk", "Lost / Low value"])
ax[2].bar(s2.index, s2.pct_customers, width=.4, label="% customers", color="#9E9E9E", align="edge")
ax[2].bar(s2.index, s2.pct_sales, width=-.4, label="% sales", color="#1565C0", align="edge")
ax[2].set_ylabel("%"); ax[2].legend(frameon=False); ax[2].tick_params(axis="x", rotation=20)
fig.suptitle("RFM segments from K-Means (k=4)"); fig.tight_layout()
fig.savefig(CHARTS / "07_rfm_segments.png", dpi=150); plt.close(fig)
