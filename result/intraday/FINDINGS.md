# Step 1 — is the intraday basis capturable?

Trigger: first minute per day in the continuous session with displayed basis − bar ≥ 0, dte ≥ 7. Bar = VN30 × (40 bps fees+tax + 4.5% × dte/365 carry). Capturable = futures bid − fit basket at ask, after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). A stock quote counts only if two-sided, not crossed and within 3% of its last trade (a ceiling-locked stock has no ask); events with < 90% of basket weight quotable, a locked futures book, or a fill that lands in the lunch break / ATC are dropped (36 event×delay rows of 380).

## By delay from signal to fill (index points)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0s | 87 | +9.34 | +9.43 | +7.73 | 8.49 | **-0.75** | -1.01 | -5.02 | 17% |
| 30s | 86 | +9.37 | +8.81 | +7.11 | 8.52 | **-1.41** | -1.39 | -6.15 | 15% |
| 60s | 86 | +9.37 | +8.44 | +6.79 | 8.52 | **-1.73** | -1.63 | -5.94 | 17% |
| 120s | 85 | +9.32 | +8.19 | +6.55 | 8.44 | **-1.89** | -1.63 | -8.25 | 12% |

## By year (60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 11 | +9.55 | +9.30 | +7.37 | 8.39 | **-1.02** | -2.03 | -1.20 | 27% |
| 2022 | 11 | +8.13 | +7.08 | +5.39 | 7.31 | **-1.92** | -1.61 | -3.10 | 9% |
| 2023 | 3 | +7.22 | +6.32 | +4.66 | 6.10 | **-1.45** | -0.71 | -1.20 | 33% |
| 2024 | 30 | +8.09 | +7.91 | +6.54 | 7.53 | **-0.99** | -1.12 | -6.34 | 17% |
| 2025 | 16 | +10.19 | +8.25 | +6.50 | 9.41 | **-2.91** | -1.95 | -2.42 | 12% |
| 2026 | 15 | +12.26 | +10.50 | +8.62 | 11.00 | **-2.39** | -2.72 | -4.10 | 20% |

## One position at a time (first trigger per contract, 60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| per contract | 27 | +10.47 | +8.96 | +7.20 | 9.33 | **-2.13** | -1.84 | -2.56 | 30% |
