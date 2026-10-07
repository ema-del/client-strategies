#!/usr/bin/env python3
"""Pull every number the "scale" routine needs from the clients' reporting sheets.

Input: the files saved by the Google Drive `download_file_content` tool when called
with exportMimeType = xlsx (JSON with a base64 `content` field), or plain .xlsx files.

Usage:
  python3 scripts/scale_data.py --as-of 2026-10-05 pcw=/path/to/saved.txt zin=/path/to/other.txt ...

Keys must match the `key` column in CLAUDE.md's client roster. `--as-of` is today's
date; the trailing windows end the day before (today's row is usually incomplete).
"""
import argparse, base64, datetime as dt, io, json, re, sys

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl missing: run `pip install -q openpyxl` and retry")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PCT = {"CTR", "LPCR", "PQ_rate", "Q_rate", "lead_to_booked", "SUP_30", "SUP_60", "close_rate", "ROI_contracted", "ROI_collected"}

# Column names (row 1 of each month tab). Matched by name so a moved column still works.
COLS = {
    "spend": "Adspend", "impr": "Impr", "clicks": "Link Clicks", "leads": "Lead",
    "pq": "Pre-Qualified Leads", "q": "Qualified Lead",
    "b30": r"(15|30) Min Calls Booked", "t30": r"(15|30) Calls Taken",
    "b60": "60 Min Calls Booked", "t60": "60 Calls Taken",
    "new": "New Clients", "rev": "Contracted Revenue", "coll": "Collected Revenue",
}


def load(path):
    raw = open(path, "rb").read()
    if raw[:2] != b"PK":  # Drive tool JSON wrapper
        txt = raw.decode("utf-8", "ignore")
        txt = txt[txt.find("{"): txt.rfind("}") + 1]
        raw = base64.b64decode(json.loads(txt)["content"])
    return openpyxl.load_workbook(io.BytesIO(raw), data_only=True)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def col_index(header):
    idx = {}
    for key, pat in COLS.items():
        for i, h in enumerate(header):
            if h and re.match(pat, str(h).strip(), re.I):
                if key == "leads" and str(h).strip() != "Lead":
                    continue
                idx[key] = i
                break
    return idx


def daily_rows(wb):
    out = {}
    for m in MONTHS:
        if m not in wb.sheetnames:
            continue
        ws = wb[m]
        header = [c.value for c in ws[1]]
        idx = col_index(header)
        notes_i = next((i for i, h in enumerate(header) if h and str(h).lower().startswith("note")), None)
        for r in ws.iter_rows(min_row=3, values_only=True):
            if not isinstance(r[0], dt.datetime):
                continue
            row = {k: num(r[i]) if i < len(r) else 0.0 for k, i in idx.items()}
            row["blank"] = r[idx["spend"]] in (None, "")
            row["note"] = r[notes_i] if notes_i is not None and notes_i < len(r) else None
            out[r[0].date()] = row
    return out


def targets(wb, month):
    ws = wb[month]
    header = [str(c.value or "").strip() for c in ws[1]]
    tgt = [c.value for c in ws[2]]
    res = {}
    for h, t in zip(header, tgt):
        if t and str(t).strip() and str(t).strip().lower() != "targets":
            res[h] = str(t).replace("\n", " ")
    return res


def agg(rows):
    s = {k: sum(r.get(k, 0.0) for r in rows) for k in COLS}
    d = lambda a, b: round(a / b, 4) if b else None
    booked = s["b30"] + s["b60"]
    taken = s["t30"] + s["t60"]
    return {
        "days": len(rows), **{k: round(v, 2) for k, v in s.items()},
        "CPM": d(s["spend"] * 1000, s["impr"]), "CTR": d(s["clicks"], s["impr"]), "CPC": d(s["spend"], s["clicks"]),
        "LPCR": d(s["leads"], s["clicks"]), "CPL": d(s["spend"], s["leads"]),
        "PQ_rate": d(s["pq"], s["leads"]), "Q_rate": d(s["q"], s["leads"]), "cost_per_Q": d(s["spend"], s["q"]),
        "booked": booked, "lead_to_booked": d(booked, s["leads"]),
        "cost_per_booked_30": d(s["spend"], s["b30"]), "cost_per_booked_60": d(s["spend"], s["b60"]),
        "cost_per_booked_all": d(s["spend"], booked),
        "SUP_30": d(s["t30"], s["b30"]), "SUP_60": d(s["t60"], s["b60"]),
        "cost_per_taken_30": d(s["spend"], s["t30"]), "cost_per_taken_60": d(s["spend"], s["t60"]),
        "close_rate": d(s["new"], taken), "cost_per_client": d(s["spend"], s["new"]),
        "ROI_contracted": d(s["rev"], s["spend"]), "ROI_collected": d(s["coll"], s["spend"]),
        "booked_per_day": round(booked / len(rows), 2) if rows else 0,
    }


