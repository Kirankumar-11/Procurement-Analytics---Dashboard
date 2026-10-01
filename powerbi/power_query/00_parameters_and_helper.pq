// ===== Query: DataFolder (create as a Parameter: Home > Manage Parameters > New) =====
// Type: Text | Current value: full path to the data/raw folder, WITH trailing backslash
// e.g.  C:\Users\you\procurement-analytics-powerbi\data\raw\
"C:\path\to\procurement-analytics-powerbi\data\raw\"

// ===== Query: fnLoadCsv (blank query, set "Enable load" OFF) =====
(fileName as text) as table =>
let
    Source = Csv.Document(File.Contents(DataFolder & fileName & ".csv"),
                [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Promoted
