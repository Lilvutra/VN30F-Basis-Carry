# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 30 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 7 | 2 | +7.23 | +3.62 | +2.99 | +0.63 |
| 2023 | 3 | none | 9 | 2 | +11.80 | +5.90 | +1.25 | +4.65 |
| 2024 | 3 | none | 11 | 5 | +21.06 | +4.21 | +2.42 | +1.79 |
| 2025 | 3 | none | 16 | 6 | +77.39 | +12.90 | +1.79 | +11.11 |
| 2026 | 3 | none | 22 | 6 | +83.67 | +13.95 | +1.48 | +12.46 |

**Stitched OOS: 21 trades, total +201.2 pts (+20.1m VND per contract), mean +9.58, t +2.49, 81% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 45 | +175.0 | +3.89 | +2.16 | 60% |
| 0 | 20% | 30 | +149.3 | +4.98 | +2.04 | 67% |
| 0 | 25% | 36 | +153.2 | +4.25 | +2.05 | 58% |
| 1 | none | 37 | +170.1 | +4.60 | +1.94 | 62% |
| 1 | 20% | 25 | +185.7 | +7.43 | +2.58 | 68% |
| 1 | 25% | 30 | +188.6 | +6.29 | +2.57 | 67% |
| 2 | none | 32 | +189.6 | +5.93 | +2.20 | 75% |
| 2 | 20% | 23 | +183.4 | +7.97 | +2.61 | 70% |
| 2 | 25% | 26 | +199.8 | +7.69 | +2.88 | 73% |
| 3 | none | 28 | +294.7 | +10.52 | +3.47 | 86% |
| 3 | 20% | 19 | +238.3 | +12.54 | +3.17 | 84% |
| 3 | 25% | 22 | +269.8 | +12.26 | +3.49 | 86% |
| 4 | none | 22 | +248.4 | +11.29 | +3.01 | 77% |
| 4 | 20% | 14 | +210.1 | +15.01 | +2.91 | 79% |
| 4 | 25% | 17 | +231.1 | +13.59 | +3.01 | 76% |
| 5 | none | 20 | +239.0 | +11.95 | +2.88 | 70% |
| 5 | 20% | 13 | +204.6 | +15.74 | +2.82 | 69% |
| 5 | 25% | 16 | +227.1 | +14.20 | +2.95 | 69% |

## Lifecycle of the OOS trades

edge (exec − bar) +1.92, tracking until expiry +7.66 (std 17.60), cash +13.05, carry 3.48. Margin top-up on the short future: mean 33.5 pts, max 172.9 pts (17.3m VND per contract).

Open (unexpired) trades excluded: 24 combo-rows.
