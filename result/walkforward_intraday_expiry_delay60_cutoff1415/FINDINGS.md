# Walk-forward of the intraday arbitrage rule (steps 5–6)

Fees 17 bps round trip, carry rate 4.5%, fill 60 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the VN30 close, basket at its closes, dividends in). Entries need ≥ 0 days to expiry, signals up to 14:15. net = cash − carry; track = net − (exec − bar).

## Out-of-sample (anchored yearly; pick = best total net in all earlier years)

| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |
|---|---|---|---|---|---|---|---|---|
| 2022 | 3 | none | 8 | 7 | +20.48 | +2.93 | +2.16 | +0.77 |
| 2023 | 3 | none | 15 | 6 | +18.37 | +3.06 | +1.25 | +1.82 |
| 2024 | 3 | none | 21 | 8 | +30.47 | +3.81 | +2.03 | +1.78 |
| 2025 | 3 | none | 29 | 10 | +85.56 | +8.56 | +1.41 | +7.15 |
| 2026 | 3 | none | 39 | 9 | +68.53 | +7.61 | +1.02 | +6.59 |

**Stitched OOS: 40 trades, total +223.4 pts (+22.3m VND per contract), mean +5.59, t +2.61, 75% positive.**

## Every combo, whole sample (comparison only: not out-of-sample)

| buffer | vol cap | trades | total | mean | t | >0 |
|---|---|---|---|---|---|---|
| 0 | none | 61 | +112.0 | +1.84 | +1.28 | 41% |
| 0 | 20% | 45 | +80.1 | +1.78 | +1.00 | 42% |
| 0 | 25% | 54 | +92.7 | +1.72 | +1.12 | 39% |
| 1 | none | 56 | +158.9 | +2.84 | +1.81 | 54% |
| 1 | 20% | 41 | +158.8 | +3.87 | +2.07 | 54% |
| 1 | 25% | 50 | +153.6 | +3.07 | +1.92 | 50% |
| 2 | none | 52 | +226.7 | +4.36 | +2.69 | 73% |
| 2 | 20% | 38 | +195.7 | +5.15 | +2.68 | 71% |
| 2 | 25% | 45 | +214.6 | +4.77 | +2.88 | 71% |
| 3 | none | 48 | +323.6 | +6.74 | +3.54 | 79% |
| 3 | 20% | 34 | +271.9 | +8.00 | +3.26 | 76% |
| 3 | 25% | 39 | +295.2 | +7.57 | +3.46 | 77% |
| 4 | none | 42 | +311.0 | +7.40 | +3.59 | 81% |
| 4 | 20% | 30 | +256.1 | +8.54 | +3.22 | 83% |
| 4 | 25% | 33 | +287.5 | +8.71 | +3.54 | 85% |
| 5 | none | 31 | +278.4 | +8.98 | +3.27 | 77% |
| 5 | 20% | 23 | +245.1 | +10.66 | +3.14 | 78% |
| 5 | 25% | 25 | +265.8 | +10.63 | +3.38 | 80% |

## Lifecycle of the OOS trades

edge (exec − bar) +1.55, tracking until expiry +4.03 (std 13.44), cash +7.57, carry 1.99. Margin top-up on the short future: mean 20.6 pts, max 172.9 pts (17.3m VND per contract).

## OOS trades by days to expiry at entry

| days to expiry | trades | total | mean | edge | track |
|---|---|---|---|---|---|
| 0 (expiry day) | 6 | +7.4 | +1.24 | +1.23 | +0.01 |
| 1–6 | 12 | +20.7 | +1.72 | +1.28 | +0.44 |
| ≥ 7 | 22 | +195.3 | +8.88 | +1.79 | +7.09 |

Open (unexpired) trades excluded: 6 combo-rows.
