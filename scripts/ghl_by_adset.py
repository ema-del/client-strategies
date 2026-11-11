#!/usr/bin/env python3
"""Real leads, CPL and bookings per Meta ad set, counted from GHL contacts (not Meta's lead count).

Standalone: reads two files, prints a table. Doesn't import or change the other scripts.

  python3 scripts/ghl_by_adset.py --meta meta_ads.json --ghl ghl_contacts.json [--from 2026-10-19 --to 2026-11-01]
                                   [--map "100k2027reminder=100k2027reminder" ...]

--meta  JSON list (or CSV with a header) of ads: ad, adset, spend, meta_leads (optional).
--ghl   JSON from GHL contact search: a list of contacts, or {"contacts": [...]}, or a list of pages.
        Per contact it reads utm_content (attributionSource / lastAttributionSource / customFields / utm_content),
        tags and dateAdded.
--map   "<ghl utm_content>=<meta ad name>" for names the fuzzy match gets wrong. Repeatable.

Each GHL utm_content is matched to a Meta ad (exact after normalizing, then the closest name).
Everything that doesn't match is printed under UNMATCHED, so nothing is silently dropped.
"""
import argparse, csv, difflib, json, re, sys
from collections import defaultdict

TAGS = {  # regex on each tag, lowercased. Defaults fit Pacow; override with --tag key=regex.
    "prequal": r"(?<!not )prequalified",
    "qual": r"qualified lead",
    "b30": r"connection call \| booked|30.?min.*booked|call booked",
    "b60": r"decision booked|60.?min.*booked",
    "noshow": r"no.?show",
    "won": r"purchased|closed won|new client",
}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def first_num(v):
    """Meta sometimes labels results ("130 profile visits"): take the leading number."""
    m = re.match(r"\s*(-?[\d,]*\.?\d+)", str(v or 0))
    return float(m.group(1).replace(",", "")) if m else 0.0


def load_meta(path):
    if path.endswith(".csv"):
        rows = list(csv.DictReader(open(path)))
    else:
        rows = json.load(open(path))
    out = []
    for r in rows:
        out.append({"ad": r["ad"], "adset": r["adset"], "spend": first_num(r.get("spend")),
                    "meta_leads": first_num(r.get("meta_leads"))})
    return out


def contacts(data):
    if isinstance(data, dict):
        data = data.get("contacts", [data])
    for item in data:
        if isinstance(item, dict) and "contacts" in item:
            yield from item["contacts"]
        elif isinstance(item, list):
            yield from contacts(item)
        else:
            yield item


def utm_content(c):
    for k in ("attributionSource", "lastAttributionSource"):
        v = (c.get(k) or {}).get("utmContent") or (c.get(k) or {}).get("utm_content")
        if v:
            return v
    for f in c.get("customFields") or []:
        if "utm_content" in str(f.get("key") or f.get("name") or "").lower() and f.get("value"):
            return f["value"]
    return c.get("utm_content") or c.get("utmContent")


def match(utm, ads, manual):
    if utm in manual:
        return manual[utm]
    n = norm(utm)
    by_norm = {norm(a): a for a in ads}
    if n in by_norm:
        return by_norm[n]
    inside = [k for k in by_norm if n and (n in k or k in n)]
    if len(inside) == 1:
        return by_norm[inside[0]]
    if len(inside) > 1:  # e.g. "breakingvika" fits "breaking vika claude" and "breakingvikap1..p5": never guess
        return None
    best = difflib.get_close_matches(n, list(by_norm), n=1, cutoff=0.6)
    return by_norm[best[0]] if best else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--meta", required=True)
    p.add_argument("--ghl", required=True, nargs="+")
    p.add_argument("--from", dest="frm")
    p.add_argument("--to")
    p.add_argument("--map", action="append", default=[])
    p.add_argument("--tag", action="append", default=[], help="key=regex, keys: " + ",".join(TAGS))
    a = p.parse_args()

    tags = dict(TAGS)
    for t in a.tag:
        k, v = t.split("=", 1)
        tags[k] = v
    manual = dict(m.split("=", 1) for m in a.map)
    meta = load_meta(a.meta)
    ad_set = {m["ad"]: m["adset"] for m in meta}

    per_ad = defaultdict(lambda: defaultdict(int))
    unmatched = defaultdict(int)
    seen = set()
    for path in a.ghl:
        for c in contacts(json.load(open(path))):
            cid = c.get("id") or id(c)
            if cid in seen:
                continue
            seen.add(cid)
            day = str(c.get("dateAdded") or "")[:10]
            if (a.frm and day and day < a.frm) or (a.to and day and day > a.to):
                continue
            utm = utm_content(c)
            if not utm:
                continue
            ad = match(utm, ad_set, manual)
            if not ad:
                unmatched[utm] += 1
                continue
            row = per_ad[ad]
            row["leads"] += 1
            tl = [str(t).lower() for t in c.get("tags") or []]
            for k, rx in tags.items():
                if any(re.search(rx, t) for t in tl):
                    row[k] += 1

    sets = defaultdict(lambda: defaultdict(float))
    for m in meta:
        s = sets[m["adset"]]
        s["spend"] += m["spend"]
        s["meta_leads"] += m["meta_leads"]
        for k, v in per_ad.get(m["ad"], {}).items():
            s[k] += v

    def line(name, r):
        leads = r.get("leads", 0)
        cpl = f"{r['spend'] / leads:,.0f}" if leads else "-"
        b30 = r.get("b30", 0)
        cpb = f"{r['spend'] / b30:,.0f}" if b30 else "-"
        ml = r.get("meta_leads", 0)
        ratio = f"{ml / leads:.1f}x" if leads else ("inf" if ml else "-")
        return (f"| {name} | {r['spend']:,.0f} | {leads:.0f} | {cpl} | {r.get('prequal', 0):.0f} | "
                f"{b30:.0f} | {r.get('b60', 0):.0f} | {cpb} | {r.get('won', 0):.0f} | {ml:.0f} | {ratio} |")

    head = "| {} | Spend | GHL leads | CPL | Prequal | Booked 30 | Booked 60 | Cost/30 booked | Won | Meta leads | Meta ÷ GHL |"
    sep = "|---" * 11 + "|"
    print("AD SETS (leads and bookings from GHL)")
    print(head.format("Ad set"))
    print(sep)
    for name, r in sorted(sets.items(), key=lambda x: -x[1]["spend"]):
        print(line(name, r))
    print("\nADS")
    print(head.format("Ad (ad set)"))
    print(sep)
    for m in sorted(meta, key=lambda x: -x["spend"]):
        r = defaultdict(float, per_ad.get(m["ad"], {}))
        r["spend"], r["meta_leads"] = m["spend"], m["meta_leads"]
        print(line(f"{m['ad']} ({m['adset']})", r))
    if unmatched:
        print("\nUNMATCHED GHL utm_content (add --map \"<utm>=<meta ad>\"):")
        for u, n in sorted(unmatched.items(), key=lambda x: -x[1]):
            print(f"  {u}: {n} leads")


if __name__ == "__main__":
    sys.exit(main())
