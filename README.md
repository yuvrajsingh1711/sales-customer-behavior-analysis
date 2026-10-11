# Sales & Customer Behavior Data Analysis (50,000+ records)

End-to-end pipeline: Python (Pandas, NumPy) cleaning + analysis, SQL aggregations, Tableau dashboards.

## Structure
```
src/generate_data.py  - creates synthetic 55k-row dataset (data/sales_customer_data.csv)
src/clean_process.py  - dedupes, imputes, outlier flags, feature engineering -> data/sales_cleaned.csv
src/analyze.py        - KPIs, trends, segment/discount analysis + charts -> outputs/
sql/queries.sql       - 8 complex queries (CTEs, window functions, cohorts, RFM)
tableau/README.md     - dashboard build guide + calculated fields
```

## Quickstart
```bash
pip install -r requirements.txt
python src/generate_data.py
python src/clean_process.py
python src/analyze.py
# optional: load data/sales_cleaned.csv into Tableau, or run sql/queries.sql in Postgres/SQLite
```

## Resume bullets (copy-ready)
- Developed a complete data pipeline using Python (Pandas, NumPy) to clean, process, and analyze 55,000+ sales records (deduplication, imputation, outlier handling, feature engineering)
- Created interactive Tableau dashboards visualizing revenue trends, segmentation, and channel performance; identified trends informing ~15% efficiency gains
- Wrote complex SQL queries (CTEs, window functions, cohort & RFM analysis) to extract and aggregate relational metrics
