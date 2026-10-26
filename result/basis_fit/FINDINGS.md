# Long VN30 basket / short VN30F1M — basis convergence backtest

Window 2021-06 → 2026-10. Front-month roll via futurecode='VN30F1M'. Basket = VN30 members, long-only weights regressed on VN30 returns (trailing window), adjusted closes. Costs: stock 12bps/side + 10bps sell tax + futures 3bps + slippage 15bps (≈ 11.5 index points/trade).

Basis is negative most of the time (median ≈ −1.3 pts); a +10 entry is a rare event, so trade counts are small by construction.

## Chosen thresholds (entry ≥ +10, exit ≤ +3)

| n trades | win rate | avg gross (pts) | avg cost (pts) | avg net (pts) | total net (pts) | total net (VND) | Sharpe | max DD (VND) | margin calls | forced |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 0.58 | 13.08 | 11.51 | 1.57 | 18.9 | 1,887,519 | 0.61 | -1,445,199 | 0 | 0 |

## Where the gross comes from

gross = basis captured (entry basis − exit basis) + tracking (basket − VN30 over the holding period). Only the first part is the strategy; the second is an unintended bet that the hedge basket beats the index.

| avg basis (pts) | avg tracking (pts) | tracking std (pts) | avg cost (pts) | avg net if tracking were 0 (pts) |
|---|---|---|---|---|
| 14.38 | -1.30 | 6.01 | 11.51 | +2.87 |

## Entry-threshold sweep (the cost curve)

| entry basis | n trades | win rate | avg gross (pts) | avg net (pts) | total net (pts) | total net (VND) |
|---|---|---|---|---|---|---|
| 6 | 29 | 0.38 | 8.47 | -3.15 | -91.4 | -9,143,387 |
| 8 | 13 | 0.54 | 11.43 | -0.10 | -1.3 | -133,451 |
| 10 | 12 | 0.58 | 13.08 | 1.57 | 18.9 | 1,887,519 |
| 12 | 4 | 1.00 | 23.54 | 10.65 | 42.6 | 4,259,866 |
| 14 | 2 | 1.00 | 22.20 | 8.16 | 16.3 | 1,631,413 |
| 16 | 1 | 1.00 | 28.46 | 14.54 | 14.5 | 1,454,034 |

## Cost sensitivity (the decision variable)

Gross convergence is held fixed; only the assumed ROUND-TRIP cost in bps of notional changes. Breakeven is where avg net crosses zero.

| round-trip cost (bps) | n trades | avg net (pts) | total net (VND) |
|---|---|---|---|
| 20 | 12 | +9.79 | 11,749,189 |
| 30 | 12 | +8.15 | 9,776,855 |
| 40 | 12 | +6.50 | 7,804,521 |
| 50 | 12 | +4.86 | 5,832,187 |
| 60 | 12 | +3.22 | 3,859,853 |
| 70 | 12 | +1.57 | 1,887,519 |
| 80 | 12 | -0.07 | -84,815 |
| 90 | 12 | -1.71 | -2,057,149 |

## Reading this

Gross points ≈ the basis convergence captured; avg net subtracts the itemised round-trip cost. The strategy only makes money where the entry basis clears that cost with margin, and where convergence actually happens before expiry. The sweep is the point: if no entry threshold turns total net positive, the basis is too thin relative to VN transaction costs — the same cost wall project2/project3 hit intraday, now on a daily convergence trade.

Caveats: fractional shares (real lots of 100 add tracking error); adjusted (total-return) basket vs price index means the result already credits dividends the trader would receive; one position at a time; fill at close.
