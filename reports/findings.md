# Findings and recommendations

All figures are produced by `python src/run_all.py` and checked by `src/06_validate_results.py`.
Currency is US dollars (Superstore sample data). The analysis is observational, not causal.

## 1. Business context
| KPI | Value |
|---|---|
| Order lines / orders / customers | 9,994 / 5,009 / 793 |
| Sales / profit | $2,297,201 / $286,397 |
| Overall profit margin | 12.47% |
| Average discount | 15.6% |
| Loss-making order lines | 1,871 (18.7%) |

## 2. Margin erosion: discounts above 20%
| Discount band | Order lines | Profit margin | Lines that lose money |
|---|---:|---:|---:|
| 0% (none) | 4,798 | **+29.5%** | 0% |
| 0-20% | 3,803 | +11.9% | 13.8% |
| 20-40% | 460 | **-15.3%** | 90.2% |
| >40% | 933 | -77.4% | 100% |
| *All lines over 20%* | *1,393* | *-37.3%* | *96.8%* |
| *All lines up to 20%* | *8,601* | *+21.8%* | |

- Margin flips from positive to negative exactly when discounts pass 20%.
- Lines discounted above 20% are only **13.9% of order lines** and **15.8% of sales**, yet they lose **$135,376**.
- Without them, profit would be about **$421,773, roughly 47% higher**, at a **21.8% margin**.

## 3. Loss-making sub-categories
| Sub-category | Profit | Margin | Note |
|---|---:|---:|---|
| Tables | -$17,725 | -8.6% | Loses -$30,698 on >20% discount lines; earns +$12,973 on the rest |
| Bookcases | -$3,473 | -3.0% | Loses -$11,098 on >20% discount lines; earns +$7,625 on the rest |
| Supplies | -$1,189 | -2.6% | No lines above 20% discount, so the cause is **not** discounting (likely cost/pricing) |

## 4. Customer segments (K-Means on log-scaled RFM, k = 4, silhouette 0.255)
| Segment | Customers | % customers | % sales | Margin |
|---|---:|---:|---:|---:|
| Champions | 246 | 31% | 51.8% | 13.4% |
| Recent buyers | 198 | 25% | 23.4% | 13.3% |
| At risk | 262 | 33% | 23.0% | 10.3% |
| Lost / Low value | 87 | 11% | 1.7% | 3.7% |

Silhouette of 0.255 indicates moderate, overlapping segments: typical for RFM data, which is a continuum rather than
sharply separated groups. k = 4 was chosen for business interpretability, with the elbow and silhouette curves shown in
`outputs/charts/06_kmeans_k_selection.png`.

## 5. Sales forecast (Holt-Winters, monthly, seasonal period 12)
Back-test (train 2014-2016, test 2017):

| Model | MAPE |
|---|---:|
| HW additive trend + multiplicative seasonality (selected) | 20.8% |
| HW additive trend + additive seasonality | 20.9% |
| HW damped trend + multiplicative seasonality | 23.0% |
| HW no trend + multiplicative seasonality | 23.3% |
| Seasonal naive benchmark | 24.5% |

Monthly sales are volatile and only four years of history exist, so the model beats the benchmark by a modest margin.
2018 projection (80% simulation interval):

| Quarter | Forecast | 80% interval | vs same quarter 2017 |
|---|---:|---:|---:|
| Q1 2018 | $123,043 | $91,927 - $153,802 | -0.1% |
| Q2 2018 | $151,835 | $117,726 - $188,206 | +13.5% |
| Q3 2018 | $206,960 | $157,628 - $260,910 | +5.5% |
| Q4 2018 | $295,885 | $225,221 - $370,298 | +5.7% |

FY2018 projection: **$777,723** vs FY2017 actual $733,215 (about +6.1%).

## 6. Recommendations
1. **Introduce a discount guardrail of 20%.** Require approval for any line above 20% (13.9% of lines today).
2. **Reprice or review Tables and Bookcases.** Their losses come entirely from deep-discount lines.
3. **Investigate Supplies separately.** It loses money without heavy discounting, which points to cost or pricing.
4. **Run a win-back campaign for the "At risk" segment** (33% of customers, avg 228 days since last order) using non-margin-eroding incentives.
5. **Protect Champions** (31% of customers, 52% of sales) with loyalty benefits rather than blanket discounts.
6. **Use the forecast for planning, with the interval,** not the point estimate, especially for Q4, which carries the most sales and the widest range.

## 7. Limitations
- Observational data: discounts may be applied to already weak products, so the margin drop is not proven to be caused by discounting alone.
- Sales and profit are as recorded; discounts and costs are not decomposed any further.
- Four years of monthly data is a short history for a seasonal model.
- RFM segments overlap; they are a practical grouping, not natural clusters.
