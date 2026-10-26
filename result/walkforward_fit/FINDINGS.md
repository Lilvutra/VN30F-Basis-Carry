# Walk-forward — long VN30 basket / short VN30F1M

Grid: entry 6,8,10,12,14 × exit 0,3,5 × basket fit = 15 combos. Pick rule: best total net points on trades entered before the test window, with at least 3 of them; otherwise the pre-registered spec 10/3/equal.

Entry rule: points. Execution: close. The prior-spec benchmark uses the points rule with the same execution.

## Anchored walk-forward (train = all history before the test year)

| test year | picked entry/exit/basket | IS trades | IS net (pts) | OOS trades | OOS net (pts) | OOS avg basis | OOS avg tracking | prior spec OOS net (pts) |
|---|---|---|---|---|---|---|---|---|
| 2023 | 6 / 0 / fit | 5 | +21.2 | 0 | +0.0 |  |  | +0.0 |
| 2024 | 6 / 0 / fit | 5 | +21.2 | 5 | -8.0 | +8.82 | -1.52 | +0.4 |
| 2025 | 6 / 0 / fit | 10 | +13.2 | 3 | +1.2 | +9.02 | +1.58 | +10.3 |
| 2026 | 6 / 0 / fit | 13 | +14.4 | 11 | -66.5 | +11.61 | -4.01 | -55.4 |

| stitched OOS | trades | avg net (pts) | t-stat | total net (pts) | total net (VND) |
|---|---|---|---|---|---|
| walk-forward pick | 19 | -3.86 | -1.93 | -73.3 | -7,325,486 |
| prior spec 10/3/equal | 10 | -4.47 | -1.28 | -44.7 | -4,471,596 |

## Single split (train < 2025-01-01, test ≥ 2025-01-01)

Picked 6 / 0 / fit: in-sample 10 trades, +13.2 pts; out-of-sample 14 trades, -65.3 pts (avg -4.66, t -1.74).

Its test-period result ranks 14 of 15 combos; 60% of all combos were net positive in the test period.

Top 5 combos in the test period (hindsight, for reference only):

| entry / exit / basket | trades | total net (pts) | avg net | avg tracking |
|---|---|---|---|---|
| 12 / 0 / fit | 3 | +30.2 | +10.07 | -1.06 |
| 12 / 3 / fit | 3 | +30.2 | +10.07 | -1.06 |
| 10 / 3 / fit | 8 | +27.5 | +3.44 | -0.56 |
| 10 / 0 / fit | 7 | +22.5 | +3.22 | -2.87 |
| 14 / 0 / fit | 2 | +16.3 | +8.16 | -7.07 |
