# Step 1 — is the intraday basis capturable?

Trigger: first minute per day in the continuous session with displayed basis − bar ≥ 5, dte ≥ 7. Bar = VN30 × (40 bps fees+tax + 4.5% × dte/365 carry). Capturable = futures bid − fit basket at ask, after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). A stock quote counts only if two-sided, not crossed and within 3% of its last trade (a ceiling-locked stock has no ask); events with < 90% of basket weight quotable, a locked futures book, or a fill that lands in the lunch break / ATC are dropped (15 event×delay rows of 52).

## By delay from signal to fill (index points)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 0s | 10 | +15.44 | +14.66 | +12.48 | 9.17 | **+3.31** | +4.02 | +4.18 | 90% |
| 30s | 9 | +15.46 | +14.40 | +12.34 | 9.08 | **+3.26** | +4.25 | +3.30 | 89% |
| 60s | 9 | +15.46 | +14.03 | +11.77 | 9.08 | **+2.69** | +3.24 | +2.61 | 78% |
| 120s | 9 | +15.26 | +13.01 | +10.89 | 9.11 | **+1.78** | +2.90 | +1.40 | 78% |

## By year (60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 4 | +14.31 | +15.35 | +13.45 | 8.58 | **+4.87** | +5.29 | +6.72 | 100% |
| 2022 | 2 | +15.09 | +12.06 | +8.76 | 8.45 | **+0.30** | +0.30 | +0.10 | 50% |
| 2025 | 1 | +15.19 | +13.60 | +11.94 | 7.48 | **+4.46** | +4.46 | +nan | 100% |
| 2026 | 2 | +18.26 | +13.58 | +11.35 | 11.49 | **-0.14** | -0.14 | -0.11 | 50% |

## One position at a time (first trigger per contract, 60 s delay)

| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|---|
| per contract | 6 | +16.15 | +14.05 | +11.61 | 9.25 | **+2.36** | +3.85 | +1.64 | 67% |
