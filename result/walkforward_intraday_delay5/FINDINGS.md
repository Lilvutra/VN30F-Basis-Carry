# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 5 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). Entries need ≥ 7 days to expiry. net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 7 | 2 | +7.20 | +3.60 | +1.70 | +1.90 |
| 2023 | 3 | none | 9 | 2 | +15.89 | +7.94 | +3.29 | +4.65 |
| 2024 | 3 | none | 11 | 5 | +21.19 | +4.24 | +2.45 | +1.79 |
| 2025 | 3 | none | 16 | 6 | +79.59 | +13.26 | +2.16 | +11.11 |
| 2026 | 3 | none | 22 | 7 | +74.48 | +10.64 | +1.44 | +9.20 |

**Stitched OOS: 22 trades, total +198.3 pts (+19.8m VND per contract), mean +9.02, t +2.43, 77% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 47 | +164.2 | +3.49 | +1.94 | 53% |
| 0 | 20% | 32 | +135.8 | +4.24 | +1.77 | 59% |
| 0 | 25% | 38 | +138.7 | +3.65 | +1.75 | 50% |
| 1 | none | 38 | +181.7 | +4.78 | +2.06 | 63% |
| 1 | 20% | 26 | +185.4 | +7.13 | +2.49 | 69% |
| 1 | 25% | 31 | +190.7 | +6.15 | +2.52 | 68% |
| 2 | none | 33 | +191.6 | +5.81 | +2.24 | 76% |
| 2 | 20% | 24 | +184.4 | +7.68 | +2.51 | 71% |
| 2 | 25% | 27 | +203.5 | +7.54 | +2.78 | 74% |
| 3 | none | 29 | +287.5 | +9.92 | +3.34 | 83% |
| 3 | 20% | 20 | +229.0 | +11.45 | +2.96 | 80% |
| 3 | 25% | 23 | +261.6 | +11.37 | +3.28 | 83% |
| 4 | none | 23 | +246.6 | +10.72 | +3.00 | 78% |
| 4 | 20% | 15 | +194.4 | +12.96 | +2.60 | 73% |
| 4 | 25% | 18 | +231.9 | +12.88 | +3.02 | 78% |
| 5 | none | 21 | +252.3 | +12.02 | +3.12 | 81% |
| 5 | 20% | 14 | +198.6 | +14.18 | +2.69 | 79% |
| 5 | 25% | 17 | +237.8 | +13.99 | +3.15 | 82% |

## Lifecycle of the OOS trades

edge (exec − bar) +2.06, tracking until expiry +6.96 (std 17.53), cash +12.51, carry 3.50. Margin top-up on the short future: mean 33.0 pts, max 175.4 pts (17.5m VND per contract).

## OOS trades by days to expiry at entry

| days to expiry | trades | total | mean | edge | track |
|---|---|---|---|---|---|
| ≥ 7 | 22 | +198.3 | +9.02 | +2.06 | +6.96 |

Open (unexpired) trades excluded: 6 combo-rows.
