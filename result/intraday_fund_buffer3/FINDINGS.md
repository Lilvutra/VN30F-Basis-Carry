# Step 1 — is the intraday basis capturable?

Trigger: first minute per day in the continuous session with displayed basis − bar ≥ 3, dte ≥ 7. Bar = VN30 × (17 bps fees+tax + 4.5% × dte/365 carry). Capturable = futures bid − fit basket at ask, after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). A stock quote counts only if two-sided, not crossed and within 3% of its last trade (a ceiling-locked stock has no ask); events with < 90% of basket weight quotable, a locked futures book, or a fill that lands in the lunch break / ATC are dropped (1270 event×delay rows of 1648).

Fees 17 bps round trip. Base tables use 1 contract(s); the book is walked up to 3 levels and a trade counts only if all of it fills.

## By delay from signal to fill (index points)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0s | 95 | +9.17 | +9.32 | +7.54 | 5.27 | **+2.27** | +2.07 | +15.62 | 96% |
| 30s | 94 | +9.17 | +8.86 | +7.13 | 5.29 | **+1.84** | +1.75 | +10.67 | 94% |
| 60s | 94 | +9.17 | +8.74 | +7.02 | 5.29 | **+1.73** | +1.49 | +10.07 | 89% |
| 120s | 95 | +9.21 | +8.17 | +6.45 | 5.28 | **+1.17** | +1.28 | +4.99 | 73% |

## By year (60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 15 | +9.04 | +8.89 | +7.03 | 4.96 | **+2.07** | +1.30 | +3.14 | 80% |
| 2022 | 10 | +8.21 | +7.84 | +5.91 | 4.67 | **+1.23** | +0.85 | +1.95 | 80% |
| 2023 | 3 | +7.94 | +6.52 | +4.77 | 3.54 | **+1.24** | +1.66 | +0.95 | 67% |
| 2024 | 29 | +8.16 | +7.97 | +6.60 | 4.56 | **+2.04** | +1.84 | +12.67 | 100% |
| 2025 | 17 | +9.68 | +8.98 | +7.35 | 5.95 | **+1.39** | +1.18 | +4.14 | 88% |
| 2026 | 20 | +10.96 | +10.33 | +8.26 | 6.61 | **+1.64** | +1.41 | +4.14 | 90% |

## By size (60 s delay, from 2023-01-03: order-book sizes start then)

| contracts | triggers | fully fillable | capturable | bar | edge mean | t | edge > 0 |
|---|---|---|---|---|---|---|---|
| 1 | 69 | 100% | +7.18 | 5.45 | **+1.73** | +10.51 | 93% |
| 10 | 69 | 97% | +6.99 | 5.44 | **+1.54** | +8.96 | 85% |
| 50 | 69 | 42% | +6.41 | 4.97 | **+1.44** | +6.39 | 93% |
| 100 | 69 | 19% | +5.87 | 4.61 | **+1.26** | +5.68 | 100% |

## One position at a time (first trigger per contract, 60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| per contract | 29 | +10.24 | +9.93 | +8.14 | 6.13 | **+2.01** | +1.75 | +5.14 | 86% |
