# Menu 003: This week on a local AI box (the week of 2026-11-23)

**Status: DRAFT v0.1, built in public.** A *menu* is a combination of parts plus routing and workflow that does a job, published with the same receipts. This one is a week of seven small jobs you can run on any local AI machine: measure, queue, time, check, test. The first dish has a Week 4 answer we do not have yet, and says so. Labels: **MEASURED** = computed from a raw file in this repo (the three scripts in this folder recompute each one); **SOURCED** = read from a named record; **REPORTED** = transcribed receipt, log not published (not quoted in posts); **NOT RUN** / **NEEDS-DATA** = we do not have it. **Our numbers are one lab's numbers from one machine. They are examples of what to record, not targets.**

*Beeatrice is an AI-generated persona. This menu is made with AI tools; approved for publication by the studio owner on [APPROVAL DATE: fill when Danny approves].*

## The job

Run a local AI machine so that you can say, with files, what it did this week. Each day has one small job, one thing to write down, and one honest limit.

## The raw files and scripts

- `raw/three-weeks-20261114/gpu_daily_usage_UTC.csv` (daily GPU summaries, 18 UTC dates, Oct 29 to Nov 15; the last day is partial).
- `raw/image-job-timings-20261106.csv` (268 image jobs).
- `raw/compaction-records-20261107.csv` (54 compaction records).
- In this folder: `idle_hours.py`, `cold_vs_warm.py`, `compaction_summary.py` (MIT; standard library only; each prints the numbers quoted below when pointed at the file above).

## The week

| Day | Dish | What to run | What to write down | Our number, if we have one |
|---|---|---|---|---|
| Mon | **Count your idle hours** | Log utilisation about once a minute per GPU. Count a minute as busy at 50 percent or more (a blunt line; pick your own and say what it is). Run `idle_hours.py` on your daily file. | minutes under your line per GPU per day | GPU 1, 2026-11-07 to 2026-11-14: 4,655 minutes under 50 percent, 9.70 hours a day on average (lowest day 5.88 h, highest 15.08 h) [MEASURED from the daily file]. The Week 4 file is not public yet [NEEDS-DATA] |
| Tue | **Put a standing queue behind the second GPU** | A queue of ready jobs with three rules: urgent work goes first; one job at a time on the GPU; a heat gate that cancels the job when a temperature line is crossed. Receipt every job; never overwrite an output. | jobs started, finished, cancelled, failed, per day | Our first receipts look like a retry loop that has since stopped; the cause is not traced and no counts are quoted [NEEDS-DATA]. Our heat line is one lab's guardrail, not advice |
| Wed | **Cold versus warm** | Time one job per model right after a model load and again with the model resident. Run `cold_vs_warm.py` on your job log. | load seconds, generation seconds, whether the worker was resident | A 4-step image model: median generation 1.5 s over 46 jobs, median cold load 11.7 s over its 8 cold jobs. A 50-step model: median generation 64.7 s and cold load 25.0 s over 87 jobs [MEASURED from the job-timing file] |
| Thu | **Read the input before the batch** | Open every conditioning image at full size. Run one canary clip per model and have someone who did not build the batch look at it. | the hash of each input; one line per canary: what you saw | See [recipe 022](../../recipes/022-read-the-input-gate-the-output-image-to-video/RECIPE.md) (REPORTED, one clip per case) |
| Fri | **Check what is missing** | Write the required elements of each outgoing post (hashtags, alt text, disclosure line) as data. Lint one real sheet. Add a "required elements present: Y/N" line to your reviewer's list. | blocks written; blocks missing an element, by stage | 58 blocks, 21 missing an element in one sheet [MEASURED from the lint report]; see [recipe 020](../../recipes/020-required-elements-gate-and-lint-omission-blindness/RECIPE.md) |
| Sat | **Test one "allowed" action end to end** | Pick one allow-list or permission. Perform the allowed action once on a known item and compare the result. Do not stop at "it loads". | allowed entries tested; entries found to be no-ops | See [recipe 021](../../recipes/021-a-control-that-does-nothing-empty-allow-list-inheritance-only-acl/RECIPE.md) (REPORTED) |
| Sun | **Count your agent's compactions** | When a long agent session fills its context, record each compaction: time, seconds, status. Run `compaction_summary.py`. | records, failures, median completed seconds, share from your largest session | 54 records, 46 completed, 8 failed; median completed 183.0 s; 47 of 54 came from one session [MEASURED from the compaction file]; see [menu 002](../002-compaction-brief/MENU.md) |

## How to read this honestly

- Monday's number is a mean over eight days on one GPU, and "under 50 percent" is not "idle": some of it is models loading or light work.
- The Wednesday numbers come from one lab's job log, which mixes earlier campaigns with test waves.
- Sunday's 54 records are mostly one session; do not read the failure share as a rate.
- Nothing in this menu says a queue, a gate or a check improves anything. Each day tells you what to write down so that you can find out.

## Not measured

Whether any of the seven dishes changes an outcome for you; wall-socket power; output quality; anything for a single-GPU machine.

## How to rerun

Clone the repository with `git config core.autocrlf false` (the CSV files use CRLF line endings and hash checks fail if git rewrites them). Then, from this folder:

```
python idle_hours.py ../../raw/three-weeks-20261114/gpu_daily_usage_UTC.csv 1 2026-11-07 2026-11-14
python cold_vs_warm.py ../../raw/image-job-timings-20261106.csv
python compaction_summary.py ../../raw/compaction-records-20261107.csv
```

Expected output lines (these are what we got): `minutes under 50 percent: 4655`; `mean hours per day under 50 percent: 9.70`; `qwen-image-2512: 87 jobs, median generation 64.7 s, 87 cold, median cold load 25.0 s`; `54 records: {'completed': 46, 'failed': 8}`; `median completed seconds: 183.0`; `largest single session: 47 of 54 records`.

## Files

`idle_hours.py`, `cold_vs_warm.py`, `compaction_summary.py` (sha256 in `SHA256SUMS.txt`).

## Licence
Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see [`LICENSE-DOCS.md`](../../LICENSE-DOCS.md).

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on [APPROVAL DATE: fill when Danny approves].
