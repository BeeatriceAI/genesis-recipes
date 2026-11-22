# Recipe 020: Omission blindness: a required-elements gate and lint for campaign copy

**Status: DRAFT v0.1, 2026-11-21. FIELD NOTE FROM ONE CAMPAIGN SHEET; ONE LINT RUN; THE LINT IS NOT PUBLISHED, SO THIS CANNOT BE REPRODUCED YET.** Times are ET.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (the number is transcribed in `raw/receipts.public.json` with its basis, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Receipt |
|---|---|---|
| One campaign sheet, linted for required elements | 58 post blocks checked; 21 blocks miss a required element: 7 LinkedIn drafts with no hashtags, 7 TikTok captions with no hashtags, 7 Instagram posts with no alt text | [E-01 · MEASURED] |
| Blocks by platform in that sheet | X 8, Bluesky 15, Threads 7, Facebook 7, Instagram 7, TikTok 7, LinkedIn 7 (sum 58) | [E-01 · MEASURED] |
| The miss that started it | one LinkedIn draft with zero hashtags passed four stages (author, reader, approver, poster) before a person caught it at the last step | [E-02 · REPORTED] |
| The same class elsewhere | a reader passed 21 of 26 merchandise images and failed none, while none was print-ready: 1,024 px is 3.4 in at 300 PPI (1024 / 300 = 3.41) | [E-05 · REPORTED] |

One limitation next to the headline: this is one sheet and one lint run. It shows that the lint finds a known class of omission; it does not show how often the fault happens, and the lint is not yet wired into live posting, so today it is a check, not a block [E-06 · REPORTED].

## 1. What this recipe is

A way to catch things that are missing. The chain that produced the miss had four stages and every one was a negative check: it looked for defects in the text that was there. The required elements (hashtags, alt text, an AI-disclosure line) were defined in one example (the Instagram block had hashtags; the LinkedIn block had none) and not in a rule a machine could check. The reader's checklist had no per-platform completeness line, and the poster was right to type the approved text exactly as approved [E-02 · REPORTED].

The fix has four parts:
1. A **required-elements table** per platform (the registry).
2. A **lint** that parses each post block of a campaign sheet and checks it against the registry.
3. A **reader line** per platform: "required elements present: Y/N". A missing element is FIX, never PASS.
4. A **stop-and-ask rule** for the posting agent: if the approved block lacks an element, stop and ask; never add text on your own and never post incomplete text.

## 2. Software pins

CPU only, no GPU. The lint is a Python script that reads a Markdown campaign sheet and writes a JSON report. Python 3.14. The script and its tests are not published [E-03 · REPORTED].

## 3. The registry (our house rules, not a standard)

SOURCED from our internal gate document, version 1, dated 2026-11-20:

| Platform | Hashtags | Also required |
|---|---|---|
| LinkedIn | 3-5 | hook 150 characters or fewer (advisory), AI line last |
| Instagram | 3-5 | alt text, AI label |
| X | 0-2 | AI line |
| Bluesky, Threads | 0-3 | AI line |
| Facebook | 0-3 | AI line |
| TikTok | 3-5 | AI-generated label |
| YouTube | 3 in the description | title 100 characters or fewer, AI line last |

The AI line is "AI-assisted, human-directed." and goes last, with the hashtags on the line above it.

## 4. The method

```
1. For every platform, write the required elements as data (counts, ranges, flags).
2. Parse each post block of the sheet; run each block against its platform's row.
3. Report per block: platform, line number in the sheet, missing elements.
4. Add one human line per platform to the reader's checklist: required elements present Y/N.
5. Before posting, the poster diffs the approved block against the registry; any gap stops the run.
6. When a person reports a miss: write the RCA, sweep the same fault across every sheet, update the registry.
```

## 5. Patches and workarounds

None. This is a process change plus a script, not a patch to a model or an engine.

## 6. Results and how they were measured

The lint ran on one campaign sheet (not published) and wrote a JSON report. The report is in `raw/lint-report.public.json`; one field (the local sheet path) is redacted and the rest is byte-for-byte what the tool wrote. Its own summary: 58 blocks; 21 block-severity findings; TikTok no hashtags x7, LinkedIn no hashtags x7, Instagram no alt text x7 [E-01 · MEASURED].

Check it yourself: count the entries in `findings` by `platform` and by `missing`; the three groups are 7 each. The `blocks_by_platform` object sums to 58.

Our command, from the retro that recorded it (paths shortened): `python -I -B req_lint_sheet.py --sheet <sheet.md> --report <report.json>` [E-03 · REPORTED]. The tool's tests: 10 passed, including 3 mutation kills (a mutation kill = a deliberately broken copy of the lint that the tests must reject) [E-03 · REPORTED].

## 7. Thermal behaviour

Not applicable (CPU script).

## 8. What did not work

- **The first lint run on the real sheet found nothing it could use.** The lint had passed its own tests (35 of 35 at that point) but could not parse the real sheet: the report showed 90 "UNSPECIFIED" results. A second round fixed the parser and then reproduced the 21 findings. The lesson: tests on invented input prove the code runs, not that it reads your real files [E-04 · REPORTED].
- **Negative-only checks.** Every stage looked for what was wrong. None asked what was required.
- **The lint is not wired into live posting.** The gate says the poster should run the diff before typing; no automatic hook blocks a post when the lint fails [E-06 · REPORTED].
- **The same fault was not only in copy.** The sweep that followed found missing alt text across image rows, a merch gate with no wordmark or print-resolution rule, and a reader whose verdict noted that none was print-ready while the written merch gate had no print-size rule [E-05 · REPORTED].

## 9. Not measured

How often the omission happens (no baseline of misses per 100 blocks before the lint); whether the gate lowers it over the coming weeks; the lint's false-positive rate on other sheets; sheets in other formats; whether hashtag counts help reach (we are not claiming they do).

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Write your required elements for each channel as data, not prose.
2. Write a parser for your own sheet format and run it on your real sheet first, not only on a synthetic one. If it cannot parse a block, that block is a finding.
3. Break the lint on purpose (remove a hashtag, drop an alt text) and confirm the tests fail; that is the mutation check.
4. Add the Y/N completeness line to the reader's checklist.
5. Make the posting step stop on any gap.

**How to measure whether it works (to do):** record, per week, blocks written, blocks with a missing element at the author stage, at the reader stage and at the posting stage. A working gate moves misses earlier, toward the author. Publish the three counts.

## 11. Licence and credits

Recipe text CC BY 4.0. No third-party model is used.

## 12. Changelog

- 2026-1121 v1: first write-up from the retro of 2026-11-21, the omission sweep of 2026-11-20 and the lint report.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on [APPROVAL DATE: fill when Danny approves].
