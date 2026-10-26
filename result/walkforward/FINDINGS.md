# Walk-forward — long VN30 basket / short VN30F1M

Grid: entry 6,8,10,12,14 × exit 0,3,5 × basket equal,fit,etf = 45 combos. Pick rule: best total net points on trades entered before the test window, with at least 3 of them; otherwise the pre-registered spec 10/3/equal.

Entry rule: points. Execution: close. The prior-spec benchmark uses the points rule with the same execution.

## Anchored walk-forward (train = all history before the test year)

| test year | picked entry/exit/basket | IS trades | IS net (pts) | OOS trades | OOS net (pts) | OOS avg basis | OOS avg tracking | prior spec OOS net (pts) |
|---|---|---|---|---|---|---|---|---|
| 2023 | 6 / 0 / fit | 5 | +21.2 | 0 | +0.0 |  |  | +0.0 |
| 2024 | 6 / 0 / fit | 5 | +21.2 | 5 | -8.0 | +8.82 | -1.52 | +0.4 |
| 2025 | 10 / 0 / equal | 4 | +17.1 | 2 | +12.4 | +15.57 | -0.39 | +10.3 |
| 2026 | 10 / 0 / equal | 6 | +29.5 | 5 | -58.9 | +19.36 | -17.66 | -55.4 |

| stitched OOS | trades | avg net (pts) | t-stat | total net (pts) | total net (VND) |
|---|---|---|---|---|---|
| walk-forward pick | 12 | -4.54 | -1.41 | -54.5 | -5,448,528 |
| prior spec 10/3/equal | 10 | -4.47 | -1.28 | -44.7 | -4,471,596 |

## Single split (train < 2025-01-01, test ≥ 2025-01-01)

Picked 10 / 0 / equal: in-sample 4 trades, +17.1 pts; out-of-sample 7 trades, -46.5 pts (avg -6.64, t -1.21).

Its test-period result ranks 32 of 45 combos; 33% of all combos were net positive in the test period.

Top 5 combos in the test period (hindsight, for reference only):

| entry / exit / basket | trades | total net (pts) | avg net | avg tracking |
|---|---|---|---|---|
| 12 / 3 / etf | 3 | +32.8 | +10.92 | -0.22 |
| 12 / 0 / etf | 3 | +32.8 | +10.92 | -0.22 |
| 12 / 3 / fit | 3 | +30.2 | +10.07 | -1.06 |
| 12 / 0 / fit | 3 | +30.2 | +10.07 | -1.06 |
| 10 / 3 / fit | 8 | +27.5 | +3.44 | -0.56 |
