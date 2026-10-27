# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 60 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 7 | 2 | +8.78 | +4.39 | +3.98 | +0.41 |
| 2023 | 3 | none | 9 | 2 | +11.35 | +5.68 | +1.02 | +4.65 |
| 2024 | 3 | none | 11 | 5 | +19.39 | +3.88 | +2.09 | +1.79 |
| 2025 | 3 | none | 16 | 6 | +77.74 | +12.96 | +1.85 | +11.11 |
| 2026 | 3 | none | 22 | 6 | +79.89 | +13.32 | +0.85 | +12.46 |

**Stitched OOS: 21 trades, total +197.2 pts (+19.7m VND per contract), mean +9.39, t +2.43, 76% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 45 | +162.8 | +3.62 | +2.01 | 53% |
| 0 | 20% | 30 | +142.9 | +4.76 | +1.97 | 60% |
| 0 | 25% | 36 | +151.5 | +4.21 | +2.05 | 53% |
| 1 | none | 37 | +154.6 | +4.18 | +1.77 | 62% |
| 1 | 20% | 25 | +182.8 | +7.31 | +2.58 | 68% |
| 1 | 25% | 30 | +182.8 | +6.09 | +2.51 | 67% |
| 2 | none | 32 | +180.1 | +5.63 | +2.08 | 75% |
| 2 | 20% | 23 | +181.3 | +7.88 | +2.62 | 70% |
| 2 | 25% | 26 | +196.5 | +7.56 | +2.86 | 73% |
| 3 | none | 28 | +292.9 | +10.46 | +3.44 | 82% |
| 3 | 20% | 19 | +241.7 | +12.72 | +3.21 | 79% |
| 3 | 25% | 22 | +271.5 | +12.34 | +3.53 | 82% |
| 4 | none | 22 | +235.2 | +10.69 | +2.81 | 77% |
| 4 | 20% | 14 | +207.2 | +14.80 | +2.89 | 79% |
| 4 | 25% | 17 | +221.1 | +13.01 | +2.85 | 76% |
| 5 | none | 20 | +220.9 | +11.04 | +2.60 | 70% |
| 5 | 20% | 13 | +200.1 | +15.39 | +2.78 | 69% |
| 5 | 25% | 16 | +214.7 | +13.42 | +2.75 | 69% |

## Lifecycle of the OOS trades

edge (exec − bar) +1.75, tracking until expiry +7.64 (std 17.62), cash +12.86, carry 3.48. Margin top-up on the short future: mean 33.5 pts, max 172.9 pts (17.3m VND per contract).

Open (unexpired) trades excluded: 24 combo-rows.
