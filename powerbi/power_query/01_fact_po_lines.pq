// Query: fact_po_lines
// Cleans the raw extract and adds the row-level flags used by the DAX measures.
let
    Source   = fnLoadCsv("fact_po_lines"),
    Typed    = Table.TransformColumnTypes(Source, {
                 {"po_line_id", Int64.Type}, {"po_number", type text}, {"po_date", type date},
                 {"supplier_id", Int64.Type}, {"item_id", Int64.Type}, {"dept_id", Int64.Type},
                 {"quantity", Int64.Type}, {"unit_price", type number}, {"contract_price", type number},
                 {"promised_date", type date}, {"delivery_date", type date},
                 {"qty_received", Int64.Type}, {"qty_rejected", Int64.Type},
                 {"invoice_date", type date}, {"due_date", type date}, {"paid_date", type date},
                 {"is_on_contract", type logical}}, "en-IE"),

    // Data quality: the extract contains exact duplicate PO lines
    Dedup    = Table.Distinct(Typed, {"po_line_id"}),

    // Values
    LineValue     = Table.AddColumn(Dedup, "line_value", each [quantity] * [unit_price], type number),
    ContractValue = Table.AddColumn(LineValue, "contract_value", each [quantity] * [contract_price], type number),

    // Delivery performance (null = not yet delivered)
    DelayDays = Table.AddColumn(ContractValue, "delivery_delay_days",
                  each if [delivery_date] = null then null else Duration.Days([delivery_date] - [promised_date]), Int64.Type),
    OnTime    = Table.AddColumn(DelayDays, "is_on_time",
                  each if [delivery_date] = null then null else [delivery_date] <= [promised_date], type nullable logical),
    InFull    = Table.AddColumn(OnTime, "is_in_full",
                  each if [qty_received] = null then null else [qty_received] >= [quantity], type nullable logical),
    OTIF      = Table.AddColumn(InFull, "is_otif",
                  each if [is_on_time] = null then null else [is_on_time] and [is_in_full], type nullable logical),

    // Payment performance (null = not yet paid)
    DaysToPay = Table.AddColumn(OTIF, "days_invoice_to_paid",
                  each if [paid_date] = null then null else Duration.Days([paid_date] - [invoice_date]), Int64.Type),
    PaidOnTime = Table.AddColumn(DaysToPay, "is_paid_on_time",
                  each if [paid_date] = null then null else [paid_date] <= [due_date], type nullable logical)
in
    PaidOnTime
