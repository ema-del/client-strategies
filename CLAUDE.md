# Pacow Client Scaling Review

Trigger word: **"scale"**. When Ema says "scale" (optionally + a client name to scope it to one client), run this routine.

This file reuses the rules from the weekly funnel reporting session (`ema-del/business` → `CLAUDE.md`), with one change: the goal is **scaling clients**, not just finding bottlenecks. Every run answers two questions per client: **Can we scale? If yes, what's the next scaling step? If no, what has to be fixed first?**

Source for the scaling rules: "Pacow Playbook (from Skool)" in Google Drive (01. Clients), sections "Scaling & Optimizing", "Live Webinar / Challenge Funnel", "IG Follower Funnel / DM Ad Funnel" and "Ads Foundations". Follow the playbook, not generic advice.

This routine is **READ-ONLY**. Never write, PUT, POST, or otherwise modify any Google Sheet, landing page, ad account or budget. Diagnosis and recommendations only. Ema makes every live change.

## Data source

Sheet-only for the standard run. Pull numbers from the client's Google Sheet, not the Meta Ads API.

- **Eligibility check:** open the client's Sheet, current month's tab (daily rows), look at the two most recent dated rows. If both show $0/blank spend, skip the client for this run.
- **Performance window:** trailing 7 days of daily rows, aggregated from raw counts (sum numerators and denominators, then compute rates). Never average daily percentage columns.
- **Scaling window:** also check the **trailing 3 days** of cost per booked call. The playbook's refresh and budget decisions run on the trailing 3 days.
- **Booked calls per day:** total booked calls in the trailing 7 days ÷ 7. This sets the client's scaling level.
- **Fallback targets:** if a client's own Dash "Targets" cell is blank, use the client's best historical month for that metric. Only then use the generic fallback (CPM <$30, CPC <$4, directional only for non-USD accounts).

### Known Google Drive tooling limitation
`read_file_content` on large multi-tab sheets may return a structural summary instead of cell values. Retry once, then fall back to `download_file_content` (CSV export), which only reaches the first tab ("Dash"). If daily-tab data is needed and both fail, say so. Never guess numbers.

### Meta Ads access
Use the Meta Ads MCP for deep dives when a scaling call needs it: ad set learning status, current daily budget, ABO vs CBO setup, number of live ads, which ad is winning, frequency. Check `is_ads_mcp_enabled` via `ads_get_ad_accounts` first. If an account is blocked, say so plainly. **Read only. Never change a budget, status or ad.**

## Core scaling rules (from the playbook)

1. **Fix the funnel before the ads.** "Great ads pouring into a leaky funnel still won't make you money." If anything upstream is broken, the action is a fix, not a budget increase.
2. **Scale on cost per booked call, never CPL.** "You'd rather have a $40 CPL and low cost per booking than $4 CPL." Use the client's own Cost Per Booked target from the sheet. Playbook default if blank: about $150 per booked call.
3. **Leave winners alone.** Untouched winning ads stay consistent. Find winners by checking **utm_content** in GHL for each booked call (webinars: the H AD ID on the form submission).
4. **Feed Meta good data.** Only fire the Lead event on qualified opt-ins. As a client scales, optimize for deeper events (qualified booked calls, applications, purchases).
5. **Budget down rule:** if numbers go south, cut 20%. Never drop back to the starting budget in one go.
6. **Ad bank:** a scaling client needs new ads built every 1-2 weeks, ready before they're needed. Never rush an ad because a campaign is tanking.

## Scaling levels (conversion / lead funnels)

Set each client's level from booked calls per day (trailing 7 days).

**Level 1: under 3 booked calls/day**
- Setup: 1 campaign, 1 ad set, 5 ads. Start $100/day B2C, $250/day B2B.
- Raise budget **+20% every 2-3 days**, only when the ad set is out of learning AND cost per booked call is at target.
- **Refresh** when cost per booked call is **50%+ above normal over the trailing 3 days**: add 2-3 new ads from the winning pain point, in different formats. Not 10. One rough day is not a signal.
- Launch never worked (none of the 5 ads booking at a reasonable cost): don't wait for fatigue. New pain points and angles, then relaunch.
- Graduate to Level 2 at **3+ booked calls a day**.

**Level 2: 3-10 booked calls/day**
- Same campaign. Keep scaling the main ad set.
- Add a **testing ad set at $100-200/day** with 3-5 new ads. Never scale the testing ad set.
- Promote a test ad after **2-3 calls at or under target**: duplicate it into the scaling ad set, turn off the test copy, then turn off the testing ad set and launch a new one.
- Judge on cost first: 1 call at $90 vs a $200 target has earned its spot. 3 calls at $400 each hasn't.
- **ABO, not CBO.** Graduate to Level 3 at **10+ booked calls a day**.

**Level 3: 10+ booked calls/day**
- Diversify across several ABO ad sets, 1-3 winners each.
- Launch fresh sets of about 5 ads. New winners seed new ad sets.

## Funnel-specific scaling rules

**DM ads**
- Green light: running **3+ days**, at least **1 call booked**, and **20-25% of leads look qualified**.
- Then +20% every 2-3 days, in the morning. If things go south, drop 20%.

**IG follower / remix scaling**
- Find the pain point booking the cheapest qualified calls. Build 5 new ads around it (new angles first, then new formats or awareness levels).
- Launch them in a **new ad set** at $50-100/day next to the winner. Never add ads into a winning ad set.

