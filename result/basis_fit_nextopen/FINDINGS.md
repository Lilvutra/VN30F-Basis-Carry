# Long VN30 basket / short VN30F1M — basis convergence backtest

Window 2021-06 → 2026-10. Front-month roll via futurecode='VN30F1M'. Basket = VN30 members, long-only weights regressed on VN30 returns (trailing window), adjusted closes. Costs: stock 12bps/side + 10bps sell tax + futures 3bps + slippage 15bps (≈ 11.5 index points/trade).

Basis is negative most of the time (median ≈ −1.3 pts); a +10 entry is a rare event, so trade counts are small by construction.

## Chosen thresholds (entry ≥ +10, exit ≤ +3)

| n trades | win rate | avg gross (pts) | avg cost (pts) | avg net (pts) | total net (pts) | total net (VND) | Sharpe | max DD (VND) | margin calls | forced |
|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 0.08 | 1.16 | 11.53 | -10.38 | -124.5 | -12,452,506 | -3.94 | -12,788,474 | 0 | 0 |

## Where the gross comes from

gross = basis captured (entry basis − exit basis) + tracking (basket − VN30 over the holding period). Only the first part is the strategy; the second is an unintended bet that the hedge basket beats the index.

| avg basis (pts) | avg tracking (pts) | tracking std (pts) | avg cost (pts) | avg net if tracking were 0 (pts) |
|---|---|---|---|---|
| 3.91 | -2.76 | 6.05 | 11.53 | -7.62 |

## Entry-threshold sweep (the cost curve)

| entry basis | n trades | win rate | avg gross (pts) | avg net (pts) | total net (pts) | total net (VND) |
|---|---|---|---|---|---|---|
| 6 | 27 | 0.11 | 3.27 | -8.41 | -227.0 | -22,704,813 |
| 8 | 13 | 0.15 | 2.85 | -8.80 | -114.4 | -11,438,703 |
| 10 | 12 | 0.08 | 1.16 | -10.38 | -124.5 | -12,452,506 |
| 12 | 4 | 0.25 | -0.85 | -13.78 | -55.1 | -5,511,035 |
| 14 | 2 | 0.00 | -1.46 | -15.54 | -31.1 | -3,107,939 |
| 16 | 1 | 0.00 | -0.19 | -14.10 | -14.1 | -1,409,909 |

## Cost sensitivity (the decision variable)

Gross convergence is held fixed; only the assumed ROUND-TRIP cost in bps of notional changes. Breakeven is where avg net crosses zero.

| round-trip cost (bps) | n trades | avg net (pts) | total net (VND) |
|---|---|---|---|
| 20 | 12 | -2.14 | -2,567,806 |
| 30 | 12 | -3.79 | -4,544,746 |
| 40 | 12 | -5.43 | -6,521,686 |
| 50 | 12 | -7.08 | -8,498,626 |
| 60 | 12 | -8.73 | -10,475,566 |
| 70 | 12 | -10.38 | -12,452,506 |
| 80 | 12 | -12.02 | -14,429,446 |
| 90 | 12 | -13.67 | -16,406,386 |

## Reading this

Gross points ≈ the basis convergence captured; avg net subtracts the itemised round-trip cost. The strategy only makes money where the entry basis clears that cost with margin, and where convergence actually happens before expiry. The sweep is the point: if no entry threshold turns total net positive, the basis is too thin relative to VN transaction costs — the same cost wall project2/project3 hit intraday, now on a daily convergence trade.

Caveats: fractional shares (real lots of 100 add tracking error); adjusted (total-return) basket vs price index means the result already credits dividends the trader would receive; one position at a time; fill at close.
