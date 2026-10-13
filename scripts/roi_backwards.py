#!/usr/bin/env python3
"""Walk backwards from ROI through every metric in a client's sheet.

ROI is a chain of multiplications:
  revenue = spend / CPM x CTR x LPCR x qual rate x booking rate x show-up
            x (30 -> 60 step) x show-up 60 x close rate x deal size
so ROI = revenue / spend is the product of every stage after spend.
That means fixing ONE stage multiplies ROI by (target / actual) for that stage,
with everything else unchanged. The script prints every stage, its baseline,
and that multiplier, then ranks stages by how much ROI they're costing.

Baseline per stage = the sheet's target if it has one, else the client's best
month this year (with enough volume), else the playbook default.

Usage:
  python3 scripts/roi_backwards.py --as-of 2026-10-13 pcw=<path> [zin=<path> ...]
"""
import argparse, datetime as dt, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from scale_data import load, daily_rows, MONTHS, UNTRACKED_Q  # noqa: E402

PLAYBOOK = {"LPCR": 0.20, "Q_rate": 0.20, "CTR": 0.01, "SUP30": 0.65, "SUP60": 0.75, "close": 0.30}


def sums(rows):
    keys = ["spend", "impr", "clicks", "leads", "q", "b30", "t30", "b60", "t60", "new", "rev", "coll", "trial", "mrr"]
    return {k: sum(r.get(k, 0.0) for r in rows) for k in keys}


RATE_CAP = {"Show-up 30-min", "Show-up 60-min", "30-min taken to 60-min booked", "Collected / contracted",
            "Lead to qualified", "Qualified to booked (30-min)", "Lead to booked (30-min)"}


def stages(s, two_step, has_q):
    """Ordered (name, value, direction) for each link of the chain. direction: +1 higher is better, -1 lower."""
    d = lambda a, b: a / b if b else None
    if has_q and s["b30"] > s["q"]:
        has_q = False  # more bookings than qualified leads: qualified isn't a real gate in this window
    out = [("CPM (cost per 1,000 views)", d(s["spend"] * 1000, s["impr"]), -1),
           ("CTR (clicks / views)", d(s["clicks"], s["impr"]), 1),
           ("LPCR (leads / clicks)", d(s["leads"], s["clicks"]), 1)]
    if has_q:
        out += [("Lead to qualified", d(s["q"], s["leads"]), 1),
                ("Qualified to booked (30-min)", d(s["b30"], s["q"]), 1)]
    else:
        out += [("Lead to booked (30-min)", d(s["b30"], s["leads"]), 1)]
    out += [("Show-up 30-min", d(s["t30"], s["b30"]), 1)]
    if two_step:
        out += [("30-min taken to 60-min booked", d(s["b60"], s["t30"]), 1),
                ("Show-up 60-min", d(s["t60"], s["b60"]), 1),
                ("Close rate (clients / 60-min taken)", d(s["new"], s["t60"]), 1)]
    else:
        out += [("Close rate (clients / calls taken)", d(s["new"], s["t30"]), 1)]
    out += [("Deal size (contracted per client)", d(s["rev"], s["new"]), 1),
            ("Collected / contracted", d(s["coll"], s["rev"]), 1)]
    return out


def fmt(name, v):
    if v is None:
        return "-"
    if name.startswith("CPM"):
        return f"{v:,.2f}"
    if name.startswith("Deal size"):
        return f"{v:,.0f}"
    return f"{v * 100:.1f}%"


