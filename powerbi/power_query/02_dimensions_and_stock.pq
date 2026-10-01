// Each block below is a SEPARATE query. Name the query exactly as in the first comment line.

// ---- Query: dim_supplier ----
let
    Source = fnLoadCsv("dim_supplier"),
    Typed  = Table.TransformColumnTypes(Source, {{"supplier_id", Int64.Type}, {"supplier_name", type text},
               {"country", type text}, {"primary_category_id", Int64.Type}, {"payment_terms_days", Int64.Type},
               {"supplier_tier", type text}}),
    Trimmed = Table.TransformColumns(Typed, {{"supplier_name", Text.Trim, type text}})
in
    Trimmed

// ---- Query: dim_item ----
let
    Source = fnLoadCsv("dim_item"),
    Typed  = Table.TransformColumnTypes(Source, {{"item_id", Int64.Type}, {"item_name", type text}, {"sku", type text},
               {"category_id", Int64.Type}, {"list_price", type number}, {"unit_of_measure", type text},
               {"standard_lead_time_days", Int64.Type}})
in
    Typed

// ---- Query: dim_category ----
let
    Source = fnLoadCsv("dim_category"),
    Typed  = Table.TransformColumnTypes(Source, {{"category_id", Int64.Type}, {"category_name", type text}})
in
    Typed

// ---- Query: dim_department ----
let
    Source = fnLoadCsv("dim_department"),
    Typed  = Table.TransformColumnTypes(Source, {{"dept_id", Int64.Type}, {"dept_name", type text}})
in
    Typed

// ---- Query: dim_date ----
let
    Source = fnLoadCsv("dim_date"),
    Typed  = Table.TransformColumnTypes(Source, {{"Date", type date}, {"Year", Int64.Type}, {"Quarter", type text},
               {"MonthNum", Int64.Type}, {"MonthName", type text}, {"YearMonth", type text}, {"IsWeekend", type logical}}, "en-IE")
in
    Typed
// After loading: select MonthName > Column tools > Sort by column > MonthNum. Then Table tools > Mark as date table (Date).

// ---- Query: fact_stock_snapshot ----
let
    Source = fnLoadCsv("fact_stock_snapshot"),
    Typed  = Table.TransformColumnTypes(Source, {{"snapshot_date", type date}, {"item_id", Int64.Type},
               {"on_hand_qty", Int64.Type}, {"reorder_level", Int64.Type}, {"avg_monthly_usage", Int64.Type},
               {"is_stockout", type logical}, {"is_below_reorder", type logical}}, "en-IE")
in
    Typed
