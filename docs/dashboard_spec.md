# Report Build Spec (Power BI Desktop)

Theme: clean, one accent colour (teal) + red for exceptions. Font: Segoe UI. Canvas 1280x720. Every page has a slicer bar: Year, Quarter, Category, Department.

## Page 1 - Executive Overview
- Cards: Total Spend, Spend YoY %, PO Count, Active Suppliers, Contract Compliance %, OTIF %
- Line chart: Total Spend by YearMonth + Spend 3M Rolling Avg
- Bar: Total Spend by Category
- Donut/bar: Spend by Country (supplier)
- Decomposition tree or matrix: Spend by Category > Supplier

## Page 2 - Supplier Performance
- Table/matrix: Supplier, Total Spend, OTIF %, Rejection Rate %, Price Variance %, Supplier Score, Supplier Rating (conditional formatting: red/amber/green on score)
- Scatter: X = OTIF %, Y = Rejection Rate %, size = Total Spend, legend = Supplier Tier (top-right = good, bottom-left quadrant = problem)
- Bar: Top 10 suppliers by Total Spend with Top 10 Supplier Share % card
- Tooltip page: monthly OTIF trend for the hovered supplier

## Page 3 - Spend Concentration (Pareto)
- Combo chart: supplier spend columns (sorted desc) + Cumulative Spend % (Pareto) line, 80% reference line
- Cards: Top 10 Supplier Share %, Active Suppliers
- Insight: a small group of suppliers drives most spend -> negotiation leverage and supplier-risk exposure

## Page 4 - Contract Compliance & Price
- Cards: Contract Compliance %, Maverick Spend, Price Variance, Maverick Price Premium
- Bar: Maverick spend % by Department (sorted desc)
- Table: Top 15 items by Price Variance (Item, Supplier, Qty, Paid vs Contract)
- Line: Price Variance % by month (shows the mid-2025 electrical price shock)

## Page 5 - Delivery & Payments
- Cards: On-Time %, In-Full %, OTIF %, Avg Delay (Late Lines Only), Open Lines
- Line: OTIF % by month (use inactive relationship on delivery_date via `USERELATIONSHIP` measure variant)
- Column: Avg delay by Category
- Cards: Paid On Time %, Avg Days To Pay, Overdue Unpaid Value
- Matrix: supplier x payment terms vs Paid On Time %

## Page 6 - Stock Health
- Cards: Closing On Hand, Months of Cover, Stock-out Items, Below Reorder Items
- Line: Stock-out Rate % by month
- Table: items with Months of Cover < 1 (conditional formatting)
- Scatter: Months of Cover vs Total Spend by Item (overstock vs stock-out risk)

## Interactivity checklist
- Drill-through from supplier (Page 1/2) to a Supplier 360 page
- Bookmarks: "Executive view" / "Detail view"
- Sync slicers across pages; Edit interactions to stop cards filtering each other wrongly
- Add alt text to every visual; tab order set
- Save as `powerbi/Procurement_Analytics.pbix`, export page screenshots to `docs/screenshots/`
