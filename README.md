# project5 — long VN30 basket / short VN30F1M (basis convergence)

A plutus-style quant hypothesis project, DB-backed. It implements the operational
recipe for a **cash-and-carry basis trade**: when the VN30 front-month future
(`VN30F1M`) trades rich versus the VN30 index, buy a VN30-like basket of stocks and
short one futures contract, then unwind as the basis converges into expiry.

Same database (`algotradeDB`) and conventions as project2–4. This is a different
hypothesis from the pairs screen in `project4`: the anchor here is the **basis at
expiry**, not a statistical peer relationship.

## Hypothesis

> VN30F1M periodically trades at a premium to the VN30 index. Buying the basket and
> shorting the future locks the basis, which is contractually pulled to zero at
> settlement. If the entry basis exceeds the round-trip transaction cost plus a
> buffer, the trade earns the convergence, market-neutral.

## Pipeline

```
sql/vn30f_frontmonth.sql   → data/raw/vn30f_frontmonth.parquet   (futures + index)
sql/vn30_membership.sql    → data/raw/vn30_membership.parquet    (VN30 snapshots)
sql/basket_prices.sql      → data/raw/vn30_basket_prices.parquet (member adj+raw close, vol,
                                                                  + VN30 index + E1VFVN30 ETF)
        ▼
scripts/basis_backtest.py  → result/basis{,_fit,_etf}/  (trades, sweep, cost curve, findings, figures)
scripts/tracking_error.py  → result/tracking/           (hedge-basket tracking gap, every 5-session window)
scripts/walk_forward.py    → result/walkforward{,_fit,_cost_*}/ (anchored yearly walk-forward + 2025 split)
sql/intraday_basis_minute.sql + tick/book data
scripts/intraday_check.py  → result/intraday*/          (displayed vs capturable basis at triggers)
scripts/capacity.py        → result/capacity/           (partial fills from the top-3 book, P&L by size)
```

## Nine-step map

| step | where | status |
|---|---|---|
| 1 Hypothesis | *Hypothesis* | done |
| 2 Data collection | *Pipeline*, `sql/`, `scripts/download_data.py` | done |
| 3 Data processing | *Data*, *The tracking gap…* (`tracking_error.py`) | done |
| 4 In-sample backtest | *Result*, *Gross = basis captured + tracking gap* (`basis_backtest.py`) | done |
| 5 Optimization | *Walk-forward* (entry × exit × basket grid, picked in-sample per fold) | done |
| 6 Out-of-sample | *Walk-forward*, *Cost-relative entry + next-open execution*, *Intraday step 1*, *Fund-level costs and size*, *Capacity with partial fills* | done → **STOP** |
| 7 Paper trading | — | not started: stopped at step 6 |
| 8–9 Live trading onward | — | not started |

### Data

- **`vn30f_frontmonth`** — the front-month contract each day, spliced via
  `quote.futurecontractcode.futurecode = 'VN30F1M'`, with its close, settlement,
  open interest, the VN30 index level and the contract expiry (→ days-to-expiry).
  History 2021-06 → now.
- **`vn30_membership`** — 30-ticker snapshots; the basket uses the latest snapshot
  on or before each trade date (no survivorship).
- **`basket_prices`** — daily **adjusted** (total-return) close, raw close + volume for
  every stock that was ever a VN30 member, plus `VN30` and the `E1VFVN30` ETF, from 2020-06
  (so the `fit` basket has a trailing window before the first trade). Adjusted on purpose: the basket holder receives
  the dividends and the future drops on the ex-date, so total return is the correct
  hedge P&L, not double counting.

### The trade, as implemented

1. **Capital** — basket notional + futures margin + a cash reserve for margin calls
   (`--reserve-mult`).
2. **Basket** (`--basket-mode`) — `equal`: equal-weight VN30 members; `fit`: the same
   members with long-only weights regressed on VN30 over the trailing 120 sessions (the DB
   has no shares-outstanding for banks/brokers/insurers, so true cap weights are not
   available); `etf`: hold E1VFVN30. Valued at adjusted close (fractional shares).
3. **Basis** — `fut_close − vn30_index`, tracked daily with days-to-expiry.
4. **Costs** — stock fee both sides, 0.1% sell tax, futures fee, slippage, converted
   to index points. Entry is basis ≥ `--entry-basis`, a fixed point level; it is not
   compared with the cost (see Walk-forward).
