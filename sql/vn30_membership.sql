-- project5 — VN30 index membership snapshots.
--
-- The hedge basket must be VN30-like for the basis to be the thing we capture.
-- `quote.vn30` stores membership as snapshots (30 tickers per date, roughly
-- semi-annual reviews). The backtest uses the LATEST snapshot on or before a
-- trade date, so a basket is never built from names that were not yet (or no
-- longer) in the index — avoiding survivorship bias.
SELECT
    datetime        AS date,
    tickersymbol    AS ticker
FROM quote.vn30
ORDER BY datetime, tickersymbol;
