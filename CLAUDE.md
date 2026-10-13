# Pacow Client Scaling Review

Trigger word: **"scale"**. When Ema says "scale" (optionally + a client name to scope it to one client), run this routine.

This file reuses the rules from the weekly funnel reporting session (`ema-del/business` → `CLAUDE.md`), with one change: the goal is **scaling clients**, not just finding bottlenecks. Every run answers per client: **Is there a funnel leak? If not, do they match the scaling rules? Verdict: Scale, or Don't scale (first fix x, y, z).**

Source for the scaling rules: "Pacow Playbook (from Skool)" in Google Drive (01. Clients), sections "Scaling & Optimizing", "Live Webinar / Challenge Funnel", "IG Follower Funnel / DM Ad Funnel" and "Ads Foundations". Follow the playbook, not generic advice.

This routine is **READ-ONLY**. Never write, PUT, POST, or otherwise modify any Google Sheet, landing page, ad account or budget. Diagnosis and recommendations only. Ema makes every live change.

## Data source (ALWAYS follow these steps, in order)

Every "scale" run pulls the full daily data for every client. Do not skip steps, do not use `read_file_content` on the sheets (it only returns the sheet structure, no numbers), and never guess numbers.

**Step 1. Download every workbook (all 10 in one parallel batch).**
For each client in the roster, call Google Drive `download_file_content` with:
- `fileId` = the client's Sheet ID
- `exportMimeType` = `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

This exports the whole workbook (every month tab, daily rows). The result is too big for chat, so the tool saves it to a file and the error message gives the path (`.../tool-results/mcp-Google_Drive-download_file_content-XXXX.txt`). Note each client's path. That's expected, not a failure.

**Step 2. Run the data script once with all 10 files.**
```
python3 scripts/scale_data.py --as-of <today YYYY-MM-DD> pcw=<path> edv=<path> zin=<path> cmtc=<path> pp=<path> c101=<path> nae=<path> sma=<path> uca=<path> ms=<path>
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
- **SCORECARD T7** (top of funnel: CTR, LPCR, CPL, lead-to-qualified, cost per booked) and **SCORECARD last full month** (every metric with a sheet target, including show-up, cost per call taken, close rate, cost per client, ROI). Each line says Good / Borderline / BAD, then an **ALL BAD** line.
- **ROI CHECK** for the last full month, the last 3 full months and year to date, with **ROI FLAG** when collected ROI is under 200% or contracted ROI is under 400%.

The windows end **yesterday**, because today's row is usually incomplete.

**Step 3. Only if a download fails** for a client: retry that one once. If it still fails, say so for that client and carry on with the rest. Never fill gaps with guesses.

**Step 4. Meta Ads (only for clients that pass step 1, "no leak").** Use the Meta Ads MCP to check what the sheet can't show: ad set learning status, last budget change, current daily budget, ABO vs CBO, number of live ads, testing ad set (Level 2+), and frequency. Check `is_ads_mcp_enabled` via `ads_get_ad_accounts` first. EdvancedLearning and Class101 are MCP-blocked: write "verify in Ads Manager". **Read only. Never change a budget, status or ad.**

### Reading the data
- **Calls taken lag:** if the script flags calls taken = 0 with bookings > 0, the sheet hasn't been updated yet. Judge show-up on the last full month instead, and say so once.
- **Template targets:** right now the 8 call-funnel sheets carry the same template targets (CPL <$15, max $45; cost per 30-min booked <$150, max $300; cost per 60-min booked <$250, max $500), in USD even for Smarta (GBP). Use them, but note it once per run until the sheets get client-specific targets.
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
7. **Never "kill or keep" without branching.** Before recommending turning off a campaign, ad set or ad (or comparing two campaigns), walk ITS funnel stage by stage (CPM → CTR → LPCR → prequalified → survey taken → qualified → booked → show-up → close), side by side with the alternative, and find WHY it's underperforming. If the bottleneck is downstream or shared by both (survey step, show-up, close rate, tracking), the answer is: fix that bottleneck first, then re-judge the campaign on cost per qualified call. Switching campaigns doesn't fix a leak that sits after the opt-in. A kill rule (e.g. 2-3x cost-per-call target with no qualified call) only applies once the funnel behind it is working.

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

## ALWAYS walk backwards from ROI (every client, every run)

Run `python3 scripts/roi_backwards.py --as-of <today> <key>=<path> ...` on the same files as step 2. It treats ROI as a chain of multiplications and walks it **backwards, metric by metric, through every metric in the sheet**:

collected/contracted → deal size → close rate → show-up (60) → 30-min taken to 60-min booked → show-up (30) → booked rate → lead to qualified → LPCR → CTR → CPM

