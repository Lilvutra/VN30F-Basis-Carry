# Step 1 — is the intraday basis capturable?

Trigger: first minute per day in the continuous session with displayed basis − bar ≥ 3, dte ≥ 7. Bar = VN30 × (40 bps fees+tax + 4.5% × dte/365 carry). Capturable = futures bid − fit basket at ask, after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). A stock quote counts only if two-sided, not crossed and within 3% of its last trade (a ceiling-locked stock has no ask); events with < 90% of basket weight quotable, a locked futures book, or a fill that lands in the lunch break / ATC are dropped (22 event×delay rows of 120).

## By delay from signal to fill (index points)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0s | 25 | +12.78 | +12.99 | +10.96 | 8.78 | **+2.18** | +2.25 | +6.95 | 92% |
| 30s | 24 | +12.93 | +12.28 | +10.16 | 8.91 | **+1.26** | +1.76 | +1.79 | 88% |
| 60s | 25 | +12.78 | +10.94 | +9.05 | 8.78 | **+0.27** | +1.29 | +0.26 | 84% |
| 120s | 24 | +12.85 | +11.00 | +9.11 | 8.77 | **+0.33** | +0.71 | +0.59 | 67% |

## By year (60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 6 | +12.43 | +13.58 | +11.63 | 8.15 | **+3.48** | +3.22 | +5.17 | 100% |
| 2022 | 5 | +11.58 | +9.90 | +8.07 | 8.01 | **+0.06** | +0.82 | +0.04 | 80% |
| 2023 | 1 | +9.05 | +8.48 | +7.05 | 5.62 | **+1.43** | +1.43 | +nan | 100% |
| 2024 | 2 | +11.35 | +10.81 | +9.55 | 8.13 | **+1.42** | +1.42 | +1.76 | 100% |
| 2025 | 3 | +11.58 | +0.93 | -1.03 | 7.76 | **-8.79** | -9.72 | -1.32 | 33% |
| 2026 | 8 | +15.05 | +13.69 | +11.64 | 10.67 | **+0.96** | +1.24 | +2.34 | 88% |

## One position at a time (first trigger per contract, 60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| per contract | 12 | +13.46 | +11.16 | +9.28 | 9.27 | **+0.01** | +1.63 | +0.01 | 83% |
