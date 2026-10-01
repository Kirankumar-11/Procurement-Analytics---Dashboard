# Procurement Analytics - Power BI

End-to-end procurement analytics project: spend analysis, supplier scorecards, contract compliance, delivery and payment performance, and stock health. Built on a star-schema model with Power Query transformations and a documented DAX measure library.

> **Data note:** the dataset is fully **synthetic** (fixed random seed, fictional suppliers) and modelled on a mid-size Irish company. No real company data is used.

## Business questions answered
- Where is money going, and how is it trending year on year?
- Which suppliers are reliable, which are risky, and how concentrated is spend?
- How much is bought off-contract, by whom, and what does it cost?
- Are we paying suppliers on time, and are stock-outs linked to supplier performance?

## Tech
Power BI Desktop, Power Query (M), DAX, Python (pandas) for data generation and independent KPI reconciliation.

## Repository structure
```
data/generate_data.py        reproducible synthetic data generator
data/raw/                    7 CSV tables (5 dimensions, 2 facts)
powerbi/power_query/         M scripts: cleaning, typing, row-level flags
powerbi/dax/measures.dax     40+ documented measures
analysis/kpi_summary.py      pandas calculation of headline KPIs (validates the report)
docs/data_model.md           star schema, relationships, grain, data dictionary
docs/dashboard_spec.md       page-by-page report design
docs/insights.md             findings and recommendations
```

## How to build the report
1. `pip install -r requirements.txt` then `python data/generate_data.py` (CSVs are already included).
2. Power BI Desktop > Get Data > Blank Query. Create the `DataFolder` parameter and `fnLoadCsv` function from `powerbi/power_query/00_*.pq`, then one query per table from `01_*.pq` and `02_*.pq`.
3. Create relationships as listed in `docs/data_model.md`; mark `dim_date` as the date table.
4. Add the measures from `powerbi/dax/measures.dax` to a `_Measures` table.
5. Build the pages from `docs/dashboard_spec.md`.
6. Reconcile: the cards should match `python analysis/kpi_summary.py`.

## Headline results
EUR 27.6M spend across 60 suppliers - OTIF 73.8% - 87.1% contract compliance - top 10 suppliers = 48% of spend - 12.5% of item-months in stock-out. Full findings in `docs/insights.md`.

## Author
Kirankumar R - github.com/Kirankumar-11
