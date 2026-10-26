-- project5 — continuous VN30 FRONT-MONTH futures series + the VN30 index it settles to.
--
-- Strategy: long a basket of VN30 stocks, short VN30F1M, harvest the basis
-- (futures minus index) as it converges into expiry. This query is the futures
-- leg and the reference index.
--
-- `quote.futurecontractcode` tags every dated contract (VN30F2501, VN30F2502, ...)
-- with its rank code (VN30F1M = front month, VN30F2M = second, VN30F1Q/F2Q =
-- quarterlies) per (ticker, date). Filtering futurecode = 'VN30F1M' gives the
-- front-month contract for each date — the splice the strategy would actually roll.
--
-- Output per (date): the front contract, its close and settlement, open interest,
-- the VN30 index level (basis = fut_close - vn30_index) and the contract expiry
-- (so days-to-expiry, and therefore the expected convergence, can be computed).
--
-- Next-open execution: VN30 `open` is the 09:15 ATO index level, but the futures
-- daily `open` is the 08:45 print, taken while the index is still at yesterday's
-- close. So the futures leg uses `fut_open915` = the first matched trade at or
-- after 09:15:00, the same moment the stock/index ATO prints.
--
-- History starts 2021-06 (first date the rank codes exist). The join to
-- quote.close on the same date drops the placeholder 2030 rows in the mapping table.
SELECT
    f.datetime                   AS date,
    f.tickersymbol               AS contract,
    c.price::double precision    AS fut_close,
    s.price::double precision    AS fut_settle,
    o.quantity                   AS open_interest,
    i.price::double precision    AS vn30_index,
    io.price::double precision   AS vn30_open,
    fo.price::double precision   AS fut_open915,
    t.expdate                    AS expdate
FROM quote.futurecontractcode f
JOIN quote.ticker t
  ON t.tickersymbol = f.tickersymbol
JOIN quote.close c
  ON c.tickersymbol = f.tickersymbol AND c.datetime = f.datetime
JOIN quote.close i
  ON i.tickersymbol = 'VN30' AND i.datetime = f.datetime
LEFT JOIN quote.settlementprice s
  ON s.tickersymbol = f.tickersymbol AND s.datetime = f.datetime
LEFT JOIN quote.oi o
  ON o.tickersymbol = f.tickersymbol AND o.datetime = f.datetime
LEFT JOIN quote.open io
  ON io.tickersymbol = 'VN30' AND io.datetime = f.datetime
LEFT JOIN LATERAL (
    SELECT m.price
    FROM quote.matched m
    WHERE m.tickersymbol = f.tickersymbol
      AND m.datetime >= f.datetime + time '09:15:00'
      AND m.datetime <  f.datetime + time '11:30:00'
    ORDER BY m.datetime
    LIMIT 1
) fo ON true
WHERE f.futurecode = 'VN30F1M'
  AND f.datetime >= date '2021-06-01'
ORDER BY f.datetime;
