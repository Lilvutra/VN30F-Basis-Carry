#!/usr/bin/env python3
"""project5 — walk-forward test of the basis strategy.

Every choice made so far (entry +10, exit +3, the "fit" basket) was picked
looking at the whole 2021–2026 sample. This script asks whether those choices
would have been picked IN ADVANCE and still worked afterwards.

Grid: --entries × --exits × --modes. Each combo is backtested once over the full
history (parameters are fixed per combo, so slicing its trades by entry date is
exactly what that combo would have done inside any window). Then:

  * anchored walk-forward: for each test year Y, pick the combo with the best
    total net points on trades entered before Y (at least --min-trades of them;
    otherwise fall back to the original pre-registered spec 10/3/equal), and
    record that combo's trades entered in Y;
  * single split: train before --split, test from --split on.

Outputs (--outdir, default result/walkforward/):
  grid.csv        every combo × calendar year: trades, gross split, net
  folds.csv       per test year: chosen combo, its in-sample and out-of-sample result
  oos_trades.csv  the stitched out-of-sample trades
  FINDINGS.md     the verdict

Usage:
    python scripts/walk_forward.py \
        --futures data/raw/vn30f_frontmonth.parquet \
        --basket data/raw/vn30_basket_prices.parquet \
        --membership data/raw/vn30_membership.parquet
"""
from __future__ import annotations

import argparse
import copy
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from basis_backtest import build_parser, load_basket, load_futures, load_members, run

PRIOR = (10.0, 3.0, "equal")          # the spec project5 started with, before any tuning


def _floats(s: str) -> list[float]:
    return [float(x) for x in s.split(",")]


def stats(t: pd.DataFrame) -> dict:
    n = len(t)
    if n == 0:
        return {"n": 0, "net_pts": 0.0, "avg_net": np.nan, "t_stat": np.nan,
                "avg_basis": np.nan, "avg_track": np.nan, "avg_cost": np.nan,
                "win_rate": np.nan, "net_vnd": 0.0}
    net = t["net_points"]
    sd = net.std() if n > 1 else np.nan
    return {"n": n, "net_pts": float(net.sum()), "avg_net": float(net.mean()),
            "t_stat": float(net.mean() / sd * np.sqrt(n)) if sd and sd > 0 else np.nan,
            "avg_basis": float(t["basis_points"].mean()),
            "avg_track": float(t["track_points"].mean()),
            "avg_cost": float(t["cost_points"].mean()),
            "win_rate": float((net > 0).mean()), "net_vnd": float(t["net_vnd"].sum())}


def pick(trades: dict, combos: list, end, min_trades: int):
    """Best combo by total net points on trades entered before `end`."""
    best, best_key = PRIOR, None
    for combo, t in trades.items():
        if combo not in combos:
            continue
        tr = t[t["entry_date"] < end]
        if len(tr) < min_trades:
            continue
        key = (tr["net_points"].sum(), tr["net_points"].mean())
        if best_key is None or key > best_key:
            best, best_key = combo, key
    return best, best_key is None


def fmt(x, spec="+.2f"):
    return "" if pd.isna(x) else format(x, spec)


