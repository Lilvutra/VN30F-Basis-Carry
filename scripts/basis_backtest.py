#!/usr/bin/env python3
"""project5 — long-VN30-basket / short-VN30F1M basis strategy backtest.

The trade: when the front-month future is RICH versus the VN30 index (basis
positive and large enough), buy a VN30-like basket of stocks and short one
VN30F1M contract, then unwind as the basis converges into expiry. P&L in index
points ≈ (entry basis − exit basis) + dividends − tracking error − costs.

This file implements the operational recipe end to end:
  1/2. capital split: basket notional + futures margin + a cash reserve,
  3.  basis tracked per day WITH days-to-expiry (a +10 with 2 days left is not
      the same signal as +10 with 3 weeks left),
  4.  costs itemised (stock fee both sides, 0.1% sell tax, futures fee, slippage)
      and converted to index points; entry when basis >= --entry-basis (a fixed
      point level, not compared with the cost),
  5.  filters: enough days to expiry, market not overheated, basket names liquid,
  6.  both legs entered together, recorded at the traded basis,
  7.  daily futures mark-to-market, reserve top-ups, forced-exit on margin call,
  8.  exit on convergence, at expiry settlement, or on a widening stop,
  9.  T+2: the stock leg cannot be sold in the first two sessions.

Basket (--basket-mode): equal-weight VN30 members from the latest membership
snapshot on or before the entry date; or those members with long-only weights
regressed on VN30 returns ("fit"); or the E1VFVN30 ETF ("etf"). Priced on
ADJUSTED (total-return) closes. Fractional
shares are used for valuation; real lot-of-100 rounding is noted as a caveat.

Backtest simplifications (explicit): one position at a time; entry/exit at the
daily close; futures P&L from close-to-close; no intraday financing beyond the
flat cost model; settlement uses the index on the expiry day.

Outputs (--outdir, default result/basis/):
  trades.csv      every trade with entry/exit basis, points, costs, margin events
  summary.csv     per-entry-threshold sweep (this is the cost curve)
  basis.svg       basis vs time, thresholds, entry/exit markers
  equity.svg      cumulative net P&L of the chosen threshold
  FINDINGS.md     the verdict

Usage:
    python scripts/basis_backtest.py \
        --futures data/raw/vn30f_frontmonth.parquet \
        --basket data/raw/vn30_basket_prices.parquet \
        --membership data/raw/vn30_membership.parquet \
        --outdir result/basis
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# --------------------------------------------------------------------------- load

def load_futures(path: Path) -> pd.DataFrame:
    f = pd.read_parquet(path)
    f["date"] = pd.to_datetime(f["date"])
    f["expdate"] = pd.to_datetime(f["expdate"])
    f["basis"] = f["fut_close"] - f["vn30_index"]
    f["dte"] = (f["expdate"] - f["date"]).dt.days
    return f.sort_values("date").reset_index(drop=True)


def load_basket(path: Path):
    b = pd.read_parquet(path)
    b["date"] = pd.to_datetime(b["date"])
    px = b.pivot_table(index="date", columns="ticker", values="adj_close").sort_index()
    vol = b.pivot_table(index="date", columns="ticker", values="volume", aggfunc="last").sort_index()
    raw = (b.pivot_table(index="date", columns="ticker", values="close").sort_index()
           if "close" in b.columns else px)
    popen = (b.pivot_table(index="date", columns="ticker", values="adj_open").sort_index()
             if "adj_open" in b.columns else px)
    return px, vol, raw, popen


def load_members(path: Path):
    m = pd.read_parquet(path)
    m["date"] = pd.to_datetime(m["date"])
    snaps = [(d, g["ticker"].tolist()) for d, g in m.groupby("date")]
    return sorted(snaps)


def members_on(snaps, date):
    chosen = snaps[0][1]
    for d, names in snaps:
        if d <= date:
            chosen = names
        else:
            break
    return chosen


# ----------------------------------------------------------------------- backtest

def _price_on(px: pd.DataFrame, date, tickers):
    """Latest available adjusted close at or before `date` for each ticker."""
    sub = px.loc[:date]
    if sub.empty:
        return pd.Series(dtype=float)
    sub = sub.tail(30)          # last ~6 weeks, unlimited otherwise
    out = {}
    for t in tickers:
        if t in sub.columns:
            s = sub[t].dropna()
            if len(s):
                out[t] = float(s.iloc[-1])
    return pd.Series(out)


ETF = "E1VFVN30"
BASKET_DESC = {
    "equal": "equal-weight VN30 members (latest snapshot)",
    "fit": "VN30 members, long-only weights regressed on VN30 returns (trailing window)",
    "etf": "the E1VFVN30 ETF",
}


def fit_weights(raw: pd.DataFrame, date, names, window: int) -> pd.Series:
    """Long-only weights (sum 1) whose raw-close returns best track VN30 over the
    `window` sessions up to and including `date` — no look-ahead past the entry
    close. Stands in for the real free-float cap weights, which the DB lacks for
    banks/brokers/insurers."""
    from scipy.optimize import nnls
    names = [n for n in names if n in raw.columns]
    ret = raw.loc[:date, names + ["VN30"]].tail(window + 1).pct_change().iloc[1:]
    ret = ret.loc[:, ret.notna().mean() >= 0.9].fillna(0.0)
    X, y = ret.drop(columns="VN30").to_numpy(), ret["VN30"].to_numpy()
    lam = 100.0                                   # soft sum-to-one constraint
    w, _ = nnls(np.vstack([X, lam * np.ones(X.shape[1])]), np.append(y, lam))
    w = pd.Series(w, index=ret.columns.drop("VN30"))
    return w[w > 1e-6] / w.sum()


def basket_weights(mode: str, prices: pd.Series, raw: pd.DataFrame, date, args) -> pd.Series:
    if mode == "fit":
        w = fit_weights(raw, date, list(prices.index), args.fit_window)
        return w.reindex(prices.index).dropna()
    return pd.Series(1.0 / len(prices), index=prices.index)


def round_trip_bps(args) -> float:
    return (2 * args.stock_fee_bps + args.sell_tax_bps + 2 * args.slippage_bps
            + 2 * args.futures_fee_bps)


def _fill(rows, k, px, popen, args):
    """Execution prices for a fill on row k: (fut, index, basket price frame, date).
    close: the signal close itself. next_open: the 09:15 ATO of the following session
    (futures = first trade at/after 09:15, stocks/index = ATO open)."""
    r = rows.iloc[k]
    if args.execution == "close" or pd.isna(r.get("fut_open915")):
        return r["fut_close"], r["vn30_index"], px
    return r["fut_open915"], r["vn30_open"], popen


def run(fut: pd.DataFrame, px: pd.DataFrame, vol: pd.DataFrame, snaps,
        entry_basis: float, args, raw: pd.DataFrame | None = None,
        popen: pd.DataFrame | None = None):
    """Signals are read at each session's close. With --execution close they fill at
    that same close; with next_open they fill at the next session's 09:15 open, so the
    trade never uses a price it could not have acted on. Expiry always settles at the
    expiry-day close (the contract's final settlement)."""
    mult = args.multiplier
    nxt = args.execution == "next_open"
    rows = fut.reset_index(drop=True)
    trades = []
    daily = pd.Series(0.0, index=rows["date"])
    pos = None
    reserve = 0.0
    rt = round_trip_bps(args)

    def close_out(pos, k, exit_fut, exit_idx, bpx, reason):
        date = rows["date"].iloc[k]
        exit_basis = exit_fut - exit_idx
        gross = pos["notional"] * _basket_return(pos, bpx, date)
        gross += (pos["fut_entry"] - exit_fut) * mult
        # gross = basis captured + (basket − VN30) tracking, in index points
        basis_pts = pos["basis_entry"] - exit_basis
        track_pts = gross / mult - basis_pts
        exit_cost = (args.stock_fee_bps + args.sell_tax_bps
                     + args.slippage_bps + args.futures_fee_bps) / 1e4 * pos["notional"]
        cost = pos["cost_entry"] + exit_cost
        net = gross - cost
        daily.iloc[k] -= exit_cost
        trades.append({
            "contract": pos["contract"], "signal_date": pos["signal_date"],
            "entry_date": pos["entry_date"], "exit_date": date,
            "entry_index": pos["vn30_index"], "signal_basis": pos["signal_basis"],
            "entry_basis": pos["basis_entry"], "exit_basis": exit_basis,
            "held_sessions": k - pos["i"], "dte_entry": pos["dte_entry"], "reason": reason,
            "n_names": len(pos["shares"]),
            "gross_points": gross / mult, "basis_points": basis_pts,
            "track_points": track_pts, "cost_points": cost / mult,
            "net_points": net / mult, "net_vnd": net, "margin_calls": pos["calls"],
        })

    for i in range(len(rows)):
        r = rows.iloc[i]
        date, cur_fut, cur_idx, basis = r["date"], r["fut_close"], r["vn30_index"], r["basis"]

        if pos is not None and i >= pos["i"]:
            # --- a next-open exit signalled yesterday fills at today's open
            if pos.get("exit_reason"):
                f, x, bpx = _fill(rows, i, px, popen, args)
                bval = _basket_value(pos, bpx, date)
                daily.iloc[i] += (pos["prev_fut"] - f) * mult + (bval - pos["prev_basket"])
                close_out(pos, i, f, x, bpx, pos["exit_reason"])
                pos = None
            else:
                # --- daily mark-to-market for margin and equity
                fut_pnl = (pos["prev_fut"] - cur_fut) * mult            # short future
                pos["margin"] += fut_pnl
                bval = _basket_value(pos, px, date)
                daily.iloc[i] += fut_pnl + (bval - pos["prev_basket"])
                pos["prev_fut"], pos["prev_basket"] = cur_fut, bval

                # --- margin call top-up from reserve
                maint = pos["notional"] * args.maintenance_ratio
                if pos["margin"] < maint:
                    topup = pos["notional"] * args.margin_ratio - pos["margin"]
                    if reserve >= topup:
                        reserve -= topup
                        pos["margin"] += topup
                        pos["calls"] += 1
                    else:
                        pos["forced"] = True

                # --- exit conditions (read at this close)
                held = i - pos["i"] + (1 if nxt else 0)              # sessions at the fill
                expired = date >= pos["expdate"]
                converged = basis <= args.exit_basis
                stopped = args.stop_basis > 0 and basis >= entry_basis + args.stop_basis
                reason = ("expiry" if expired else "forced" if pos["forced"] else
                          "stop" if stopped else "converged" if converged else None)
                if expired:                                          # settles to the index
                    close_out(pos, i, cur_idx, cur_idx, px, reason)
                    pos = None
                elif reason and held >= args.settlement_days:
                    if nxt and i + 1 < len(rows):
                        pos["exit_reason"] = reason
                    else:
                        close_out(pos, i, cur_fut, cur_idx, px, reason)
                        pos = None
            continue
        if pos is not None:                                          # entry pending
            continue

        # --- no position: look for an entry
        if r["dte"] < args.min_days_expiry:
            continue
        edge = basis - (rt / 1e4 * cur_idx if args.entry_rule == "cost" else 0.0)
        if edge < entry_basis:
            continue
        # market not overheated: skip if VN30 ran up hard recently
        if args.max_runup > 0 and i >= args.runup_window:
            runup = cur_idx / rows["vn30_index"].iloc[i - args.runup_window] - 1
            if runup > args.max_runup:
                continue
        names = members_on(snaps, date)
        prices = _price_on(px, date, names)
        if len(prices) < args.min_names:
            continue
        if args.basket_mode == "etf":
            prices = _price_on(px, date, [ETF])
            if prices.empty:
                continue
        # liquidity filter on the basket
        if args.min_turnover > 0:
            vv = vol.loc[:date].tail(args.runup_window)
            turn = (vv[prices.index].tail(1) * prices).dropna()
            if turn.sum() < args.min_turnover:
                continue

        k = i + 1 if nxt else i                                      # fill row
        if k >= len(rows) or rows["contract"].iloc[k] != r["contract"]:
            continue
        f, x, bpx = _fill(rows, k, px, popen, args)
        weights = basket_weights(args.basket_mode, prices, raw, date, args)  # info up to signal
        fill_px = _price_on(bpx, rows["date"].iloc[k], list(weights.index)).reindex(weights.index)
        weights, fill_px = weights[fill_px.notna()], fill_px.dropna()
        weights = weights / weights.sum()
        notional = x * mult
        shares = (weights * notional) / fill_px
        cost_entry = (args.stock_fee_bps + args.slippage_bps
                      + args.futures_fee_bps) / 1e4 * notional
        reserve = notional * args.reserve_mult
        pos = {
            "i": k, "contract": r["contract"], "signal_date": date,
            "entry_date": rows["date"].iloc[k], "expdate": r["expdate"],
            "vn30_index": x, "fut_entry": f, "basis_entry": f - x, "signal_basis": basis,
            "dte_entry": int(rows["dte"].iloc[k]), "notional": notional, "shares": shares,
            "entry_prices": fill_px, "prev_fut": f,
            "prev_basket": float((shares * fill_px).sum()),
            "margin": notional * args.margin_ratio, "cost_entry": cost_entry,
            "calls": 0, "forced": False,
        }
        daily.iloc[k] -= cost_entry

    equity = daily.cumsum()
    return pd.DataFrame(trades), daily, equity


def _basket_value(pos, px, date):
    prices = _price_on(px, date, pos["shares"].index)
    return float((pos["shares"] * prices.reindex(pos["shares"].index)).sum())


def _basket_return(pos, px, date):
    prices = _price_on(px, date, pos["shares"].index)
    r = (prices.reindex(pos["entry_prices"].index) / pos["entry_prices"] - 1)
    w = pos["shares"] * pos["entry_prices"]
    w = w / w.sum()
    return float((w * r).sum())


def summarise(trades: pd.DataFrame, daily: pd.Series, args) -> dict:
    if trades.empty:
        return {"n_trades": 0, "win_rate": np.nan, "avg_gross_points": np.nan,
                "avg_basis_points": np.nan, "avg_track_points": np.nan,
                "std_track_points": np.nan, "avg_cost_points": np.nan, "avg_net_points": np.nan,
                "total_net_points": 0.0, "total_net_vnd": 0.0, "avg_held": np.nan,
                "avg_dte_entry": np.nan, "sharpe": np.nan, "max_dd_vnd": 0.0,
                "margin_calls": 0, "forced_exits": 0}
    d = daily[daily != 0] if (daily != 0).any() else daily
    sd = d.std(ddof=1)
    cap = args.multiplier * 1500 * (1 + args.margin_ratio + args.reserve_mult)  # approx capital
    eq = trades["net_vnd"].cumsum()
    dd = float((eq - eq.cummax()).min())
    return {
        "n_trades": len(trades),
        "win_rate": float((trades["net_points"] > 0).mean()),
        "avg_gross_points": float(trades["gross_points"].mean()),
        "avg_basis_points": float(trades["basis_points"].mean()),
        "avg_track_points": float(trades["track_points"].mean()),
        "std_track_points": float(trades["track_points"].std()),
        "avg_cost_points": float(trades["cost_points"].mean()),
        "avg_net_points": float(trades["net_points"].mean()),
        "total_net_points": float(trades["net_points"].sum()),
        "total_net_vnd": float(trades["net_vnd"].sum()),
        "avg_held": float(trades["held_sessions"].mean()),
        "avg_dte_entry": float(trades["dte_entry"].mean()),
        "sharpe": float(d.mean() / sd * np.sqrt(252)) if sd and sd > 0 else np.nan,
        "max_dd_vnd": dd,
        "margin_calls": int(trades["margin_calls"].sum()),
        "forced_exits": int((trades["reason"] == "forced").sum()),
    }


# ----------------------------------------------------------------------- outputs

def plot_basis(fut: pd.DataFrame, trades: pd.DataFrame, args, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(fut["date"], fut["basis"], lw=0.9, color="tab:blue", label="basis (VN30F1M − VN30)")
    ax.axhline(args.entry_basis, color="green", ls="--", lw=1.0, label=f"entry  +{args.entry_basis:g}")
    ax.axhline(args.exit_basis, color="red", ls="--", lw=1.0, label=f"exit   +{args.exit_basis:g}")
    ax.axhline(0, color="black", lw=0.8)
    if not trades.empty:
        ax.scatter(trades["entry_date"], trades["entry_basis"], marker="^", s=70,
                   color="green", zorder=5, label="entry")
        ax.scatter(trades["exit_date"], trades["exit_basis"], marker="v", s=70,
                   color="red", zorder=5, label="exit")
    ax.set_ylabel("basis (index points)")
    ax.set_title("VN30F1M basis, entry/exit thresholds and executed trades")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)


def plot_equity(equity: pd.Series, out: Path, args) -> None:
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(equity.index, equity.values, lw=1.1, color="tab:purple")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("cumulative net P&L (VND, 1 contract)")
    ax.set_title(f"Basis strategy equity — entry ≥ +{args.entry_basis:g}, exit ≤ +{args.exit_basis:g}")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)


