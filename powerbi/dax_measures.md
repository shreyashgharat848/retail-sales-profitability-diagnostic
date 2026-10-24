# DAX measures

Create a measures table (Home → Enter Data → name it `_Measures`) and add the measures below.
All column names match the CSVs in `powerbi/data/`.

## Data model

| Relationship | Cardinality | Filter direction |
|---|---|---|
| `dim_date[date]` → `fact_orders[order_date]` | One-to-many | Single |
| `rfm_segments[customer_id]` → `fact_orders[customer_id]` | One-to-many | Single |

`sales_forecast` is a stand-alone table (its own `month` column is the axis).
Mark `dim_date` as the date table: Table tools → Mark as date table → `date`.
In the model view, set `fact_orders[discount]` to *Don't summarize* and format it as a percentage.

## 1. Core KPIs

```dax
Total Sales = SUM ( fact_orders[sales] )

Total Profit = SUM ( fact_orders[profit] )

Profit Margin % = DIVIDE ( [Total Profit], [Total Sales] )

Orders = DISTINCTCOUNT ( fact_orders[order_id] )

Customers = DISTINCTCOUNT ( fact_orders[customer_id] )

Avg Discount % = AVERAGE ( fact_orders[discount] )

Order Lines = COUNTROWS ( fact_orders )

Loss-Making Lines = CALCULATE ( COUNTROWS ( fact_orders ), fact_orders[profit] < 0 )

Loss Line % = DIVIDE ( [Loss-Making Lines], [Order Lines] )
```

## 2. Time intelligence

```dax
Sales PY = CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( dim_date[date] ) )

Sales YoY % = DIVIDE ( [Total Sales] - [Sales PY], [Sales PY] )

Profit PY = CALCULATE ( [Total Profit], SAMEPERIODLASTYEAR ( dim_date[date] ) )

Profit YoY % = DIVIDE ( [Total Profit] - [Profit PY], [Profit PY] )

Sales YTD = TOTALYTD ( [Total Sales], dim_date[date] )
```

## 3. Discount diagnostic (the core finding)

```dax
Margin % - No Discount =
CALCULATE ( [Profit Margin %], fact_orders[discount] = 0 )

Margin % - Up to 20% =
CALCULATE ( [Profit Margin %], fact_orders[discount] <= 0.2 )

Margin % - Over 20% =
CALCULATE ( [Profit Margin %], fact_orders[discount] > 0.2 )

Margin % - 20 to 40% =
CALCULATE ( [Profit Margin %], fact_orders[discount] > 0.2, fact_orders[discount] <= 0.4 )

Profit - Over 20% Discount =
CALCULATE ( [Total Profit], fact_orders[discount] > 0.2 )

Share of Lines Over 20% Discount =
DIVIDE ( CALCULATE ( [Order Lines], fact_orders[discount] > 0.2 ), [Order Lines] )

Margin Gap (pts) = [Margin % - No Discount] - [Margin % - Over 20%]
```

## 4. Sub-category flag

```dax
Profit Status =
IF ( [Total Profit] < 0, "Loss-making", "Profitable" )

Profit Colour =
IF ( [Total Profit] < 0, "#C62828", "#1565C0" )     -- use in Format → Conditional formatting → Field value
```

## 5. RFM customer segments (use `rfm_segments` columns)

```dax
Avg Recency (days) = AVERAGE ( rfm_segments[recency_days] )

Avg Orders per Customer = AVERAGE ( rfm_segments[frequency] )

Avg Spend per Customer = AVERAGE ( rfm_segments[monetary] )

% of Customers =
DIVIDE ( DISTINCTCOUNT ( rfm_segments[customer_id] ),
         CALCULATE ( DISTINCTCOUNT ( rfm_segments[customer_id] ), ALL ( rfm_segments ) ) )

% of Sales =
DIVIDE ( [Total Sales], CALCULATE ( [Total Sales], ALL ( rfm_segments ) ) )
```

## 6. Forecast (use `sales_forecast`)

```dax
Actual Sales (monthly) = SUM ( sales_forecast[actual] )

Forecast Sales (monthly) = SUM ( sales_forecast[forecast] )

Forecast Lower 80 = SUM ( sales_forecast[lower_80] )

Forecast Upper 80 = SUM ( sales_forecast[upper_80] )

FY2018 Projected Sales =
CALCULATE ( SUM ( forecast_quarterly[forecast] ) )
```
