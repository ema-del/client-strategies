Pacow Daily Marketing Report — MAIN Routine (v18, runs 09:05 UTC). Paste this whole file into the scheduled task. It replaces v8–v17 completely; nothing else is needed.

CHANGES vs v17 (v18):
- Removed for good (offboarded): EdvancedLearning, Zinkerz, Core Medical Training Center (all of old section 6B) and ST (Smarta Tutoring). Never process them.
- Personalized Prep and Class101 moved to their new Messenger (DM ad) sheets, with their own DM layout (section 13). The old sheets are retired.
- New: Pacow Mini-Course sheet (section 14). Mini-course contacts and the OMiniCourse ad set are no longer counted on the main Pacow sheet.
- New: Gaja Collective (section 12).
- North Avenue Education: only the lead campaign is ours (section 1 note).
Earlier changes still apply: Pacow is ONE main sheet and stops at P; the Pacow OCR sheet is retired; Tutoring Club has its own layout (section 10); IPS and CNA are Meta-only (section 11); UCA is Meta-only; CPP has its own separate late routine; any contact who has EVER booked the Pacow calendar 7NPxioFxJEtTGHdLoBzx ("Free Growth Call with Pacow Media") is removed from the Pacow P count, and that calendar is never tracked.

Objective: Once daily, pull yesterday's paid-social lead performance from Meta Ads + GoHighLevel for each active client and write it into the correct row of that client's Google Sheet. Silent on success; notify (PushNotification, ONE message covering everything) only on failure or anomaly.

================================================== 0. GENERAL RULES (apply to every client)
Columns the routine may write (the script enforces this; a refusal means your ranges are wrong, never work around it):

Meta-only clients (UCA, IPS, CNA; no GHL): B (Adspend), C (Impr), E (Link Clicks) ONLY. Never write H or anything else.
Standard clients (North Avenue, Gaja Collective): B, C, E, H (Lead), I (Pre-Qualified), J (Qualified), P (30 Min Calls Booked).
Pacow Media (main sheet): B, C, E, H, I, J, P ONLY. NEVER write, overwrite, blank or "fix" S, V, X, AA, AD or AE, even if they look stale or wrong. Never touch the old OCR sheet.
Pacow Mini-Course sheet: B, C, E, H, P ONLY (section 14). Never I, J or anything else.
Messenger (DM) clients (Personalized Prep, Class101): B, C, E, H (Messages) ONLY (section 13). Never the call, keyword, client or revenue columns.
Tutoring Club of Round Rock (OWN LAYOUT): B, C, E, H (Lead), M (30 Min Calls Booked). Never I, J, P or anything else on this sheet.
MuchSmarter: B, C, E, H, I (Free Trial Starts), J (Paid Subs), K (Unsubscribed). No P.

D, F, G and every other column hold the sheet's own formulas (or human input): never write, read-modify, or blank them, not even as an empty string. Only write what was actually pulled; never write a guessed/default number.

Sheet layout: tab = the 3-letter month of the row's own date (e.g. "Nov"). Row 1 = headers, row 2 = "Targets", data starts row 3. Column A = date shown as "Ddd, Mon D" (stored as a serial, so match against FORMATTED_VALUE). Never assume a row number; find the row by exact text match in column A every time.

Google Sheets access ONLY through scripts/sheets_io.py, run from the repo folder (it prints JSON and never shows a credential). The spreadsheet id is the first argument:

Read: python3 scripts/sheets_io.py read <spreadsheetId> "Nov!A1:AE40" FORMATTED_VALUE (render: FORMATTED_VALUE | UNFORMATTED_VALUE | FORMULA)
Several ranges: python3 scripts/sheets_io.py batchget <spreadsheetId> UNFORMATTED_VALUE "Nov!B8:C8" "Nov!H8:J8"
Write: echo '[{"range":"Nov!B8:C8","values":[[314.4,3048]]},{"range":"Nov!E8","values":[[57]]}]' | python3 scripts/sheets_io.py write <spreadsheetId> (There is no "tabs" command.)

