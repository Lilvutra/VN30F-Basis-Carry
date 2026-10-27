#!/usr/bin/env python3
"""project5 — steps 5–6 for the intraday arbitrage rule: walk-forward + full lifecycle.

The intraday check (intraday_check.py) showed +1.73 pts/trade at fund fees with a
buffer of 3, but that buffer was picked after seeing the whole sample, and the
edge (exec − bar) treated the basket's tracking until expiry as zero. Here:

  1. triggers for every buffer in --buffers: the first session minute of a day with
        displayed basis − bar ≥ buffer, dte ≥ --min-days-expiry,
        bar = VN30 × (fee_bps/1e4 + rate × dte/365);
     optional volatility filter: trailing 20-session VN30 vol (annualised, known
     before the day) below a cap in --vol-caps (0 = no filter);
  2. one position per contract: the first trigger of the contract that passes;
  3. each trade's full lifecycle, 1 contract:
        entry  --delay s after the signal: sell the future at its best bid, buy the
               fit-weighted basket at each name's best ask (same quote checks as
               intraday_check.py);
        hold   to expiry; the futures leg is marked daily on the futures close to
               measure the margin top-up the short needs (in points);
        exit   the future settles at the VN30 close on expiry day, the basket is
               sold at each name's close (ATC), dividends included via the
               adjusted/raw close ratio;
        cash   = futures P&L + basket P&L − fees
        net    = cash − carry (VN30 × rate × dte/365, the deposit the capital forgoes)
        track  = net − (exec − bar)       (the basket-vs-index drift while held)
  4. anchored yearly walk-forward: for each test year, pick (buffer, vol cap) with
     the highest total net in all earlier data (≥ --min-trades trades), trade the
     test year with it. Fixed combos are reported for comparison only.

Outputs (--outdir, default result/walkforward_intraday/):
  fills.parquet  cached fills + lifecycle per trigger minute (reused across runs)
  trades.csv     every combo's trades
  grid.csv       every combo, per year
  folds.csv      the pick per test year and its OOS result
  oos_trades.csv the stitched out-of-sample trades
  FINDINGS.md

Usage:
    python scripts/walk_forward_intraday.py   # fund fees 17 bps, rate 4.5 %
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from basis_backtest import fit_weights, load_basket, load_futures, load_members, members_on
from intraday_check import SESSION, SESSION_FILL, asof, minute_basis, quotes


def fill_and_hold(r, raw, adj, snaps, fut, args) -> dict:
    """Entry at the quotes --delay s after the signal minute, held to expiry."""
    ts = r.minute + pd.Timedelta(seconds=59)
    tf = ts + pd.Timedelta(seconds=args.delay)
    prev = raw.index[raw.index < r.date]
    w = fit_weights(raw, prev[-1], members_on(snaps, r.date), args.fit_window)
    q = quotes(w.index, r.contract, r.date.date(), tf)
    last0 = asof(q, "last", ts).reindex(w.index)
    ask, bid = asof(q, "ask", tf), asof(q, "bid", tf)
    sa, sb = ask.reindex(w.index), bid.reindex(w.index)
    ok = (sa.notna() & sb.notna() & last0.notna() & (sb > 0) & (sa > sb)
          & ((sa / last0 - 1).abs() <= args.max_quote_gap))
    out = {"date": r.date, "minute": r.minute, "contract": r.contract, "dte": r.dte,
           "vn30": r.vn30, "disp": r.disp, "weight_quoted": float(w[ok].sum()),
           "fill_in_session": any(a <= tf.time() <= b for a, b in SESSION_FILL)}
    f_bid, f_ask = bid.get(r.contract, np.nan), ask.get(r.contract, np.nan)
    out["fut_spread"] = f_ask - f_bid
    if not ok.any() or pd.isna(f_bid):
        return out
    ww = w[ok] / w[ok].sum()
    exec_ = f_bid - r.vn30 * float((ww * sa[ok] / last0[ok]).sum())

    exp = r.expdate
    if exp not in raw.index:                                   # contract not expired yet
        return {**out, "exec": exec_}
    names = ww.index
    close_t = raw.loc[:exp, names].ffill().loc[exp]
    g = ((adj.loc[exp, names] / raw.loc[exp, names])
         / (adj.loc[r.date, names] / raw.loc[r.date, names])).fillna(1.0)   # dividends
    fsp = float(fut.loc[fut["date"] == exp, "vn30_index"].iloc[0])
    basket_pnl = r.vn30 * float((ww * (close_t * g - sa[ok]) / last0[ok]).sum())
    fut_pnl = f_bid - fsp
    hold = fut[(fut["date"] > r.date) & (fut["date"] <= exp) & (fut["contract"] == r.contract)]
    worst = float(np.maximum(hold["fut_close"].max() - f_bid, 0)) if len(hold) else 0.0
    return {**out, "exec": exec_, "fsp": fsp, "fut_pnl": fut_pnl, "basket_pnl": basket_pnl,
            "margin_topup": worst}


def main() -> None:
    ap = argparse.ArgumentParser(description="Walk-forward of the intraday arbitrage rule.")
    ap.add_argument("--futures", type=Path, default=Path("data/raw/vn30f_frontmonth.parquet"))
    ap.add_argument("--basket", type=Path, default=Path("data/raw/vn30_basket_prices.parquet"))
    ap.add_argument("--membership", type=Path, default=Path("data/raw/vn30_membership.parquet"))
    ap.add_argument("--minute-sql", type=Path, default=Path("sql/intraday_basis_minute.sql"))
    ap.add_argument("--minute-cache", type=Path, default=Path("data/raw/intraday_basis_minute.parquet"))
    ap.add_argument("--fills-cache", type=Path, default=Path("data/raw/walkforward_intraday_fills.parquet"))
    ap.add_argument("--outdir", type=Path, default=Path("result/walkforward_intraday"))
    ap.add_argument("--fee-bps", type=float, default=17.0)
    ap.add_argument("--rate", type=float, default=0.045)
    ap.add_argument("--buffers", default="0,1,2,3,4,5")
    ap.add_argument("--vol-caps", default="0,25,20", help="annualised %%; 0 = no filter.")
    ap.add_argument("--min-days-expiry", type=int, default=7)
    ap.add_argument("--delay", type=int, default=60)
    ap.add_argument("--fit-window", type=int, default=120)
    ap.add_argument("--max-quote-gap", type=float, default=0.03)
    ap.add_argument("--min-quoted", type=float, default=0.9)
    ap.add_argument("--min-trades", type=int, default=3)
    ap.add_argument("--test-years", default="2022,2023,2024,2025,2026")
    ap.add_argument("--multiplier", type=float, default=100000.0)
    args = ap.parse_args()
    buffers = [float(x) for x in args.buffers.split(",")]
    caps = [float(x) for x in args.vol_caps.split(",")]
    test_years = [int(x) for x in args.test_years.split(",")]

    fut = load_futures(args.futures)
    expiry = fut.groupby("contract")["expdate"].first()
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
    m = m[m["dte"] >= args.min_days_expiry]
    trig = {b: m[m["disp"] - m["bar"] >= b].groupby("date").head(1) for b in buffers}
    need = pd.concat(trig.values()).drop_duplicates("minute")

    cache = pd.read_parquet(args.fills_cache) if args.fills_cache.exists() else pd.DataFrame()
    done = set(pd.to_datetime(cache["minute"])) if len(cache) else set()
    todo = need[~need["minute"].isin(done)]
    print(f"[wf-intraday] {len(need)} trigger minutes, {len(todo)} to fill", flush=True)
    rows = []
    for n, r in enumerate(todo.itertuples(), 1):
        rows.append(fill_and_hold(r, raw, adj, snaps, fut, args))
        if n % 25 == 0:
            print(f"[wf-intraday] {n}/{len(todo)}", flush=True)
            part = pd.concat([cache, pd.DataFrame(rows)], ignore_index=True)
            args.fills_cache.parent.mkdir(parents=True, exist_ok=True)
            part.to_parquet(args.fills_cache)
    fills = pd.concat([cache, pd.DataFrame(rows)], ignore_index=True)
    fills.to_parquet(args.fills_cache)
    fills["minute"] = pd.to_datetime(fills["minute"])
    fills = fills.drop_duplicates("minute").set_index("minute")

    # lifecycle P&L under this run's fee and rate
    f = fills.copy()
    f["bar"] = f["vn30"] * (args.fee_bps / 1e4 + args.rate * f["dte"] / 365)
    f["edge"] = f["exec"] - f["bar"]
    f["fees"] = f["vn30"] * args.fee_bps / 1e4
    f["carry"] = f["vn30"] * args.rate * f["dte"] / 365
    f["cash"] = f["fut_pnl"] + f["basket_pnl"] - f["fees"]
    f["net"] = f["cash"] - f["carry"]
    f["track"] = f["net"] - f["edge"]
    f["valid"] = (f["fill_in_session"] & (f["fut_spread"] > 0)
                  & (f["weight_quoted"] >= args.min_quoted) & f["exec"].notna())
    f["vol20"] = pd.to_datetime(f["date"]).map(vol20)

    trades = []
    for b in buffers:
        t = f.loc[f.index.isin(trig[b]["minute"])]
        for cap in caps:
            s = t[t["valid"] & ((cap == 0) | (t["vol20"] < cap))]
            s = s.sort_index().groupby("contract").head(1)          # one position per contract
            trades.append(s.assign(buffer=b, vol_cap=cap))
    trades = pd.concat(trades).reset_index()
    trades["year"] = pd.to_datetime(trades["date"]).dt.year
    closed = trades[trades["net"].notna()]

    def stats(x: pd.Series) -> pd.Series:
        return pd.Series({"n": len(x), "total": x.sum(), "mean": x.mean(),
                          "t": x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan,
                          "share_pos": (x > 0).mean()})

    grid = closed.groupby(["buffer", "vol_cap"])["net"].apply(stats).unstack()
    by_year = closed.pivot_table(index=["buffer", "vol_cap"], columns="year", values="net", aggfunc="sum")

    folds, oos = [], []
    for y in test_years:
        train = closed[closed["year"] < y]
        g = train.groupby(["buffer", "vol_cap"])["net"].agg(["count", "sum"])
        g = g[g["count"] >= args.min_trades]
        if g.empty:
            continue
        b, cap = g["sum"].idxmax()
        test = closed[(closed["year"] == y) & (closed["buffer"] == b) & (closed["vol_cap"] == cap)]
        oos.append(test)
        folds.append({"test_year": y, "buffer": b, "vol_cap": cap, "train_n": int(g.loc[(b, cap), "count"]),
                      "train_total": g.loc[(b, cap), "sum"], "test_n": len(test),
                      "test_total": test["net"].sum(), "test_mean": test["net"].mean(),
                      "test_edge": test["edge"].mean(), "test_track": test["track"].mean()})
    folds = pd.DataFrame(folds)
    oos = pd.concat(oos) if oos else closed.iloc[:0]
    o = stats(oos["net"]) if len(oos) else pd.Series(dtype=float)

    args.outdir.mkdir(parents=True, exist_ok=True)
    trades.to_csv(args.outdir / "trades.csv", index=False)
    pd.concat([grid, by_year], axis=1).to_csv(args.outdir / "grid.csv")
    folds.to_csv(args.outdir / "folds.csv", index=False)
    oos.to_csv(args.outdir / "oos_trades.csv", index=False)

    vnd = args.multiplier / 1e6
    lines = [
        "# Walk-forward of the intraday arbitrage rule (steps 5–6)", "",
        f"Fees {args.fee_bps:g} bps round trip, carry rate {args.rate:.1%}, fill {args.delay} s after the "
        f"signal at bid/ask, 1 contract, one position per contract, held to expiry (future at the "
        f"VN30 close, basket at its closes, dividends in). net = cash − carry; track = net − (exec − bar).",
        "", "## Out-of-sample (anchored yearly; pick = best total net in all earlier years)", "",
        "| test year | buffer | vol cap | train trades | test trades | test total | mean | edge | track |",
        "|---|---|---|---|---|---|---|---|---|",
        *[f"| {x.test_year} | {x.buffer:g} | {'none' if x.vol_cap == 0 else f'{x.vol_cap:g}%'} | {x.train_n} "
          f"| {x.test_n} | {x.test_total:+.2f} | {x.test_mean:+.2f} | {x.test_edge:+.2f} | {x.test_track:+.2f} |"
          for x in folds.itertuples()],
        "",
        (f"**Stitched OOS: {int(o['n'])} trades, total {o['total']:+.1f} pts "
         f"({o['total'] * vnd:+.1f}m VND per contract), mean {o['mean']:+.2f}, t {o['t']:+.2f}, "
         f"{o['share_pos']:.0%} positive.**") if len(oos) else "No OOS trades.",
        "", "## Every combo, whole sample (comparison only: not out-of-sample)", "",
        "| buffer | vol cap | trades | total | mean | t | >0 |", "|---|---|---|---|---|---|---|",
        *[f"| {b:g} | {'none' if c == 0 else f'{c:g}%'} | {int(x.n)} | {x.total:+.1f} | {x['mean']:+.2f} "
          f"| {x.t:+.2f} | {x.share_pos:.0%} |" for (b, c), x in grid.iterrows()],
        "", "## Lifecycle of the OOS trades", "",
        f"edge (exec − bar) {oos['edge'].mean():+.2f}, tracking until expiry {oos['track'].mean():+.2f} "
        f"(std {oos['track'].std():.2f}), cash {oos['cash'].mean():+.2f}, carry {oos['carry'].mean():.2f}. "
        f"Margin top-up on the short future: mean {oos['margin_topup'].mean():.1f} pts, "
        f"max {oos['margin_topup'].max():.1f} pts ({oos['margin_topup'].max() * vnd:.1f}m VND per contract)."
        if len(oos) else "",
        "", f"Open (unexpired) trades excluded: {int(trades['net'].isna().sum())} combo-rows.",
    ]
    (args.outdir / "FINDINGS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
