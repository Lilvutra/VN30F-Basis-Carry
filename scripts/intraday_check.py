#!/usr/bin/env python3
"""project5 — step 1 intraday check: is the on-screen basis actually capturable?

The daily backtest only made money when it filled at the same close that produced
the signal; at the next 09:15 open the basis was gone. This asks the intraday
version of the question, without a full backtest:

  1. per-minute displayed basis = last futures trade − last VN30 print, front month,
     continuous session only (09:16–11:29, 13:00–14:29);
  2. a trigger is the first minute of a day where
        displayed basis − bar ≥ --buffer,
        bar = VN30 × (fees + carry) = VN30 × (--fee-bps/1e4 + --rate × dte/365);
     fees are the round trip without slippage (stock 12+12, sell tax 10, futures
     3+3 = 40 bps): slippage is replaced by actually crossing the spread below.
     Carry is the fair premium a future earns over the index for tying up no cash,
     which the daily backtest ignored;
  3. at each trigger, after --delays seconds, the CAPTURABLE basis:
        exec = futures best bid − VN30(t) × Σ w_i · ask_i / last_i(t)
     i.e. sell the future at the bid and buy the fit-weighted basket at the ask,
     relative to the stock prices behind the VN30 print at the signal. `mid` is the
     same with mid quotes, so (disp − mid) = market move + index staleness during the
     delay, and (mid − exec) = half-spreads paid;
  4. holding to expiry settles the basis to 0 (stocks sold in the expiry ATC, no
     spread), so expected net per trade ≈ exec − bar, tracking noise aside.

Outputs (--outdir, default result/intraday/):
  events.csv     one row per trigger day × delay
  summary.csv    by delay: counts, displayed/mid/exec/bar/edge, share with edge > 0
  FINDINGS.md    the verdict

Usage:
    python scripts/intraday_check.py \
        --futures data/raw/vn30f_frontmonth.parquet \
        --basket data/raw/vn30_basket_prices.parquet \
        --membership data/raw/vn30_membership.parquet
"""
from __future__ import annotations

import argparse
from datetime import time
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl

from basis_backtest import fit_weights, load_basket, load_futures, load_members, members_on
from download_data import _clean_sql, build_uri

SESSION = [(time(9, 16), time(11, 29)), (time(13, 0), time(14, 29))]
SESSION_FILL = [(time(9, 15, 30), time(11, 30)), (time(13, 0), time(14, 30))]   # continuous matching


def query(sql: str) -> pd.DataFrame:
    return pl.read_database_uri(query=_clean_sql(sql), uri=build_uri()).to_pandas()


