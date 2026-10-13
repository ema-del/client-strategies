#!/usr/bin/env python3
"""Per-campaign funnel for clients running 2+ campaigns.

Meta gives spend / impressions / link clicks per campaign. GHL gives what happened
to each lead, split by the contact's campaign attribution (utm_campaign).
This joins the two and prints the chain per campaign, side by side.

Usage:
  python3 scripts/campaign_split.py --from 2026-10-09 --to 2026-10-12 \
      --meta "newmay2026:OLead=1196,9000,203" --meta "ocompleteregistration:OCR=1004,7698,135" \
      ghl_page1.txt [ghl_page2.txt ...]

--meta "<utm_campaign>:<label>=<spend>,<impressions>,<link clicks>" (one per campaign, from Meta)
GHL files = saved results of HighLevel search-contacts-advanced (dateAdded range covering the window).
Tag names default to Pacow's; override with --tag key="tag text" (key: prequal, qual, booked, showed, won).
"""
import argparse, collections, json

DEFAULT_TAGS = {
    "prequal": ["meta | prequalified"],
    "qual": ["meta | qualified lead"],
    "booked": ["connection call | booked", "decision booked"],
    "showed": ["attended", "showed"],
    "won": ["purchased", "won", "client"],
}


def load_contacts(paths):
    out = []
    for p in paths:
        s = open(p).read()
        d = json.loads(s[s.find("{"): s.rfind("}") + 1])
        out += d.get("data", d)["contacts"]
    return out


def camp(c):
    a = c.get("attributionSource") or {}
    return (a.get("campaign") or a.get("utmCampaign") or "-").lower(), (a.get("utmMedium") or a.get("medium") or "")


def pct(a, b, dec=0):
    return f"{a / b * 100:.{dec}f}%" if b else "-"


def money(a, b):
    return f"{a / b:,.0f}" if b else "-"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="lo", required=True)
    ap.add_argument("--to", dest="hi", required=True)
    ap.add_argument("--meta", action="append", required=True)
    ap.add_argument("--tag", action="append", default=[])
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    tags = {k: list(v) for k, v in DEFAULT_TAGS.items()}
    for t in a.tag:
        k, v = t.split("=", 1)
        tags.setdefault(k, []).append(v.lower())

    meta = {}
    for m in a.meta:
        key, nums = m.split("=", 1)
        utm, label = key.split(":", 1)
        sp, im, cl = (float(x) for x in nums.split(","))
        meta[utm.lower()] = (label, sp, im, cl)

    counts = collections.defaultdict(collections.Counter)
    for c in load_contacts(a.files):
        if not (a.lo <= c["dateAdded"][:10] <= a.hi):
            continue
        cp, med = camp(c)
        if cp not in meta:
            continue
        t = " || ".join(x.lower() for x in (c.get("tags") or []))
        counts[cp]["leads"] += 1
        for k, needles in tags.items():
            if any(n in t for n in needles):
                counts[cp][k] += 1

    rows = [("Spend", lambda m, c: f"{m[1]:,.0f}"),
            ("CPM", lambda m, c: money(m[1] * 1000, m[2])),
            ("Link CTR", lambda m, c: pct(m[3], m[2], 1)),
            ("Link clicks", lambda m, c: f"{m[3]:.0f}"),
            ("Leads (GHL)", lambda m, c: str(c["leads"])),
            ("LPCR", lambda m, c: pct(c["leads"], m[3], 1)),
            ("CPL", lambda m, c: money(m[1], c["leads"])),
            ("Prequalified", lambda m, c: f"{c['prequal']} ({pct(c['prequal'], c['leads'])})"),
            ("Qualified", lambda m, c: f"{c['qual']} ({pct(c['qual'], c['leads'])})"),
            ("Cost per qualified", lambda m, c: money(m[1], c["qual"])),
            ("Booked", lambda m, c: f"{c['booked']} ({pct(c['booked'], c['leads'])} of leads)"),
            ("Cost per booked", lambda m, c: money(m[1], c["booked"])),
            ("Showed", lambda m, c: f"{c['showed']} ({pct(c['showed'], c['booked'])})"),
            ("Won", lambda m, c: str(c["won"])),
            ]
    keys = list(meta)
    print(f"Window {a.lo} to {a.hi}")
    print("| Metric | " + " | ".join(meta[k][0] for k in keys) + " |")
    print("|---|" + "---|" * len(keys))
    for name, f in rows:
        print(f"| {name} | " + " | ".join(f(meta[k], counts[k]) for k in keys) + " |")
    small = [meta[k][0] for k in keys if counts[k]["booked"] < 3]
    if small:
        print(f"\nSMALL SAMPLE: under 3 bookings for {', '.join(small)}. Bookings lag leads by days.")
