# Long VN30 basket / short VN30F1M — basis convergence backtest

Window 2021-06 → 2026-10. Front-month roll via futurecode='VN30F1M'. Basket = the E1VFVN30 ETF, adjusted closes. Costs: stock 12bps/side + 10bps sell tax + futures 3bps + slippage 15bps (≈ 11.5 index points/trade).

Basis is negative most of the time (median ≈ −1.3 pts); a +10 entry is a rare event, so trade counts are small by construction.

## Chosen thresholds (entry ≥ +10, exit ≤ +3)

| n trades | win rate | avg gross (pts) | avg cost (pts) | avg net (pts) | total net (pts) | total net (VND) | Sharpe | max DD (VND) | margin calls | forced |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 0.50 | 9.38 | 11.51 | -2.13 | -25.6 | -2,555,871 | -0.54 | -4,765,684 | 0 | 0 |

## Where the gross comes from

gross = basis captured (entry basis − exit basis) + tracking (basket − VN30 over the holding period). Only the first part is the strategy; the second is an unintended bet that the hedge basket beats the index.

| avg basis (pts) | avg tracking (pts) | tracking std (pts) | avg cost (pts) | avg net if tracking were 0 (pts) |
|---|---|---|---|---|
| 14.38 | -5.00 | 16.63 | 11.51 | +2.87 |

## Entry-threshold sweep (the cost curve)

| entry basis | n trades | win rate | avg gross (pts) | avg net (pts) | total net (pts) | total net (VND) |
|---|---|---|---|---|---|---|
| 6 | 28 | 0.32 | 6.11 | -5.62 | -157.4 | -15,736,291 |
| 8 | 13 | 0.54 | 10.73 | -0.80 | -10.4 | -1,044,415 |
| 10 | 12 | 0.50 | 9.38 | -2.13 | -25.6 | -2,555,871 |
| 12 | 4 | 0.75 | 11.11 | -1.78 | -7.1 | -710,825 |
| 14 | 2 | 1.00 | 22.96 | 8.91 | 17.8 | 1,782,842 |
| 16 | 1 | 1.00 | 16.21 | 2.29 | 2.3 | 229,015 |

## Cost sensitivity (the decision variable)

Gross convergence is held fixed; only the assumed ROUND-TRIP cost in bps of notional changes. Breakeven is where avg net crosses zero.

| round-trip cost (bps) | n trades | avg net (pts) | total net (VND) |
|---|---|---|---|
| 20 | 12 | +6.09 | 7,305,799 |
| 30 | 12 | +4.44 | 5,333,465 |
| 40 | 12 | +2.80 | 3,361,131 |
| 50 | 12 | +1.16 | 1,388,797 |
| 60 | 12 | -0.49 | -583,537 |
| 70 | 12 | -2.13 | -2,555,871 |
| 80 | 12 | -3.77 | -4,528,205 |
| 90 | 12 | -5.42 | -6,500,539 |

## Reading this

Gross points ≈ the basis convergence captured; avg net subtracts the itemised round-trip cost. The strategy only makes money where the entry basis clears that cost with margin, and where convergence actually happens before expiry. The sweep is the point: if no entry threshold turns total net positive, the basis is too thin relative to VN transaction costs — the same cost wall project2/project3 hit intraday, now on a daily convergence trade.

Caveats: fractional shares (real lots of 100 add tracking error); adjusted (total-return) basket vs price index means the result already credits dividends the trader would receive; one position at a time; fill at close.