def minute_basis(sql_path: Path, cache: Path, years) -> pd.DataFrame:
    if cache.exists():
        return pd.read_parquet(cache)
    tmpl, parts = sql_path.read_text(), []
    for y in years:
        start = "2021-06-01" if y == 2021 else f"{y}-01-01"
        print(f"[intraday] minute basis {y} ...", flush=True)
        parts.append(query(tmpl.format(start=start, end=f"{y + 1}-01-01")))
    m = pd.concat(parts, ignore_index=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    m.to_parquet(cache)
    return m


def quotes(tickers, contract, day, until) -> pd.DataFrame:
    """Every top-3 book change (price and size, bid and ask) and every trade of the
    basket names, the contract and VN30 from 09:00 to `until`. Books are stored as
    changes per depth level, so the state at t is the last row per (ticker, depth)."""
    names = ",".join(f"'{t}'" for t in list(tickers) + [contract, "VN30"])
    lo, hi = f"{day} 09:00", until.strftime("%Y-%m-%d %H:%M:%S")
    where = f"WHERE tickersymbol IN ({names}) AND datetime >= '{lo}' AND datetime <= '{hi}'"
    sql = " UNION ALL ".join(
        [f"SELECT '{side}' AS side, tickersymbol AS ticker, datetime, {col}::double precision AS p, "
         f"depth::int AS depth FROM quote.{table} {where} AND depth <= 3"
         for side, table, col in [("ask", "askprice", "price"), ("bid", "bidprice", "price"),
                                  ("asksz", "asksize", "quantity"), ("bidsz", "bidsize", "quantity")]]
        + [f"SELECT 'last', tickersymbol, datetime, price::double precision, 0 FROM quote.matched {where}"])
    q = query(sql)
    q["datetime"] = pd.to_datetime(q["datetime"])
    return q.sort_values("datetime")


def asof(q: pd.DataFrame, side: str, ts, depth: int = 1) -> pd.Series:
    s = q[(q["side"] == side) & (q["datetime"] <= ts) & (q["depth"] == (0 if side == "last" else depth))]
    return s.groupby("ticker")["p"].last()


def book(q: pd.DataFrame, side: str, ts) -> pd.DataFrame:
    """(ticker, depth) → price, size for one side of the book at ts."""
    s = q[(q["side"].isin([side, side + "sz"])) & (q["datetime"] <= ts) & (q["depth"] >= 1)]
    s = s.groupby(["ticker", "depth", "side"])["p"].last().unstack("side")
    return s.rename(columns={side: "price", side + "sz": "size"}).reindex(columns=["price", "size"])


def walk(levels: pd.DataFrame | None, qty: float) -> float:
    """Average fill price for `qty` taken through the visible levels; NaN if the top 3
    levels do not hold enough."""
    if levels is None or qty <= 0:
        return np.nan
    lv = levels.dropna().sort_index()
    lv = lv[(lv["price"] > 0) & (lv["size"] > 0)]
    take = np.minimum(lv["size"].to_numpy(), np.maximum(qty - (lv["size"].cumsum() - lv["size"]).to_numpy(), 0))
    return float((take * lv["price"].to_numpy()).sum() / qty) if take.sum() >= qty - 1e-9 else np.nan


def main() -> None:
    ap = argparse.ArgumentParser(description="Intraday capturable-basis check.")
    ap.add_argument("--futures", type=Path, required=True)
    ap.add_argument("--basket", type=Path, required=True)
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--minute-sql", type=Path, default=Path("sql/intraday_basis_minute.sql"))
    ap.add_argument("--minute-cache", type=Path, default=Path("data/raw/intraday_basis_minute.parquet"))
    ap.add_argument("--outdir", type=Path, default=Path("result/intraday"))
    ap.add_argument("--fee-bps", type=float, default=40.0, help="round-trip fees+tax, no slippage.")
    ap.add_argument("--rate", type=float, default=0.045, help="annual funding rate for carry.")
    ap.add_argument("--buffer", type=float, default=0.0, help="trigger: displayed − bar ≥ this (pts).")
    ap.add_argument("--min-days-expiry", type=int, default=7)
    ap.add_argument("--delays", default="0,30,60,120", help="seconds from signal to fill.")
    ap.add_argument("--fit-window", type=int, default=120)
    ap.add_argument("--sizes", default="1", help="contracts per trade; the book is walked 3 levels deep.")
    ap.add_argument("--multiplier", type=float, default=100000.0, help="VND per index point.")
    ap.add_argument("--depth-from", default="2023-01-03",
                    help="first date with order-book sizes; the by-size table starts here.")
    ap.add_argument("--max-quote-gap", type=float, default=0.03,
                    help="drop a stock quote whose ask is further than this from its last trade.")
    ap.add_argument("--min-quoted", type=float, default=0.9,
                    help="drop an event if less than this share of basket weight is quotable.")
    args = ap.parse_args()
    delays = [int(x) for x in args.delays.split(",")]
    sizes = [int(x) for x in args.sizes.split(",")]

    fut = load_futures(args.futures)
    expiry = fut.groupby("contract")["expdate"].first()
    _, _, raw, _ = load_basket(args.basket)
    snaps = load_members(args.membership)

    m = minute_basis(args.minute_sql, args.minute_cache, range(2021, 2027))
    m["minute"] = pd.to_datetime(m["minute"])
    m["date"] = m["minute"].dt.normalize()
    tod = m["minute"].dt.time
    m = m[np.logical_or.reduce([(tod >= a) & (tod <= b) for a, b in SESSION])].copy()
    m["dte"] = (m["contract"].map(expiry) - m["date"]).dt.days
    m["disp"] = m["fut_last"] - m["vn30"]
    m["bar"] = m["vn30"] * (args.fee_bps / 1e4 + args.rate * m["dte"] / 365)
    trig = m[(m["dte"] >= args.min_days_expiry) & (m["disp"] - m["bar"] >= args.buffer)]
    trig = trig.groupby("date").head(1)
    print(f"[intraday] {m['date'].nunique()} days, {len(m)} session minutes; "
          f"{len(trig)} trigger days", flush=True)

    rows = []
    for n, r in enumerate(trig.itertuples(), 1):
        ts = r.minute + pd.Timedelta(seconds=59)            # the minute's last print
        prev = raw.index[raw.index < r.date]
        w = fit_weights(raw, prev[-1], members_on(snaps, r.date), args.fit_window)
        q = quotes(w.index, r.contract, r.date.date(), ts + pd.Timedelta(seconds=max(delays)))
        last0 = asof(q, "last", ts).reindex(w.index)
        idx0 = r.vn30
        for d in delays:
            tf = ts + pd.Timedelta(seconds=d)
            ask, bid = asof(q, "ask", tf), asof(q, "bid", tf)
            fl = asof(q, "last", tf)
            sa, sb = ask.reindex(w.index), bid.reindex(w.index)
            # a usable quote: two-sided, not crossed, near the last trade. A stock locked
            # at its ceiling has no real ask (you cannot buy it), so it fails this too.
            ok = (sa.notna() & sb.notna() & last0.notna() & (sb > 0) & (sa > sb)
                  & ((sa / last0 - 1).abs() <= args.max_quote_gap))
            ww = w[ok] / w[ok].sum()
            f_bid, f_ask = bid.get(r.contract, np.nan), ask.get(r.contract, np.nan)
            mid = ((f_bid + f_ask) / 2
                   - idx0 * float((ww * (sa[ok] + sb[ok]) / 2 / last0[ok]).sum()))
            asks, bids = book(q, "ask", tf), book(q, "bid", tf)
            for size in sizes:
                if size == 1:                    # one contract: top of book, as in the base check
                    fills, f_fill = sa[ok], f_bid
                else:
                    # shares of each name for `size` contracts of notional (prices in '000 VND)
                    need = ww * size * idx0 * args.multiplier / (last0[ok] * 1000)
                    lv = asks.index.get_level_values(0)
                    fills = pd.Series({t: walk(asks.loc[t] if t in lv else None, need[t])
                                       for t in ww.index})
                    f_fill = walk(bids.loc[r.contract] if r.contract in bids.index.get_level_values(0)
                                  else None, size)
                filled = bool(fills.notna().all() and pd.notna(f_fill))
                exec_ = (f_fill - idx0 * float((ww * fills / last0[ok]).sum())) if filled else np.nan
                rows.append({
                    "date": r.date.date(), "signal": ts, "delay_s": d, "size": size,
                    "contract": r.contract, "dte": r.dte, "vn30": idx0, "disp": r.disp,
                    "disp_fill": fl.get(r.contract, np.nan) - fl.get("VN30", np.nan),
                    "mid": mid, "exec": exec_, "bar": r.bar, "edge": exec_ - r.bar,
                    "filled": filled, "names_short": int(fills.isna().sum()),
                    "fut_spread": f_ask - f_bid, "weight_quoted": float(w[ok].sum()),
                    "fill_in_session": any(a <= tf.time() <= b for a, b in SESSION_FILL),
                    "n_names": int(ok.sum()),
                })
        if n % 20 == 0:
            print(f"[intraday] {n}/{len(trig)} events", flush=True)

    ev = pd.DataFrame(rows)
    ev["year"] = pd.to_datetime(ev["date"]).dt.year
    fut_ok = ev["fut_spread"] > 0                      # a crossed/locked futures book is not a fill
    valid = ev[(ev["weight_quoted"] >= args.min_quoted) & fut_ok & ev["fill_in_session"]]
    good = valid[valid["filled"] & (valid["size"] == sizes[0])]        # base tables: smallest size

    def agg(g):
        e = g["edge"]
        return pd.Series({
            "n": len(g), "disp": g["disp"].mean(), "disp_fill": g["disp_fill"].mean(),
            "mid": g["mid"].mean(), "exec": g["exec"].mean(), "bar": g["bar"].mean(),
            "edge_mean": e.mean(), "edge_median": e.median(),
            "t": e.mean() / e.std() * np.sqrt(len(e)) if len(e) > 1 and e.std() > 0 else np.nan,
            "share_pos": (e > 0).mean()})

    summ = good.groupby("delay_s")[good.columns].apply(agg)
    by_year = good[good["delay_s"] == 60].groupby("year")[good.columns].apply(agg)
    first_per_contract = good[good["delay_s"] == 60].groupby("contract").head(1)
    fpc = agg(first_per_contract)
    v60 = valid[(valid["delay_s"] == (60 if 60 in delays else delays[-1]))
                & (pd.to_datetime(valid["date"]) >= args.depth_from)]   # sizes only exist from then
    by_size = v60.groupby("size")[v60.columns].apply(
        lambda g: pd.concat([pd.Series({"triggers": len(g), "fillable": g["filled"].mean()}),
                             agg(g[g["filled"]])]))

    args.outdir.mkdir(parents=True, exist_ok=True)
    ev.to_csv(args.outdir / "events.csv", index=False)
    summ.to_csv(args.outdir / "summary.csv")
    by_year.to_csv(args.outdir / "by_year.csv")
    by_size.to_csv(args.outdir / "by_size.csv")

    def row(name, s):
        return (f"| {name} | {s['n']:.0f} | {s['disp']:+.2f} | {s['mid']:+.2f} | {s['exec']:+.2f} | "
                f"{s['bar']:.2f} | **{s['edge_mean']:+.2f}** | {s['edge_median']:+.2f} | "
                f"{s['t']:+.2f} | {s['share_pos']:.0%} |")

    hdr = ["| | n | displayed | mid | capturable (bid/ask) | bar | edge mean | edge median | t | edge > 0 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    lines = [
        "# Step 1 — is the intraday basis capturable?",
        "",
        f"Trigger: first minute per day in the continuous session with displayed basis − bar ≥ "
        f"{args.buffer:g}, dte ≥ {args.min_days_expiry}. Bar = VN30 × ({args.fee_bps:g} bps fees+tax "
        f"+ {args.rate:.1%} × dte/365 carry). Capturable = futures bid − fit basket at ask, "
        f"after the delay. Held to expiry, so net ≈ capturable − bar (tracking aside). "
        f"A stock quote counts only if two-sided, not crossed and within "
        f"{args.max_quote_gap:.0%} of its last trade (a ceiling-locked stock has no ask); events "
        f"with < {args.min_quoted:.0%} of basket weight quotable, a locked futures book, or a fill "
        f"that lands in the lunch break / ATC are dropped ({len(ev) - len(good)} event×delay rows of {len(ev)}).",
        "",
        f"Fees {args.fee_bps:g} bps round trip. Base tables use {sizes[0]} contract(s); the "
        f"book is walked up to 3 levels and a trade counts only if all of it fills.",
        "",
        "## By delay from signal to fill (index points)",
        "",
        *hdr,
        *[row(f"{d}s", s) for d, s in summ.iterrows()],
        "",
        "## By year (60 s delay)",
        "",
        *hdr,
        *[row(str(y), s) for y, s in by_year.iterrows()],
        "",
        f"## By size (60 s delay, from {args.depth_from}: order-book sizes start then)",
        "",
        "| contracts | triggers | fully fillable | capturable | bar | edge mean | t | edge > 0 |",
        "|---|---|---|---|---|---|---|---|",
        *[f"| {z} | {s['triggers']:.0f} | {s['fillable']:.0%} | {s['exec']:+.2f} | {s['bar']:.2f} | "
          f"**{s['edge_mean']:+.2f}** | {s['t']:+.2f} | {s['share_pos']:.0%} |"
          for z, s in by_size.iterrows()],
        "",
        "## One position at a time (first trigger per contract, 60 s delay)",
        "",
        *hdr,
        row("per contract", fpc),
        "",
    ]
    (args.outdir / "FINDINGS.md").write_text("\n".join(lines))
    print(summ.round(2).to_string())
    print(by_year.round(2).to_string())
    print(by_size.round(2).to_string())
    print("first per contract:", fpc.round(2).to_dict())
    print(f"[intraday] wrote {args.outdir}/")


if __name__ == "__main__":
    main()