5. **Filters** — min days-to-expiry, market not overheated (`--max-runup`), basket
   liquidity (`--min-turnover`, off by default).
6. **Two legs together** — entered on the same close; entry basis recorded.
7. **Daily MTM** — futures marked daily; reserve tops up margin calls; forced exit if
   the reserve is exhausted.
8. **Exit** — basis convergence, expiry settlement, or a widening stop.
9. **T+2** — the stock leg cannot be sold in the first two sessions.

## Setup / Run

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env && set -a; source .env; set +a

python scripts/download_data.py --query-file sql/vn30f_frontmonth.sql -o data/raw/vn30f_frontmonth.parquet
python scripts/download_data.py --query-file sql/vn30_membership.sql  -o data/raw/vn30_membership.parquet
python scripts/download_data.py --query-file sql/basket_prices.sql    -o data/raw/vn30_basket_prices.parquet

python scripts/basis_backtest.py \
    --futures data/raw/vn30f_frontmonth.parquet \
    --basket data/raw/vn30_basket_prices.parquet \
    --membership data/raw/vn30_membership.parquet \
    --entry-basis 10 --exit-basis 3 --basket-mode fit --outdir result/basis_fit
    # --basket-mode equal → result/basis, etf → result/basis_etf

python scripts/tracking_error.py \
    --basket data/raw/vn30_basket_prices.parquet \
    --membership data/raw/vn30_membership.parquet

python scripts/walk_forward.py \
    --futures data/raw/vn30f_frontmonth.parquet \
    --basket data/raw/vn30_basket_prices.parquet \
    --membership data/raw/vn30_membership.parquet
    # --modes fit --outdir result/walkforward_fit  → basket fixed to fit, thresholds tuned
    # --entry-rule cost --execution next_open --outdir result/walkforward_cost_next_open

python scripts/intraday_check.py \
    --futures data/raw/vn30f_frontmonth.parquet \
    --basket data/raw/vn30_basket_prices.parquet \
    --membership data/raw/vn30_membership.parquet
    # --fee-bps 17 --buffer 3 --sizes 1,10,50,100 --outdir result/intraday_fund_buffer3

