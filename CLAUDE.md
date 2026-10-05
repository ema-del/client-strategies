# Pacow Client Scaling Review

Trigger word: **"scale"**. When Ema says "scale" (optionally + a client name to scope it to one client), run this routine.

This file reuses the rules from the weekly funnel reporting session (`ema-del/business` → `CLAUDE.md`), with one change: the goal is **scaling clients**, not just finding bottlenecks. Every run answers per client: **Is there a funnel leak? If not, do they match the scaling rules? Verdict: Scale, or Don't scale (first fix x, y, z).**

Source for the scaling rules: "Pacow Playbook (from Skool)" in Google Drive (01. Clients), sections "Scaling & Optimizing", "Live Webinar / Challenge Funnel", "IG Follower Funnel / DM Ad Funnel" and "Ads Foundations". Follow the playbook, not generic advice.

This routine is **READ-ONLY**. Never write, PUT, POST, or otherwise modify any Google Sheet, landing page, ad account or budget. Diagnosis and recommendations only. Ema makes every live change.

## Data source (ALWAYS follow these steps, in order)

Every "scale" run pulls the full daily data for every client. Do not skip steps, do not use `read_file_content` on the sheets (it only returns the sheet structure, no numbers), and never guess numbers.

**Step 1. Download every workbook (all 8 in one parallel batch).**
For each client in the roster, call Google Drive `download_file_content` with:
- `fileId` = the client's Sheet ID
- `exportMimeType` = `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

This exports the whole workbook (every month tab, daily rows). The result is too big for chat, so the tool saves it to a file and the error message gives the path (`.../tool-results/mcp-Google_Drive-download_file_content-XXXX.txt`). Note each client's path. That's expected, not a failure.

**Step 2. Run the data script once with all 8 files.**
```
python3 scripts/scale_data.py --as-of <today YYYY-MM-DD> pcw=<path> edv=<path> zin=<path> cmtc=<path> pp=<path> c101=<path> nae=<path> sma=<path>
```
(`openpyxl` is installed by the SessionStart hook in `.claude/settings.json`. If it's missing: `pip install -q openpyxl`.)

Per client the script prints:
- **ELIGIBLE:** checks the two most recent dated rows up to yesterday. "NO" = skip the client this run.
- **TARGETS** from the current month tab.
- **DAILY last 10 days** (spend / clicks / leads / booked 30 / booked 60 / taken 30 / taken 60, plus notes).
- **T7** (yesterday and the 6 days before) and **T3** (last 3 days), aggregated from raw counts: CPM, CTR, CPC, LPCR, CPL, pre-qualified and qualified rates, cost per qualified, lead to booked, cost per booked (30, 60, all), show-up, close rate, cost per client, booked calls per day.
- **Month history:** current month to date + the last 3 full months.
- **BEST MONTH** cost per booked call (months with 5+ bookings), the fallback baseline when a target is blank.
- **FLAG** when calls taken = 0 but bookings > 0 in T7.

The windows end **yesterday**, because today's row is usually incomplete.

**Step 3. Only if a download fails** for a client: retry that one once. If it still fails, say so for that client and carry on with the rest. Never fill gaps with guesses.

**Step 4. Meta Ads (only for clients that pass step 1, "no leak").** Use the Meta Ads MCP to check what the sheet can't show: ad set learning status, last budget change, current daily budget, ABO vs CBO, number of live ads, testing ad set (Level 2+), and frequency. Check `is_ads_mcp_enabled` via `ads_get_ad_accounts` first. EdvancedLearning and Class101 are MCP-blocked: write "verify in Ads Manager". **Read only. Never change a budget, status or ad.**

### Reading the data
- **Calls taken lag:** if the script flags calls taken = 0 with bookings > 0, the sheet hasn't been updated yet. Judge show-up on the last full month instead, and say so once.
- **Template targets:** right now all 8 sheets carry the same template targets (CPL <$15, max $45; cost per 30-min booked <$150, max $300; cost per 60-min booked <$250, max $500), in USD even for Smarta (GBP). Use them, but note it once per run until the sheets get client-specific targets.
- **Which booked call counts:** for Pacow, the 60-min call is the real goal (the 30-min call is the first step). For the B2C clients, the 30-min call is the main booking.
- **Year boundary:** sheets are per year. In early January the T7 window can reach into last year's sheet. If so, say which days are missing.
- **Fallback targets:** if a target cell is blank, use the client's BEST MONTH from the script. Only then the generic fallback (CPM <$30, CPC <$4, directional only for non-USD accounts).

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

Every "scale" run answers 3 questions per client, in this order:

1. **Is there a funnel leak?** Run the backward decision tree. Any Bad number (or a Borderline one that clearly drags booked calls) is a leak. If there's a leak, stop here: the verdict is Don't scale.
2. **If no leak: do they match the scaling rules?** Check against their level:
   - Cost per booked call at/under target on the trailing 7 days AND trailing 3 days.
   - Not 50%+ above normal over the trailing 3 days (that's a refresh, not a scale).
   - Ad set out of learning, and no budget change in the last 2-3 days (check Meta if access allows; otherwise flag as "verify in Ads Manager").
   - Enough sample to trust it (not 1-2 booked calls).
   - Level 2+: a testing ad set exists. Level 2+: ABO, not CBO.
3. **Final verdict:** exactly one of
   - **✅ Scale:** the next step for their level (e.g. "+20% budget on the main ad set", "add a $100-200/day testing ad set", "promote ad X").
   - **❌ Don't scale. First fix:** x, y, z (in order, most upstream first, each as Issue → Solution → Tangible Action).

## Output format

- Chat tables, **never an artifact**.
- Per client: level (1/2/3), booked calls/day, cost per booked call (3-day and 7-day vs target), then the 3 questions above.
- Every fix uses **Issue → Solution → Tangible Action**. Simple, concrete, no fluff.
- Every client gets a full, independent write-up. Never "same as above."
- End every full run with a recap table: client, verdict, first thing to do. Include ⚠️ small sample / revenue lag flags.
- Ema's writing rules apply: no em dashes, no buzzwords, short sentences, specific numbers.

## Client roster

| Key | Client | Meta Account | Sheet ID | Notes |
|---|---|---|---|---|
| pcw | Pacow Media | act_3720107534883410 | `1Rnf9ydutojWkWozdMgp6tXvZL8yGHZ-dzS1e36LUffU` | B2B |
| edv | EdvancedLearning | act_912963885192972 | `1wiyaH2GaVdBmUgN1r5ETsswxaG7SQ72zHGShsuA7JaY` | Ads MCP blocked (rolling out) |
| zin | Zinkerz | act_638396012894614 | `1zJqc4H7PsyAzext6MMpuGFYMPrr2Yrx1sUCCpy2fSho` | |
| cmtc | Core Medical Training Center | act_1101825501101670 | `1nordSfrBDgMIz80lf_VSbQA7Y9w4w9zxawph4okq2L8` | Pre-Qualified/Qualified not tracked by design |
| pp | Personalized Prep | act_1747267276471518 | `1tNfePmCajYBhJRibCiVeUk4UJZPn1IXTnxW7X9k3W4Y` | |
| c101 | Class101 | act_2980228195651210 | `1BDn5J24XwEhq6IagIqGZAOd6nO-J6QAGM5Xdc3ebDxk` | Ads MCP blocked (rolling out) |
| nae | North Avenue Education | act_10100817269307566 | `1Z82ommJsxEn13PArnAGGu1Ki5H1OAvhVWnhze-DnDKI` | |
| sma | Smarta Tutoring | act_597834280814934 (Ad Account #1, the only funded one) | `1hILrWWaiuV06tTlFmhPBj7iqfxIHiS1WMZUIzoqHweM` | Pre-Qualified/Qualified not tracked by design. GBP. |

College Zoom is offboarded (2026-09-29). "Smarta Tutoring" and "Much Smarter 1:1 Coaching" (act_1188526852804019) are different companies. Never mix them up.

Before writing anything client-facing, check the client's offer (GrowthOS 90-day, Done for you, Coaching only, Course only) in "01. Clients → 00. Client Profiles (Claude)".
