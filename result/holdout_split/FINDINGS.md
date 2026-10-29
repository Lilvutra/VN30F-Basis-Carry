# Train / validation / test split of the intraday rule

Fees 17 bps round trip, carry 4.5%, fill 5 s after the signal at bid/ask, 1 contract, one position per contract, held to expiry. Periods by entry date, purged: a trade counts only if it expires inside its period.

| period | dates | role |
|---|---|---|
| train | 2021-06-01 → 2023-12-31 | fit the buffer per variant |
| validation | 2024-01-01 → 2024-12-31 | choose the variant |
| test | 2025-01-01 → 2026-10-15 (last expiry) | scored once with the frozen rule |

28 variants × 21 buffers declared before the run; 28 had ≥ 3 train trades, 28 also ≥ 3 validation trades.

## Validation: top 10 variants (buffer fitted on train)

| rule | filters | buffer | train trades | train total | val trades | val total | val mean |
|---|---|---|---|---|---|---|---|
| up to expiry day, signals ≤ 14:15 | 1 | 3 | 21 | +144.7 | 8 | +31.9 | +3.99 |
| up to expiry day, fut spread ≤ 0.5, signals ≤ 14:15 | 2 | 3 | 21 | +139.9 | 8 | +31.9 | +3.99 |
| up to expiry day, vol < 25% when < 7 days, signals ≤ 14:15 | 2 | 3 | 18 | +133.0 | 8 | +31.9 | +3.99 |
| up to expiry day, vol < 25%, signals ≤ 14:15 | 2 | 3 | 15 | +96.3 | 8 | +31.9 | +3.99 |
| up to expiry day, vol < 25% when < 7 days, fut spread ≤ 0.5, signals ≤ 14:15 | 3 | 3 | 18 | +128.3 | 8 | +31.9 | +3.99 |
| up to expiry day, vol < 25%, fut spread ≤ 0.5, signals ≤ 14:15 | 3 | 3 | 15 | +91.5 | 8 | +31.9 | +3.99 |
| up to expiry day | 0 | 3 | 21 | +136.9 | 9 | +31.3 | +3.48 |
| up to expiry day, fut spread ≤ 0.5 | 1 | 3 | 21 | +135.7 | 9 | +31.3 | +3.48 |
| up to expiry day, vol < 25% when < 7 days | 1 | 3 | 18 | +120.9 | 9 | +31.3 | +3.48 |
| up to expiry day, vol < 25% | 1 | 3 | 15 | +84.1 | 9 | +31.3 | +3.48 |

**Chosen: up to expiry day, signals ≤ 14:15; buffer refitted on train + validation = 3 (29 trades, +176.6).**

## Test (scored once)

| delay | trades | total | mean | t | >0 |
|---|---|---|---|---|---|
| 5 s | 19 | +165.9 | +8.73 | +2.06 | 74% |
| 30 s | 19 | +158.5 | +8.34 | +1.93 | 74% |
| 60 s | 19 | +154.1 | +8.11 | +1.88 | 74% |

Test at 5 s: +16.6m VND per contract over the period; edge (exec − bar) +1.85 (t +6.1), tracking +6.88. Open trades not yet expired: 0.

For comparison only (picked after seeing 2022–2026): the earlier adopted rule (up to expiry day, buffer 3, no filters) on the same test period: 19 trades, +165.2, mean +8.70.

Caveat: the analyst had seen these years before the split, so the test is cleaner than the walk-forward but not untouched. Paper trading after the data end is the only clean test.
