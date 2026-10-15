-- project5 — daily split/dividend-ADJUSTED close + volume for every stock that
-- has ever been a VN30 member.
--
-- Backtest basket leg: on entry we buy an equal-weight basket of the then-current
-- VN30 members at their adjusted close. Adjusted prices are used on purpose:
-- they fold in splits AND cash dividends, i.e. they are total-return. That is the
-- correct basis for the hedge, because the index/futures are price-based and drop
-- on the ex-dividend day while the basket holder still receives the cash — the
-- short futures gains from that drop, so the dividend is realised income, not
-- double counting. (Using raw close here would understate the basket leg.)
--
-- Volume is pulled so the backtest can optionally refuse to build a basket from
-- illiquid names (you cannot buy 1/30th of a contract in a stock with no trades).
WITH members AS (
    SELECT DISTINCT tickersymbol
    FROM quote.vn30
)
SELECT
    ac.datetime                 AS date,
    ac.tickersymbol             AS ticker,
    ac.price::double precision  AS adj_close,
    dv.quantity                 AS volume
FROM quote.adjclose ac
JOIN members m ON m.tickersymbol = ac.tickersymbol
LEFT JOIN quote.dailyvolume dv
       ON dv.tickersymbol = ac.tickersymbol AND dv.datetime = ac.datetime
WHERE ac.datetime >= date '2021-01-01'
  AND ac.price > 0
ORDER BY ac.tickersymbol, ac.datetime;
