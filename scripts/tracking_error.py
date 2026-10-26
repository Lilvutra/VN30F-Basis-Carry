#!/usr/bin/env python3
"""project5 — how well does each hedge basket track VN30?

The basis trade only earns the basis if the long leg moves exactly like the
index. Any gap (basket − VN30) is an unintended bet. Eleven trades are too few
to measure that gap, so this script measures it on EVERY non-overlapping
--hold-session window 2021-06 → now: build the basket at the window start
exactly as the backtest would (same membership snapshot, same weights, same
adjusted prices), hold it, and record (basket return − VN30 return) × VN30
level, i.e. the tracking gap in index points.

Modes: equal (equal-weight members), fit (long-only weights regressed on VN30
over the trailing --fit-window sessions), etf (E1VFVN30).

Outputs (--outdir, default result/tracking/):
  tracking_error.csv   one row per window, gap in points per mode
  summary.csv          distribution per mode, plus std by year

Usage:
    python scripts/tracking_error.py \
        --basket data/raw/vn30_basket_prices.parquet \
        --membership data/raw/vn30_membership.parquet
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from basis_backtest import ETF, _price_on, fit_weights, load_basket, load_members, members_on


def main() -> None:
    ap = argparse.ArgumentParser(description="Tracking gap of each hedge basket vs VN30.")
    ap.add_argument("--basket", type=Path, required=True)
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=Path("result/tracking"))
    ap.add_argument("--start", default="2021-06-01")
    ap.add_argument("--hold", type=int, default=5, help="sessions per window (≈ avg trade length).")
    ap.add_argument("--fit-window", type=int, default=120)
    args = ap.parse_args()

    px, _, raw, _ = load_basket(args.basket)
    snaps = load_members(args.membership)
    idx = raw["VN30"].dropna()
    dates = idx.loc[args.start:].index

    rows = []
    for k in range(0, len(dates) - args.hold, args.hold):
        d0, d1 = dates[k], dates[k + args.hold]
        p0 = _price_on(px, d0, members_on(snaps, d0))
        r = _price_on(px, d1, p0.index).reindex(p0.index) / p0 - 1
        ri = idx[d1] / idx[d0] - 1
        w = fit_weights(raw, d0, list(p0.index), args.fit_window)
        e0, e1 = px[ETF].get(d0), px[ETF].get(d1)
        rets = {"equal": r.mean(), "fit": (w * r.reindex(w.index)).sum(),
                "etf": e1 / e0 - 1 if pd.notna(e0) and pd.notna(e1) else np.nan}
        rows.append({"date": d0, **{m: (x - ri) * idx[d0] for m, x in rets.items()}})
    t = pd.DataFrame(rows).set_index("date")

    summ = t.describe(percentiles=[.05, .95]).T
    summ["share_abs_gt_10"] = (t.abs() > 10).sum() / t.notna().sum()
    by_year = t.groupby(t.index.year).std().T.add_prefix("std_")
    summ = summ.join(by_year)

    args.outdir.mkdir(parents=True, exist_ok=True)
    t.to_csv(args.outdir / "tracking_error.csv")
    summ.to_csv(args.outdir / "summary.csv")
    print(f"[tracking] {len(t)} windows of {args.hold} sessions (gap in VN30 points)")
    print(summ[["count", "mean", "std", "5%", "95%", "share_abs_gt_10"]].round(2).to_string())
    print(f"[tracking] wrote {args.outdir}/")


if __name__ == "__main__":
    main()
