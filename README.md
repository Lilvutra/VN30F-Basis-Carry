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
sql/basket_prices.sql      → data/raw/vn30_basket_prices.parquet (member adj close+vol)
        ▼
scripts/basis_backtest.py  → result/basis/  (trades, sweep, cost curve, findings, figures)
```

### Data

- **`vn30f_frontmonth`** — the front-month contract each day, spliced via
  `quote.futurecontractcode.futurecode = 'VN30F1M'`, with its close, settlement,
  open interest, the VN30 index level and the contract expiry (→ days-to-expiry).
  History 2021-06 → now.
- **`vn30_membership`** — 30-ticker snapshots; the basket uses the latest snapshot
  on or before each trade date (no survivorship).
- **`basket_prices`** — daily **adjusted** (total-return) close + volume for every
  stock that was ever a VN30 member. Adjusted on purpose: the basket holder receives
  the dividends and the future drops on the ex-date, so total return is the correct
  hedge P&L, not double counting.

### The trade, as implemented

1. **Capital** — basket notional + futures margin + a cash reserve for margin calls
   (`--reserve-mult`).
2. **Basket** — equal-weight VN30 members, valued at adjusted close (fractional
   shares; real lot-of-100 adds tracking error).
3. **Basis** — `fut_close − vn30_index`, tracked daily with days-to-expiry.
4. **Costs** — stock fee both sides, 0.1% sell tax, futures fee, slippage, converted
   to index points; enter only when basis clears the cost bar.
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
    --entry-basis 10 --exit-basis 3 --outdir result/basis
```

## Result (2021-06 → 2026-10)

- 1,334 front-month days, 65 contracts. Basis ranges **−32 to +22**, median **−1.3**;
  only ~2% of days have basis ≥ +8. **The future usually trades at a discount**, so
  the long-basket/short-future direction is a rare setup.
- At entry ≥ +10 / exit ≤ +3: **11 trades**, avg gross **+8.5 pts**, avg cost
  **11.4 pts**, avg net **−2.9 pts** — a **loss**.
- **Breakeven round-trip cost ≈ 50 bps.** Above that the edge is gone.

| round-trip cost | avg net (pts) | total (VND, 1 contract) |
|---|---|---|
| 30 bps | +3.58 | +3.9m |
| 50 bps | +0.34 | +0.4m |
| 70 bps (default itemised) | −2.90 | −3.2m |
| 90 bps | −6.15 | −6.8m |

**Verdict: the mechanism is real but the edge is cost-sized.** The basis converges as
theory says, and the gross capture (~8.5 pts) is stable; but realistic VN retail costs
(≈60–90 bps round trip, i.e. 8–14 index points) exceed it, so the trade loses after
costs. It only clears if round-trip cost is pushed below ~50 bps — i.e. institutional
fees / a market-maker, not retail.

That is the same wall project2 and project3 hit intraday, now on a daily convergence
trade: **cost, not signal, is the binding constraint** — and here also tracking error
(equal-weight basket vs the cap-weighted index) and the rarity of a premium basis.

## Outputs (`result/basis/`)

- `trades.csv` — each trade: entry/exit basis, points, costs, margin events, reason.
- `summary.csv` — entry-threshold sweep.
- `cost_curve.csv` — net vs assumed round-trip cost.
- `basis.svg` — basis with thresholds and executed trades.
- `equity.svg` — cumulative net P&L at the chosen thresholds.
- `FINDINGS.md` — the verdict.

## Caveats

- Fractional basket shares; real lots of 100 add tracking error.
- One position at a time; fill at the daily close; no intraday financing beyond the
  flat cost model.
- Equal-weight basket ≠ cap-weighted index — tracking error is real (one trade shows
  −45 pts of it) and is not controllable without index weights.
- No out-of-sample split yet; 65 contracts over 5 years is a small sample and the
  result should be re-checked with a walk-forward before any capital.
