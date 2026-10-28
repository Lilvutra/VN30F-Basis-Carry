# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 60 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). Entries need ≥ 0 days to expiry. net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 8 | 7 | +20.48 | +2.93 | +2.16 | +0.77 |
| 2023 | 3 | none | 15 | 6 | +11.35 | +1.89 | +0.67 | +1.22 |
| 2024 | 3 | none | 21 | 9 | +23.06 | +2.56 | +1.32 | +1.24 |
| 2025 | 3 | none | 30 | 10 | +85.57 | +8.56 | +1.43 | +7.13 |
| 2026 | 3 | none | 40 | 9 | +68.53 | +7.61 | +1.02 | +6.59 |

**Stitched OOS: 41 trades, total +209.0 pts (+20.9m VND per contract), mean +5.10, t +2.40, 71% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 62 | +105.4 | +1.70 | +1.22 | 42% |
| 0 | 20% | 46 | +79.3 | +1.72 | +0.99 | 43% |
| 0 | 25% | 55 | +86.1 | +1.57 | +1.06 | 40% |
| 1 | none | 59 | +138.2 | +2.34 | +1.52 | 54% |
| 1 | 20% | 44 | +163.7 | +3.72 | +2.12 | 55% |
| 1 | 25% | 53 | +150.8 | +2.84 | +1.90 | 51% |
| 2 | none | 53 | +195.2 | +3.68 | +2.18 | 75% |
| 2 | 20% | 40 | +193.8 | +4.85 | +2.62 | 72% |
| 2 | 25% | 46 | +203.7 | +4.43 | +2.75 | 72% |
| 3 | none | 49 | +308.2 | +6.29 | +3.31 | 76% |
| 3 | 20% | 36 | +267.1 | +7.42 | +3.18 | 72% |
| 3 | 25% | 40 | +276.3 | +6.91 | +3.16 | 72% |
| 4 | none | 43 | +277.1 | +6.44 | +3.07 | 77% |
| 4 | 20% | 31 | +256.1 | +8.26 | +3.19 | 81% |
| 4 | 25% | 34 | +246.4 | +7.25 | +2.86 | 76% |
| 5 | none | 33 | +261.3 | +7.92 | +2.98 | 76% |
| 5 | 20% | 24 | +252.6 | +10.52 | +3.22 | 79% |
| 5 | 25% | 26 | +245.4 | +9.44 | +2.99 | 77% |

## Lifecycle of the OOS trades

edge (exec − bar) +1.33, tracking until expiry +3.77 (std 13.38), cash +7.10, carry 2.00. Margin top-up on the short future: mean 21.1 pts, max 172.9 pts (17.3m VND per contract).

## OOS trades by days to expiry at entry

| days to expiry | trades | total | mean | edge | track |
|---|---|---|---|---|---|
| 0 (expiry day) | 4 | +6.3 | +1.58 | +1.43 | +0.15 |
| 1–6 | 15 | +14.7 | +0.98 | +0.73 | +0.25 |
| ≥ 7 | 22 | +187.9 | +8.54 | +1.72 | +6.82 |

Open (unexpired) trades excluded: 6 combo-rows.
