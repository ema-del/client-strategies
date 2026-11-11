# Airtable ad board cleanup: brief for each client

Goal (Wednesday Airtable sync, step 7 of the Wednesday SOP): make each client's cards in Airtable base apprmTJjM1hGBQJAG, table tblKMxDFIz7lT7djE ("Paid Ads 🚀") match reality. Every ad that ran from the client's launch (or 2026-05-01, whichever is later) gets one card. Every card gets: Concept Name, Status, Type of Ad, Level of Awareness, Angle, Pain Point / Benefit, Offer, Hook 1, Client.

Meta, GHL and Drive are read only. Airtable is written only after Ema approves the change list. When the work is split across helper agents, they write a proposal file and the main session reviews and applies it.

## Field IDs and allowed values
- Concept Name fldvf9ThDq0F21iTJ (text). Style: "<Client short> - <format> <short description of the hook>", e.g. "NAE - static founder image SAT score jump".
- Client fldcKxGk8BIs4Z2nm (text). Use the existing code on that client's cards (e.g. NAE, TC, IPS, MS, PP, C101, CNA, CPP, UCA, Gaja). Check what's already used before inventing one.
- Status fldjfaj0CKRggS3Ec: "Testing" (live now), "Winners (Live/Not)", "Not Winners/Killed", "In Bank" (in Drive creatives/ad bank, never launched). Leave cards in Big Idea/To Do, Doing It, Writing, Ready to Film, Editing alone unless the ad actually launched (then Testing/Winner/Killed).
- Type of Ad fldLaZ16OXNDLONCi: Static, Video, B-Roll, Carousel, UGC
- Level of Awareness fldJWysTKf0UMvt4r: "Unaware (I don't know I have a problem)", "Problem Aware (I know I have a problem)", "Solution Aware (I know coaching/method exists)", "Aware of My Offer (I know you exist)"
- Pain Point / Benefit fldHkc4QltP6UwJaj: "pain 1".."pain 5" (from the client's launch pain list in Drive; most ad names carry P1..P5 / p1..p5)
- Angle flderwtUW9tQ8yyjH: Mistakes, New Method, Proof, Personal Story, Benefit, Contrarian, Guarantee (never "Gaurantee")
- Offer fldJtNWn8gmASyONc: Follower Ad, Direct Offer, Webinar, Low-Ticket, Freebie
- Hook 1 fldl3Uo7UOeWd3CKh: the hook as written ON the image (look at the image) or the first line of the video captions/script. If you can't see it, write "check hook (<format>, Meta ad: <ad name>)". Never guess.

## Status rules
- Live now in Meta (effective status ACTIVE) and not a winner: Testing.
- Winner: 1+ sale with cost per sale under $2,000, OR cost per main booked call at/under the sheet's MAX (B2C call funnels: cost per 30-min booked max $300; DM/Messenger funnels PP and Class101: cost per booked call max $250). Bookings and sales per ad come from GHL contacts (utm_content on the contact = Meta ad name, tags: "connection call | booked" / "call booked" = booked, "purchased" / "closed won" / "new client" = sale; check the client's own tag names). Spend = Meta lifetime spend for that ad name (sum duplicates).
- Off/paused/never delivering after spend, not a winner: Not Winners/Killed.
- In Drive ad bank / creatives folder but never launched in Meta: In Bank.
- Pre-launch / pre-May ads: leave existing cards alone, don't create new ones.
- Clients that left (cards already deleted): ignore.

## Sources
- Meta Ads MCP (load with ToolSearch "select:mcp__Meta_ads__ads_get_ad_entities,mcp__Meta_ads__ads_get_creatives,mcp__Meta_ads__ads_get_field_context"). Every ad with spend > 0 since launch, any status: ad name, ad set, campaign, effective status, created, lifetime spend, creative title/body, image URL (curl it into scratchpad/at/<key>_img/<ad_id>.jpg and LOOK at it with the Read tool to get the hook).
- GHL (HighLevel MCP, search contacts, location = the client's) for leads/bookings/sales per utm_content since launch. Read only.
- Drive (Google Drive MCP): the client's folder in "01. Clients" (pain point list P1-P5 from launch strategy / ad map docs; creatives folder; ad bank folder). read_file_content works on PNG (OCR) and on videos with transcripts; if OCR is empty, download_file_content and decode the base64 to a file, then Read it.
- Existing cards: mcp__Airtable__list_records_for_table with a filter on Client (fldcKxGk8BIs4Z2nm) = the client code. Match cards to Meta ads by name/hook. Fix anything wrong on existing cards (wrong status, wrong pain, blank fields, hook that doesn't match the image).
- Reporting sheets and GHL location IDs: see /home/user/client-strategies/CLAUDE.md roster.

## Output (one file per client): /tmp/claude-0/-home-user-client-strategies/4b4f8475-d6b7-5989-b96d-c68f860a4731/scratchpad/at/proposal_<key>.json
{
 "client": "<code>",
 "updates": [{"id": "rec...", "fields": {"<fieldId>": "<value>"}, "why": "short reason with numbers"}],
 "creates": [{"fields": {...all 9 fields...}, "why": "Meta ad name, spend, status"}],
 "deletes": [{"id": "rec...", "why": "duplicate of rec... / not a real ad"}],
 "perf": [{"ad": "<meta ad name>", "spend": 0, "status": "", "leads": 0, "booked": 0, "sales": 0, "cpb": 0, "card": "rec... or new"}],
 "notes": ["anything you couldn't verify"]
}
Field values in "fields" use field IDs as keys and plain option names as values.

## Decisions from the first cleanup (Ema, 2026-11-11)
- Timeline: ads since 2026-05-01 (or the client's launch if later). Older cards stay as they are.
- Winner rule: a sale is the best signal (cost per sale under $2,000, the sheet's max cost per new client). Otherwise judge on cost per booked call at/under the sheet's max: Pacow 60-min booked €500, B2C 30-min booked $300, DM funnels (PP, Class101) $250. One booking on a live ad = keep Testing.
- Pacow pain points: ed biz = pain 1 (grinding on content, relying on referrals); Course Creators PP1-PP5 and Mini-Course p1-p5 use their own launch lists (Drive "04. Media Buying / Ads").
- Offboarded clients' cards were deleted (Smarta, CMS, Zinkerz, EdvancedLearning, Button School, College Zoom, CCUS). USM, AIS and LWT cards are kept.
- Ad bank = creatives in the client's Drive ad bank folder that never launched. Ema makes placeholder cards (e.g. "P1 card") in the ad bank session.
- No extra columns on the table. "Field 17" stays unused.
