# Long VN30 basket / short VN30F1M — basis convergence backtest

Window 2021-06 → 2026-10. Front-month roll via futurecode='VN30F1M'. Basket = equal-weight VN30 members (latest snapshot), adjusted closes. Costs: stock 12bps/side + 10bps sell tax + futures 3bps + slippage 15bps (≈ 11.4 index points/trade).

Basis is negative most of the time (median ≈ −1.3 pts); a +10 entry is a rare event, so trade counts are small by construction.

## Chosen thresholds (entry ≥ +10, exit ≤ +3)

| n trades | win rate | avg gross (pts) | avg cost (pts) | avg net (pts) | total net (pts) | total net (VND) | Sharpe | max DD (VND) | margin calls | forced |
|---|---|---|---|---|---|---|---|---|---|---|
| 11 | 0.45 | 8.45 | 11.35 | -2.90 | -32.0 | -3,195,368 | -1.21 | -4,536,824 | 0 | 0 |

## Entry-threshold sweep (the cost curve)

| entry basis | n trades | win rate | avg gross (pts) | avg net (pts) | total net (pts) | total net (VND) |
|---|---|---|---|---|---|---|
| 6 | 28 | 0.25 | 7.10 | -4.47 | -125.0 | -12,503,217 |
| 8 | 12 | 0.25 | 5.99 | -5.41 | -64.9 | -6,492,586 |
| 10 | 11 | 0.45 | 8.45 | -2.90 | -32.0 | -3,195,368 |
| 12 | 4 | 0.50 | 9.00 | -3.89 | -15.5 | -1,554,237 |
| 14 | 2 | 0.00 | -3.21 | -17.26 | -34.5 | -3,451,567 |
| 16 | 1 | 0.00 | -15.73 | -29.64 | -29.6 | -2,964,397 |

## Cost sensitivity (the decision variable)

Gross convergence is held fixed; only the assumed ROUND-TRIP cost in bps of notional changes. Breakeven is where avg net crosses zero.

| round-trip cost (bps) | n trades | avg net (pts) | total net (VND) |
|---|---|---|---|
| 20 | 11 | +5.21 | 5,726,017 |
| 30 | 11 | +3.58 | 3,941,740 |
| 40 | 11 | +1.96 | 2,157,463 |
| 50 | 11 | +0.34 | 373,186 |
| 60 | 11 | -1.28 | -1,411,091 |
| 70 | 11 | -2.90 | -3,195,368 |
| 80 | 11 | -4.53 | -4,979,645 |
| 90 | 11 | -6.15 | -6,763,922 |

## Reading this

Gross points ≈ the basis convergence captured; avg net subtracts the itemised round-trip cost. The strategy only makes money where the entry basis clears that cost with margin, and where convergence actually happens before expiry. The sweep is the point: if no entry threshold turns total net positive, the basis is too thin relative to VN transaction costs — the same cost wall project2/project3 hit intraday, now on a daily convergence trade.

Caveats: fractional shares (real lots of 100 add tracking error); adjusted (total-return) basket vs price index means the result already credits dividends the trader would receive; one position at a time; fill at close.
