# Recipe 021: A control that exists but does nothing: an empty allow-list and an inheritance-only permission

**Status: DRAFT v0.1, 2026-11-21. TWO FIELD NOTES FROM ONE WEEK; NO BASELINE; THE CODE AND POLICY FILES ARE NOT PUBLISHED, SO NEITHER CASE CAN BE REPRODUCED YET.** Times are ET.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (the number is transcribed in `raw/receipts.public.json` with its basis, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Receipt |
|---|---|---|
| A browser governor's policy listed "extract" as allowed but listed no readable fields | red squad 15's review returned GO with no blockers (6 medium findings; squads 12 to 14 had said NO-GO on earlier versions); the first live trial refused every field name | [G-01 · REPORTED] |
| A permission repair on a private local vault | every file ended with no entry that applied to it, so no account, including the owner, could read any file; the first check only confirmed that forbidden groups were absent | [G-02 · REPORTED] |
| The corrected check | requires an effective owner entry and a successful read; 5 tests passed | [G-03 · REPORTED] |

One limitation next to the headline: two cases from one week, found and written up by the same lab that caused them. They show a failure shape, not how common it is [G-06 · NOT RUN].

## 1. What this recipe is

A pair of cases with one shape: **a control that is present and does nothing, passed by checks that confirm presence or the absence of bad things, never an effect.**

- **Case A, the empty allow-list.** A policy entry for one website listed the actions `read` and `extract`, but had no list saying which fields could be read. The code needs that list to know what `extract` may return; with none, every field is refused. The loader accepted the policy, the server started, the journal wrote, the run cap claimed a slot, and the model could not read a single field [G-01 · REPORTED].
- **Case B, the inheritance-only permission.** A repair command meant to make a private vault owner-only was applied to a whole tree. On directories the flags it used grant access to the directory and pass it to children; on files they left the file with no entry that applied to it once the file's own inheritance was off. Every file was unreadable by anyone [G-02 · REPORTED]. INFERENCE: the mechanism (inheritance already off on the files, then a directory-style grant on the file) was reproduced on a throwaway folder by the independent reader on 2026-11-21; an entry marked (I) that is inherited does grant access, so an (I) mark is not the fault by itself. The verifier that followed checked that the forbidden groups (all users, authenticated users, everyone) were absent. It never opened a file. "Owner-only" had been asserted by checking what was missing [G-02 · REPORTED].

## 2. Software pins

No model, no GPU. Case A: a local browser-control server with a JSON policy file (not published). Case B: Windows file permissions (`icacls`), a Python verifier (not published), Python 3.14 [G-04 · REPORTED].

## 3. What the checks looked at, and what they should have looked at

| Case | What passed | What was never tested |
|---|---|---|
| A: allow-list | policy loads; server starts; apply and rollback drills pass | reading one known field end to end |
| B: permissions | forbidden principals absent from the permission listing | the owner's effective access; one real file read |

## 4. The method (the fix, as we wrote it down)

```
Allow-lists:
  1. For every entry whose actions include X, require at least one concrete item in the list that X needs.
  2. Add a drill that performs X on a known item and compares the returned value to a known value.
  3. Run the drill through the real client, not only through the loader.

Permissions:
  1. List permissions on a sample of files (`icacls <file>`): an empty list, or only entries that do not apply to this object, means no effective access. Entries marked (I) are inherited and DO grant access. The test is the read in step 2.
  2. Open one sample file for read as the intended owner; a failed read is a failed check.
  3. Also check that forbidden principals are absent (the old check); keep it, add the effect test.
  4. Grant files and directories separately; do not reuse a directory flag set on files.
```

For case A, the fix below is a proposal, not applied: the retro that found the cause lists these as proposals (it says "propose the text, do not edit"); when this note was written the fix had not been applied [G-01 · REPORTED]. For case B, the corrected verifier and its tests were applied [G-03 · REPORTED].

## 5. Patches and workarounds

Case B: files and directories are now granted separately, and the verifier checks an effective owner entry plus a real read. Case A: none yet. We also built a claim audit that sweeps a day's notes for words such as "owner-only", "private" and "verified" and flags any with no command or test output beside it. Its first 24-hour sweep returned 40 findings (flags, not confirmed faults); its mutation testing killed 13 mutations (12 required) and 29 tests pass [G-05 · REPORTED].

## 6. Results and how they were measured

Both cases were found by running the real thing: case A by the first live trial of the governor (open, close, journal and run cap worked; the field read refused; a partial pass), case B because the next processing stage was blocked, and the root cause of the block was traced to the repair. Neither number in this note comes from a data file; both are transcribed in `raw/receipts.public.json` [G-01 · REPORTED] [G-02 · REPORTED].

Red squad 15's verdict was GO with no blockers and 6 medium findings; they covered journal writes, path aliases and a scheduled-task rewrite, and none concerned the missing field list [G-01 · REPORTED].

## 7. Thermal behaviour

Not applicable.

## 8. What did not work

- **Reviews and drills that exercised apply, rollback, pinning and kill paths.** None read a field end to end, which is the one thing the policy was written to allow.
- **Verifying a security claim by what is absent.** The claim "owner-only" was a label; the test that makes it true is a listing plus a successful read.
- **Our own repair.** The lead agent's repair command caused case B. The mistake is ours.

## 9. Not measured

How many other policy entries or folders have the same shape; whether any other review would have caught case A before the trial; Linux or macOS equivalents of case B; whether the proposed drills are enough. We also did not measure any cost of the fix [G-06 · NOT RUN].

## 10. Reproduction steps (draft: not reproducible until the code is published)

**Case A, to try on your own policy:**
1. List every entry that grants an action.
2. For each, find the data the action needs (fields, paths, tools). If it is empty or absent, you have a no-op.
3. Perform the action once on a known item and compare the result.

**Case B, to try on your own folders (placeholders for your own paths):**
1. `icacls <folder-or-file>`: an empty list, or only entries that do not apply to this object, means no effective access. Entries marked `(I)` are inherited and DO grant access. The test is the read in step 2.
2. Read the first line of a sample file as the owner, for example with `Get-Content <file> -TotalCount 1`.
3. Treat "no forbidden accounts listed" as half a test.

**How to measure whether it works (to do):** per release of a policy or a permission change, record how many "allowed" entries have an effect test, and how many were found empty by that test.

## 11. Licence and credits

Recipe text CC BY 4.0. No third-party model is used.

## 12. Changelog

- 2026-1121 v1: first write-up from the retros of 2026-11-20 and 2026-11-21 and the squad board.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on [APPROVAL DATE: fill when Danny approves].