def cost_curve(trades: pd.DataFrame, args, bps_list):
    """Net result if the ROUND-TRIP cost were `bps` of notional (gross held fixed)."""
    rows = []
    for bps in bps_list:
        if trades.empty:
            rows.append((bps, 0, 0.0, 0.0)); continue
        cost = bps / 1e4 * trades["entry_index"] * args.multiplier
        net = trades["gross_points"] * args.multiplier - cost
        rows.append((bps, len(trades), float((net / args.multiplier).mean()),
                     float(net.sum())))
    return pd.DataFrame(rows, columns=["round_trip_bps", "n_trades", "avg_net_points", "total_net_vnd"])


def write_findings(summary: pd.DataFrame, chosen: dict, trades: pd.DataFrame, ccurve: pd.DataFrame, args, out: Path) -> None:
    best = summary.sort_values("total_net_vnd", ascending=False).iloc[0]
    lines = [
        "# Long VN30 basket / short VN30F1M — basis convergence backtest",
        "",
        f"Window {args.formation_note}. Front-month roll via futurecode='VN30F1M'. "
        f"Basket = {BASKET_DESC[args.basket_mode]}, adjusted closes. "
        f"Costs: stock {args.stock_fee_bps:.0f}bps/side + {args.sell_tax_bps:.0f}bps sell tax "
        f"+ futures {args.futures_fee_bps:.0f}bps + slippage {args.slippage_bps:.0f}bps "
        f"(≈ {chosen.get('avg_cost_points', float('nan')):.1f} index points/trade).",
        "",
        f"Basis is negative most of the time (median ≈ −1.3 pts); a +{args.entry_basis:g} "
        f"entry is a rare event, so trade counts are small by construction.",
        "",
        "## Chosen thresholds (entry ≥ +{e:g}, exit ≤ +{x:g})".format(e=args.entry_basis, x=args.exit_basis),
        "",
        f"| n trades | win rate | avg gross (pts) | avg cost (pts) | avg net (pts) | "
        f"total net (pts) | total net (VND) | Sharpe | max DD (VND) | margin calls | forced |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        f"| {chosen['n_trades']} | {chosen['win_rate']:.2f} | {chosen['avg_gross_points']:.2f} | "
        f"{chosen['avg_cost_points']:.2f} | {chosen['avg_net_points']:.2f} | "
        f"{chosen['total_net_points']:.1f} | {chosen['total_net_vnd']:,.0f} | "
        f"{chosen['sharpe']:.2f} | {chosen['max_dd_vnd']:,.0f} | {chosen['margin_calls']} | "
        f"{chosen['forced_exits']} |",
        "",
        "## Where the gross comes from",
        "",
        "gross = basis captured (entry basis − exit basis) + tracking (basket − VN30 "
        "over the holding period). Only the first part is the strategy; the second is "
        "an unintended bet that the hedge basket beats the index.",
        "",
        "| avg basis (pts) | avg tracking (pts) | tracking std (pts) | avg cost (pts) | "
        "avg net if tracking were 0 (pts) |",
        "|---|---|---|---|---|",
        f"| {chosen['avg_basis_points']:.2f} | {chosen['avg_track_points']:+.2f} | "
        f"{chosen['std_track_points']:.2f} | {chosen['avg_cost_points']:.2f} | "
        f"{chosen['avg_basis_points'] - chosen['avg_cost_points']:+.2f} |",
        "",
        "## Entry-threshold sweep (the cost curve)",
        "",
        "| entry basis | n trades | win rate | avg gross (pts) | avg net (pts) | total net (pts) | total net (VND) |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in summary.itertuples():
        lines.append(
            f"| {r.entry_basis:g} | {r.n_trades} | "
            f"{'' if r.n_trades == 0 else f'{r.win_rate:.2f}'} | "
            f"{'' if r.n_trades == 0 else f'{r.avg_gross_points:.2f}'} | "
            f"{'' if r.n_trades == 0 else f'{r.avg_net_points:.2f}'} | "
            f"{r.total_net_points:.1f} | {r.total_net_vnd:,.0f} |"
        )
    lines += [
        "",
        "## Cost sensitivity (the decision variable)",
        "",
        "Gross convergence is held fixed; only the assumed ROUND-TRIP cost in bps of "
        "notional changes. Breakeven is where avg net crosses zero.",
        "",
        "| round-trip cost (bps) | n trades | avg net (pts) | total net (VND) |",
        "|---|---|---|---|",
    ]
    for r in ccurve.itertuples():
        lines.append(f"| {r.round_trip_bps:.0f} | {r.n_trades} | {r.avg_net_points:+.2f} | "
                     f"{r.total_net_vnd:,.0f} |")
    lines += [
        "",
        "## Reading this",
        "",
        "Gross points ≈ the basis convergence captured; avg net subtracts the itemised "
        "round-trip cost. The strategy only makes money where the entry basis clears "
        "that cost with margin, and where convergence actually happens before expiry. "
        "The sweep is the point: if no entry threshold turns total net positive, the "
        "basis is too thin relative to VN transaction costs — the same cost wall "
        "project2/project3 hit intraday, now on a daily convergence trade.",
        "",
        "Caveats: fractional shares (real lots of 100 add tracking error); adjusted "
        "(total-return) basket vs price index means the result already credits "
        "dividends the trader would receive; one position at a time; fill at close.",
        "",
    ]
    out.write_text("\n".join(lines))


# -------------------------------------------------------------------------- main

def build_parser(ap: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """Strategy/cost options shared with walk_forward.py."""
    ap = ap or argparse.ArgumentParser(description="VN30F1M basis convergence backtest.")
    ap.add_argument("--futures", type=Path, required=True)
    ap.add_argument("--basket", type=Path, required=True)
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=Path("result/basis"))
    ap.add_argument("--multiplier", type=float, default=100000.0, help="VND per index point.")
    ap.add_argument("--entry-basis", type=float, default=10.0, help="enter when basis >= this.")
    ap.add_argument("--exit-basis", type=float, default=3.0, help="exit when basis <= this.")
    ap.add_argument("--stop-basis", type=float, default=0.0,
                    help="exit if basis >= entry + this (0 = off).")
    ap.add_argument("--min-days-expiry", type=int, default=7)
    ap.add_argument("--settlement-days", type=int, default=2, help="T+2 stock sell lock.")
    ap.add_argument("--stock-fee-bps", type=float, default=12.0)
    ap.add_argument("--sell-tax-bps", type=float, default=10.0, help="0.1% sell tax.")
    ap.add_argument("--futures-fee-bps", type=float, default=3.0)
    ap.add_argument("--slippage-bps", type=float, default=15.0)
    ap.add_argument("--margin-ratio", type=float, default=0.18)
    ap.add_argument("--maintenance-ratio", type=float, default=0.12)
    ap.add_argument("--reserve-mult", type=float, default=0.30, help="cash reserve = notional×this.")
    ap.add_argument("--min-names", type=int, default=20, help="min basket members with prices.")
    ap.add_argument("--min-turnover", type=float, default=0.0,
                    help="min basket daily turnover in thousands VND (0 = off).")
    ap.add_argument("--max-runup", type=float, default=0.05,
                    help="skip entry if VN30 rose more than this over --runup-window (0 = off).")
    ap.add_argument("--runup-window", type=int, default=5)
    ap.add_argument("--basket-mode", choices=["equal", "fit", "etf"], default="equal",
                    help="equal = equal-weight members; fit = long-only weights regressed on "
                         "VN30 over --fit-window; etf = hold E1VFVN30.")
    ap.add_argument("--fit-window", type=int, default=120, help="sessions for --basket-mode fit.")
    ap.add_argument("--execution", choices=["close", "next_open"], default="close",
                    help="fill at the signal close, or at the next session's 09:15 open.")
    ap.add_argument("--entry-rule", choices=["points", "cost"], default="points",
                    help="points: basis >= --entry-basis; cost: basis − round-trip cost "
                         "(in index points) >= --entry-basis, i.e. --entry-basis is a buffer.")
    ap.add_argument("--formation-note", default="2021-06 → 2026-10")
    ap.add_argument("--sweep", default="6,8,10,12,14,16",
                    help="comma list of entry thresholds for the sweep table.")
    return ap


def main() -> None:
    args = build_parser().parse_args()

    fut = load_futures(args.futures)
    px, vol, raw, popen = load_basket(args.basket)
    snaps = load_members(args.membership)

    thresholds = [float(x) for x in args.sweep.split(",")]
    sweep_rows = []
    chosen_trades = chosen_daily = chosen_equity = None
    for th in thresholds:
        tr, dly, eq = run(fut, px, vol, snaps, th, args, raw, popen)
        s = summarise(tr, dly, args)
        s["entry_basis"] = th
        sweep_rows.append(s)
        if abs(th - args.entry_basis) < 1e-9:
            chosen_trades, chosen_daily, chosen_equity = tr, dly, eq
    if chosen_trades is None:                       # entry not in sweep: run it
        chosen_trades, chosen_daily, chosen_equity = run(fut, px, vol, snaps, args.entry_basis, args, raw, popen)
    chosen = summarise(chosen_trades, chosen_daily, args)

    args.outdir.mkdir(parents=True, exist_ok=True)
    chosen_trades.to_csv(args.outdir / "trades.csv", index=False)
    pd.DataFrame(sweep_rows).to_csv(args.outdir / "summary.csv", index=False)
    ccurve = cost_curve(chosen_trades, args, [20, 30, 40, 50, 60, 70, 80, 90])
    ccurve.to_csv(args.outdir / "cost_curve.csv", index=False)
    plot_basis(fut, chosen_trades, args, args.outdir / "basis.svg")
    plot_equity(chosen_equity, args.outdir / "equity.svg", args)
    write_findings(pd.DataFrame(sweep_rows), chosen, chosen_trades, ccurve, args,
                   args.outdir / "FINDINGS.md")

    print(f"[basis] {len(fut)} front-month days, {fut['contract'].nunique()} contracts, "
          f"basis {fut['basis'].min():.1f}..{fut['basis'].max():.1f}")
    for r in pd.DataFrame(sweep_rows).itertuples():
        print(f"[basis] entry>={r.entry_basis:>4g}: {r.n_trades:>2} trades  "
              f"avg net {r.avg_net_points if r.n_trades else float('nan'):+.2f} pts  "
              f"total {r.total_net_vnd:>12,.0f} VND")
    print(f"[basis] wrote {args.outdir}/")


if __name__ == "__main__":
    main()
