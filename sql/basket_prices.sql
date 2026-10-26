-- project5 — daily split/dividend-ADJUSTED close, RAW close and volume for every
-- stock that has ever been a VN30 member, plus the VN30 index itself and the
-- E1VFVN30 ETF.
--
-- Backtest basket leg: on entry we buy a basket of the then-current VN30 members
-- at their adjusted close. Adjusted prices are used on purpose: they fold in
-- splits AND cash dividends, i.e. they are total-return. That is the correct
-- basis for the hedge, because the index/futures are price-based and drop on the
-- ex-dividend day while the basket holder still receives the cash — the short
-- futures gains from that drop, so the dividend is realised income, not double
-- counting. (Using raw close here would understate the basket leg.)
--
-- Raw close is pulled too: the VN30 index is a PRICE index, so the "fit" basket
-- estimates its weights by regressing index returns on raw-close returns.
-- 'VN30' (index, no adjclose → falls back to close) and 'E1VFVN30' (the ETF
-- hedge alternative) ride along in the same file.
--
-- Adjusted open (09:15 ATO) is pulled for next-open execution.
--
-- Volume is pulled so the backtest can optionally refuse to build a basket from
-- illiquid names (you cannot buy 1/30th of a contract in a stock with no trades).
WITH members AS (
    SELECT DISTINCT tickersymbol FROM quote.vn30
    UNION SELECT 'VN30'
    UNION SELECT 'E1VFVN30'
)
SELECT
    c.datetime                                          AS date,
    c.tickersymbol                                      AS ticker,
    COALESCE(ac.price, c.price)::double precision       AS adj_close,
    c.price::double precision                           AS close,
    COALESCE(ao.price, o.price)::double precision       AS adj_open,
    dv.quantity                                         AS volume
FROM quote.close c
JOIN members m ON m.tickersymbol = c.tickersymbol
LEFT JOIN quote.adjclose ac
       ON ac.tickersymbol = c.tickersymbol AND ac.datetime = c.datetime
LEFT JOIN quote.adjopen ao
       ON ao.tickersymbol = c.tickersymbol AND ao.datetime = c.datetime
LEFT JOIN quote.open o
       ON o.tickersymbol = c.tickersymbol AND o.datetime = c.datetime
LEFT JOIN quote.dailyvolume dv
       ON dv.tickersymbol = c.tickersymbol AND dv.datetime = c.datetime
WHERE c.datetime >= date '2020-06-01'
  AND c.price > 0
ORDER BY c.tickersymbol, c.datetime;
