# Capacity with partial fills

Events: 69 triggers from result/intraday_fund_buffer3/events.csv, 60 s delay, 2023-01-03 → 2026-10-06 (3.76 years).

## Fill rate and edge by size (all events)

| k | fully fillable | edge if filled | futures leg short |
|---|---|---|---|
| 1 | 100% | +1.72 | 0% |
| 2 | 100% | +1.69 | 0% |
| 3 | 99% | +1.66 | 0% |
| 5 | 97% | +1.62 | 0% |
| 7 | 97% | +1.58 | 0% |
| 10 | 97% | +1.54 | 0% |
| 15 | 90% | +1.44 | 4% |
| 20 | 84% | +1.44 | 6% |
| 30 | 72% | +1.44 | 16% |
| 40 | 57% | +1.49 | 25% |
| 50 | 42% | +1.44 | 36% |
| 75 | 26% | +1.61 | 51% |
| 100 | 19% | +1.26 | 67% |

## Profit by target size (trade the best k ≤ target)

| policy | target | traded/events | avg k | edge (k-wtd) | P&L m VND/yr | peak contracts | capital bn | %/yr above carry |
|---|---|---|---|---|---|---|---|---|
| every | 10 | 64/69 | 9.2 | +1.88 | 29.6 | 113 | 27.59 | 0.11% |
| every | 20 | 64/69 | 17.3 | +1.80 | 53.1 | 213 | 52.01 | 0.10% |
| every | 50 | 64/69 | 33.4 | +1.70 | 96.6 | 483 | 117.95 | 0.08% |
| every | 100 | 64/69 | 45.1 | +1.56 | 119.8 | 758 | 185.10 | 0.06% |
| first | 10 | 19/19 | 8.8 | +2.11 | 9.4 | 10 | 2.44 | 0.38% |
| first | 20 | 19/19 | 16.2 | +2.04 | 16.7 | 20 | 4.88 | 0.34% |
| first | 50 | 19/19 | 28.8 | +1.93 | 28.1 | 50 | 12.21 | 0.23% |
| first | 100 | 19/19 | 34.1 | +1.94 | 33.4 | 100 | 24.42 | 0.14% |

Capital = peak open contracts × max VN30 × multiplier × (1 + 0.2 margin).