Write only non-contiguous ranges, one row per range. Per client:

Standard (North Avenue, Gaja) and Pacow main: {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}:J{r}, {tab}!P{r}.
Pacow Mini-Course: {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}, {tab}!P{r}.
PP / Class101: {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}.
MuchSmarter: {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}:K{r}.
UCA / IPS / CNA: {tab}!B{r}:C{r} and {tab}!E{r} only.
Tutoring Club: {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}, {tab}!M{r} only.

Never run scripts/get_token.py, never open or print anything in .secrets/. If the script itself fails or refuses a sheet, notify and stop that step; do not try another way to get a Google token.

Tip: when you read a range that starts above the target row (for example A19:AE21), the first returned row is row 19, not the target. Compute the row number from the match, not from the position in a partial read.

Overwrite safety: non-empty cells may be overwritten (idempotent daily rerun) ONLY if they still look like this routine's own output. Read the target cells first; if a cell holds a non-zero value that differs from what you computed AND it is not one of this routine's own outputs, do NOT overwrite it, skip that cell, and mention it in the notification. After writing, read back the written columns on the row plus the row above and below and confirm neighbours and formula columns are untouched.

================================================== 1. CLIENTS
Format: # Client | Meta ad account (act_) | GHL locationId | Timezone | Sheet id

1. Pacow Media (main sheet) | 3720107534883410 | 0qwvw0jdwrp2PHxMeBiF | Europe/Madrid | 1Rnf9ydutojWkWozdMgp6tXvZL8yGHZ-dzS1e36LUffU
2. Pacow Mini-Course (same ad account and location) | 3720107534883410 | 0qwvw0jdwrp2PHxMeBiF | Europe/Madrid | 1pnisEwkxJuXlf3FLtB5ibLFxPXaf8seGKcc1t_Tj5k4
3. Personalized Prep (DM funnel) | 1747267276471518 | ED1AmWov8r8nkMVd2j7d | America/Los_Angeles | 17fseVTM39w18nAD3PvdSBIAh_kfqHB-qPBF0Z8fntYo
4. Class101 (DM funnel) | 2980228195651210 | aHEltqJeunfokavH34Dp | America/Detroit | 1Ata7HhBeW5ci4FK8uMr4kToyQH7XcwCBUe7bXaZxhIU
5. North Avenue Education | 10100817269307566 | 5FdOp9F5Ykv0utafqtJw | America/Los_Angeles | 1Z82ommJsxEn13PArnAGGu1Ki5H1OAvhVWnhze-DnDKI
6. MuchSmarter (USD) | 1188526852804019 | BiXA05d3lZtOOKL4qz29 | America/New_York | 1xFKdhYqGNlY-R0NEnJYmSM8S25ra9kRQU_kY563YI6A
7. UCA (Ultimate College Admissions), Meta only | 1150974895696033 | no GHL | America/Los_Angeles (ad account tz) | 1L23VKg6j2MG5g7f8vq5XuF-LWgIMP7K9QMTulyDijw4
8. Tutoring Club of Round Rock | 1083923977552261 | obAQOtXrmIZEg3fdnN0o | America/Chicago | 1E1dYj8DHjuyD7B1h6pVVMEiVAxdl-q735id5_15QzLE
9. IPS (Institute of Pediatric Sleep and Parenting), Meta only | 54671718 | no GHL | ad account tz | 1gEF5m_tq_UkkBfkJDcnIN3bJK8b4n8lTig0FcTSXNZU
10. CNA Training, Meta only | 10150383113508216 | no GHL | ad account tz | 11wgx68clelDJNlI3PlMNQNd-ZBGPiiml3wPBK5YbkNM
11. Gaja Collective | 1095582199186919 | UAYJ0s7WOOyMnEyh7uEv | America/Los_Angeles | 1KxiVVZbHiX0ckZisPrS06_lrQ6LHBXl1_N3-IhO_FUk