**Webinars / challenges**
- Ads run 5-10 days. Fill the tracking sheet daily before touching anything.
- Cost per registration good: raise budget **20-50% per day** (up to 100% if numbers are strong). Not good: kill weak ads, shift budget, add new ads.
- Fix checks after each webinar: landing page under 20% → fix the page. Show rate under 30% → fix reminders. Judge lead quality only after $3-5k spent and 50-100+ people live.
- Scale by frequency: monthly → every other week → weekly. Never put a specific date in ad copy.

**"Hammer Them" retargeting (recommend once a client has steady leads)**
- Awareness objective, CBO, **$1/day per ad set** (5+ ad sets), max reach, frequency cap 1 per 5-7 days.
- Audience: leads, qualified leads, booked calls and attendees (last 30 days) + IG/FB engagers (last 30 days). Use existing organic posts.

## Diagnostic method (same as the reporting session)

Before any scaling call, run the backward decision tree:

1. Start at the bottom-line number (booked calls, new clients, ROI) and walk upstream one stage at a time: Call Taken → Call Booked → Qualified → Pre-Qualified → Lead → Link Clicks → Impressions/CPM.
2. Judge each stage against the sheet's Target/Max first, then the client's best month, then the generic fallback.
3. Context-adjust: B2B CPM/CPC runs higher than B2C. Judge against that client's ICP and history.
4. Find the **single most-upstream broken number**. Name independent problems separately.
5. If the ask was "scale X" but X has a broken upstream number, say so: "You asked to scale, but the real blocker is Y."

### Metric thresholds

**LPCR (Leads ÷ Link Clicks).** Goal 20%. ≥15% Good, 12-15% Borderline, <12% Bad.

**Single-threshold metrics** (below target = miss): CTR, SUP-% (show-up), Lead-to-Qualified, Closing Rate, ROI.

**Target/Max cost metrics:** below Target = Good, Target to ~1.3× Max = Borderline, beyond ~1.3× Max = Bad.

### Interpretive rules
1. CTR healthy + LPCR low → landing page/offer mismatch is the primary suspect, above CPM.
2. Real clicks + near-0 leads → top priority, always.
3. Real leads + 0 downstream movement → assume a disconnected post-lead pipeline first.
4. Pre-Qualified/Qualified 0/0 by design → "not tracked, skip evaluating" (Core Medical Training Center, Smarta Tutoring). Qualified > 0 with Pre-Qualified = 0 → funnel/process gap, not CRM.
5. Revenue lag: closing rate, cost per client and ROI lag spend by weeks. Flag it.
6. Small sample: 1-2 booked/taken/closed in the window → say so, don't treat as signal.

## Scaling decision per client

Every client lands in exactly one bucket:

- **🟢 Scale:** funnel healthy, cost per booked call at/under target on trailing 3 and 7 days, ad set out of learning. Give the next step for their level (e.g. "+20% budget", "add testing ad set", "promote ad X").
- **🟡 Hold / Refresh:** on target but not ready (in learning, just scaled within 2-3 days, small sample), or cost per booked call 50%+ above normal over trailing 3 days → refresh with 2-3 ads.
- **🔴 Fix first:** a broken upstream number. No budget increase until it's fixed.

## Output format

- Chat tables, **never an artifact**.
- Per client: level (1/2/3), booked calls/day, cost per booked call (3-day and 7-day vs target), bucket (🟢/🟡/🔴).
- Every recommendation uses **Issue → Solution → Tangible Action**. Simple, concrete, no fluff.
- Every client gets a full, independent write-up. Never "same as above."
- End every full run with a short recap: 🟢 who to scale and how, 🔴 who to fix first and what. Include ⚠️ small sample / revenue lag flags.
- Ema's writing rules apply: no em dashes, no buzzwords, short sentences, specific numbers.

## Client roster

| Client | Meta Account | Sheet ID | Notes |
|---|---|---|---|
| Pacow Media | act_3720107534883410 | `1Rnf9ydutojWkWozdMgp6tXvZL8yGHZ-dzS1e36LUffU` | B2B |
| EdvancedLearning | act_912963885192972 | `1wiyaH2GaVdBmUgN1r5ETsswxaG7SQ72zHGShsuA7JaY` | Ads MCP blocked (rolling out) |
| Zinkerz | act_638396012894614 | `1zJqc4H7PsyAzext6MMpuGFYMPrr2Yrx1sUCCpy2fSho` | |
| Core Medical Training Center | act_1101825501101670 | `1nordSfrBDgMIz80lf_VSbQA7Y9w4w9zxawph4okq2L8` | Pre-Qualified/Qualified not tracked by design |
| Personalized Prep | act_1747267276471518 | `1tNfePmCajYBhJRibCiVeUk4UJZPn1IXTnxW7X9k3W4Y` | |
| Class101 | act_2980228195651210 | `1BDn5J24XwEhq6IagIqGZAOd6nO-J6QAGM5Xdc3ebDxk` | Ads MCP blocked (rolling out) |
| North Avenue Education | act_10100817269307566 | `1Z82ommJsxEn13PArnAGGu1Ki5H1OAvhVWnhze-DnDKI` | |
| Smarta Tutoring | act_597834280814934 (Ad Account #1, the only funded one) | `1hILrWWaiuV06tTlFmhPBj7iqfxIHiS1WMZUIzoqHweM` | Pre-Qualified/Qualified not tracked by design. GBP. |

College Zoom is offboarded (2026-09-29). "Smarta Tutoring" and "Much Smarter 1:1 Coaching" (act_1188526852804019) are different companies. Never mix them up.

Before writing anything client-facing, check the client's offer (GrowthOS 90-day, Done for you, Coaching only, Course only) in "01. Clients → 00. Client Profiles (Claude)".
