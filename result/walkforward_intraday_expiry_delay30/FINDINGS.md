# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 30 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). Entries need ≥ 0 days to expiry. net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 8 | 7 | +20.96 | +2.99 | +2.16 | +0.83 |
| 2023 | 3 | none | 15 | 6 | +15.75 | +2.62 | +1.40 | +1.22 |
| 2024 | 3 | none | 21 | 9 | +29.28 | +3.25 | +2.01 | +1.24 |
| 2025 | 3 | none | 30 | 10 | +85.81 | +8.58 | +1.45 | +7.13 |
| 2026 | 3 | none | 40 | 9 | +72.52 | +8.06 | +1.47 | +6.59 |

**Stitched OOS: 41 trades, total +224.3 pts (+22.4m VND per contract), mean +5.47, t +2.59, 76% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 62 | +117.9 | +1.90 | +1.36 | 48% |
| 0 | 20% | 46 | +86.4 | +1.88 | +1.07 | 50% |
| 0 | 25% | 55 | +89.2 | +1.62 | +1.09 | 44% |
| 1 | none | 59 | +161.7 | +2.74 | +1.77 | 56% |
| 1 | 20% | 44 | +172.6 | +3.92 | +2.22 | 57% |
| 1 | 25% | 53 | +165.4 | +3.12 | +2.08 | 53% |
| 2 | none | 53 | +203.5 | +3.84 | +2.28 | 72% |
| 2 | 20% | 40 | +193.5 | +4.84 | +2.58 | 70% |
| 2 | 25% | 46 | +205.8 | +4.47 | +2.75 | 70% |
| 3 | none | 49 | +321.5 | +6.56 | +3.48 | 80% |
| 3 | 20% | 36 | +271.1 | +7.53 | +3.26 | 78% |
| 3 | 25% | 40 | +284.0 | +7.10 | +3.28 | 78% |
| 4 | none | 43 | +298.8 | +6.95 | +3.35 | 81% |
| 4 | 20% | 31 | +266.5 | +8.60 | +3.33 | 87% |
| 4 | 25% | 34 | +265.5 | +7.81 | +3.12 | 82% |
| 5 | none | 33 | +282.5 | +8.56 | +3.26 | 76% |
| 5 | 20% | 24 | +257.9 | +10.74 | +3.26 | 79% |
| 5 | 25% | 26 | +258.9 | +9.96 | +3.17 | 77% |

## Lifecycle of the OOS trades

edge (exec − bar) +1.69, tracking until expiry +3.78 (std 13.37), cash +7.47, carry 2.00. Margin top-up on the short future: mean 21.1 pts, max 172.9 pts (17.3m VND per contract).

## OOS trades by days to expiry at entry

| days to expiry | trades | total | mean | edge | track |
|---|---|---|---|---|---|
| 0 (expiry day) | 4 | +7.5 | +1.87 | +1.71 | +0.15 |
| 1–6 | 15 | +25.3 | +1.69 | +1.44 | +0.25 |
| ≥ 7 | 22 | +191.5 | +8.71 | +1.86 | +6.84 |

Open (unexpired) trades excluded: 6 combo-rows.
