"""
Generate a synthetic (fictional) procurement dataset for a mid-size Irish company.
Reproducible: fixed random seed. All supplier names are fictional.

Run:  python data/generate_data.py
Output: data/raw/*.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "raw"
OUT.mkdir(exist_ok=True)

START, END = pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31")   # END = data cut-off date

# id, name, price_low, price_high, qty_low, qty_high, n_items, lead_time_days, demand weight, base item names
CATS = [
    (1, "Electrical Equipment", 15, 350, 5, 40, 18, 14, 1.3, ["Circuit Breaker", "Cable Drum", "LED Panel", "Distribution Board", "Socket Set", "Contactor"]),
    (2, "Building Materials", 5, 400, 20, 400, 16, 7, 1.2, ["Insulation Roll", "Plasterboard", "Cement Bag", "Timber Batten", "Sealant Case", "Fixings Box"]),
    (3, "IT Hardware & Software", 40, 1800, 1, 40, 14, 10, 1.3, ["Laptop", "Monitor", "Network Switch", "Docking Station", "Software Licence", "Server Disk"]),
    (4, "Safety & PPE", 3, 150, 20, 500, 14, 6, 0.8, ["Hi-Vis Jacket", "Safety Boots", "Hard Hat", "Gloves Box", "Safety Goggles", "First Aid Kit"]),
    (5, "Packaging", 1, 60, 100, 2000, 14, 7, 0.9, ["Carton Pack", "Pallet Wrap", "Bubble Wrap Roll", "Packing Tape Box", "Pallet", "Label Roll"]),
    (6, "Tools & Maintenance (MRO)", 4, 500, 5, 100, 16, 8, 1.0, ["Drill Bit Set", "Lubricant Drum", "Bearing", "Hydraulic Hose", "Power Tool", "Filter Kit"]),
    (7, "Fleet & Vehicle Parts", 10, 1200, 2, 60, 12, 12, 1.1, ["Tyre", "Brake Pad Set", "Battery", "Wiper Set", "Service Kit", "Headlamp Unit"]),
    (8, "Office & Facilities Supplies", 2, 120, 10, 300, 16, 4, 0.6, ["Paper Box", "Toner", "Cleaning Kit", "Desk Chair", "Kitchen Supplies", "Stationery Pack"]),
]
cat_df = pd.DataFrame([(c[0], c[1]) for c in CATS], columns=["category_id", "category_name"])

items, item_id = [], 1
for cid, cname, plo, phi, qlo, qhi, n, lead, _, bases in CATS:
    for k in range(n):
        price = float(np.round(np.exp(rng.uniform(np.log(plo), np.log(phi))), 2))
        items.append(dict(
            item_id=item_id, item_name=f"{bases[k % len(bases)]} Type {chr(65 + k // len(bases))}",
            sku=f"{cname[:3].upper()}-{item_id:03d}", category_id=cid,
            list_price=price, unit_of_measure="Each", standard_lead_time_days=int(lead + rng.integers(-2, 4)),
            qty_low=qlo, qty_high=qhi))
        item_id += 1
item_df = pd.DataFrame(items)

dept_df = pd.DataFrame({
    "dept_id": range(1, 9),
    "dept_name": ["Operations", "Facilities", "IT", "Finance", "Sales", "Logistics", "Health & Safety", "Projects"],
    "maverick_rate": [0.12, 0.09, 0.05, 0.03, 0.16, 0.11, 0.04, 0.18],   # chance a line is bought off-contract
})

prefixes = ["Atlas", "Celtic", "Emerald", "Northway", "Liffey", "Shannon", "Aurora", "Keystone", "Vertex", "Harbour",
            "Summit", "Ironbridge", "Clarion", "Pinnacle", "Meridian", "Orbit", "Bluegate", "Redwood", "Falcon", "Granite"]
suffixes = ["Supplies", "Industrial", "Trading", "Solutions", "Components", "Distribution"]
combos = [f"{p} {s}" for p in prefixes for s in suffixes]
names = rng.choice(combos, size=60, replace=False)
countries = rng.choice(["Ireland", "United Kingdom", "Germany", "Netherlands", "Poland", "France", "Spain", "China", "United States"],
                       size=60, p=[.40, .15, .10, .08, .06, .06, .05, .06, .04])
sup = pd.DataFrame({
    "supplier_id": range(1, 61),
    "supplier_name": names,
    "country": countries,
    "primary_category_id": [(i % 8) + 1 for i in range(60)],
    "payment_terms_days": rng.choice([30, 45, 60], size=60, p=[.5, .3, .2]),
    "supplier_tier": rng.choice(["Strategic", "Preferred", "Approved", "Tactical"], size=60, p=[.1, .3, .4, .2]),
})
sup["_reliability"] = np.clip(rng.beta(8, 2, 60), 0.45, 0.98)
sup["_reject_rate"] = np.clip(rng.beta(1.2, 40, 60), 0.002, 0.12)
sup["_discount"] = rng.uniform(0.03, 0.18, 60)
sup.loc[sup.supplier_id.isin([7, 23, 41]), "_reliability"] = 0.55   # deliberately poor delivery performers to discover
sup.loc[sup.supplier_id.isin([12, 35]), "_reject_rate"] = 0.10      # deliberately poor quality suppliers to discover

month_w = np.array([.9, .9, 1.0, 1.0, 1.0, .95, .85, .75, 1.05, 1.1, 1.2, 1.15])
days = pd.date_range(START, END - pd.Timedelta(days=1))
days = days[days.dayofweek < 5]
day_w = month_w[days.month - 1]
day_w = day_w / day_w.sum()

cat_w = {c[0]: c[8] for c in CATS}
rank_w = 1.0 / (np.arange(1, 61) ** 0.6)
rng.shuffle(rank_w)
sup_w = np.array([rank_w[i] * cat_w[sup.primary_category_id[i]] for i in range(60)])
sup_w = sup_w / sup_w.sum()

N_PO = 3200
po_dates = np.sort(rng.choice(days, size=N_PO, p=day_w))
po_sup = rng.choice(sup.supplier_id, size=N_PO, p=sup_w)
po_dept = rng.choice(dept_df.dept_id, size=N_PO, p=[.2, .1, .12, .05, .12, .18, .08, .15])
n_lines = rng.choice([1, 2, 3, 4, 5], size=N_PO, p=[.35, .30, .20, .10, .05])

mav = dept_df.set_index("dept_id")["maverick_rate"].to_dict()
items_by_cat = {cid: item_df[item_df.category_id == cid] for cid in item_df.category_id.unique()}
sup_i = sup.set_index("supplier_id")

rows, line_id = [], 1
for p in range(N_PO):
    s = int(po_sup[p]); d = int(po_dept[p]); po_date = pd.Timestamp(po_dates[p])
    srow = sup_i.loc[s]
    pool = items_by_cat[int(srow.primary_category_id)]
    chosen = pool.sample(n=min(int(n_lines[p]), len(pool)), random_state=int(rng.integers(0, 1_000_000)))
    for _, it in chosen.iterrows():
        qty = int(max(1, np.round(np.exp(rng.uniform(np.log(max(it.qty_low, 1)), np.log(it.qty_high))))))
        uplift = 1.0 if po_date.year == 2024 else 1.025
        if it.category_id == 1 and po_date >= pd.Timestamp("2025-06-01"):
            uplift *= 1.06                                   # commodity price shock on electrical
        contract = round(it.list_price * (1 - srow._discount) * uplift, 2)
        on_contract = bool(rng.random() > mav[d])
        if on_contract:
            price = contract * (1 + (rng.normal(0.03, 0.015) if rng.random() < 0.15 else 0))
        else:
            price = it.list_price * uplift * (1 + rng.uniform(0.02, 0.12))
        price = round(price, 2)

        promised = po_date + pd.Timedelta(days=int(it.standard_lead_time_days))
        delay = -int(rng.integers(0, 3)) if rng.random() < srow._reliability else 1 + int(rng.geometric(0.22))
        delivery = promised + pd.Timedelta(days=delay)
        if rng.random() < (0.6 + 0.4 * srow._reliability):
            recv = qty
        else:
            recv = max(1, int(round(qty * (1 - rng.uniform(0.1, 0.4)))))
        rej = int(rng.binomial(recv, srow._reject_rate))
        invoice = delivery + pd.Timedelta(days=int(rng.integers(1, 6)))
        due = invoice + pd.Timedelta(days=int(srow.payment_terms_days))
        paid = due - pd.Timedelta(days=int(rng.integers(0, 8))) if rng.random() < 0.72 else due + pd.Timedelta(days=int(rng.integers(1, 31)))

        if delivery > END:                       # still open at cut-off
            delivery = invoice = due = paid = pd.NaT; recv = rej = np.nan
        elif paid > END:                         # delivered, not yet paid
            paid = pd.NaT

        rows.append(dict(
            po_line_id=line_id, po_number=f"PO{100000 + p}", po_date=po_date, supplier_id=s, item_id=int(it.item_id), dept_id=d,
            quantity=qty, unit_price=price, contract_price=contract, promised_date=promised, delivery_date=delivery,
            qty_received=recv, qty_rejected=rej, invoice_date=invoice, due_date=due, paid_date=paid, is_on_contract=on_contract))
        line_id += 1

fact = pd.DataFrame(rows)
for c in ["qty_received", "qty_rejected"]:
    fact[c] = fact[c].astype("Int64")
clean_fact = fact.copy()
# Inject 25 exact duplicate rows so the Power Query clean-up step has real work to do
fact = pd.concat([fact, fact.sample(25, random_state=1)]).sample(frac=1, random_state=2).reset_index(drop=True)

# ---- Stock snapshots (month-end), driven by actual accepted receipts ----
recv_df = clean_fact.dropna(subset=["delivery_date"]).copy()
recv_df["ym"] = recv_df.delivery_date.dt.to_period("M")
recv_df["accepted"] = (recv_df.qty_received - recv_df.qty_rejected).astype(float)
months = pd.period_range(START, END, freq="M")
rec_piv = recv_df.pivot_table(index="item_id", columns="ym", values="accepted", aggfunc="sum").reindex(index=item_df.item_id, columns=months).fillna(0)

snap = []
for iid in item_df.item_id:
    r = rec_piv.loc[iid].values
    mean_use = max(r.mean(), 1.0)
    on_hand = 1.2 * mean_use
    reorder = int(round(0.9 * mean_use))
    for t, m in enumerate(months):
        usage = mean_use * month_w[m.month - 1] * np.exp(rng.normal(0, 0.25))
        on_hand = max(0.0, on_hand + r[t] - usage)
        oh = int(round(on_hand))
        snap.append(dict(snapshot_date=m.to_timestamp(how="end").normalize(), item_id=iid, on_hand_qty=oh,
                         reorder_level=reorder, avg_monthly_usage=int(round(mean_use)),
                         is_stockout=oh == 0, is_below_reorder=oh < reorder))
stock = pd.DataFrame(snap)

dd = pd.date_range(START, END)
date_df = pd.DataFrame({"Date": dd, "Year": dd.year, "Quarter": "Q" + dd.quarter.astype(str), "MonthNum": dd.month,
                        "MonthName": dd.strftime("%b"), "YearMonth": dd.strftime("%Y-%m"), "IsWeekend": dd.dayofweek >= 5})

sup_out = sup.drop(columns=[c for c in sup.columns if c.startswith("_")])
item_out = item_df.drop(columns=["qty_low", "qty_high"])
for name, df in {"dim_supplier": sup_out, "dim_item": item_out, "dim_category": cat_df,
                 "dim_department": dept_df.drop(columns=["maverick_rate"]), "dim_date": date_df,
                 "fact_po_lines": fact, "fact_stock_snapshot": stock}.items():
    df.to_csv(OUT / f"{name}.csv", index=False, date_format="%Y-%m-%d")
    print(f"{name:22s} {len(df):>6,} rows")
