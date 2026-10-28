# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 5 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). Entries need ≥ 0 days to expiry. net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 8 | 7 | +23.95 | +3.42 | +2.23 | +1.19 |
| 2023 | 3 | none | 15 | 6 | +21.09 | +3.51 | +2.29 | +1.22 |
| 2024 | 3 | none | 21 | 9 | +31.30 | +3.48 | +2.25 | +1.23 |
| 2025 | 3 | none | 30 | 10 | +90.31 | +9.03 | +1.90 | +7.13 |
| 2026 | 3 | none | 40 | 9 | +74.93 | +8.33 | +1.74 | +6.59 |

**Stitched OOS: 41 trades, total +241.6 pts (+24.2m VND per contract), mean +5.89, t +2.84, 78% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 62 | +126.2 | +2.03 | +1.43 | 47% |
| 0 | 20% | 46 | +89.5 | +1.95 | +1.10 | 46% |
| 0 | 25% | 55 | +93.5 | +1.70 | +1.11 | 40% |
| 1 | none | 59 | +180.7 | +3.06 | +1.99 | 56% |
| 1 | 20% | 44 | +177.1 | +4.03 | +2.23 | 57% |
| 1 | 25% | 53 | +174.3 | +3.29 | +2.15 | 55% |
| 2 | none | 53 | +220.1 | +4.15 | +2.52 | 72% |
| 2 | 20% | 40 | +203.9 | +5.10 | +2.67 | 70% |
| 2 | 25% | 46 | +221.7 | +4.82 | +2.90 | 70% |
| 3 | none | 49 | +333.4 | +6.80 | +3.68 | 82% |
| 3 | 20% | 36 | +275.7 | +7.66 | +3.37 | 81% |
| 3 | 25% | 40 | +291.8 | +7.29 | +3.41 | 80% |
| 4 | none | 43 | +315.1 | +7.33 | +3.65 | 86% |
| 4 | 20% | 31 | +267.9 | +8.64 | +3.43 | 87% |
| 4 | 25% | 34 | +285.0 | +8.38 | +3.47 | 85% |
| 5 | none | 33 | +309.5 | +9.38 | +3.72 | 88% |
| 5 | 20% | 24 | +260.9 | +10.87 | +3.38 | 88% |
| 5 | 25% | 26 | +279.5 | +10.75 | +3.56 | 88% |

## Lifecycle of the OOS trades

edge (exec − bar) +2.05, tracking until expiry +3.84 (std 13.33), cash +7.89, carry 2.00. Margin top-up on the short future: mean 21.2 pts, max 175.4 pts (17.5m VND per contract).

## OOS trades by days to expiry at entry

| days to expiry | trades | total | mean | edge | track |
|---|---|---|---|---|---|
| 0 (expiry day) | 4 | +10.0 | +2.51 | +2.35 | +0.15 |
| 1–6 | 15 | +33.2 | +2.21 | +1.97 | +0.24 |
| ≥ 7 | 22 | +198.3 | +9.02 | +2.06 | +6.96 |

Open (unexpired) trades excluded: 6 combo-rows.