def fmt(a):
    out = []
    for k, v in a.items():
        if v is None:
            out.append(f"{k}=-")
        elif k in PCT:
            out.append(f"{k}={v * 100:.1f}%")
        else:
            out.append(f"{k}={v:,.2f}" if isinstance(v, float) else f"{k}={v}")
    return " | ".join(out)


# Sheet target column -> computed key. Cost metrics use "Target: < $X Max: $Y"; rate metrics use "> N%".
TARGET_MAP = [
    (r"^CTR", "CTR", "spend"), (r"^Cost per Lead", "CPL", "leads"),
    (r"^Cost Per (15|30) Booked", "cost_per_booked_30", "b30"), (r"^(15|30) SUP", "SUP_30", "b30"),
    (r"^Cost Per (15|30) Call Taken", "cost_per_taken_30", "t30"),
    (r"^Cost Per 60 Booked", "cost_per_booked_60", "b60"), (r"^60 SUP", "SUP_60", "b60"),
    (r"^Cost Per 60 Call Taken", "cost_per_taken_60", "t60"),
    (r"^Call Closing Rate", "close_rate", "t30"), (r"^Cost Per New Client", "cost_per_client", "new"),
    (r"^Contracted-ROI", "ROI_contracted", "spend"), (r"^Collected-ROI", "ROI_collected", "spend"),
]
UNTRACKED_Q = {"cmtc", "sma"}  # Pre-Qualified/Qualified not tracked by design


def parse_target(t):
    t = str(t)
    nums = [float(x.replace(",", "")) for x in re.findall(r"[\d][\d,]*\.?\d*", t)]
    if "Max" in t and len(nums) >= 2:
        return ("cost", nums[0], nums[1])
    if ">" in t and nums:
        return ("rate", nums[0] / 100, None)
    return None


def scorecard(key, wb, month, a, label, top_only=False, uses_60=True):
    """Every metric in the chain, judged Good / Borderline / BAD. Nothing skipped."""
    ws = wb[month]
    header = [str(c.value or "").strip() for c in ws[1]]
    tgt = [c.value for c in ws[2]]
    lines, bad = [], []

    def judge(name, val, rule, events_key):
        if a["spend"] <= 0:
            return
        if val is None:
            if rule[0] == "cost" and a.get(events_key, 0) == 0:
                lines.append(f"{name}: none on ${a['spend']:,.0f} spend -> BAD"); bad.append(f"{name} (zero on ${a['spend']:,.0f})")
            return
        if rule[0] == "cost":
            t, mx = rule[1], rule[2]
            v = "Good" if val < t else ("Borderline" if val <= 1.3 * mx else "BAD")
            lines.append(f"{name}: {val:,.2f} (target <{t:g}, max {mx:g}) -> {v}")
        else:
            v = "Good" if val >= rule[1] else "BAD"
            lines.append(f"{name}: {val * 100:.1f}% (target >{rule[1] * 100:g}%) -> {v}")
        if v == "BAD":
            bad.append(name)

    # LPCR: fixed rule (goal 20%, >=15 good, 12-15 borderline, <12 bad)
    if a["LPCR"] is not None and a["spend"] > 0:
        v = "Good" if a["LPCR"] >= 0.15 else ("Borderline" if a["LPCR"] >= 0.12 else "BAD")
        lines.append(f"LPCR: {a['LPCR'] * 100:.1f}% (goal 20%) -> {v}")
        if v == "BAD":
            bad.append("LPCR")
    # Lead-to-qualified: playbook target >20% (skip where not tracked by design)
    if key not in UNTRACKED_Q and a["leads"] > 0:
        v = "Good" if (a["Q_rate"] or 0) >= 0.20 else "BAD"
        lines.append(f"Lead-to-qualified: {(a['Q_rate'] or 0) * 100:.1f}% (target >20%) -> {v}")
        if v == "BAD":
            bad.append("Lead-to-qualified")
    lagging = {"SUP_30", "SUP_60", "cost_per_taken_30", "cost_per_taken_60", "close_rate",
               "cost_per_client", "ROI_contracted", "ROI_collected"}
    for pat, k, ev in TARGET_MAP:
        if top_only and k in lagging:
            continue  # calls taken / closes / revenue lag the spend: judged on the last full month
        if not uses_60 and k.endswith("_60"):
            continue  # client doesn't run 60-min calls
        for h, t in zip(header, tgt):
            if re.match(pat, h, re.I) and t:
                rule = parse_target(t)
                if rule:
                    judge(h, a.get(k), rule, ev)
                break
    print(f"SCORECARD {label}:")
    for l in lines:
        print("   ", l)
    if top_only:
        print("    (show-up, cost per call taken, close rate, cost per client and ROI are judged on the last full month: they lag)")
    print(f"ALL BAD ({label}):", ", ".join(bad) if bad else "none")