North Avenue Education: only the lead campaign "OLead - NAE - 30+" is ours. The SAT/ACT Webinar traffic campaign and any Marketplace listing boost (e.g. "2 Beds 1 Bath House") are the client's own: never count them. The Step 2 lead rule already leaves them out; if one of them ever qualifies, leave it out anyway and mention it.

CPP (The College Prep Pro) is NOT part of this routine; it runs in its own late routine. Do not touch the CPP sheet or ad account here.

Offboarded / retired (never process, never write, never mention): EdvancedLearning, Zinkerz, Core Medical Training Center, ST (Smarta Tutoring), College Zoom, Lingua Verna, Cyber6, Englisher; the Pacow OCompleteRegistration sheet (1bkzfuqn968YoJXiY7GHTLNzCA8JFB2Ak7swifecJw9E); the old PP sheet (1tNfePmCajYBhJRibCiVeUk4UJZPn1IXTnxW7X9k3W4Y); the old Class101 sheet (1BDn5J24XwEhq6IagIqGZAOd6nO-J6QAGM5Xdc3ebDxk). Frozen archive, never write: the "- OSchedule" sheet (17KWKi3khYLMdBn8SabayX79RotaOpBmpdwzLkGMmpck).

Per-client blockers (check each run, don't dig further): the Class101 and CNA Training (10150383113508216) Meta ad accounts are is_ads_mcp_enabled:false. Leave their Meta cells untouched (do not write empty strings) until that flips. Re-check each run via ads_get_ad_accounts and mention the blocks once in the notification.

================================================== 2. STEP 1 — Dates (per client's own timezone)
"Yesterday" is computed in each client's own timezone (use Python zoneinfo, so DST is right). Contact dateAdded cutoffs and calendar-event local dates both use that client's own offset, never one blanket timezone. Sheet label "Ddd, Mon D". On a month rollover use the tab of that client's own "yesterday". Convert the local midnight-to-midnight window to UTC ISO strings for GHL range filters.

================================================== 3. STEP 2 — Meta Ads (B, C, E)
Every Meta tool call needs client_conversation_id (a 20-char alphanumeric id, reuse it) and client_model. Use ads_get_ad_entities with date_preset "yesterday" (the ad account's own day). Pull at AD-SET level with filtering amount_spent GREATER_THAN 0, fields: name, campaign_id, optimization_goal, promoted_object, amount_spent, impressions, unique_link_click (verify names with ads_get_field_context if a call errors). Pull campaign level (objective) the same way if you need the objective. If the response carries next_actions, you may ignore the optimisation suggestions (they are not part of this job); never run anything that changes the account.

A campaign/ad set counts as a LEAD campaign if EITHER the campaign objective is OUTCOME_LEADS or LEAD_GENERATION, OR an ad set has optimization_goal LEAD_GENERATION / QUALITY_LEAD, OR promoted_object.custom_event_type is LEAD or SCHEDULE. Never match on names. Sum amount_spent -> B, impressions -> C, unique_link_click -> E across all qualifying entities with nonzero spend (de-duplicate by campaign; no double counting of ad sets and their campaign). Never compute or write CPM/CTR/CPC. If the account is blocked/unqueryable leave B, C, E blank and flag it. If the account is queryable and nothing qualifies, the real value is 0: write 0 and mention it in the notification.

Exceptions to the lead rule: UCA (purchase ad sets, below), PP and Class101 (Messenger ad sets, section 13), Pacow Mini-Course (custom conversion ad set, section 14).

UCA (Meta only): its ad sets are Sales/Purchase (promoted_object.custom_event_type PURCHASE), so count every ad set with nonzero spend whose custom_event_type is PURCHASE or LEAD / COMPLETE_REGISTRATION / SCHEDULE (skip REACH/traffic/engagement-only ad sets). Row date = "yesterday" in America/Los_Angeles. Only write {tab}!B{r}:C{r} and {tab}!E{r}. Overwrite rule: values already on the row that equal what you pulled (within rounding) are left as is; a different non-zero value that is clearly not an earlier run of this routine is not overwritten, mention it.

PACOW MAIN (account 3720107534883410): use only ad sets whose promoted_object.custom_event_type is LEAD or SCHEDULE (or optimization_goal LEAD_GENERATION/QUALITY_LEAD). Ad sets with custom_event_type COMPLETE_REGISTRATION are ignored (OCR is retired). The OMiniCourse ad set (promoted_object.custom_conversion_id 1373721174841333) belongs to the Mini-Course sheet (section 14), never to the main sheet. REACH, profile-visit, traffic and engagement ad sets are not reported. If an ad set spends and clearly fits none of these and is not an obvious REACH/traffic/engagement one, do not guess: leave it out and mention it in the notification. If the account is queryable and nothing qualifies, write B=0, C=0, E=0 and mention it. Pacow spends in EUR while the sheet header says USD: write the number as pulled (this is known, do not notify about it).

================================================== 4. STEP 3 — GHL contacts (H, I, J)
Tool: mcp__HighLevel__execute_operation, operationId "search-contacts-advanced" (POST /contacts/search), locationId = the client's location. Body example: {"body":{"pageLimit":100,"filters":[{"field":"customFields.utm_medium","operator":"eq","value":"paid_social"},{"field":"dateAdded","operator":"range","value":{"gte":"2026-10-08T07:00:00.000Z","lt":"2026-10-09T07:00:00.000Z"}}],"sort":[{"field":"dateAdded","direction":"asc"}]}} Paginate with the searchAfter value of the last contact if total exceeds the page. Results are big (each contact is several KB): parse locally with python3 -I, or delegate the pull to a subagent that returns only compact numbers; never dump raw contacts into the main context.

H = number of contacts returned by the base filter. I and J: NEVER use a tags filter parameter on search (unreliable, false zeros). Count locally from each contact's own tags array: I = tags contains exactly "meta | prequalified"; J = tags contains exactly "meta | qualified lead". Tutoring Club uses its own base filter (section 10). Suspicious zero (spend or prior-day activity but H=0): sanity-check the same base filter with the date range removed (pageLimit 1, sort dateAdded desc) and look at the newest contact's dateAdded. If it returns contacts, the zero is real. If it returns nothing even unbounded, leave H blank and flag it. Never sanity-check with a tags filter.

PACOW MAIN: base filter is paid_social + date range (Madrid day). Contacts whose utm_campaign custom field (id 5UyghXB1i6Y8IJHD1ABx) is "ocompleteregistration" or "minicourse" (case-insensitive) are ignored; every other contact counts. H, I, J are counted from the remaining contacts (I/J from their tags arrays). Mini-course contacts go to section 14.

================================================== 5. STEP 4 — Booked calls (P)
A booked call counts when BOTH: (a) an event on one of the client's calendars has a startTime whose own embedded local date equals the target date (get-calendar-events with a wide window of at least +/-48 h around the date, startTime/endTime as epoch milliseconds as strings, with locationId; never a single-timezone window); every appointment status counts, including cancelled/noshow, except "invalid"; and (b) the event's contact is fetched with get-contact (params {"contactId": ...}) and its customFields contain utm_medium = "paid_social" (never rely on a search filter for this). De-duplicate by event id and merge across the client's calendars.

Calendars: Gaja Collective 4l2eMiqhazLL94EUBQFV ("Free Career Call"; never the inactive "Copy of Free Career Call" Y9MIpAC0CEYtSutPomH4).

North Avenue Education (no calendar): pipeline tbujhUfuCBX4AMhV0mk8, stage c198a889-0ca3-4777-9e3e-8ef8768a8e1d ("Call Booked"). operationId search-opportunity (GET /opportunities/search) with pipelineId, pipelineStageId, status "all", limit 100; P = distinct opportunities whose lastStageChangeAt falls on the target date in America/Los_Angeles (local midnight to local midnight converted to UTC); paginate with startAfter/startAfterId; de-duplicate by id. Known limitation: an opportunity booked that day but already moved to a later stage is not seen, so P can undercount slightly (mention only if implausibly low).

PACOW, P (main sheet and Mini-Course sheet):

ONLY these two calendars are tracked: onANWvEUKrrzjBKeyIpf ("Free Growth Call with Viktorija") and Qsn57viBHccrK39K8CnN ("Free Growth Call").
The calendar 7NPxioFxJEtTGHdLoBzx ("Free Growth Call with Pacow Media") is NEVER tracked. Moreover, any contact who has EVER had an event on 7NPxioFxJEtTGHdLoBzx (check with get-appointments-for-contact, any date, any status) is excluded from both Pacow P counts.
Appointments with status "invalid" are not counted (cancelled/noshow still count).
The contact must have utm_medium = paid_social (custom field id gWXLWeq6a8JlF5VLn3DJ). Contacts whose utm_campaign is "ocompleteregistration" are ignored. Contacts whose utm_campaign is "minicourse" count on the Mini-Course sheet's P, never on the main sheet's P. Every other contact counts on the main sheet's P.
Use each event's own embedded local (Madrid) date.
Do NOT look at the Next Steps calendar (5kcuM5ysh6TuK4tC04oD), the Growth Accelerator pipeline, the Transactions ledger or the Drive file. None of that is used for Pacow any more.

================================================== 6. (REMOVED) Pacow extras, Pacow OCR, Core Medical
Pacow S, V, X, AA, AD and AE are not part of this routine, the Pacow OCompleteRegistration sheet is retired, and Core Medical Training Center is offboarded. Do not compute, read-modify or write any of it, and do not raise notifications about it.

================================================== 7. MUCHSMARTER (Free Game trial -> paid subscription) — own funnel and columns
Columns: B Adspend, C Impr, E Link Clicks, H Lead, I Free Trial Starts, J Paid Subs, K Unsubscribed. Never write anything else (D, F, G, L-S, U are formulas; T "New MRR" is typed by a human). The sheets script enforces it.

B, C, E: exactly Step 2 (qualifying lead campaigns, yesterday in America/New_York), yesterday only.
H, I, J, K (GHL, search-contacts-advanced, paginate with searchAfter): base filter customFields.utm_campaign eq "pacow_freetrial" + dateAdded range = that row's date in America/New_York. H = count. From the SAME contacts' tags arrays (never a tags filter): I = tag exactly "game funnel | free trial"; J = "game funnel | paid subscriber"; K = "game funnel | unsubscribed". Tags are cumulative (a paid sub also has the trial tag; an unsubscribed person also has the paid tag): do not make them exclusive. K = cancelled a paid subscription.
Rolling window: trials, paid and cancellations happen days after opt-in and the row is by opt-in date (cohort view), so every run re-pulls and overwrites H, I, J, K for yesterday and the 13 days before it (14 rows; B, C, E are yesterday only). One search over the 14-day range, then bucket contacts by their own local opt-in date. Rows may sit in the previous month's tab: use each row's own month. Same overwrite-safety rule as section 0.
Notify: the utm_campaign filter returns zero even date-unbounded, Meta account blocked, a row not found, or a neighbour row changed.

================================================== 8. NOTIFICATION POLICY
Success (every row matched, wrote cleanly, neighbours untouched, values non-negative) -> no notification, finish quietly. Otherwise ONE PushNotification covering all clients, text inside <routine_summary> tags, first sentence = the headline.

Notify for:

auth/script errors (including the script refusing a sheet id);
a row not found; a neighbouring row changed;
spend or leads zero across every lead campaign for a client (always mention, use judgment on plausibility; a client whose campaign is paused on purpose is fine, mention it in one short line);
a base filter (utm_medium, utm_campaign, or a documented tag exception) that no longer resolves even date-unbounded;
a Meta account blocked (once per run);
Pacow: a GHL calendar query failing, an ad set that fits none of the allowed types, or a partial run (state exactly which columns/clients were skipped and why);
Gaja: paid contacts with utm_medium "paid" (section 12);
MuchSmarter: see section 7;
IPS/CNA: see section 11;
PP/Class101: see section 13.

================================================== 9. OPERATING NOTES (learned from live runs)

HighLevel is reached through mcp__HighLevel__ tools: execute_operation with operationId (search-contacts-advanced, get-contact, get-calendar-events, get-appointments-for-contact, search-opportunity) and locationId. Meta through mcp__Meta-ads__ tools. If the MCP servers are still connecting, ToolSearch waits for them.
GHL range filter value shape: {"gte": "", "lt": ""}. Filter field names are camelCase. get-calendar-events sometimes times out after 60s: retry once with a smaller window.
search-opportunity params are camelCase (pipelineId, pipelineStageId, contactId, status, limit), not snake_case.
Compute every date window with Python zoneinfo, never by hand.
Large GHL results (contacts, events, opportunities) can be hundreds of KB: parse with python3 -I instead of reading them raw. Delegating big pulls to subagents that return only a compact summary is fine and keeps the main context small.
Do not create PRs, do not change the repo, do not edit scripts/sheets_io.py during a run.

================================================== 10. TUTORING CLUB OF ROUND ROCK (own layout: H Lead, I Qualified Lead, M 30 Min Calls Booked)
Write only {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}, {tab}!M{r}. Never I, J, P or any other column (the script enforces it). Yesterday in America/Chicago, run at the same time as everyone else.

B, C, E: exactly Step 2 (Meta ad account 1083923977552261, lead campaigns, yesterday).
H (Lead): the location has no utm_medium data, so the base filter is tags eq "meta | new lead" + dateAdded in the local day, paginate with searchAfter. Low or zero numbers are normal.
I (Qualified Lead): NOT written yet (no qualified tag exists). Skip it until the owner defines a tag, then count it locally from each contact's tags array.
M (30 Min Calls Booked): events on calendar "Free Academic Assessment" 5Nl6tXqKurgs7SK6wBEk whose own local date is the target date (any status counts), contact fetched with get-contact and tagged "meta | new lead". Staff test bookings (e.g. ema@pacowmedia.com) have no such tag and are not counted. The "Enrollment Meeting" calendar Wr9voN5hMpetAlcaaId9 is the 60-minute call; the sheet has no column for it, so it is NOT tracked.

================================================== 11. IPS AND CNA TRAINING (Meta only, like UCA)
No GHL for these two clients (owner decision): they are Meta-only. Only B, C, E are written. Sheets: IPS 1gEF5m_tq_UkkBfkJDcnIN3bJK8b4n8lTig0FcTSXNZU, CNA 11wgx68clelDJNlI3PlMNQNd-ZBGPiiml3wPBK5YbkNM. Both have 3-letter month tabs; row found by exact text in column A. Write only {tab}!B{r}:C{r} and {tab}!E{r}. Never H, I, J, P, M or anything else (the script enforces it). Meta: IPS ad account 54671718 (queryable); CNA ad account 10150383113508216 (Ads MCP NOT enabled yet; a second CNA account 303912897274562 exists but is not the reporting account, do not use it). Each run re-check with ads_get_ad_accounts. If the account is queryable, pull B, C, E with the standard lead rule (Step 2), "yesterday" in the ad account's own timezone. If it is blocked, write nothing (leave the cells untouched) and mention the block once in the notification; it starts working by itself as soon as the account is enabled. Overwrite rule as for UCA. Human-typed cells such as IPS J/P on the same row are not ours: never touch them. IPS campaigns can be paused for short breaks: write the real 0 and mention it in one line.

================================================== 12. GAJA COLLECTIVE (standard client)
Write only {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}:J{r}, {tab}!P{r}. Never S, V, X, AA, AD, AE or anything else. Yesterday in America/Los_Angeles.
B, C, E: exactly Step 2 (Meta ad account 1095582199186919, lead campaigns: ad set OLead, custom_event_type LEAD). The account holds many older paused campaigns (webinar, SFM, Chopra, yoga, Ayurveda, BFCM) that are not ours: if one of them spends, leave it out and mention it.
H, I, J: exactly Step 3 (utm_medium = paid_social + Los Angeles day). I = tag exactly "meta | prequalified", J = tag exactly "meta | qualified lead", counted locally from each contact's tags. Contacts with utm_medium "paid" come from an ad with broken URL parameters: they are NOT counted; if any show up for the day, mention the count once in the notification so the ad gets fixed.
P: exactly Step 4 on calendar "Free Career Call" 4l2eMiqhazLL94EUBQFV, contact must have utm_medium = paid_social. The Gaja team books test appointments (names with "Test", the owner, staff): they have no paid_social and are not counted. Appointments with status "invalid" are not counted.
The organic webinar ("Start Your Coaching Career in 21 Weeks", tag "webinar") is not paid social: never counted in H or P.
Overwrite rule as section 0. The sheet was filled by hand before the routine took over: hand-typed values that differ are skipped and mentioned.

================================================== 13. PERSONALIZED PREP AND CLASS101 (Messenger / DM ad funnel, own layout)
New sheets: PP 17fseVTM39w18nAD3PvdSBIAh_kfqHB-qPBF0Z8fntYo, Class101 1Ata7HhBeW5ci4FK8uMr4kToyQH7XcwCBUe7bXaZxhIU ("FB DM Ad Tracking Sheet - B2C"). Header row: A Date, B Adspend (USD), C Impr, D Cost Per Impression, E Link Clicks, F CTR, G CPC, H Messages, I Cost per Message, then 15/60-min calls, Keyword, clients and revenue columns. Write only {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}. Never I or anything to the right of it: the calls, keywords, clients and revenue are typed by the team from the DMs (the two sheets have different column positions after H, so never write by position past H).
Yesterday in the client's own timezone (PP America/Los_Angeles, Class101 America/Detroit).
B, C, E: ad sets with nonzero spend whose optimization_goal is CONVERSATIONS (Messenger / DM ads) or that pass the standard lead rule. Sum amount_spent -> B, impressions -> C, unique_link_click -> E.
H (Messages): the Meta action onsite_conversion.messaging_conversation_started_7d (verify the field name with ads_get_field_context), summed over the same ad sets. This comes from Meta, not GHL.
Class101's Meta account is blocked (section 1): write nothing for Class101 until it is enabled, mention it once.
If a campaign is paused (PP was paused on Nov 16), the queryable account returns nothing: write B=0, C=0, E=0, H=0 and mention it in one line.

================================================== 14. PACOW MINI-COURSE (sheet 1pnisEwkxJuXlf3FLtB5ibLFxPXaf8seGKcc1t_Tj5k4)
Same layout as the main Pacow sheet. Write only {tab}!B{r}:C{r}, {tab}!E{r}, {tab}!H{r}, {tab}!P{r}. Never I, J (the mini-course has no survey, so no prequalified/qualified tags) or anything else. Yesterday in Europe/Madrid.
B, C, E: the OMiniCourse ad set(s) in account 3720107534883410, identified by promoted_object.custom_conversion_id 1373721174841333 (never by name). Sum amount_spent -> B, impressions -> C, unique_link_click -> E. Spend is EUR (header says USD): write as pulled. If a new mini-course ad set optimizes on a different custom conversion, leave it out and mention it.
H: Step 3 base filter (paid_social + Madrid day), keeping ONLY contacts whose utm_campaign (custom field 5UyghXB1i6Y8IJHD1ABx) is "minicourse" (case-insensitive). Contacts tagged "mini-course lead" without that utm_campaign are not paid: not counted.
P: Step 4 Pacow rules (the same two calendars, the 7NPxioFxJEtTGHdLoBzx exclusion, no "invalid"), keeping ONLY contacts whose utm_campaign is "minicourse".
Overwrite rule as section 0 (rows from Nov 13 were typed by hand).

(End of routine.)
