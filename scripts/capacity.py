#!/usr/bin/env python3
"""project5 — capacity with partial fills.

intraday_check.py counts a size-N trade only if all N contracts fill within the top-3
book; otherwise the event is dropped. A real desk would take what the book offers.
Here, for every trigger of an intraday_check run (60 s delay, from --depth-from, when
order-book sizes exist), the book is walked for each k in --grid and the edge at k is
recorded. For a target size N the trade size is the k ≤ N that maximises k × edge(k)
among fully fillable k with edge > 0 (the book and the bar are both visible at the
fill, so this choice uses no future information); no trade if none qualifies.

Two policies:
  every   trade on every trigger day; positions in a contract add up until expiry
  first   only the first trigger per contract (one position at a time)

Capital = peak open contracts × VN30 × multiplier × (1 + --margin), i.e. the basket
plus futures margin held in cash.

Outputs (--outdir): fills.csv (event × k), capacity.csv, FINDINGS.md
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from basis_backtest import fit_weights, load_basket, load_members, members_on
from intraday_check import asof, book, quotes, walk


def main() -> None:
    ap = argparse.ArgumentParser(description="Capacity with partial fills.")
    ap.add_argument("--events", type=Path, default=Path("result/intraday_fund_buffer3/events.csv"))
    ap.add_argument("--basket", type=Path, default=Path("data/raw/vn30_basket_prices.parquet"))
    ap.add_argument("--membership", type=Path, default=Path("data/raw/vn30_membership.parquet"))
    ap.add_argument("--outdir", type=Path, default=Path("result/capacity"))
    ap.add_argument("--grid", default="1,2,3,5,7,10,15,20,30,40,50,75,100")
    ap.add_argument("--targets", default="10,20,50,100")
    ap.add_argument("--delay", type=int, default=60)
    ap.add_argument("--depth-from", default="2023-01-03")
    ap.add_argument("--fit-window", type=int, default=120)
    ap.add_argument("--multiplier", type=float, default=100000.0)
    ap.add_argument("--margin", type=float, default=0.2, help="futures margin as share of notional.")
    ap.add_argument("--max-quote-gap", type=float, default=0.03)
    ap.add_argument("--min-quoted", type=float, default=0.9)
    args = ap.parse_args()
    grid = [int(x) for x in args.grid.split(",")]
    targets = [int(x) for x in args.targets.split(",")]

    ev = pd.read_csv(args.events, parse_dates=["signal"])
    ev = ev[(ev["delay_s"] == args.delay) & (ev["size"] == ev["size"].min()) & ev["fill_in_session"]
            & (ev["fut_spread"] > 0) & (ev["weight_quoted"] >= args.min_quoted)
            & (pd.to_datetime(ev["date"]) >= args.depth_from)].reset_index(drop=True)
    _, _, raw, _ = load_basket(args.basket)
    snaps = load_members(args.membership)
    expiry = None

    rows = []
    for n, r in enumerate(ev.itertuples(), 1):
        day = pd.Timestamp(r.date)
        prev = raw.index[raw.index < day]
        w = fit_weights(raw, prev[-1], members_on(snaps, day), args.fit_window)
        tf = r.signal + pd.Timedelta(seconds=args.delay)
        q = quotes(w.index, r.contract, day.date(), tf)
        last0 = asof(q, "last", r.signal).reindex(w.index)
        sa, sb = asof(q, "ask", tf).reindex(w.index), asof(q, "bid", tf).reindex(w.index)
        ok = (sa.notna() & sb.notna() & last0.notna() & (sb > 0) & (sa > sb)
              & ((sa / last0 - 1).abs() <= args.max_quote_gap))
        ww = w[ok] / w[ok].sum()
        asks, bids = book(q, "ask", tf), book(q, "bid", tf)
        lv = asks.index.get_level_values(0)
        fb = bids.loc[r.contract] if r.contract in bids.index.get_level_values(0) else None
        for k in grid:
            need = ww * k * r.vn30 * args.multiplier / (last0[ok] * 1000)
            fills = pd.Series({t: walk(asks.loc[t] if t in lv else None, need[t]) for t in ww.index})
            f_fill = walk(fb, k)
            filled = bool(fills.notna().all() and pd.notna(f_fill))
            exec_ = (f_fill - r.vn30 * float((ww * fills / last0[ok]).sum())) if filled else np.nan
            rows.append({"date": r.date, "contract": r.contract, "vn30": r.vn30, "k": k,
                         "filled": filled, "edge": exec_ - r.bar, "fut_short": f_fill != f_fill,
                         "names_short": int(fills.isna().sum())})
        if n % 10 == 0:
            print(f"[capacity] {n}/{len(ev)} events", flush=True)

    f = pd.DataFrame(rows)
    years = (pd.to_datetime(ev["date"]).max() - pd.Timestamp(args.depth_from)).days / 365.25

    out = []
    for policy in ["every", "first"]:
        for N in targets:
            picks = []
            for (date, contract), g in f[f["k"] <= N].groupby(["date", "contract"], sort=True):
                g = g[g["filled"] & (g["edge"] > 0)]
                if g.empty:
                    picks.append({"date": date, "contract": contract, "k": 0, "edge": np.nan, "vn30": np.nan})
                    continue
                b = g.loc[(g["k"] * g["edge"]).idxmax()]
                picks.append({"date": date, "contract": contract, "k": int(b.k), "edge": b.edge, "vn30": b.vn30})
            p = pd.DataFrame(picks)
            if policy == "first":
                p = p[p["k"] > 0].groupby("contract").head(1)
            traded = p[p["k"] > 0]
            pnl = (traded["k"] * traded["edge"] * args.multiplier).sum()
            peak = traded.groupby("contract")["k"].sum().max() if len(traded) else 0
            cap = peak * ev["vn30"].max() * args.multiplier * (1 + args.margin)
            out.append({"policy": policy, "target": N, "events": len(p), "traded": len(traded),
                        "avg_k": traded["k"].mean(), "contracts_total": traded["k"].sum(),
                        "edge_wavg": (traded["k"] * traded["edge"]).sum() / max(traded["k"].sum(), 1),
                        "pnl_m_per_yr": pnl / years / 1e6, "peak_contracts": peak,
                        "capital_bn": cap / 1e9,
                        "pct_per_yr": pnl / years / cap * 100 if cap else np.nan})
    res = pd.DataFrame(out)

    args.outdir.mkdir(parents=True, exist_ok=True)
    f.to_csv(args.outdir / "fills.csv", index=False)
    res.to_csv(args.outdir / "capacity.csv", index=False)
    fk = f.groupby("k").agg(fillable=("filled", "mean"),
                            edge=("edge", "mean"),
                            fut_short=("fut_short", "mean"))
    print(f"[capacity] {len(ev)} events over {years:.2f} years")
    print(fk.round(3).to_string())
    print(res.round(2).to_string())
    (args.outdir / "FINDINGS.md").write_text("\n".join([
        "# Capacity with partial fills", "",
        f"Events: {len(ev)} triggers from {args.events}, {args.delay} s delay, "
        f"{args.depth_from} → {pd.to_datetime(ev['date']).max().date()} ({years:.2f} years).", "",
        "## Fill rate and edge by size (all events)", "",
        "| k | fully fillable | edge if filled | futures leg short |", "|---|---|---|---|",
        *[f"| {k} | {x.fillable:.0%} | {x.edge:+.2f} | {x.fut_short:.0%} |" for k, x in fk.iterrows()],
        "", "## Profit by target size (trade the best k ≤ target)", "",
        "| policy | target | traded/events | avg k | edge (k-wtd) | P&L m VND/yr | peak contracts "
        "| capital bn | %/yr above carry |", "|---|---|---|---|---|---|---|---|---|",
        *[f"| {x.policy} | {x.target} | {x.traded}/{x.events} | {x.avg_k:.1f} | {x.edge_wavg:+.2f} "
          f"| {x.pnl_m_per_yr:.1f} | {x.peak_contracts} | {x.capital_bn:.2f} | {x.pct_per_yr:.2f}% |"
          for x in res.itertuples()],
        "", f"Capital = peak open contracts × max VN30 × multiplier × (1 + {args.margin:g} margin).",
    ]) + "\n")


if __name__ == "__main__":
    main()
