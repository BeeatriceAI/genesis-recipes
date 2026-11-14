# Menu 002: Keeping an agent alive through "compaction" (the deterministic brief)

**Status: DRAFT v0.2, built in public.** A *menu* is a combination of parts plus routing and workflow that does a job, published with the same receipts. This one is about a failure we hit and the fixes we tried. Labels: **MEASURED** = computed from a raw file in this repo ([`raw/compaction-records-20261107.csv`](raw/compaction-records-20261107.csv)); **SOURCED** = read from a named record; **REPORTED** = said by a driver or operator, not in a raw file here; **UNKNOWN** / **NEEDS-DATA** = we do not have it. **The numbers below show what happened and how long it took. They do not show that the new brief is as good as the old summaries: that has not been reviewed.**

*Beeatrice is an AI-generated persona. This menu is made with AI tools; approved for publication by the studio owner on 2026-11-13.*

## The job
A long-running AI agent session fills its context window. "Compaction" replaces the old conversation with a short summary so the session can continue. We need that step to finish, to be fast, and to carry only true facts forward.

## The raw file
`raw/compaction-records-20261107.csv`: 54 rows from 2026-10-29 to 2026-11-07, one per compaction recorded in our agent's session database: timestamp (ET), masked session id, message sequence number, mode (native or deterministic), seconds, summary length in characters, and status (46 completed, 8 failed). It holds no conversation content and no prompts. It is our driver's export; the database itself is private. sha256 in `raw/SHA256SUMS.txt`.

## The failure (Nov 4)
**SOURCED** (our status log): a compaction summary hit the 8,192-token output cap, then the context reached 262,145 tokens against a limit of 262,144, and the agent stalled. The raw file shows what compaction cost in our main session (one long session, masked id S-31533aec):
- Compactions per day Nov 1 to 5 in that session: **1, 2, 2, 7, 8** (**MEASURED**; Nov 4 includes two failed rows at 14:47 and 14:56 ET, 539.0 s and 291.3 s, 0 characters, followed by a completed one at 15:03, 434.4 s, 25,963 characters; we have not matched these rows to the stall itself). Counting every session, the per-day counts are 1, 2, 2, 8 and 10.
- Completed native compactions in that session on Nov 1 to 5: 18, median **370 s**, range 287.4 s to 1,679.1 s, median summary length about 17,984 characters (**MEASURED**). The longest is Nov 5, 19:24 ET: **1,679.1 s (28.0 minutes)**.
- Earlier, on Oct 29 to 31, completed native compactions ran from 6.9 s to 359.9 s with summaries of about 1,200 to 15,600 characters (**MEASURED**; they got slower and longer as the session grew).

## The parts and the three fixes
| Step | What it is | Label |
|---|---|---|
| Fix 1 (Nov 4) | Raise the output limit from 8,192 to 24,576 and the buffer from 10,240 to 40,960 | SOURCED (a pinned patch folder; our status log) |
| Fix 2 (Nov 4) | A V2 compaction hook that keeps summaries to about 5.4k characters | SOURCED (a pinned patch) |
| Fix 3 (Nov 6, 15:37) | A deterministic hook ("mode A"): the brief is built from files by a script, **without calling the model**; if the hook fails the native compaction runs as a fallback | SOURCED (a pinned patch) |
| Why fix 3 | Before fix 3, a native compaction on Nov 6 (14:58 ET) took **945.2 s** and wrote **14,501 characters** (**MEASURED**). Our driver's reading is that the model obeyed the built-in "you MUST use this format" instruction over our added note, so we changed the mechanism instead of the wording. That is the driver's explanation, not something we proved | REPORTED (driver analysis; hypothesis) |
Config changes to the agent are made through hash-pinned patch folders with old and new hashes and a re-pin step; hand edits break the pin chain. **SOURCED.**

## Deterministic runs so far (MEASURED, all from the raw file)
Six runs, all in the same session, 02:41 to 11:47 ET on Nov 7 (about nine hours):
| Time (ET) | Mode | Seconds | Brief length (characters) |
|---|---|---|---|
| 02:41:11 | deterministic | 0.0 | 4,729 |
| 04:35:20 | deterministic | 0.0 | 4,730 |
| 06:12:45 | deterministic | 0.0 | 4,730 |
| 09:00:49 | deterministic | 0.0 | 4,725 |
| 10:20:17 | deterministic | 0.0 | 4,295 |
| 11:47:46 | deterministic | 0.0 | 4,071 |
The last two briefs are shorter because our driver trimmed the live brief file (**REPORTED**). No hook errors were reported, and the first run was followed by 8 steps of 5 to 41 s of model time (**REPORTED**, driver morning report). All 6 rows show status completed.

## How to read this honestly
- **"0 s" is by design:** the hook makes no model call. It is not a speed-up of the model and it is not a quality result.
- **We have not reviewed whether the 4,000 to 4,700 character brief is as good as a model-written summary** (native runs on Nov 4 to 6 wrote about 12,400 to 25,963 characters). A shorter brief may drop things that matter. **NEEDS-DATA:** a review of what the brief contains against what a native summary kept.
- **Six runs in one session over about nine hours** is not a reliability measure.
- The records are our driver's export from a private database; one source.
- A wrong character description once survived inside a compaction summary and kept coming back until it was corrected (REPORTED, driver note). Summaries copy mistakes forward, so briefs built from checked files are safer than briefs built from the conversation.
- Native compaction time grew with the session in this data; we do not claim that it always does.

## Not measured
Brief quality; behaviour on sessions other than this one; how often the native fallback runs; memory use; whether the brief ever dropped an instruction the agent needed.

## How to rerun
We cannot offer a public command: the patches are internal to our configuration and the pinned chain. What we can publish is the raw file above; the table is computed by grouping its rows by date and mode. What could be published once the operator agrees: the hook's input file list. **NEEDS-DATA.**

## Files
`raw/compaction-records-20261107.csv` (sha256 in `raw/SHA256SUMS.txt`).

## Licence
Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see [`LICENSE-DOCS.md`](../../LICENSE-DOCS.md).

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
