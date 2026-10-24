# Power BI dashboard (3 pages)

Power BI Desktop saves reports in a proprietary `.pbix` format that cannot be generated from code,
so this folder contains everything needed to build the dashboard in about 30-45 minutes,
plus a place to drop your finished file.

| File | Purpose |
|---|---|
| `data/` | Clean, model-ready CSVs produced by `src/05_export_powerbi.py` |
| `dax_measures.md` | All DAX measures, the data model and relationships |
| `README.md` | Page-by-page build guide (this file) |

> After you build it, save the report as `powerbi/Retail_Profitability_Dashboard.pbix`
> and add screenshots to `powerbi/screenshots/` so reviewers can see it without Power BI.

## Load the data
Home → Get data → Text/CSV. Load: `fact_orders`, `dim_date`, `rfm_segments`, `sales_forecast`,
`forecast_quarterly`, `04_subcategory_profitability`, `02_discount_bands`.
Set up relationships and the date table exactly as described in `dax_measures.md`.

## Page 1: Executive Overview
- **KPI cards:** Total Sales, Total Profit, Profit Margin %, Orders, Customers, Loss Line %
- **Line + clustered column:** Sales and Profit by `dim_date[year_month]`, margin % on secondary axis
- **Bar:** Profit Margin % by `fact_orders[region]`
- **Matrix:** `segment` × `category` with Total Profit and conditional formatting (red < 0)
- **Slicers:** Year, Region, Segment

## Page 2: Discount & Margin Diagnostic (the headline page)
- **Column chart:** `fact_orders[discount_band]` vs `Profit Margin %` (colour negative bars red)
- **Cards:** `Margin % - No Discount`, `Margin % - 20 to 40%`, `Margin % - Over 20%`, `Share of Lines Over 20% Discount`
- **Bar chart:** `sub_category` vs `Total Profit`, colour by `Profit Colour` to flag loss-makers
- **Scatter:** x = `Avg Discount %`, y = `Profit Margin %`, details = `sub_category`, size = `Total Sales`
- **Table:** top 10 loss-making products (Top N filter on `Total Profit`, bottom 10)
- **Slicers:** Category, Discount band, Year

## Page 3: Customer Segments & Sales Forecast
- **Donut or bar:** `% of Customers` and `% of Sales` by `rfm_segments[rfm_segment]`
- **Table:** segment, customers, `Avg Recency (days)`, `Avg Orders per Customer`, `Avg Spend per Customer`, Total Profit
- **Line chart:** `sales_forecast[month]` with `Actual Sales (monthly)`, `Forecast Sales (monthly)`; add `Forecast Lower 80` / `Forecast Upper 80` as an error band
- **Clustered column:** `forecast_quarterly[quarter]` vs forecast and 2017 actual
- **Card:** `FY2018 Projected Sales`

## Design tips
Use a consistent palette (blue `#1565C0` = good/neutral, red `#C62828` = loss, orange `#EF6C00` = forecast),
keep one message per page, and give every visual a plain-English title that states the finding
(e.g. "Margin turns negative above 20% discount").