def run(key, path, as_of):
    wb = load(path)
    days = daily_rows(wb)
    end = as_of - dt.timedelta(days=1)
    pm = end.month - 1 or 12
    py = end.year if end.month > 1 else end.year - 1
    months = {}
    for m in range(1, 13):
        rows = [r for d, r in days.items() if d.year == end.year and d.month == m and d <= end]
        if rows and sum(r["spend"] for r in rows) > 0:
            months[m] = sums(rows)
    if not months:
        print(f"\n===== {key} =====\nno spend this year")
        return
    allyear = sums([r for d, r in days.items() if d.year == end.year and d <= end])
    two_step = allyear["b60"] > 0 and allyear["b30"] > 0 and key == "pcw"
    has_q = key not in UNTRACKED_Q and allyear["q"] > 0
    last3 = [m for m in range(pm - 2, pm + 1) if m in months]
    windows = [(f"{MONTHS[pm - 1]} (last full month)", months.get(pm)),
               ("Last 3 full months", sums([r for d, r in days.items() if d.year == end.year and d.month in last3]))]

    # Best month per stage (min 20 leads so tiny months don't win)
    best = {}
    for m, s in months.items():
        if s["leads"] < 20 or m == end.month:
            continue
        for name, v, dirn in stages(s, two_step, has_q):
            if v is None or v == 0 or (name in RATE_CAP and v > 1.0):
                continue
            if name not in best or (dirn == 1 and v > best[name][0]) or (dirn == -1 and v < best[name][0]):
                best[name] = (v, MONTHS[m - 1])

    ytd = {n: v for n, v, _ in stages(allyear, two_step, has_q)}

    def baseline(name):
        if name.startswith("Collected") or name.startswith("Deal size"):
            v = ytd.get(name)
            return (v, "year-to-date average", None) if v else (None, "no baseline", None)
        pb = {"CTR": "CTR", "LPCR": "LPCR", "Lead to qualified": "Q_rate", "Show-up 30": "SUP30",
              "Show-up 60": "SUP60", "Close rate": "close"}
        for prefix, k in pb.items():
            if name.startswith(prefix):
                tgt = PLAYBOOK[k]
                b = best.get(name)
                # use the sheet/playbook target; mention best month for context
                return tgt, "target", b
        b = best.get(name)
        return (b[0], f"best month ({b[1]})", b) if b else (None, "no baseline", None)

    print(f"\n===== {key} ===== ({'2-step 30 -> 60-min calls' if two_step else '1 call'}; "
          f"{'qualified tracked' if has_q else 'no qualified step'})")
    for label, s in windows:
        if not s or s["spend"] <= 0:
            continue
        roi_c = s["rev"] / s["spend"]
        roi_l = (s["coll"] + s["mrr"]) / s["spend"]
        print(f"--- {label}: spend {s['spend']:,.0f} | clients {s['new']:.0f} | contracted {s['rev']:,.0f} "
              f"({roi_c * 100:.0f}%) | collected {s['coll'] + s['mrr']:,.0f} ({roi_l * 100:.0f}%)")
        notes = []
        if has_q and s["b30"] > s["q"]:
            notes.append(f"{s['b30']:.0f} booked vs {s['q']:.0f} qualified: people book without passing the survey, so 'qualified' is skipped as a gate")
        if two_step and s["b60"] > s["t30"]:
            notes.append(f"{s['b60']:.0f} 60-min booked vs {s['t30']:.0f} 30-min taken: 30-min calls taken are under-logged (or 60s booked directly)")
        if s["b30"] + s["b60"] > 0 and s["t30"] + s["t60"] == 0:
            notes.append("calls taken = 0: not entered yet")
        for n in notes:
            print("    DATA:", n)
        print("    Stage | actual | baseline | ROI x if fixed alone")
        ranked = []
        for name, v, dirn in reversed(stages(s, two_step, has_q)):  # backwards from revenue
            base, src, b = baseline(name)
            if v is None:
                print(f"    {name} | no data | - | -")
                continue
            if name in RATE_CAP and v > 1.0:
                print(f"    {name} | {fmt(name, v)} | - | n/a (over 100%: data gap, see DATA)")
                continue
            if v == 0 and dirn == 1:
                mult = float("inf")  # a stage at zero breaks the whole chain, baseline or not
            elif base is None:
                mult = None
            elif v == 0:
                mult = float("inf")
            else:
                mult = max(1.0, (base / v) if dirn == 1 else (v / base))
            ctx = f" (best {fmt(name, b[0])} in {b[1]})" if b and src == "target" else ""
            mtxt = "BROKEN (0)" if mult == float("inf") else (f"x{mult:.2f}" if mult else "-")
            print(f"    {name} | {fmt(name, v)} | {fmt(name, base) if base else '-'} {src}{ctx} | {mtxt}")
            if mult and mult > 1.05:
                ranked.append((mult, name))
        ranked.sort(reverse=True)
        print("    BIGGEST ROI LEAKS:", "; ".join(
            f"{n} ({'BROKEN' if m == float('inf') else f'x{m:.2f}'})" for m, n in ranked[:5]) or "none")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    for f in a.files:
        k, p = f.split("=", 1)
        try:
            run(k, p, dt.date.fromisoformat(a.as_of))
        except Exception as e:
            print(f"\n===== {k} =====\nERROR: {e}")