python scripts/capacity.py --events result/intraday_fund_buffer3/events.csv
```

## Result (2021-06 → 2026-10)

- 1,340 front-month days (to 2026-10-23). Basis ranges **−32 to +22**, median **−1.3**;
  only ~2% of days have basis ≥ +8. **The future usually trades at a discount**, so
  the long-basket/short-future direction is a rare setup.
- At entry ≥ +10 / exit ≤ +3: **12 trades**. The entry/exit days are the same in every
  basket mode; only the long leg differs. All tables in this section fill at the
  **signal close** (`--execution close`), which is optimistic; see *Execution* below.

### Gross = basis captured + tracking gap

Each trade's gross splits exactly into the basis captured (entry basis − exit basis) and
the tracking gap (basket − VN30 over the hold). The basis part is the strategy; the gap is
an unintended bet that the basket beats the index.

| basket | avg basis | avg tracking | tracking std | avg cost | avg net | total net (VND) |
|---|---|---|---|---|---|---|
| equal-weight | +14.38 | −6.38 | 14.18 | 11.51 | −3.50 | −4.2m |
| **fit (regressed weights)** | +14.38 | −1.30 | 6.01 | 11.51 | **+1.57** | **+1.9m** |
| E1VFVN30 ETF | +14.38 | −5.00 | 16.63 | 11.51 | −2.13 | −2.6m |
| *perfect hedge* | +14.38 | 0 | 0 | 11.51 | *+2.87* | *+3.4m* |

**The basis converged on 12/12 trades and averaged +14.4 pts, more than the 11.5-pt
cost.** The earlier "≈ 8.5 pts gross" figure mixed basis with tracking. The equal-weight
basket lost because of tracking error (one trade, VN30F2602, lost −45.7 pts to it), not
because of costs alone.

### The tracking gap on every 5-session window (`result/tracking/`)

269 non-overlapping windows, basket built exactly as at entry:

| basket | mean gap | std | 5%–95% | share \|gap\| > 10 pts |
|---|---|---|---|---|
| equal-weight | +0.49 | 12.0 | −16.6 … +17.7 | 26% |
| **fit** | +0.96 | **7.2** | −9.9 … +12.7 | **12%** |
| ETF | +0.44 | 13.9 | −21.1 … +21.6 | 32% |

- The mean gap is ≈ 0 for every basket, so the equal-weight "small caps beat large caps"
  bet has no edge here; it is just noise. Remove it rather than keep it.
- `fit` cuts the gap by ~40% and halves the large misses.
- The ETF is the **worst** hedge at the close. Its market price moves away from the index on
  volatile days (e.g. 2026-04-08: VN30 +4.9%, ETF +6.9%), and those are exactly the days
  the basis spikes, so you buy the ETF when it is also rich.

### Walk-forward (`result/walkforward/`, `result/walkforward_fit/`)

Every choice above (+10/+3, the `fit` basket) was made looking at the full sample. The
walk-forward asks whether they would have been chosen **in advance**. Grid: entry
{6,8,10,12,14} × exit {0,3,5} × basket. For each test year, pick the combo with the best
total net on trades entered before that year (≥ 3 trades), then trade it in that year.

| variant | OOS trades (2023–26) | avg net | t | total net |
|---|---|---|---|---|
| tune entry × exit × basket (45 combos) | 12 | −4.54 | −1.41 | **−54.5 pts** |
| basket fixed to `fit`, tune entry × exit (15) | 19 | −3.86 | −1.93 | **−73.3 pts** |
| original spec 10/3/equal, untuned | 13 | | | −44.7 pts |

Single split (train < 2025, test 2025 → 2026-10): the 45-combo pick (10/0/equal) made
+17.1 pts in-sample and **−46.5 pts** out-of-sample, ranking 32/45 in the test period.

**Why it fails out of sample.** 2021–2024 (VN30 ≈ 1,000–1,300) rewards a low +6 threshold,
because costs were only ~8–9 index points. By 2026 (VN30 ≈ 1,900) the same bps costs are
~13–14 points, so +6 entries lose (e.g. 2026: 11 trades at 6/0/fit, −66.5 pts). **A
threshold fixed in index points is not stationary while costs scale with the index
level.** The code compares the basis to a fixed number, not to the cost.

The best test-period combos (12/·/fit, 10/3/fit: +27 to +30 pts) are only visible with
hindsight. 10/3/fit, the headline spec above, is the original 10/3 thresholds plus the
basket picked on tracking quality, not on P&L. It does make +26.9 pts on 7 test trades,
but the fit choice came after seeing those trades, so it is not clean out-of-sample
evidence.

### Cost-relative entry + next-open execution (`result/walkforward_cost_*`, `result/basis_fit_nextopen/`)

Two fixes, tested together, with the walk-forward used **only** to choose the buffer:

1. **Entry relative to cost.** `--entry-rule cost`: enter when basis − round-trip cost
   (70 bps × index, in points) ≥ buffer. The bar rises with the index level.
2. **No same-close fill.** `--execution next_open`: the signal is read at the close, and
   both legs fill at the next session's 09:15. Stocks fill at their ATO open, and the future
   at its first trade at or after 09:15 (its daily `open` is the 08:45 print, taken
   while the index is still at yesterday's close). Exits fill the same way, except
   expiry, which settles at the expiry-day close.

Basket `fit`, exit +3 and buffer ∈ {−4, −2, 0, 2, 4, 6, 8} are tuned anchored by year:

| execution | OOS trades | avg net | t | total OOS | buffers positive in 2025–26 |
|---|---|---|---|---|---|
| signal close (optimistic) | 7 | +1.02 | +0.32 | +7.1 pts | 86% |
| **next open (realistic)** | 9 | **−10.49** | **−3.48** | **−94.4 pts** | **0%** |

The cost rule does fix the drift (with close fills, almost every buffer is positive in
2025–26), but **the next-open fill removes the edge**. At +10 / fit over the full sample:

| execution | avg basis captured | avg tracking | avg cost | avg net | t |
|---|---|---|---|---|---|
| signal close | +14.38 | −1.30 | 11.51 | +1.57 | +0.68 |
| next open | **+3.91** | −2.76 | 11.53 | **−10.38** | −3.80 |

A large closing basis is mostly gone by the next morning (e.g. VN30F2604: +13.96 at the
signal close, −14.42 at the next 09:15). The rich closing basis is a closing-print
dislocation that reverts overnight. It is not a convergence you can enter after seeing it.

### Intraday step 1: is the on-screen basis capturable? (`result/intraday*/`)

`scripts/intraday_check.py` uses tick data (`quote.matched`, `askprice`, `bidprice`):

- the per-minute displayed basis in the continuous session;
- a trigger is the first minute per day where displayed − bar ≥ buffer, with
  bar = VN30 × (40 bps fees+tax + 4.5% × dte/365 carry). **Carry**, the fair premium of a
  future over the index, was missing from the daily backtest, which flattered it;
- after a delay, the **capturable** basis = futures bid − fit basket at the ask. Held to
  expiry, the basis settles to 0, so net ≈ capturable − bar, tracking aside.

Quotes must be two-sided, uncrossed and within 3% of the last trade, so a ceiling-locked
stock has no ask. Fills must land in continuous trading, not lunch or ATC.

| buffer | delay | events | displayed | capturable | bar | edge mean | t | edge > 0 |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 s | 87 | 9.34 | 7.73 | 8.49 | **−0.75** | −5.0 | 17% |
| 0 | 60 s | 86 | 9.37 | 6.79 | 8.52 | **−1.73** | −5.9 | 17% |
| 3 | 60 s | 25 | 12.78 | 9.05 | 8.78 | +0.27 | +0.3 | 84% |
| 5 | 60 s | 9 | 15.46 | 11.77 | 9.08 | **+2.69** | +2.6 | 78% |
| 5, first per contract | 60 s | 6 | 16.15 | 11.61 | 9.25 | +2.36 | +1.6 | 67% |

- Trading every time the screen basis covers cost + carry **loses**, even with an instant
  fill. Crossing the spreads costs ~1.7 pts, and the basis decays ~0.5–1.5 pts within
  30–120 s.
- Only large dislocations (≥ bar + 5) survive to a capturable +2–4 pts. That is ~9 events
  (6 contracts) in 5.4 years, mostly crash/rebound days (2021-06, 2025-04, 2026-02). The
  buffer was chosen after seeing the buffer-0 result.
- **Economics:** ~1 trade a year × ~2.5 pts ≈ 250k VND per contract-year on ~280m VND of
  capital (≈ 0.1% a year). Tracking error over the 1–4 weeks to expiry (several points)
  is as large as the edge. Lot-of-100 rounding and ask depth on those volatile days are
  unmodelled.

### Fund-level costs and size (`result/intraday_fund_buffer{0,3}/`)

The same check with **assumed** institutional fees: 17 bps round trip (brokerage ~3 bps a
side, the 0.1% sell tax applies to funds too, futures ~1 bps). Larger orders walk the
top-3 book (`--sizes`). Order-book sizes exist only from 2023-01-03, so the size table
starts there.

| fees | buffer | triggers | edge @60 s, 1 contract | t | edge > 0 | first per contract |
|---|---|---|---|---|---|---|
| 40 bps (retail) | 0 | 86 | −1.73 | −5.9 | 17% | −2.13 (27) |
| 17 bps (fund) | 0 | 245 | −1.04 | −8.0 | 23% | −0.99 (47) |
| 17 bps (fund) | 3 | 94 | **+1.73** | +10.1 | 89% | **+2.01 (29), t +5.1** |

With fund fees and buffer 3, the edge is positive in **every year** 2021–2026 (+1.2 to
+2.1 pts). By size (60 s, 2023+, buffer 3):

| contracts | fully fillable in top 3 levels | edge | t |
|---|---|---|---|
| 1 | 100% | +1.73 | +10.5 |
| 10 | 97% | +1.54 | +9.0 |
| 50 | 42% | +1.44 | +6.4 |
| 100 | 19% | +1.26 | +5.7 |

- Lower fees are what turns it positive. Size erodes the edge slowly, but **capacity**
  is the binding limit: above ~10 contracts most triggers cannot be filled from the
  visible book in one go (slicing over minutes is untested).
- **Economics at capacity:** see the partial-fill table below: ≈ 9m VND a year on
  ~2.4bn VND at 10 contracts, ≈ 0.4% a year above the 4.5% carry. Real, but far too
  small to matter for a fund.

### Capacity with partial fills (`result/capacity/`, `scripts/capacity.py`)

Instead of dropping a trigger the book cannot fill in full, each of the 69 fund
buffer-3 triggers from 2023-01-03 (60 s delay) takes the size k ≤ target that maximises
k × edge(k) among fully fillable sizes with edge > 0 (both visible at the fill). Capital =
peak open contracts × max VN30 × 100k × 1.2 (basket + 20% futures margin). 3.76 years.

| policy | target | avg k | edge | P&L m VND/yr | peak contracts | capital bn | %/yr above carry |
|---|---|---|---|---|---|---|---|
| first trigger per contract | 10 | 8.8 | +2.11 | 9.4 | 10 | 2.4 | 0.38% |
| first trigger per contract | 20 | 16.2 | +2.04 | 16.7 | 20 | 4.9 | 0.34% |
| first trigger per contract | 50 | 28.8 | +1.93 | 28.1 | 50 | 12.2 | 0.23% |
| first trigger per contract | 100 | 34.1 | +1.94 | 33.4 | 100 | 24.4 | 0.14% |
| every trigger day (adds up) | 10 | 9.2 | +1.88 | 29.6 | 113 | 27.6 | 0.11% |
| every trigger day (adds up) | 50 | 33.4 | +1.70 | 96.6 | 483 | 118 | 0.08% |
| every trigger day (adds up) | 100 | 45.1 | +1.56 | 119.8 | 758 | 185 | 0.06% |

The futures bid is the first leg to run out (short in 36% of triggers at 50 contracts,
67% at 100). P&L in VND grows far slower than size; the return on capital falls
monotonically. Trading every trigger day raises VND profit but needs ~10× the capital
because positions pile up before expiry.
- Caveats: the fee level is an assumption; buffer 3 was picked after seeing buffer 0
  (only 0 and 3 were tried for funds); holding to expiry adds tracking noise of the same
  order as the edge (a fund replicating the official weights would have less than `fit`).

### Verdict

**Stop: the strategy is not tradeable.** Basis convergence is real. The `fit` basket removes
most of the small-vs-large-cap bet, and a cost-relative threshold fixes the drift in the
cost bar. But every positive daily result depended on filling at the same close that
produced the signal; at the next open the captured basis falls from ~14 to ~4 points.
Intraday, at retail fees, the on-screen basis mostly fails to cover spread + decay + fees +
carry. At fund-level fees, a buffer of 3 pts gives a consistent +1.5–2 pts per trade.
But the visible book caps it at ~10 contracts, about 0.3% a year above carry: a real
edge, too small to be worth running.

Cost sensitivity (equal-weight, gross held fixed): breakeven round trip ≈ 50 bps; see
`result/basis*/cost_curve.csv`.

**Fix in this revision:** an exit at expiry used to settle the future at the *entry* index
level instead of the expiry-day index. No +10 trade reached expiry, but the +6 sweep row
did (VN30F2402). With data to 2026-10-23 that row is −17.7m VND (29 trades); the old code
reported −12.5m.

## Outputs (`result/basis/`, `result/basis_fit/`, `result/basis_etf/`)

- `trades.csv` — each trade: signal date/basis, fill entry/exit basis, gross split into
  `basis_points` + `track_points`, costs, margin events, reason.
- `summary.csv` — entry-threshold sweep.
- `cost_curve.csv` — net vs assumed round-trip cost.
- `basis.svg` — basis with thresholds and executed trades.
- `equity.svg` — cumulative net P&L at the chosen thresholds.
- `FINDINGS.md` — the verdict.

## Caveats

- Fractional basket shares; real lots of 100 add tracking error.
- One position at a time; fill at the daily close; no intraday financing beyond the
  flat cost model.
- `fit` weights are estimated, not the index's real free-float cap weights; they still
  leave ~7 pts of 5-session tracking std. Weights are fit on closes up to the entry close.
- Next-open: the VN30 09:15 print can be stale on gap days (constituents not yet matched),
  so the `basis_points`/`track_points` split is noisy at the open; net P&L uses the actual
  fills (stock ATO opens, future 09:15 trade) and is not affected. Stocks with no ATO
  match fall back to their latest available open.
- Walk-forward is anchored by calendar year with few trades per fold (0–11); trades are
  assigned to a fold by entry date.
