# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 60 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 7 | 2 | +8.78 | +4.39 | +3.98 | +0.41 |
| 2023 | 3 | none | 9 | 2 | +11.35 | +5.68 | +1.02 | +4.65 |
| 2024 | 3 | none | 11 | 5 | +19.39 | +3.88 | +2.09 | +1.79 |
| 2025 | 3 | none | 16 | 6 | +77.74 | +12.96 | +1.85 | +11.11 |
| 2026 | 3 | none | 22 | 7 | +70.65 | +10.09 | +0.89 | +9.20 |

**Stitched OOS: 22 trades, total +187.9 pts (+18.8m VND per contract), mean +8.54, t +2.26, 73% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 47 | +146.9 | +3.13 | +1.78 | 51% |
| 0 | 20% | 32 | +127.1 | +3.97 | +1.69 | 56% |
| 0 | 25% | 38 | +135.7 | +3.57 | +1.78 | 50% |
| 1 | none | 38 | +147.4 | +3.88 | +1.67 | 61% |
| 1 | 20% | 26 | +175.6 | +6.76 | +2.43 | 65% |
| 1 | 25% | 31 | +175.6 | +5.67 | +2.37 | 65% |
| 2 | none | 33 | +169.2 | +5.13 | +1.92 | 73% |
| 2 | 20% | 24 | +170.4 | +7.10 | +2.38 | 67% |
| 2 | 25% | 27 | +185.6 | +6.87 | +2.61 | 70% |
| 3 | none | 29 | +283.7 | +9.78 | +3.25 | 79% |
| 3 | 20% | 20 | +232.4 | +11.62 | +2.97 | 75% |
| 3 | 25% | 23 | +262.2 | +11.40 | +3.28 | 78% |
| 4 | none | 23 | +225.1 | +9.79 | +2.61 | 74% |
| 4 | 20% | 15 | +197.0 | +13.13 | +2.60 | 73% |
| 4 | 25% | 18 | +211.0 | +11.72 | +2.61 | 72% |
| 5 | none | 21 | +216.3 | +10.30 | +2.51 | 67% |
| 5 | 20% | 14 | +195.5 | +13.96 | +2.62 | 64% |
| 5 | 25% | 17 | +210.1 | +12.36 | +2.63 | 65% |

## Lifecycle of the OOS trades

edge (exec − bar) +1.72, tracking until expiry +6.82 (std 17.62), cash +12.04, carry 3.50. Margin top-up on the short future: mean 32.7 pts, max 172.9 pts (17.3m VND per contract).

Open (unexpired) trades excluded: 6 combo-rows.
