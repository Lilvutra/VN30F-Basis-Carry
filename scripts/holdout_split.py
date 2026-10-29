#!/usr/bin/env python3
"""project5 — train / validation / test split for the intraday arbitrage rule.

The walk-forward (walk_forward_intraday.py) scored 2022–2026 out of sample, but the
entry rule was then revised after seeing those years, so they no longer count as
unseen. This script redoes the selection on a fixed protocol, declared here before
it was run:

  periods (by entry date; purged: a trade counts in a period only if it also
  expires before the next period starts, so no outcome leaks across a boundary)
        train       2021-06-01 → 2023-12-31   fit the buffer
        validation  2024-01-01 → 2024-12-31   choose the rule variant
        test        2025-01-01 → data end     scored once, nothing changed after

  candidates (every rule considered in this project, declared up front)
        buffer          0 → 10 pts in 0.5 steps          (fitted on train; the range
                        is set by the cost scale: 10 pts ≈ the whole bar ~30 days out)
        min days        0 (up to expiry day), 7
        vol cap         none, 25%, 20%                  (all entries)
        late vol cap    none, 25% when dte < 7          (only with min days 0, no vol cap)
        futures spread  none, ≤ 0.5 pts
        last signal     none, 14:15
     the fill delay is an execution assumption, not a parameter: fixed at --delay
     (5 s), with the frozen rule re-scored at --sens-delays for comparison.

  protocol
     1. train: for each variant, buffer = highest total net with ≥ --min-trades trades
     2. validation: score each variant with its train buffer; pick the highest
        validation total net with ≥ --min-trades trades; ties go to the variant
        with fewer filters, then the lower buffer
     3. refit the buffer of the chosen variant on train + validation
     4. test: trade the test period once with that rule; report whatever comes out

Caveat: the analyst had already seen 2022–2026 results before writing this, so the
split limits but cannot remove that knowledge. Paper trading after the data end is
the only untouched test.

Trigger fills come from the walk-forward's cache (data/raw/wfi_fills_delay{d}.parquet),
filled from the database for any trigger minute it lacks.

Outputs (--outdir, default result/holdout_split/):
  variants.csv   every variant: train buffer, train/validation results
  test_trades.csv the test trades of the frozen rule
  FINDINGS.md

Usage:
    python scripts/holdout_split.py
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from basis_backtest import load_basket, load_futures, load_members
from intraday_check import SESSION, minute_basis
from walk_forward_intraday import fill_and_hold

PERIODS = {"train": ("2021-06-01", "2023-12-31"),
           "validation": ("2024-01-01", "2024-12-31"),
           "test": ("2025-01-01", "2099-12-31")}
# 0 → 10 pts in 0.5 steps: 10 pts is about the whole bar ~30 days before expiry, a range set
# by the cost scale, not by any result (the step-4 exploration had found 3 on the whole sample)
BUFFERS = [x / 2 for x in range(21)]
VARIANTS = [dict(min_days=md, vol_cap=vc, late_cap=lc, max_spread=sp, last_signal=ls)
            for md, vc, lc, sp, ls in itertools.product([0, 7], [0, 25, 20], [0, 25], [0, 0.5], ["", "14:15"])
            if not (lc and (md >= 7 or vc))]                  # the late cap is redundant there


def describe(v: dict) -> str:
    parts = ["up to expiry day" if v["min_days"] == 0 else f"≥ {v['min_days']} days"]
    if v["vol_cap"]:
        parts.append(f"vol < {v['vol_cap']:g}%")
    if v["late_cap"]:
        parts.append(f"vol < {v['late_cap']:g}% when < 7 days")
    if v["max_spread"]:
        parts.append(f"fut spread ≤ {v['max_spread']:g}")
    if v["last_signal"]:
        parts.append(f"signals ≤ {v['last_signal']}")
    return ", ".join(parts)


def n_filters(v: dict) -> int:
    return sum(bool(v[k]) for k in ("vol_cap", "late_cap", "max_spread", "last_signal")) + (v["min_days"] > 0)


def stats(x: pd.Series) -> dict:
    return {"n": len(x), "total": x.sum(), "mean": x.mean() if len(x) else np.nan,
            "t": x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan,
            "share_pos": (x > 0).mean() if len(x) else np.nan}


def main() -> None:
    ap = argparse.ArgumentParser(description="Train / validation / test split of the intraday rule.")
    ap.add_argument("--futures", type=Path, default=Path("data/raw/vn30f_frontmonth.parquet"))
    ap.add_argument("--basket", type=Path, default=Path("data/raw/vn30_basket_prices.parquet"))
    ap.add_argument("--membership", type=Path, default=Path("data/raw/vn30_membership.parquet"))
    ap.add_argument("--minute-sql", type=Path, default=Path("sql/intraday_basis_minute.sql"))
    ap.add_argument("--minute-cache", type=Path, default=Path("data/raw/intraday_basis_minute.parquet"))
    ap.add_argument("--outdir", type=Path, default=Path("result/holdout_split"))
    ap.add_argument("--fee-bps", type=float, default=17.0)
    ap.add_argument("--rate", type=float, default=0.045)
    ap.add_argument("--delay", type=int, default=5)
    ap.add_argument("--sens-delays", default="30,60")
    ap.add_argument("--fit-window", type=int, default=120)
    ap.add_argument("--max-quote-gap", type=float, default=0.03)
    ap.add_argument("--min-quoted", type=float, default=0.9)
    ap.add_argument("--min-trades", type=int, default=3)
    ap.add_argument("--multiplier", type=float, default=100000.0)
    args = ap.parse_args()
    bounds = {k: (pd.Timestamp(a), pd.Timestamp(b)) for k, (a, b) in PERIODS.items()}

    fut = load_futures(args.futures)
    expiry = fut.groupby("contract")["expdate"].first()
    last_day = fut.groupby("contract")["date"].max()
    trading = set(fut["date"])
    expiry = pd.Series({c: d if (d in trading or d > fut["date"].max()) else last_day[c]
                        for c, d in expiry.items()})
    fut = fut.assign(expdate=fut["contract"].map(expiry))
    adj, _, raw, _ = load_basket(args.basket)
    snaps = load_members(args.membership)
    daily = fut.drop_duplicates("date").set_index("date")["vn30_index"].sort_index()
    vol20 = daily.pct_change().rolling(20).std().shift(1) * np.sqrt(252) * 100

    m = minute_basis(args.minute_sql, args.minute_cache, range(2021, 2027))
    m["minute"] = pd.to_datetime(m["minute"])
    m["date"] = m["minute"].dt.normalize()
    tod = m["minute"].dt.time
    m = m[np.logical_or.reduce([(tod >= a) & (tod <= b) for a, b in SESSION])].copy()
    m["expdate"] = m["contract"].map(expiry)
    m["dte"] = (m["expdate"] - m["date"]).dt.days
    m["disp"] = m["fut_last"] - m["vn30"]
    m["bar"] = m["vn30"] * (args.fee_bps / 1e4 + args.rate * m["dte"] / 365)

    # first trigger minute of each day per (buffer, min days, last signal)
    trig = {}
    for b, md, ls in itertools.product(BUFFERS, {v["min_days"] for v in VARIANTS},
                                       {v["last_signal"] for v in VARIANTS}):
        x = m[(m["dte"] >= md) & (m["disp"] - m["bar"] >= b)]
        if ls:
            x = x[x["minute"].dt.time <= pd.Timestamp(ls).time()]
        trig[b, md, ls] = set(x.groupby("date").head(1)["minute"])
    need = m[m["minute"].isin(set().union(*trig.values()))].drop_duplicates("minute")

    def fills_for(delay: int, minutes: pd.DataFrame) -> pd.DataFrame:
        args.delay = delay
        path = Path(f"data/raw/wfi_fills_delay{delay}.parquet")
        cache = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        done = set(pd.to_datetime(cache["minute"])) if len(cache) else set()
        todo = minutes[~minutes["minute"].isin(done)]
        print(f"[holdout] delay {delay}s: {len(minutes)} trigger minutes, {len(todo)} to fill", flush=True)
        rows = []
        for n, r in enumerate(todo.itertuples(), 1):
            rows.append(fill_and_hold(r, raw, adj, snaps, fut, args))
            if n % 25 == 0 or n == len(todo):
                print(f"[holdout] {n}/{len(todo)}", flush=True)
                pd.concat([cache, pd.DataFrame(rows)], ignore_index=True).to_parquet(path)
        if rows:
            cache = pd.concat([cache, pd.DataFrame(rows)], ignore_index=True)
        f = cache.copy()
        f["minute"] = pd.to_datetime(f["minute"])
        f = f.drop_duplicates("minute").set_index("minute").sort_index()
        f["date"] = pd.to_datetime(f["date"])
        f["expdate"] = f["contract"].map(expiry)
        f["bar"] = f["vn30"] * (args.fee_bps / 1e4 + args.rate * f["dte"] / 365)
        f["edge"] = f["exec"] - f["bar"]
        f["fees"] = f["vn30"] * args.fee_bps / 1e4
        f["carry"] = f["vn30"] * args.rate * f["dte"] / 365
        f["cash"] = f["fut_pnl"] + f["basket_pnl"] - f["fees"]
        f["net"] = f["cash"] - f["carry"]
        f["track"] = f["net"] - f["edge"]
        f["vol20"] = f["date"].map(vol20)
        f["valid"] = (f["fill_in_session"] & (f["fut_spread"] > 0)
                      & (f["weight_quoted"] >= args.min_quoted) & f["exec"].notna())
        return f

    def trades(f: pd.DataFrame, v: dict, b: float) -> pd.DataFrame:
        t = f[f.index.isin(trig[b, v["min_days"], v["last_signal"]]) & f["valid"]]
        if v["vol_cap"]:
            t = t[t["vol20"] < v["vol_cap"]]
        if v["late_cap"]:
            t = t[(t["dte"] >= 7) | (t["vol20"] < v["late_cap"])]
        if v["max_spread"]:
            t = t[t["fut_spread"] <= v["max_spread"]]
        return t.groupby("contract").head(1)                    # one position per contract

    def period(t: pd.DataFrame, *names: str) -> pd.DataFrame:
        """Closed trades entered in the named periods and expired before the next one starts."""
        lo, hi = bounds[names[0]][0], bounds[names[-1]][1]
        return t[(t["date"] >= lo) & (t["date"] <= hi) & (t["expdate"] <= hi) & t["net"].notna()]

    def fit_buffer(f: pd.DataFrame, v: dict, *names: str):
        best = None
        for b in BUFFERS:
            s = period(trades(f, v, b), *names)["net"]
            if len(s) >= args.min_trades and (best is None or s.sum() > best[1]):
                best = (b, s.sum(), len(s))
        return best

    delay = args.delay
    f = fills_for(delay, need)
    rows = []
    for i, v in enumerate(VARIANTS):
        fit = fit_buffer(f, v, "train")
        if fit is None:
            continue
        b, tr_total, tr_n = fit
        val = stats(period(trades(f, v, b), "validation")["net"])
        rows.append({"variant": i, "rule": describe(v), "filters": n_filters(v), "buffer": b,
                     "train_n": tr_n, "train_total": tr_total, "val_n": val["n"],
                     "val_total": val["total"], "val_mean": val["mean"]})
    var = pd.DataFrame(rows)
    ok = var[var["val_n"] >= args.min_trades]
    pick = ok.sort_values(["val_total", "filters", "buffer"], ascending=[False, True, True]).iloc[0]
    v = VARIANTS[int(pick["variant"])]
    b_final, tv_total, tv_n = fit_buffer(f, v, "train", "validation")

    test = period(trades(f, v, b_final), "test")
    open_n = int(trades(f, v, b_final).pipe(lambda t: t[(t["date"] >= bounds["test"][0]) & t["net"].isna()]).shape[0])
    ts = stats(test["net"])
    sens = []
    for d in [int(x) for x in args.sens_delays.split(",") if x]:
        mins = need[need["minute"].isin(trig[b_final, v["min_days"], v["last_signal"]])]
        s = stats(period(trades(fills_for(d, mins), v, b_final), "test")["net"])
        sens.append((d, s))

    # the rule adopted earlier (up to expiry day, buffer 3, no filters) on the same test period
    adopted = stats(period(trades(f, VARIANTS[0], 3.0), "test")["net"])

    args.outdir.mkdir(parents=True, exist_ok=True)
    var.sort_values("val_total", ascending=False).to_csv(args.outdir / "variants.csv", index=False)
    test.reset_index().to_csv(args.outdir / "test_trades.csv", index=False)

    vnd = args.multiplier / 1e6
    top = var.sort_values(["val_total", "filters", "buffer"], ascending=[False, True, True]).head(10)
    end = test["expdate"].max().date() if len(test) else "-"
    lines = [
        "# Train / validation / test split of the intraday rule", "",
        f"Fees {args.fee_bps:g} bps round trip, carry {args.rate:.1%}, fill {delay} s "
        "after the signal at bid/ask, 1 contract, one position per contract, held to expiry. "
        "Periods by entry date, purged: a trade counts only if it expires inside its period.", "",
        "| period | dates | role |", "|---|---|---|",
        f"| train | {PERIODS['train'][0]} → {PERIODS['train'][1]} | fit the buffer per variant |",
        f"| validation | {PERIODS['validation'][0]} → {PERIODS['validation'][1]} | choose the variant |",
        f"| test | {PERIODS['test'][0]} → {end} (last expiry) | scored once with the frozen rule |", "",
        f"{len(VARIANTS)} variants × {len(BUFFERS)} buffers declared before the run; "
        f"{len(var)} had ≥ {args.min_trades} train trades, {len(ok)} also ≥ {args.min_trades} validation trades.", "",
        "## Validation: top 10 variants (buffer fitted on train)", "",
        "| rule | filters | buffer | train trades | train total | val trades | val total | val mean |",
        "|---|---|---|---|---|---|---|---|",
        *[f"| {x.rule} | {x.filters} | {x.buffer:g} | {x.train_n} | {x.train_total:+.1f} | {x.val_n} "
          f"| {x.val_total:+.1f} | {x.val_mean:+.2f} |" for x in top.itertuples()],
        "", f"**Chosen: {describe(v)}; buffer refitted on train + validation = {b_final:g} "
        f"({tv_n} trades, {tv_total:+.1f}).**", "",
        "## Test (scored once)", "",
        "| delay | trades | total | mean | t | >0 |", "|---|---|---|---|---|---|",
        f"| {delay} s | {ts['n']} | {ts['total']:+.1f} | {ts['mean']:+.2f} | {ts['t']:+.2f} | {ts['share_pos']:.0%} |",
        *[f"| {d} s | {s['n']} | {s['total']:+.1f} | {s['mean']:+.2f} | {s['t']:+.2f} | {s['share_pos']:.0%} |"
          for d, s in sens],
        "",
        (f"Test at {delay} s: {ts['total'] * vnd:+.1f}m VND per contract over the period; "
         f"edge (exec − bar) {test['edge'].mean():+.2f} (t {stats(test['edge'])['t']:+.1f}), tracking {test['track'].mean():+.2f}. "
         f"Open trades not yet expired: {open_n}.") if len(test) else "No test trades.",
        "",
        f"For comparison only (picked after seeing 2022–2026): the earlier adopted rule (up to expiry day, "
        f"buffer 3, no filters) on the same test period: {adopted['n']} trades, {adopted['total']:+.1f}, "
        f"mean {adopted['mean']:+.2f}.",
        "", "Caveat: the analyst had seen these years before the split, so the test is cleaner than the "
        "walk-forward but not untouched. Paper trading after the data end is the only clean test.",
    ]
    (args.outdir / "FINDINGS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