def main() -> None:
    ap = build_parser(argparse.ArgumentParser(description="Walk-forward of the basis strategy."))
    ap.set_defaults(outdir=Path("result/walkforward"))
    ap.add_argument("--entries", default="6,8,10,12,14")
    ap.add_argument("--exits", default="0,3,5")
    ap.add_argument("--modes", default="equal,fit,etf")
    ap.add_argument("--test-years", default="2023,2024,2025,2026")
    ap.add_argument("--split", default="2025-01-01", help="single train/test split date.")
    ap.add_argument("--min-trades", type=int, default=3, help="min in-sample trades to pick a combo.")
    args = ap.parse_args()

    fut = load_futures(args.futures)
    px, vol, raw, popen = load_basket(args.basket)
    snaps = load_members(args.membership)

    combos = list(itertools.product(_floats(args.entries), _floats(args.exits), args.modes.split(",")))
    trades, grid = {}, []
    for entry, exit_, mode in combos + ([PRIOR] if PRIOR not in combos else []):
        a = copy.copy(args)
        a.exit_basis, a.basket_mode = exit_, mode
        if (entry, exit_, mode) not in combos:      # prior spec is always the fixed-points rule
            a.entry_rule = "points"
        t, _, _ = run(fut, px, vol, snaps, entry, a, raw, popen)
        if t.empty:
            t = pd.DataFrame(columns=["entry_date", "net_points", "basis_points", "track_points",
                                      "cost_points", "net_vnd"])
        t["entry_date"] = pd.to_datetime(t["entry_date"])
        trades[(entry, exit_, mode)] = t
        if (entry, exit_, mode) not in combos:      # prior spec: benchmark only, not pickable
            continue
        for y, g in t.groupby(t["entry_date"].dt.year):
            grid.append({"entry": entry, "exit": exit_, "mode": mode, "year": y, **stats(g)})
        print(f"[wf] {a.entry_rule:<6} {entry:>4g}/{exit_:<3g} {mode:<5}  {len(t):>2} trades  "
              f"net {t['net_points'].sum():+7.1f} pts")

    # ---- anchored walk-forward by year
    folds, oos = [], []
    for y in [int(x) for x in args.test_years.split(",")]:
        start, end = pd.Timestamp(f"{y}-01-01"), pd.Timestamp(f"{y + 1}-01-01")
        combo, fallback = pick(trades, combos, start, args.min_trades)
        t = trades[combo]
        ins, out = t[t["entry_date"] < start], t[(t["entry_date"] >= start) & (t["entry_date"] < end)]
        prior = trades[PRIOR]
        prior_out = prior[(prior["entry_date"] >= start) & (prior["entry_date"] < end)]
        folds.append({"test_year": y, "entry": combo[0], "exit": combo[1], "mode": combo[2],
                      "fallback_to_prior": fallback,
                      **{f"is_{k}": v for k, v in stats(ins).items()},
                      **{f"oos_{k}": v for k, v in stats(out).items()},
                      "prior_oos_net_pts": float(prior_out["net_points"].sum())})
        oos.append(out.assign(test_year=y, combo=f"{combo[0]:g}/{combo[1]:g}/{combo[2]}"))
    folds = pd.DataFrame(folds)
    oos = pd.concat(oos, ignore_index=True)
    first = pd.Timestamp(f"{folds['test_year'].min()}-01-01")

    # ---- single split
    split = pd.Timestamp(args.split)
    s_combo, s_fallback = pick(trades, combos, split, args.min_trades)
    s_t = trades[s_combo]
    s_is, s_oos = stats(s_t[s_t["entry_date"] < split]), stats(s_t[s_t["entry_date"] >= split])

    # every combo's test-period result: where does the picked one rank?
    test_rank = pd.DataFrame([{"combo": c, **stats(t[t["entry_date"] >= split])}
                              for c, t in trades.items() if c in combos]).sort_values("net_pts", ascending=False)
    rank = int(np.flatnonzero(test_rank["combo"].map(lambda c: c == s_combo))[0]) + 1
    share_pos = float((test_rank["net_pts"] > 0).mean())

    args.outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(grid).to_csv(args.outdir / "grid.csv", index=False)
    folds.to_csv(args.outdir / "folds.csv", index=False)
    oos.to_csv(args.outdir / "oos_trades.csv", index=False)

    wf, pr = stats(oos), stats(trades[PRIOR][trades[PRIOR]["entry_date"] >= first])
    lines = [
        "# Walk-forward — long VN30 basket / short VN30F1M",
        "",
        f"Grid: entry {args.entries} × exit {args.exits} × basket {args.modes} "
        f"= {len(combos)} combos. Pick rule: best total net points on trades entered before the "
        f"test window, with at least {args.min_trades} of them; otherwise the pre-registered "
        f"spec {PRIOR[0]:g}/{PRIOR[1]:g}/{PRIOR[2]}.",
        "",
        f"Entry rule: {args.entry_rule}"
        + (" (entry value = buffer over round-trip cost in index points)" if args.entry_rule == "cost" else "")
        + f". Execution: {args.execution}. The prior-spec benchmark uses the points rule "
        f"with the same execution.",
        "",
        "## Anchored walk-forward (train = all history before the test year)",
        "",
        "| test year | picked entry/exit/basket | IS trades | IS net (pts) | OOS trades | "
        "OOS net (pts) | OOS avg basis | OOS avg tracking | prior spec OOS net (pts) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in folds.itertuples():
        tag = " (fallback)" if r.fallback_to_prior else ""
        lines.append(f"| {r.test_year} | {r.entry:g} / {r.exit:g} / {r.mode}{tag} | {r.is_n} | "
                     f"{r.is_net_pts:+.1f} | {r.oos_n} | {r.oos_net_pts:+.1f} | "
                     f"{fmt(r.oos_avg_basis)} | {fmt(r.oos_avg_track)} | {r.prior_oos_net_pts:+.1f} |")
    lines += [
        "",
        "| stitched OOS | trades | avg net (pts) | t-stat | total net (pts) | total net (VND) |",
        "|---|---|---|---|---|---|",
        f"| walk-forward pick | {wf['n']} | {fmt(wf['avg_net'])} | {fmt(wf['t_stat'])} | "
        f"{wf['net_pts']:+.1f} | {wf['net_vnd']:,.0f} |",
        f"| prior spec {PRIOR[0]:g}/{PRIOR[1]:g}/{PRIOR[2]} | {pr['n']} | {fmt(pr['avg_net'])} | "
        f"{fmt(pr['t_stat'])} | {pr['net_pts']:+.1f} | {pr['net_vnd']:,.0f} |",
        "",
        f"## Single split (train < {split.date()}, test ≥ {split.date()})",
        "",
        f"Picked {s_combo[0]:g} / {s_combo[1]:g} / {s_combo[2]}"
        f"{' (fallback)' if s_fallback else ''}: in-sample {s_is['n']} trades, "
        f"{s_is['net_pts']:+.1f} pts; out-of-sample {s_oos['n']} trades, "
        f"{s_oos['net_pts']:+.1f} pts (avg {fmt(s_oos['avg_net'])}, t {fmt(s_oos['t_stat'])}).",
        "",
        f"Its test-period result ranks {rank} of {len(test_rank)} combos; "
        f"{share_pos:.0%} of all combos were net positive in the test period.",
        "",
        "Top 5 combos in the test period (hindsight, for reference only):",
        "",
        "| entry / exit / basket | trades | total net (pts) | avg net | avg tracking |",
        "|---|---|---|---|---|",
    ]
    for r in test_rank.head(5).itertuples():
        c = r.combo
        lines.append(f"| {c[0]:g} / {c[1]:g} / {c[2]} | {r.n} | {r.net_pts:+.1f} | "
                     f"{fmt(r.avg_net)} | {fmt(r.avg_track)} |")
    lines.append("")
    (args.outdir / "FINDINGS.md").write_text("\n".join(lines))

    print(folds[["test_year", "entry", "exit", "mode", "fallback_to_prior", "is_n", "is_net_pts",
                 "oos_n", "oos_net_pts", "prior_oos_net_pts"]].to_string(index=False))
    print(f"[wf] stitched OOS: {wf['n']} trades, avg {fmt(wf['avg_net'])}, t {fmt(wf['t_stat'])}, "
          f"total {wf['net_pts']:+.1f} pts | prior spec {pr['net_pts']:+.1f} pts")
    print(f"[wf] split {split.date()}: pick {s_combo}, IS {s_is['net_pts']:+.1f} ({s_is['n']}), "
          f"OOS {s_oos['net_pts']:+.1f} ({s_oos['n']}), rank {rank}/{len(test_rank)}, "
          f"{share_pos:.0%} combos positive")
    print(f"[wf] wrote {args.outdir}/")


if __name__ == "__main__":
    main()
