# Walk-forward — long VN30 basket / short VN30F1M

Grid: entry -4,-2,0,2,4,6,8 × exit 3 × basket fit = 7 combos. Pick rule: best total net points on trades entered before the test window, with at least 3 of them; otherwise the pre-registered spec 10/3/equal.

Entry rule: cost (entry value = buffer over round-trip cost in index points). Execution: close. The prior-spec benchmark uses the points rule with the same execution.

## Anchored walk-forward (train = all history before the test year)

| test year | picked entry/exit/basket | IS trades | IS net (pts) | OOS trades | OOS net (pts) | OOS avg basis | OOS avg tracking | prior spec OOS net (pts) |
|---|---|---|---|---|---|---|---|---|
| 2023 | -2 / 3 / fit | 3 | +5.3 | 1 | -2.1 | +4.12 | +1.56 | +0.0 |
| 2024 | -2 / 3 / fit | 4 | +3.1 | 4 | -14.8 | +7.62 | -2.54 | +0.4 |
| 2025 | 2 / 3 / fit | 3 | +3.5 | 1 | +9.5 | +19.98 | -1.70 | +10.3 |
| 2026 | 2 / 3 / fit | 4 | +13.1 | 1 | +14.5 | +29.95 | -1.49 | -55.4 |

| stitched OOS | trades | avg net (pts) | t-stat | total net (pts) | total net (VND) |
|---|---|---|---|---|---|
| walk-forward pick | 7 | +1.02 | +0.32 | +7.1 | 714,531 |
| prior spec 10/3/equal | 10 | -4.47 | -1.28 | -44.7 | -4,471,596 |

## Single split (train < 2025-01-01, test ≥ 2025-01-01)

Picked 2 / 3 / fit: in-sample 3 trades, +3.5 pts; out-of-sample 2 trades, +24.1 pts (avg +12.04, t +4.81).

Its test-period result ranks 3 of 7 combos; 86% of all combos were net positive in the test period.

Top 5 combos in the test period (hindsight, for reference only):

| entry / exit / basket | trades | total net (pts) | avg net | avg tracking |
|---|---|---|---|---|
| 0 / 3 / fit | 5 | +35.9 | +7.18 | -0.13 |
| -2 / 3 / fit | 6 | +30.8 | +5.13 | +0.40 |
| 2 / 3 / fit | 2 | +24.1 | +12.04 | -1.59 |
| 4 / 3 / fit | 1 | +14.5 | +14.54 | -1.49 |
| 6 / 3 / fit | 1 | +14.5 | +14.54 | -1.49 |
