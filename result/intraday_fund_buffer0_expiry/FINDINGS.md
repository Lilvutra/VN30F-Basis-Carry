# Step 1 — is the intraday basis capturable?

Trigger: first minute per day in the continuous session with displayed basis − bar ≥ 0, dte ≥ 0. Bar = VN30 × (17 bps fees+tax + 4.5% × dte/365 carry). Capturable = futures bid − fit basket at ask, after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). A stock quote counts only if two-sided, not crossed and within 3% of its last trade (a ceiling-locked stock has no ask); events with < 90% of basket weight quotable, a locked futures book, or a fill that lands in the lunch break / ATC are dropped (104 event×delay rows of 2345).

Fees 17 bps round trip. Base tables use 1 contract(s); the book is walked up to 3 levels and a trade counts only if all of it fills.

## By delay from signal to fill (index points)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0s | 453 | +5.29 | +5.31 | +3.61 | 4.27 | **-0.66** | -0.96 | -8.26 | 22% |
| 5s | 448 | +5.27 | +5.26 | +3.55 | 4.25 | **-0.70** | -0.98 | -8.58 | 22% |
| 30s | 447 | +5.28 | +5.07 | +3.38 | 4.25 | **-0.87** | -1.14 | -9.88 | 22% |
| 60s | 447 | +5.28 | +4.88 | +3.21 | 4.25 | **-1.05** | -1.21 | -11.19 | 20% |
| 120s | 446 | +5.30 | +4.69 | +3.05 | 4.26 | **-1.20** | -1.32 | -11.83 | 20% |

## By year (60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 70 | +6.01 | +5.86 | +4.18 | 4.41 | **-0.23** | -0.83 | -0.72 | 36% |
| 2022 | 64 | +4.08 | +3.74 | +1.89 | 3.20 | **-1.31** | -1.38 | -4.42 | 22% |
| 2023 | 48 | +3.59 | +3.26 | +1.86 | 2.95 | **-1.09** | -1.11 | -6.61 | 10% |
| 2024 | 102 | +4.79 | +4.37 | +3.01 | 3.90 | **-0.89** | -1.19 | -6.48 | 18% |
| 2025 | 70 | +5.38 | +5.00 | +3.29 | 4.61 | **-1.33** | -1.36 | -7.45 | 16% |
| 2026 | 93 | +6.89 | +6.22 | +4.23 | 5.66 | **-1.42** | -1.79 | -6.44 | 18% |

## By size (60 s delay, from 2023-01-03: order-book sizes start then)

| contracts | triggers | fully fillable | capturable | bar | edge mean | t | edge > 0 |
|---|---|---|---|---|---|---|---|
| 1 | 313 | 100% | +3.26 | 4.43 | **-1.18** | -12.66 | 16% |

## One position at a time (first trigger per contract, 60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| per contract | 63 | +6.35 | +6.06 | +4.36 | 5.43 | **-1.07** | -1.27 | -3.76 | 22% |
