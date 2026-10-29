# Step 1 — is the intraday basis capturable?

Trigger: first minute per day in the continuous session with displayed basis − bar ≥ 3, dte ≥ 0. Bar = VN30 × (17 bps fees+tax + 4.5% × dte/365 carry). Capturable = futures bid − fit basket at ask, after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). A stock quote counts only if two-sided, not crossed and within 3% of its last trade (a ceiling-locked stock has no ask); events with < 90% of basket weight quotable, a locked futures book, or a fill that lands in the lunch break / ATC are dropped (2987 event×delay rows of 3900).

Fees 17 bps round trip. Base tables use 1 contract(s); the book is walked up to 3 levels and a trade counts only if all of it fills.

## By delay from signal to fill (index points)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0s | 185 | +8.09 | +8.15 | +6.35 | 4.12 | **+2.23** | +2.03 | +19.13 | 95% |
| 5s | 181 | +8.10 | +8.08 | +6.31 | 4.13 | **+2.18** | +2.08 | +19.00 | 96% |
| 30s | 182 | +8.11 | +7.79 | +6.02 | 4.13 | **+1.89** | +1.74 | +14.56 | 93% |
| 60s | 182 | +8.11 | +7.64 | +5.86 | 4.13 | **+1.73** | +1.45 | +11.73 | 87% |
| 120s | 183 | +8.13 | +7.25 | +5.49 | 4.13 | **+1.36** | +1.37 | +8.07 | 76% |

## By year (60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 30 | +8.09 | +8.15 | +6.38 | 3.93 | **+2.46** | +2.19 | +5.54 | 90% |
| 2022 | 32 | +7.19 | +6.53 | +4.62 | 3.11 | **+1.51** | +1.30 | +4.44 | 81% |
| 2023 | 12 | +6.05 | +4.89 | +3.15 | 2.35 | **+0.79** | +1.08 | +1.57 | 75% |
| 2024 | 38 | +7.70 | +7.30 | +5.90 | 4.07 | **+1.82** | +1.73 | +10.11 | 95% |
| 2025 | 28 | +8.61 | +7.88 | +6.12 | 4.89 | **+1.23** | +1.08 | +5.07 | 82% |
| 2026 | 42 | +9.44 | +9.04 | +7.01 | 5.12 | **+1.89** | +1.58 | +4.78 | 88% |

## By size (60 s delay, from 2023-01-03: order-book sizes start then)

| contracts | triggers | fully fillable | capturable | bar | edge mean | t | edge > 0 |
|---|---|---|---|---|---|---|---|
| 1 | 120 | 100% | +6.06 | 4.46 | **+1.60** | +9.47 | 88% |
| 10 | 120 | 94% | +5.92 | 4.48 | **+1.44** | +9.04 | 82% |
| 50 | 120 | 42% | +5.17 | 4.01 | **+1.16** | +6.74 | 86% |
| 100 | 120 | 14% | +5.43 | 4.02 | **+1.41** | +7.73 | 100% |

## One position at a time (first trigger per contract, 60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| per contract | 49 | +8.66 | +8.09 | +6.31 | 4.72 | **+1.58** | +1.38 | +5.77 | 84% |
