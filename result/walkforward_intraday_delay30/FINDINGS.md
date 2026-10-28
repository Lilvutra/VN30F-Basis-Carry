# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 30 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 7 | 2 | +7.23 | +3.62 | +2.99 | +0.63 |
| 2023 | 3 | none | 9 | 2 | +11.80 | +5.90 | +1.25 | +4.65 |
| 2024 | 3 | none | 11 | 5 | +21.06 | +4.21 | +2.42 | +1.79 |
| 2025 | 3 | none | 16 | 6 | +77.39 | +12.90 | +1.79 | +11.11 |
| 2026 | 3 | none | 22 | 7 | +74.05 | +10.58 | +1.38 | +9.20 |

**Stitched OOS: 22 trades, total +191.5 pts (+19.2m VND per contract), mean +8.71, t +2.31, 77% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 47 | +160.9 | +3.42 | +1.95 | 57% |
| 0 | 20% | 32 | +135.2 | +4.22 | +1.79 | 62% |
| 0 | 25% | 38 | +139.0 | +3.66 | +1.81 | 55% |
| 1 | none | 38 | +163.3 | +4.30 | +1.85 | 61% |
| 1 | 20% | 26 | +178.9 | +6.88 | +2.44 | 65% |
| 1 | 25% | 31 | +181.9 | +5.87 | +2.44 | 65% |
| 2 | none | 33 | +178.9 | +5.42 | +2.04 | 73% |
| 2 | 20% | 24 | +172.7 | +7.19 | +2.38 | 67% |
| 2 | 25% | 27 | +189.1 | +7.00 | +2.63 | 70% |
| 3 | none | 29 | +285.0 | +9.83 | +3.27 | 83% |
| 3 | 20% | 20 | +228.7 | +11.43 | +2.92 | 80% |
| 3 | 25% | 23 | +260.2 | +11.31 | +3.24 | 83% |
| 4 | none | 23 | +239.6 | +10.42 | +2.82 | 74% |
| 4 | 20% | 15 | +201.3 | +13.42 | +2.66 | 73% |
| 4 | 25% | 18 | +222.2 | +12.35 | +2.79 | 72% |
| 5 | none | 21 | +234.9 | +11.18 | +2.79 | 67% |
| 5 | 20% | 14 | +200.5 | +14.32 | +2.67 | 64% |
| 5 | 25% | 17 | +223.1 | +13.12 | +2.82 | 65% |

## Lifecycle of the OOS trades

edge (exec − bar) +1.86, tracking until expiry +6.84 (std 17.61), cash +12.20, carry 3.50. Margin top-up on the short future: mean 32.7 pts, max 172.9 pts (17.3m VND per contract).

Open (unexpired) trades excluded: 6 combo-rows.
