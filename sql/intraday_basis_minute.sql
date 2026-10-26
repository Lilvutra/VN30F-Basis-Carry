-- project5 step-1 intraday check — per-minute basis, front-month future vs VN30.
--
-- For every front-month day (futurecode = 'VN30F1M') and every minute of the
-- session, the LAST matched futures price and the LAST VN30 index print in that
-- minute. This is the "displayed" basis a trader would see on screen; whether it
-- can actually be captured is measured separately from bid/ask quotes.
-- {start} / {end} are filled in by scripts/intraday_check.py, one year per query
-- (the VN30 tick scan is the slow part).
WITH fm AS (
    SELECT datetime AS d, tickersymbol AS c
    FROM quote.futurecontractcode
    WHERE futurecode = 'VN30F1M'
      AND datetime >= date '{start}' AND datetime < date '{end}'
),
fut AS (
    SELECT DISTINCT ON (date_trunc('minute', m.datetime))
           date_trunc('minute', m.datetime) AS minute, fm.c AS contract,
           m.price::double precision AS fut_last
    FROM fm
    JOIN quote.matched m
      ON m.tickersymbol = fm.c
     AND m.datetime >= fm.d AND m.datetime < fm.d + 1
    ORDER BY date_trunc('minute', m.datetime), m.datetime DESC
),
idx AS (
    SELECT DISTINCT ON (date_trunc('minute', m.datetime))
           date_trunc('minute', m.datetime) AS minute,
           m.price::double precision AS vn30
    FROM quote.matched m
    WHERE m.tickersymbol = 'VN30'
      AND m.datetime >= date '{start}' AND m.datetime < date '{end}'
    ORDER BY date_trunc('minute', m.datetime), m.datetime DESC
)
SELECT f.minute, f.contract, f.fut_last, i.vn30
FROM fut f
JOIN idx i USING (minute)
ORDER BY f.minute;
