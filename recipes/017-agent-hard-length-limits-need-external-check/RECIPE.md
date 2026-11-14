# Recipe 017: Hard length limits need an external check: claimed and counted post lengths differed

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1108 v1; FIELD NOTE FROM 15 RUNS; ONE SESSION, NO BASELINE.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| 270-character post, 3 runs | each reply claimed 268, 264 and 270 characters; our counts, which include the label line, were 304, 289 and 307 | n/a | [L-01 · REPORTED] |
| 120-word summary, 3 runs | 2 of 3 correct; one run wrote 138 words | n/a | [L-02 · REPORTED] |
| Classification, copy-and-hash, rule extraction, 9 runs | 9 of 9 correct | n/a | [L-03 · REPORTED] |
| All 15 runs | 11 of 15 correct by manual grading; median 45.5 s to final reply (19.7-170.8 s); 0 tool errors | n/a | [L-03 · REPORTED] [L-04 · REPORTED] |

Counting caveat: our counts include the post's label line, and the gap between the claimed and the counted length (25 to 37 characters) may be that label line. We did not recount the post body alone, so we do not say the model was wrong, only that its claimed count and our count differ.

One limitation next to the headline: this is one agent session on one day, 3 runs per task, graded manually (the export does not record who graded), with no baseline run of another model, so it shows a failure mode and does not rank anything [L-05 · REPORTED] [L-06 · NOT RUN].

## 1. What this recipe is

A short test of five mundane agent tasks, run three times each against the lab's 27B local model through an agent client: classify 24 rows; summarise a text in at most 120 words with three sourced numbers; copy and hash three files; draft a post of at most 270 characters; list the never and must-not rules in a file and check a queue file against them. Timing was taken from the session record. Correctness was graded manually after reading every reply; the export does not record who graded, so the grader is UNKNOWN.

The finding is narrow and useful: the model's own count of its output length is not evidence. Each of the three replies claimed a length within 270 characters; our counts, which include the label line, were higher (304, 289 and 307) [L-01 · REPORTED].

## 2. Hardware and software pins

- The model is the lab's serving profile: Qwen3.8-27B-FP8 with MTP-2 and fp8 KV at 262,144 context (see recipe 007), shared with other consumers. Whether other load was on the engine during the 30-minute window is UNKNOWN [L-05 · REPORTED].
- Workstation: Digital Storm Aventum Pro, power limit stock 300 W, clocks stock. The client ran on a separate machine.

## 3. Model

`Qwen/Qwen3.8-27B-FP8` (Apache-2.0 on its model card, read 2026-11-06), thinking mode off as in recipe 007.

## 4. The five tasks

```
T1  classify 24 rows into labels
T2  summarise a text in at most 120 words, include 3 numbers taken from the text
T3  copy three files and report their hashes
T4  draft a post of at most 270 characters
T5  list the never and must-not rules in a file, then check a queue file for violations
runs per task: 3, randomised order, session idle between runs
```

## 5. Patches and workarounds

None. The lesson is a harness rule, not a model patch: check a hard length limit with a counter (`len()` or `wc`) outside the model, and retry or truncate from that count.

## 6. Results and how they were measured

Seconds to final reply are measured from the prompt's arrival in the session to the end of its last tool or step. Correctness is a manual grade of the reply. The automatic correctness column in the raw export was produced by a heuristic that measured the whole reply and disagrees with the manual grades for T2 and T4: it is not used here [L-05 · REPORTED].

| Task | Seconds per run | Median s | Correct (manual) | Receipt |
|---|---|---|---|---|
| T1 | 74.0, 170.8, 19.7 | 74.0 | 3 of 3 | [L-03 · REPORTED] [L-04 · REPORTED] |
| T2 | 56.0, 43.4, 57.2 | 56.0 | 2 of 3 (138 words in one) | [L-02 · REPORTED] |
| T3 | 46.2, 58.2, 47.1 | 47.1 | 3 of 3 | [L-03 · REPORTED] |
| T4 | 43.0, 24.1, 31.7 | 31.7 | 0 of 3 by our count (label line included) | [L-01 · REPORTED] |
| T5 | 43.9, 45.5, 41.1 | 43.9 | 3 of 3 | [L-03 · REPORTED] |

T4 in detail: run 1 produced 304 characters and said 268; run 2 produced 289 and said 264; run 3 produced 307 and said 270 [L-01 · REPORTED]. Tool time was 0 s in all 15 runs, so the time is model generation. T1 varied from 19.7 to 170.8 s: do not read a single run [L-04 · REPORTED].

## 7. Thermal behaviour

Not measured.

## 8. What did not work

- The model's self-report of length. Three of three counts disagreed with the claimed length on the post (label line included in ours), and one of three summaries ran over its word limit [L-01 · REPORTED] [L-02 · REPORTED].
- The automatic grader in the export, which is why the replies were graded manually [L-05 · REPORTED].

## 9. Not measured

Tokens per second; a before and after of any change; another model on the same tasks; whether an external count-and-retry loop fixes T4 (it should, and it was not run); behaviour on other limits such as line counts; the engine's other load during the window [L-06 · NOT RUN].

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Write the five tasks as fixed prompts with fixed inputs.
2. Run each three times in random order with the session idle between runs; take the time from the session record.
3. Grade by reading every reply. Count characters and words with a tool, not by estimating.
4. Publish the claimed and the actual count side by side.

Draft reproduction steps: the task prompts and inputs are not published.

## 11. Licence and credits

Recipe text CC BY 4.0. Model: Qwen3.8-27B-FP8, Apache-2.0 (model card, 2026-11-06). See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1108 v1: initial write-up from the 15-run export of 2026-11-07 and its manual grades.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
