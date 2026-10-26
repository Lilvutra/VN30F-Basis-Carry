# Walk-forward — long VN30 basket / short VN30F1M

Grid: entry -4,-2,0,2,4,6,8 × exit 3 × basket fit = 7 combos. Pick rule: best total net points on trades entered before the test window, with at least 3 of them; otherwise the pre-registered spec 10/3/equal.

Entry rule: cost (entry value = buffer over round-trip cost in index points). Execution: next_open. The prior-spec benchmark uses the points rule with the same execution.

## Anchored walk-forward (train = all history before the test year)

| test year | picked entry/exit/basket | IS trades | IS net (pts) | OOS trades | OOS net (pts) | OOS avg basis | OOS avg tracking | prior spec OOS net (pts) |
|---|---|---|---|---|---|---|---|---|
| 2023 | -2 / 3 / fit | 3 | -5.7 | 1 | +0.3 | +9.29 | -1.17 | +0.0 |
| 2024 | -2 / 3 / fit | 4 | -5.4 | 4 | -20.9 | +5.49 | -1.92 | -2.4 |
| 2025 | 2 / 3 / fit | 3 | -8.2 | 1 | -16.0 | +8.88 | -15.98 | -13.8 |
| 2026 | 0 / 3 / fit | 6 | -13.7 | 3 | -57.8 | -2.90 | -2.64 | -133.5 |

| stitched OOS | trades | avg net (pts) | t-stat | total net (pts) | total net (VND) |
|---|---|---|---|---|---|
| walk-forward pick | 9 | -10.49 | -3.48 | -94.4 | -9,438,575 |
| prior spec 10/3/equal | 10 | -14.97 | -3.10 | -149.7 | -14,970,611 |

## Single split (train < 2025-01-01, test ≥ 2025-01-01)

Picked 2 / 3 / fit: in-sample 3 trades, -8.2 pts; out-of-sample 2 trades, -30.1 pts (avg -15.04, t -16.05).

Its test-period result ranks 4 of 7 combos; 0% of all combos were net positive in the test period.

Top 5 combos in the test period (hindsight, for reference only):

| entry / exit / basket | trades | total net (pts) | avg net | avg tracking |
|---|---|---|---|---|
| 8 / 3 / fit | 0 | +0.0 |  |  |
| 4 / 3 / fit | 1 | -14.1 | -14.10 | -0.82 |
| 6 / 3 / fit | 1 | -14.1 | -14.10 | -0.82 |
| 2 / 3 / fit | 2 | -30.1 | -15.04 | -8.40 |
| 0 / 3 / fit | 5 | -51.6 | -10.33 | -1.41 |