def run(key, path, as_of):
    wb = load(path)
    days = daily_rows(wb)
    end = as_of - dt.timedelta(days=1)
    print(f"\n===== {key} =====")
    if not days:
        print("NO DAILY ROWS FOUND (check tab names / layout)")
        return
    # Eligibility: two most recent dated rows up to yesterday
    recent = [days[d] for d in sorted(days) if d <= end][-2:]
    live = any(r["spend"] > 0 for r in recent)
    print("ELIGIBLE:", "yes" if live else "NO (last 2 rows $0/blank, skip)")
    t7 = [days[end - dt.timedelta(days=i)] for i in range(6, -1, -1) if end - dt.timedelta(days=i) in days]
    t3 = t7[-3:]
    print("TARGETS (current month tab):", targets(wb, MONTHS[end.month - 1]))
    print("DAILY last 10 (date: spend/clicks/leads/booked30/booked60/taken30/taken60):")
    for d in sorted(x for x in days if x <= end)[-10:]:
        r = days[d]
        print(f"  {d} {r['spend']:.0f}/{r['clicks']:.0f}/{r['leads']:.0f}/{r['b30']:.0f}/{r['b60']:.0f}/{r['t30']:.0f}/{r['t60']:.0f}"
              + (f"  note: {r['note']}" if r["note"] else ""))
    print("T7:", fmt(agg(t7)))
    print("T3:", fmt(agg(t3)))
    taken_lag = sum(r["t30"] + r["t60"] for r in t7) == 0 and sum(r["b30"] + r["b60"] for r in t7) > 0
    if taken_lag:
        print("FLAG: calls taken = 0 in T7 with bookings > 0. Likely not filled in yet. Judge show-up on last full month.")
    # Month history: current month-to-date + previous 3 full months
    for back in range(0, 4):
        y, m = end.year, end.month - back
        while m < 1:
            m += 12; y -= 1
        rows = [r for d, r in days.items() if d.year == y and d.month == m and d <= end]
        if rows:
            label = MONTHS[m - 1] + (" (MTD)" if back == 0 else "")
            print(f"{label}:", fmt(agg(rows)))
    # Every bad number: T7 for the top of the funnel, last full month for the slower stages
    cur = MONTHS[end.month - 1]
    recent90 = [r for d, r in days.items() if end - dt.timedelta(days=90) <= d <= end]
    uses_60 = sum(r["b60"] for r in recent90) > 0
    scorecard(key, wb, cur, agg(t7), "T7", top_only=True, uses_60=uses_60)
    pm_y, pm_m = (end.year, end.month - 1) if end.month > 1 else (end.year - 1, 12)
    last_full = [r for d, r in days.items() if d.year == pm_y and d.month == pm_m]
    if last_full:
        scorecard(key, wb, MONTHS[pm_m - 1], agg(last_full), f"{MONTHS[pm_m - 1]} (last full month)", uses_60=uses_60)
    # ROI flag: collected under 2x or contracted under 4x
    print("ROI CHECK (flag if collected < 200% or contracted < 400%):")
    windows = []
    for back in range(1, 4):
        y, m = end.year, end.month - back
        while m < 1:
            m += 12; y -= 1
        windows.append((y, m))
    for lab, sel in [(f"{MONTHS[pm_m - 1]}", [(pm_y, pm_m)]), ("last 3 full months", windows),
                     ("year to date", [(end.year, m) for m in range(1, end.month + 1)])]:
        rows = [r for d, r in days.items() if (d.year, d.month) in sel and d <= end]
        a = agg(rows) if rows else None
        if not a or a["spend"] <= 0:
            continue
        rc, rl = a["ROI_contracted"] or 0, a["ROI_collected"] or 0
        flag = "ROI FLAG" if (rl < 2 or rc < 4) else "ok"
        print(f"    {lab}: spend {a['spend']:,.0f} | contracted {a['rev']:,.0f} ({rc * 100:.0f}%) | "
              f"collected {a['coll']:,.0f} ({rl * 100:.0f}%) | clients {a['new']:.0f} -> {flag}")
    # Best historical month for cost per booked (fallback baseline)
    best = None
    for m in range(1, 13):
        rows = [r for d, r in days.items() if d.month == m and d <= end]
        a = agg(rows) if rows else None
        if a and a["booked"] >= 5 and a["cost_per_booked_all"]:
            if not best or a["cost_per_booked_all"] < best[1]:
                best = (MONTHS[m - 1], a["cost_per_booked_all"], a["booked"])
    print("BEST MONTH cost/booked (5+ bookings):", best or "none")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("files", nargs="+", help="key=path")
    a = ap.parse_args()
    as_of = dt.date.fromisoformat(a.as_of)
    print(f"As of {as_of}. T7 = {as_of - dt.timedelta(days=7)} to {as_of - dt.timedelta(days=1)}, "
          f"T3 = {as_of - dt.timedelta(days=3)} to {as_of - dt.timedelta(days=1)}")
    for f in a.files:
        k, p = f.split("=", 1)
        try:
            run(k, p, as_of)
        except Exception as e:
            print(f"\n===== {k} =====\nERROR reading {p}: {e}")