For each link it prints the actual, the baseline (sheet target, else playbook target, else the client's best month with 20+ leads; deal size and collection use the year-to-date average) and **"ROI x if fixed alone"**: how many times ROI would multiply if only that link hit its baseline. A link at zero is BROKEN. It also prints **DATA** notes when the sheet itself is inconsistent (more bookings than qualified leads, more 60-min bookings than 30-min calls taken, calls taken not entered).

How to use it:
- **Start every client write-up from ROI and go backwards.** The answer to "why is there no ROI" is the ranked list of leaks with their multipliers, not the first bad number at the top of the funnel.
- **Never judge a link the DATA notes say is broken.** Say the data is wrong and what to fix in the sheet, then rank the rest.
- **Use the right close rate.** For 2-step funnels (Pacow: 30-min then 60-min), close rate = clients ÷ 60-min calls taken. The sheet's "Call Closing Rate" divides by all calls and understates it.
- **Fixes multiply.** Two x1.5 fixes = x2.25. Show what fixing the top 2-3 together does to ROI.
- **Any decision about a campaign, ad set or budget gets checked against this chain** (e.g. a campaign with 30% higher CPM has to improve later links by more than 30% to pay off).
- UCA and MS: the walk needs a full month of data. Until then, use the scorecards.

## Track every bad number (never stop at the first one)

The backward decision tree finds the **root cause** (most-upstream broken number). That's still the first fix. But every run also **lists every BAD number in the chain**, all the way to ROI. Don't stop at cost per booked, bookings or show-up.

- Use the script's two scorecards: **T7** for the top of the funnel, **last full month** for the slower stages (show-up, call taken, close rate, cost per client, ROI lag the spend, so 7 days is too early to judge them).
- In each client write-up, add an **"All bad numbers"** line with every BAD from both scorecards, grouped: root cause first, then downstream symptoms, then independent problems.
- A downstream BAD that's caused by an upstream one (e.g. high cost per client because LPCR is bad) is still listed, marked "symptom of X".
- A downstream BAD that isn't caused upstream (e.g. close rate 5% while bookings are cheap) is its own issue and gets its own Issue → Solution → Tangible Action.
- Skip 60-min call metrics for clients with no 60-min bookings in the last 90 days (the script does this).
- Pre-Qualified/Qualified stays "not tracked, skip" for Core Medical and Smarta.

## ROI flag (every run, every client)

Targets from the sheets: **Collected ROI above 200%** and **Contracted ROI above 400%**.

- **🚩 ROI FLAG** when either is under target in the **last full month** or the **last 3 full months**. Show the year-to-date number for context.
- Show it in every client write-up and in the recap table, even when the verdict is already "Don't scale".
- **Revenue lag:** clients often pay weeks after the call. A weak last month with a healthy 3-month number = flag, but say "likely lag".
- **Zero revenue:** always flag it, no exceptions. Some sheets have revenue that was never entered, others are genuinely bad. Either way it gets the 🚩. Add "(check revenue is entered)" next to the flag, but never drop or soften the flag.
- **Scaling rule:** an ROI flag on the last 3 full months blocks a "Scale" verdict unless the shortfall is clearly revenue lag. Scaling spend into a funnel that doesn't pay back makes the loss bigger.

## Scale or no scale: 4 gates (all must pass)

The ROI walk says where money leaks. The gates say whether more budget would make more money. Check in this order and stop at the first NO.

| Gate | Question | Pass when | If NO |
|---|---|---|---|
| 1. Money back | Did ads pay back? | Collected ROI 200%+ and contracted 400%+ over the last 3 full months (clearly lag = note it, can pass) | ❌ Don't scale: more spend = bigger loss |
| 2. Can they close? | Do booked calls turn into clients? | Show-up and close rate at target on 5+ calls taken (last full month or 3 months; right close rate for 2-step funnels) | ❌ Don't scale: more calls get wasted. Fix show-up / sales first |
| 3. Cheap enough calls? | Is cost per booked call at target? | CPB at/under target over T7 AND T3, 3+ bookings | ❌ Don't scale yet: the client can close, the ad/page side is the bottleneck. Fix top of funnel |
| 4. Ready in Meta | Can the ad set take more budget? | Out of learning, no budget change in 2-3 days, not 50%+ above normal CPB over T3 (that's a refresh) | Wait / refresh, then scale |

All 4 pass = ✅ Scale, with the next step for their level (+20% budget, testing ad set, promote ad X).
Gate 2 passing with gate 3 failing is the "they can close, we just need cheaper calls" case. Gate 3 passing with gate 2 failing is "we're sending calls they can't close": never scale that.
Non-call funnels (UCA, MS): gate 2 = purchase rate / trial to paid at target, gate 3 = cost per sign-up / paid sub at target.

## Clients with 2+ campaigns (per-campaign breakdown)

Ema says in advance which clients run 2+ campaigns. For those, every run adds a per-campaign split:
1. Meta: spend, impressions, link clicks per campaign for the window (ads_get_ad_entities, level adset or campaign, time_range).
2. GHL: contacts for the window (HighLevel search-contacts-advanced, dateAdded range, paginate with searchAfter).
3. Run `python3 scripts/campaign_split.py --from <date> --to <date> --meta "<utm_campaign>:<label>=<spend>,<impr>,<clicks>" ... <ghl files>`. It prints the chain per campaign side by side (CPM → CTR → LPCR → CPL → prequalified → qualified → booked → cost per booked).
4. Show-up, close and revenue usually aren't tagged per campaign in GHL: use the sheet's numbers for those and say "shared".
5. Each campaign gets its own one-line verdict (scale / hold / fix / cut) with the gate that decides it. A campaign with higher CPM has to beat the other on later links by more than that CPM gap.

| Client | Campaigns (label = utm_campaign in GHL) | GHL location |
|---|---|---|
| Pacow | OLead = `newmay2026`, OCompleteRegistration = `ocompleteregistration` (launched 2026-10-09) | `0qwvw0jdwrp2PHxMeBiF` |

## Output format (short. Ema knows what every number means: no explanations)

Per client:
```
### <Client> · Level <n> · <x> booked/day
ROI: <last month> collected <c>% / contracted <k>% · 3 months <c>% / <k>% <🚩 or ok>

| Metric (backwards from ROI) | Actual | Baseline | ROI × | Fix |
|---|---|---|---|---|
(every row from roi_backwards.py, in order. "Fix" = one short action, only on rows × 1.05+ or BROKEN. DATA gaps as one row: "data gap: <what to fix in the sheet>")

Fix top 2-3 together: ROI <now> → <after>

| Gate | Result |
|---|---|
| 1. Money back | ✅/❌ <number> |
| 2. Can they close | ✅/❌ <show-up>, <close> |
| 3. Cheap calls | ✅/❌ CPB T7 <x> / T3 <y> vs <target> |
| 4. Ready in Meta | ✅/❌/not checked |

**✅ Scale: <next step>** or **❌ Don't scale: <gate that failed, in a few words>**
```
- Multi-campaign clients: add the campaign split table + one verdict line per campaign.
- No paragraphs, no "what this means" sections. Tables + one-line fixes + verdict.
- End the run with the recap table: client · verdict · failed gate · #1 ROI leak (× multiplier) · ROI flag.
- Chat only, never an artifact. Ema's writing rules: no em dashes, no buzzwords, specific numbers.

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
| uca | UCA | act_1150974895696033 | `1L23VKg6j2MG5g7f8vq5XuF-LWgIMP7K9QMTulyDijw4` | **Low-ticket funnel** (no calls). Ads launched 2026-10-09. |
| ms | Much Smarter (MS, "TheGame") | act_1188526852804019 | `1xFKdhYqGNlY-R0NEnJYmSM8S25ra9kRQU_kY563YI6A` | **Subscription funnel** (free trial → paid sub, no calls). Ads launched 2026-10-08. |

College Zoom is offboarded (2026-09-29). "Smarta Tutoring" (sma) and "Much Smarter" (ms, act_1188526852804019) are different companies. Never mix them up.

### Non-call funnels (UCA, MS)
These two have no booked calls, so the call-based rules (booked calls/day, cost per booked call, show-up, close rate) don't apply. Judge them on their own chain:
- **UCA (low-ticket):** CPM → CTR → LPCR → CPL → **new sign-ups** (purchases) → purchase rate (sheet target >70%) → cost per new client (target <$1,000, max $2,000) → **collected ROI** (target >2x).
- **MS (subscription):** CPM → CTR → LPCR → CPL → **free trial starts** → **paid subs** → cost per paid sub → **new MRR**. ROI = new MRR ÷ spend, flagged under 2x like collected ROI. The sheet has no targets beyond CTR yet: use the generic fallbacks and say so.
- **Level** for these = paid conversions per day (sign-ups or paid subs) instead of booked calls per day, same thresholds (under 3 / 3-10 / 10+).
- The script reads both layouts: sign-ups and paid subs count as "new", new MRR counts as collected revenue.

Before writing anything client-facing, check the client's offer (GrowthOS 90-day, Done for you, Coaching only, Course only) in "01. Clients → 00. Client Profiles (Claude)".
