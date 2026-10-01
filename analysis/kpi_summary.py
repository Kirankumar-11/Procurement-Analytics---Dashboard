"""
Independent pandas calculation of the headline KPIs.
Use it to reconcile the Power BI report: every card in the dashboard should match these numbers.

Run:  python analysis/kpi_summary.py
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
f = pd.read_csv(RAW / "fact_po_lines.csv", parse_dates=["po_date", "promised_date", "delivery_date", "invoice_date", "due_date", "paid_date"])
sup = pd.read_csv(RAW / "dim_supplier.csv")
item = pd.read_csv(RAW / "dim_item.csv")
cat = pd.read_csv(RAW / "dim_category.csv")
dept = pd.read_csv(RAW / "dim_department.csv")
stock = pd.read_csv(RAW / "fact_stock_snapshot.csv", parse_dates=["snapshot_date"])

f = f.drop_duplicates("po_line_id").copy()                      # same as Table.Distinct in Power Query
f["line_value"] = f.quantity * f.unit_price
f["contract_value"] = f.quantity * f.contract_price
f["year"] = f.po_date.dt.year
d = f.dropna(subset=["delivery_date"]).copy()
d["on_time"] = d.delivery_date <= d.promised_date
d["in_full"] = d.qty_received >= d.quantity
d["otif"] = d.on_time & d.in_full
p = f.dropna(subset=["paid_date"]).copy()
p["paid_on_time"] = p.paid_date <= p.due_date

spend = f.line_value.sum()
print(f"Rows after de-dup        : {len(f):,}")
print(f"Total spend              : EUR {spend:,.0f}")
for y, g in f.groupby("year"):
    print(f"  spend {y}              : EUR {g.line_value.sum():,.0f}")
y24, y25 = [g.line_value.sum() for _, g in f.groupby("year")]
print(f"Spend YoY                : {y25 / y24 - 1:+.1%}")
print(f"PO count / suppliers     : {f.po_number.nunique():,} / {f.supplier_id.nunique()}")
print(f"Contract compliance      : {f.loc[f.is_on_contract, 'line_value'].sum() / spend:.1%}")
pv = (f.line_value - f.contract_value).sum()
print(f"Price variance vs contract: EUR {pv:,.0f} ({pv / f.contract_value.sum():+.1%})")
print(f"On-time delivery         : {d.on_time.mean():.1%}")
print(f"In-full                  : {d.in_full.mean():.1%}")
print(f"OTIF                     : {d.otif.mean():.1%}")
print(f"Avg delay (days)         : {(d.delivery_date - d.promised_date).dt.days.mean():.2f}")
print(f"Rejection rate           : {d.qty_rejected.sum() / d.qty_received.sum():.2%}")
print(f"Paid on time             : {p.paid_on_time.mean():.1%}")

s = f.groupby("supplier_id").line_value.sum().sort_values(ascending=False)
print(f"Top 10 suppliers share   : {s.head(10).sum() / spend:.1%}")
n80 = (s.cumsum() / spend <= 0.8).sum() + 1
print(f"Suppliers making 80% spend: {n80} of {len(s)}")

print("\nSpend by category")
c = f.merge(item[["item_id", "category_id"]], on="item_id").merge(cat, on="category_id")
print((c.groupby("category_name").line_value.sum().sort_values(ascending=False) / 1e6).round(2).to_string())

print("\nMaverick (off-contract) spend share by department")
m = f.merge(dept, on="dept_id")
print((m.groupby("dept_name").apply(lambda g: g.loc[~g.is_on_contract, "line_value"].sum() / g.line_value.sum()).sort_values(ascending=False) * 100).round(1).to_string())

print("\nWorst 5 suppliers by OTIF (min 40 delivered lines)")
sc = d.groupby("supplier_id").agg(lines=("otif", "size"), otif=("otif", "mean"), rej=("qty_rejected", "sum"), rec=("qty_received", "sum"))
sc["rej_rate"] = sc.rej / sc.rec
sc = sc[sc.lines >= 40].merge(sup[["supplier_id", "supplier_name"]], on="supplier_id")
print(sc.sort_values("otif").head(5)[["supplier_id", "supplier_name", "lines", "otif", "rej_rate"]].round(3).to_string(index=False))
print("\nWorst 3 suppliers by rejection rate")
print(sc.sort_values("rej_rate", ascending=False).head(3)[["supplier_id", "supplier_name", "rej_rate"]].round(3).to_string(index=False))

print("\nStock")
print(f"Stock-out item-months    : {stock.is_stockout.mean():.1%}")
print(f"Below reorder item-months: {stock.is_below_reorder.mean():.1%}")
