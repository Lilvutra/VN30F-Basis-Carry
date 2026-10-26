# Long VN30 basket / short VN30F1M — basis convergence backtest

Window 2021-06 → 2026-10. Front-month roll via futurecode='VN30F1M'. Basket = equal-weight VN30 members (latest snapshot), adjusted closes. Costs: stock 12bps/side + 10bps sell tax + futures 3bps + slippage 15bps (≈ 11.5 index points/trade).

Basis is negative most of the time (median ≈ −1.3 pts); a +10 entry is a rare event, so trade counts are small by construction.

## Chosen thresholds (entry ≥ +10, exit ≤ +3)

| n trades | win rate | avg gross (pts) | avg cost (pts) | avg net (pts) | total net (pts) | total net (VND) | Sharpe | max DD (VND) | margin calls | forced |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 0.42 | 8.00 | 11.51 | -3.50 | -42.0 | -4,200,546 | -1.52 | -5,542,001 | 0 | 0 |

## Where the gross comes from

gross = basis captured (entry basis − exit basis) + tracking (basket − VN30 over the holding period). Only the first part is the strategy; the second is an unintended bet that the hedge basket beats the index.

| avg basis (pts) | avg tracking (pts) | tracking std (pts) | avg cost (pts) | avg net if tracking were 0 (pts) |
|---|---|---|---|---|
| 14.38 | -6.38 | 14.18 | 11.51 | +2.87 |

## Entry-threshold sweep (the cost curve)

| entry basis | n trades | win rate | avg gross (pts) | avg net (pts) | total net (pts) | total net (VND) |
|---|---|---|---|---|---|---|
| 6 | 29 | 0.21 | 5.50 | -6.12 | -177.4 | -17,744,394 |
| 8 | 13 | 0.23 | 5.77 | -5.77 | -75.0 | -7,497,764 |
| 10 | 12 | 0.42 | 8.00 | -3.50 | -42.0 | -4,200,546 |
| 12 | 4 | 0.50 | 9.00 | -3.89 | -15.5 | -1,554,237 |
| 14 | 2 | 0.00 | -3.21 | -17.26 | -34.5 | -3,451,567 |
| 16 | 1 | 0.00 | -15.73 | -29.64 | -29.6 | -2,964,397 |

## Cost sensitivity (the decision variable)

Gross convergence is held fixed; only the assumed ROUND-TRIP cost in bps of notional changes. Breakeven is where avg net crosses zero.

| round-trip cost (bps) | n trades | avg net (pts) | total net (VND) |
|---|---|---|---|
| 20 | 12 | +4.72 | 5,661,124 |
| 30 | 12 | +3.07 | 3,688,790 |
| 40 | 12 | +1.43 | 1,716,456 |
| 50 | 12 | -0.21 | -255,878 |
| 60 | 12 | -1.86 | -2,228,212 |
| 70 | 12 | -3.50 | -4,200,546 |
| 80 | 12 | -5.14 | -6,172,880 |
| 90 | 12 | -6.79 | -8,145,214 |

## Reading this

Gross points ≈ the basis convergence captured; avg net subtracts the itemised round-trip cost. The strategy only makes money where the entry basis clears that cost with margin, and where convergence actually happens before expiry. The sweep is the point: if no entry threshold turns total net positive, the basis is too thin relative to VN transaction costs — the same cost wall project2/project3 hit intraday, now on a daily convergence trade.

Caveats: fractional shares (real lots of 100 add tracking error); adjusted (total-return) basket vs price index means the result already credits dividends the trader would receive; one position at a time; fill at close.
