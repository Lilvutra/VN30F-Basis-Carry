# Capacity with partial fills

Events: 120 triggers from result/intraday_fund_buffer3_expiry/events.csv, 5 s delay, 2023-01-03 → 2026-10-14 (3.78 years).

## Fill rate and edge by size (all events)

| k | fully fillable | edge if filled | futures leg short |
|---|---|---|---|
| 1 | 100% | +2.11 | 0% |
| 2 | 100% | +2.07 | 0% |
| 3 | 98% | +2.04 | 0% |
| 5 | 96% | +2.00 | 1% |
| 7 | 94% | +1.96 | 1% |
| 10 | 92% | +1.94 | 2% |
| 15 | 82% | +1.90 | 6% |
| 20 | 78% | +1.80 | 10% |
| 30 | 62% | +1.89 | 20% |
| 40 | 52% | +1.89 | 28% |
| 50 | 46% | +1.92 | 33% |
| 75 | 29% | +1.71 | 46% |
| 100 | 18% | +1.52 | 62% |

## Profit by target size (trade the best k ≤ target)

| policy | target | traded/events | avg k | edge (k-wtd) | P&L m VND/yr | peak contracts | capital bn | %/yr above carry |
|---|---|---|---|---|---|---|---|---|
| every | 10 | 115/120 | 9.3 | +2.11 | 59.4 | 113 | 28.14 | 0.21% |
| every | 20 | 115/120 | 16.8 | +2.03 | 103.9 | 220 | 54.78 | 0.19% |
| every | 50 | 115/120 | 32.8 | +1.90 | 189.5 | 483 | 120.26 | 0.16% |
| every | 100 | 115/120 | 44.6 | +1.76 | 238.5 | 708 | 176.28 | 0.14% |
| first | 10 | 34/34 | 9.2 | +2.07 | 17.1 | 10 | 2.49 | 0.69% |
| first | 20 | 34/34 | 16.8 | +2.01 | 30.5 | 20 | 4.98 | 0.61% |
| first | 50 | 34/34 | 32.7 | +1.90 | 55.9 | 50 | 12.45 | 0.45% |
| first | 100 | 34/34 | 45.2 | +1.84 | 74.8 | 100 | 24.90 | 0.30% |

Capital = peak open contracts × max VN30 × multiplier × (1 + 0.2 margin).
