#!/usr/bin/env python3
"""project5 — README figures, built only from files already in data/raw and result/.

  figures/01_basis_history.png     daily basis vs the fund cost bar, OOS entries marked
  figures/02_tracking.png          5-session tracking gap of the three hedge baskets
  figures/03_close_vs_nextopen.png basis captured: same-close fill vs next-open fill
  figures/04_waterfall.png         displayed → capturable basis → edge, intraday triggers, 5 s
  figures/05_edge_vs_delay.png     edge by fill delay, buffer 0 vs 3 (entries up to expiry day)
  figures/06_buffer_grid.png       whole-sample net/edge by buffer (comparison only), adopted rule
  figures/07_oos_trades.png        out-of-sample trades of the adopted rule (5 s, up to expiry day)
  figures/08_capacity.png          fill rate by size, P&L and return by target size, 5 s
  figures/09_data_periods.png      in-sample / OOS / validation periods of the walk-forward

Usage:  python scripts/make_figures.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BLUE, ORANGE, GREEN, RED, GREY = "#2b6cb0", "#dd6b20", "#2f855a", "#c53030", "#718096"


def save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figures] {path}")


def basis_history(R: Path, D: Path, out: Path, fee_bps: float, rate: float) -> None:
    f = pd.read_parquet(D / "vn30f_frontmonth.parquet")
    f["date"], f["expdate"] = pd.to_datetime(f["date"]), pd.to_datetime(f["expdate"])
    f = f.drop_duplicates("date").sort_values("date")
    basis = f["fut_close"] - f["vn30_index"]
    bar = f["vn30_index"] * (fee_bps / 1e4 + rate * (f["expdate"] - f["date"]).dt.days / 365)
    o = pd.read_csv(R / "walkforward_intraday_expiry" / "oos_trades.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(f["date"], basis, color=GREY, lw=0.7, label="daily closing basis (future − VN30)")
    ax.plot(f["date"], bar, color=ORANGE, lw=1.2, label=f"cost bar: fees {fee_bps:g} bps + carry {rate:.1%}")
    ax.plot(f["date"], bar + 3, color=ORANGE, lw=1, ls="--", label="bar + buffer 3 (entry line)")
    ax.scatter(o["date"], o["disp"], color=GREEN, s=28, zorder=3, label="out-of-sample entries (intraday)")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("index points")
    ax.set_title("The future usually trades at a discount; the rich setups are rare spikes")
    ax.legend(loc="lower left", fontsize=8, ncol=2)
    save(fig, out / "01_basis_history.png")


def tracking(R: Path, out: Path) -> None:
    t = pd.read_csv(R / "tracking" / "tracking_error.csv")
    s = pd.read_csv(R / "tracking" / "summary.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(8, 4))
    bins = np.arange(-40, 41, 2.5)
    for col, c, lab in [("equal", GREY, "equal-weight"), ("etf", RED, "E1VFVN30 ETF"), ("fit", BLUE, "fit (regressed)")]:
        ax.hist(t[col].dropna().clip(-40, 40), bins=bins, histtype="step", lw=1.8, color=c,
                label=f"{lab}: std {s.loc[col, 'std']:.1f} pts")
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel("basket − VN30 over 5 sessions (index points, clipped at ±40)")
    ax.set_ylabel("windows")
    ax.set_title("Hedge-basket tracking gap: fit is the tightest, the ETF the loosest")
    ax.legend(fontsize=8)
    save(fig, out / "02_tracking.png")


def close_vs_nextopen(R: Path, out: Path) -> None:
    rows = []
    for name, d in [("fill at the signal close", "basis_fit"), ("fill at the next 09:15 open", "basis_fit_nextopen")]:
        t = pd.read_csv(R / d / "trades.csv")
        rows.append((name, t["basis_points"].mean(), t["track_points"].mean(), t["cost_points"].mean(),
                     t["net_points"].mean()))
    df = pd.DataFrame(rows, columns=["execution", "basis", "tracking", "cost", "net"]).set_index("execution")
    fig, ax = plt.subplots(figsize=(8, 3.8))
    x = np.arange(4)
    w = 0.38
    for i, (name, r) in enumerate(df.iterrows()):
        vals = [r.basis, r.tracking, -r.cost, r.net]
        b = ax.bar(x + (i - 0.5) * w, vals, w, color=[BLUE, GREY, RED, GREEN], alpha=1 if i == 0 else 0.55,
                   edgecolor="black", label=name)
        ax.bar_label(b, fmt="%+.1f", fontsize=8)
    ax.set_xticks(x, ["basis captured", "tracking", "− cost", "net"])
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("points per trade")
    ax.set_title("Daily rule (+10/+3, fit): the closing basis is gone by the next open")
    ax.legend(fontsize=8, handles=[plt.Rectangle((0, 0), 1, 1, color=GREY, alpha=a) for a in (1, 0.55)],
              labels=list(df.index))
    save(fig, out / "03_close_vs_nextopen.png")


def waterfall(R: Path, out: Path) -> None:
    s = pd.read_csv(R / "intraday_fund_buffer3_expiry" / "summary.csv", index_col=0)
    z, d = s.loc[0], s.loc[5]
    steps = [("displayed\nbasis", d["disp"], "total"),
             ("index\nstaleness", z["mid"] - d["disp"], "delta"),
             ("5 s\ndecay", d["mid"] - z["mid"], "delta"),
             ("bid/ask\nspreads", d["exec"] - d["mid"], "delta"),
             ("capturable", d["exec"], "total"),
             ("fees +\ncarry", -d["bar"], "delta"),
             ("edge", d["edge_mean"], "total")]
    fig, ax = plt.subplots(figsize=(9, 4))
    level = 0.0
    for i, (lab, v, kind) in enumerate(steps):
        if kind == "total":
            ax.bar(i, v, color=BLUE if lab != "edge" else GREEN, edgecolor="black")
            ax.text(i, v + 0.15, f"{v:.2f}", ha="center", fontsize=9)
            level = v
        else:
            ax.bar(i, v, bottom=level, color=RED if v < 0 else GREEN, edgecolor="black")
            ax.text(i, max(level, level + v) + 0.15, f"{v:+.2f}", ha="center", fontsize=9)
            level += v
    ax.set_xticks(range(len(steps)), [s[0] for s in steps], fontsize=8)
    ax.set_ylim(0, d["disp"] + 1.2)
    ax.set_ylabel(f"index points (mean of {int(d['n'])} triggers)")
    ax.set_title("Fund fees, buffer 3, 5 s fill: where the on-screen basis goes before it is yours")
    save(fig, out / "04_waterfall.png")


def edge_vs_delay(R: Path, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for d, c, lab in [("intraday_fund_buffer0_expiry", RED, "buffer 0"), ("intraday_fund_buffer3_expiry", GREEN, "buffer 3")]:
        s = pd.read_csv(R / d / "summary.csv")
        ax.plot(s["delay_s"], s["edge_mean"], marker="o", color=c, label=f"{lab} ({int(s.loc[s['delay_s'] == 5, 'n'].iloc[0])} triggers at 5 s)")
        for x, y in zip(s["delay_s"], s["edge_mean"]):
            dx, ha = {0: (-4, "right"), 5: (4, "left")}.get(x, (0, "center"))   # 0 s and 5 s sit close
            ax.annotate(f"{y:+.2f}", (x, y), textcoords="offset points", xytext=(dx, 7), ha=ha, fontsize=8)
    ax.axhline(0, color="black", lw=0.6)
    ax.margins(y=0.15)
    ax.axvline(5, color=GREY, lw=0.8, ls="--")
    ax.set_xlim(-14, 128)
    ax.set_xlabel("seconds from signal to fill (dashed: the adopted 5 s)")
    ax.set_ylabel("edge per trade (points)")
    ax.set_title("The edge decays with every second of delay")
    ax.legend(fontsize=8)
    save(fig, out / "05_edge_vs_delay.png")


def buffer_grid(R: Path, out: Path) -> None:
    t = pd.read_csv(R / "walkforward_intraday_expiry" / "trades.csv")
    t = t[(t["vol_cap"] == 0) & t["net"].notna()]
    g = t.groupby("buffer").agg(n=("net", "size"), net=("net", "mean"), edge=("edge", "mean"),
                                total=("net", "sum"))
    fig, ax = plt.subplots(figsize=(8, 3.8))
    x = np.arange(len(g))
    ax.bar(x - 0.2, g["edge"], 0.4, color=BLUE, label="edge (exec − bar)")
    ax.bar(x + 0.2, g["net"], 0.4, color=GREY, label="net incl. tracking")
    for i, r in enumerate(g.itertuples()):
        ax.text(i - 0.2, r.edge + 0.3 if r.edge >= 0 else r.edge - 1, f"{r.edge:+.1f}", ha="center", fontsize=8)
        ax.text(i + 0.2, r.net + 0.3, f"{r.net:+.1f}\n({r.n})", ha="center", fontsize=7)
    ax.set_xticks(x, [f"buffer {b:g}" for b in g.index])
    ax.set_ylim(min(g["edge"].min(), 0) - 1.2, g["net"].max() * 1.25)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("points per trade")
    ax.set_title("Whole sample, one position per contract (comparison only, not OOS)")
    ax.legend(fontsize=8, loc="upper left")
    save(fig, out / "06_buffer_grid.png")


def oos_trades(R: Path, out: Path) -> None:
    o = pd.read_csv(R / "walkforward_intraday_expiry" / "oos_trades.csv", parse_dates=["date"]).sort_values("date")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    x = np.arange(len(o))
    a1.bar(x, o["edge"], color=BLUE, label=f"edge (mean {o['edge'].mean():+.2f})")
    a1.bar(x, o["track"], bottom=np.where(o["track"] >= 0, o["edge"].clip(lower=0), o["edge"].clip(upper=0)),
           color=GREY, alpha=0.7, label=f"tracking to expiry (mean {o['track'].mean():+.2f}, std {o['track'].std():.1f})")
    a1.scatter(x, o["net"], color="black", s=14, zorder=3, label="net")
    a1.axhline(0, color="black", lw=0.6)
    a1.set_ylabel("points per contract")
    a1.set_title("Out-of-sample trades (buffer 3 picked in every fold): the edge is steady, tracking is noise")
    a1.legend(fontsize=8, loc="upper left")
    a2.plot(x, o["edge"].cumsum(), color=BLUE, marker="o", ms=3, label="cumulative edge")
    a2.plot(x, o["net"].cumsum(), color="black", marker="o", ms=3, label="cumulative net")
    a2.set_ylabel("points")
    a2.legend(fontsize=8, loc="upper left")
    a2.set_xticks(x, [f"{d:%Y-%m}" for d in o["date"]], rotation=60, fontsize=7)
    save(fig, out / "07_oos_trades.png")


def capacity(R: Path, out: Path) -> None:
    f = pd.read_csv(R / "capacity_5s" / "fills.csv")
    c = pd.read_csv(R / "capacity_5s" / "capacity.csv")
    c = c[c["policy"] == "first"]
    k = f.groupby("k").agg(fillable=("filled", "mean"), fut_short=("fut_short", "mean"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
    a1.plot(k.index, k["fillable"] * 100, marker="o", color=BLUE, label="all legs fill in the top 3 levels")
    a1.plot(k.index, k["fut_short"] * 100, marker="o", color=RED, label="futures bid runs out")
    a1.set_xlabel("contracts per trade")
    a1.set_ylabel("% of triggers (2023+, 5 s)")
    a1.set_title("The book caps the size")
    a1.legend(fontsize=8)
    a2.bar(c["target"].astype(str), c["pnl_m_per_yr"], color=GREEN)
    for i, r in enumerate(c.itertuples()):
        a2.text(i, r.pnl_m_per_yr + 0.6, f"{r.pnl_m_per_yr:.0f}m\n{r.pct_per_yr:.2f}%/yr", ha="center", fontsize=8)
    a2.set_xlabel("target contracts (partial fills allowed)")
    a2.set_ylabel("m VND per year above carry")
    a2.set_ylim(0, c["pnl_m_per_yr"].max() * 1.35)
    a2.set_title("P&L grows far slower than capital")
    save(fig, out / "08_capacity.png")


def data_periods(R: Path, out: Path) -> None:
    """Which data each stage saw: warm-up, step-4 exploration, walk-forward folds, paper trading."""
    T = pd.Timestamp
    start, end = T("2021-06-01"), T("2026-10-23")
    folds = pd.read_csv(R / "walkforward_intraday_expiry" / "folds.csv")
    o = pd.read_csv(R / "walkforward_intraday_expiry" / "oos_trades.csv", parse_dates=["date"])
    rows = []                                        # (label, [(from, to, colour, hatch, text)])
    rows.append(("data", [(T("2020-06-01"), start, GREY, "//", "basket prices only:\n120-session fit warm-up"),
                          (start, T("2023-01-03"), BLUE, "", "minute basis + ticks + book prices"),
                          (T("2023-01-03"), end, BLUE, "", "… + book sizes (capacity)")]))
    rows.append(("step 4: in-sample\nexploration", [(start, end, GREY, "", "whole sample: buffer 3 found here, so steps 5–6 re-pick it")]))
    for f in folds.itertuples():
        y0 = T(f"{f.test_year}-01-01")
        y1 = min(T(f"{f.test_year}-12-31"), end)
        is_txt = (f"in-sample: {f.train_n} trades → buffer {f.buffer:g}" if (y0 - start).days > 400
                  else f"IS: {f.train_n} →\nbuffer {f.buffer:g}")
        rows.append((f"fold {f.test_year}", [(start, y0, BLUE, "", is_txt),
                                              (y0, y1, GREEN, "", f"OOS: {f.test_n}, {f.test_total:+.0f}")]))
    rows.append(("rule revision\n(5 s, to expiry)", [(T("2022-01-01"), end, ORANGE, "//",
                                                      "chosen after seeing 2022–2026 → these years acted as validation")]))
    rows.append(("step 7: paper\ntrading", [(T("2026-11-01"), T("2027-05-01"), "white", "", "clean OOS\n(not started)")]))

    fig, ax = plt.subplots(figsize=(12, 5.4))
    for i, (lab, bars) in enumerate(rows):
        yy = len(rows) - 1 - i
        for a, b, c, h, txt in bars:
            ax.barh(yy, (b - a).days, left=a, height=0.6, color=c, alpha=0.85 if c != "white" else 1,
                    hatch=h, edgecolor="black", lw=0.6, ls="--" if c == "white" else "-")
            light = c in (GREY, "white") or h
            ax.text(a + (b - a) / 2, yy, txt, ha="center", va="center", fontsize=7,
                    color="black" if light else "white",
                    bbox=dict(facecolor="white", edgecolor="none", pad=1.5) if h else None)
        if lab.startswith("fold"):
            d = o[o["year"] == int(lab.split()[1])]["date"]
            ax.scatter(d, [yy + 0.36] * len(d), marker="v", s=14, color="black", zorder=3)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1], fontsize=8)
    ax.set_xlim(T("2020-05-01"), T("2027-06-01"))
    ax.axvline(end, color=RED, lw=1, ls=":")
    ax.text(end, len(rows) - 1.5, "data end \n2026-10-23 ", color=RED, fontsize=7, ha="right", va="center")
    ax.set_title("Data periods: anchored walk-forward (in-sample grows, each year tested once), ▼ = OOS entries")
    ax.grid(axis="x", alpha=0.3)
    save(fig, out / "09_data_periods.png")


def main() -> None:
    ap = argparse.ArgumentParser(description="README figures.")
    ap.add_argument("--result", type=Path, default=Path("result"))
    ap.add_argument("--data", type=Path, default=Path("data/raw"))
    ap.add_argument("--outdir", type=Path, default=Path("figures"))
    ap.add_argument("--fee-bps", type=float, default=17.0)
    ap.add_argument("--rate", type=float, default=0.045)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    basis_history(args.result, args.data, args.outdir, args.fee_bps, args.rate)
    tracking(args.result, args.outdir)
    close_vs_nextopen(args.result, args.outdir)
    waterfall(args.result, args.outdir)
    edge_vs_delay(args.result, args.outdir)
    buffer_grid(args.result, args.outdir)
    oos_trades(args.result, args.outdir)
    capacity(args.result, args.outdir)
    data_periods(args.result, args.outdir)


if __name__ == "__main__":
    main()
