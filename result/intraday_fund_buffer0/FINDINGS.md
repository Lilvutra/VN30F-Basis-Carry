# Step 1 — is the intraday basis capturable?

Trigger: first minute per day in the continuous session with displayed basis − bar ≥ 0, dte ≥ 7. Bar = VN30 × (17 bps fees+tax + 4.5% × dte/365 carry). Capturable = futures bid − fit basket at ask, after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). A stock quote counts only if two-sided, not crossed and within 3% of its last trade (a ceiling-locked stock has no ask); events with < 90% of basket weight quotable, a locked futures book, or a fill that lands in the lunch break / ATC are dropped (3206 event×delay rows of 4192).

Fees 17 bps round trip. Base tables use 1 contract(s); the book is walked up to 3 levels and a trade counts only if all of it fills.

## By delay from signal to fill (index points)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0s | 251 | +6.47 | +6.56 | +4.85 | 5.40 | **-0.55** | -0.88 | -4.89 | 25% |
| 30s | 245 | +6.47 | +6.29 | +4.60 | 5.40 | **-0.80** | -0.96 | -6.34 | 25% |
| 60s | 245 | +6.47 | +6.02 | +4.36 | 5.40 | **-1.04** | -1.15 | -8.02 | 23% |
| 120s | 245 | +6.50 | +5.80 | +4.16 | 5.40 | **-1.23** | -1.17 | -9.01 | 20% |

## By year (60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 42 | +6.77 | +6.62 | +4.95 | 5.42 | **-0.47** | -0.84 | -1.09 | 36% |
| 2022 | 27 | +4.85 | +4.40 | +2.53 | 4.18 | **-1.65** | -1.43 | -4.18 | 26% |
| 2023 | 20 | +4.88 | +4.27 | +2.93 | 4.10 | **-1.16** | -1.00 | -3.82 | 5% |
| 2024 | 66 | +5.64 | +5.30 | +3.95 | 4.67 | **-0.72** | -1.07 | -3.87 | 21% |
| 2025 | 36 | +6.92 | +6.49 | +4.76 | 6.03 | **-1.26** | -1.24 | -5.11 | 17% |
| 2026 | 54 | +8.36 | +7.56 | +5.56 | 6.95 | **-1.39** | -1.95 | -4.37 | 24% |

## By size (60 s delay): walking the top-3 book

| contracts | triggers | fully fillable | capturable | bar | edge mean | t | edge > 0 |
|---|---|---|---|---|---|---|---|
| 1 | 245 | 100% | +4.36 | 5.40 | **-1.04** | -8.02 | 23% |
| 10 | 245 | 68% | +4.23 | 5.52 | **-1.30** | -9.42 | 16% |
| 50 | 245 | 33% | +3.54 | 4.95 | **-1.41** | -8.35 | 11% |
| 100 | 245 | 15% | +3.27 | 4.76 | **-1.50** | -6.73 | 11% |

## One position at a time (first trigger per contract, 60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| per contract | 47 | +7.41 | +7.11 | +5.40 | 6.39 | **-0.99** | -1.21 | -2.67 | 26% |
