# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 5 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 7 | 2 | +7.20 | +3.60 | +1.70 | +1.90 |
| 2023 | 3 | none | 9 | 2 | +15.89 | +7.94 | +3.29 | +4.65 |
| 2024 | 3 | none | 11 | 5 | +21.19 | +4.24 | +2.45 | +1.79 |
| 2025 | 3 | none | 16 | 6 | +79.59 | +13.26 | +2.16 | +11.11 |
| 2026 | 3 | none | 22 | 6 | +84.23 | +14.04 | +1.57 | +12.46 |

**Stitched OOS: 21 trades, total +208.1 pts (+20.8m VND per contract), mean +9.91, t +2.62, 81% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 45 | +177.3 | +3.94 | +2.14 | 56% |
| 0 | 20% | 30 | +148.8 | +4.96 | +2.00 | 63% |
| 0 | 25% | 36 | +151.8 | +4.22 | +1.97 | 53% |
| 1 | none | 37 | +187.9 | +5.08 | +2.15 | 65% |
| 1 | 20% | 25 | +191.7 | +7.67 | +2.62 | 72% |
| 1 | 25% | 30 | +197.0 | +6.57 | +2.64 | 70% |
| 2 | none | 32 | +202.5 | +6.33 | +2.41 | 78% |
| 2 | 20% | 23 | +195.3 | +8.49 | +2.76 | 74% |
| 2 | 25% | 26 | +214.4 | +8.25 | +3.04 | 77% |
| 3 | none | 28 | +297.3 | +10.62 | +3.56 | 86% |
| 3 | 20% | 19 | +238.8 | +12.57 | +3.22 | 84% |
| 3 | 25% | 22 | +271.3 | +12.33 | +3.54 | 86% |
| 4 | none | 22 | +255.4 | +11.61 | +3.20 | 82% |
| 4 | 20% | 14 | +203.2 | +14.51 | +2.85 | 79% |
| 4 | 25% | 17 | +240.7 | +14.16 | +3.28 | 82% |
| 5 | none | 20 | +256.4 | +12.82 | +3.24 | 85% |
| 5 | 20% | 13 | +202.6 | +15.58 | +2.84 | 85% |
| 5 | 25% | 16 | +241.8 | +15.11 | +3.30 | 88% |

## Lifecycle of the OOS trades

edge (exec − bar) +2.12, tracking until expiry +7.79 (std 17.52), cash +13.39, carry 3.48. Margin top-up on the short future: mean 33.9 pts, max 175.4 pts (17.5m VND per contract).

Open (unexpired) trades excluded: 24 combo-rows.
