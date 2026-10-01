# Data Model

Star schema with two fact tables sharing conformed dimensions.

```
                 dim_date
                /   |    \
   (po_date, ACTIVE)|     (snapshot_date)
                /   |      \
dim_supplier --- fact_po_lines        fact_stock_snapshot --- dim_item --- dim_category
                    |   \                                        |
              dim_department \______ item_id ____________________/
```

| Relationship | Cardinality | Filter | Status |
|---|---|---|---|
| fact_po_lines[po_date] -> dim_date[Date] | many-to-one | single | **Active** |
| fact_po_lines[delivery_date] -> dim_date[Date] | many-to-one | single | Inactive (use `USERELATIONSHIP`) |
| fact_po_lines[paid_date] -> dim_date[Date] | many-to-one | single | Inactive |
| fact_po_lines[supplier_id] -> dim_supplier[supplier_id] | many-to-one | single | Active |
| fact_po_lines[item_id] -> dim_item[item_id] | many-to-one | single | Active |
| fact_po_lines[dept_id] -> dim_department[dept_id] | many-to-one | single | Active |
| dim_item[category_id] -> dim_category[category_id] | many-to-one | single | Active |
| fact_stock_snapshot[item_id] -> dim_item[item_id] | many-to-one | single | Active |
| fact_stock_snapshot[snapshot_date] -> dim_date[Date] | many-to-one | single | Active |

## Grain
- `fact_po_lines`: one row per purchase-order line.
- `fact_stock_snapshot`: one row per item per month-end.

## Key modelling decisions
- **Role-playing date dimension.** Orders, deliveries and payments each have a date; one date table with one active and two inactive relationships avoids three copies of the calendar.
- **Row-level flags in Power Query** (`is_on_time`, `is_in_full`, `is_otif`, `is_paid_on_time`) because DAX boolean filters cannot compare two columns. Nulls mean "not yet happened", which keeps open orders out of the performance ratios.
- **Semi-additive stock measures.** Balances use `LASTDATE`, never `SUM` across months.
- **Data quality.** The raw extract contains 25 duplicate PO lines, removed on `po_line_id` in Power Query (6,955 -> 6,930 rows).

## Data dictionary (key columns)
| Column | Meaning |
|---|---|
| unit_price | Price actually paid |
| contract_price | Price that should have been paid under the supplier contract |
| is_on_contract | False = maverick (off-contract) buy |
| promised_date / delivery_date | Supplier commitment vs actual; delivery null = still open at cut-off |
| qty_received / qty_rejected | Units delivered / units failing inspection |
| due_date / paid_date | Invoice due date vs actual payment; paid null = unpaid at cut-off |
| data cut-off | 31 Dec 2025 |
