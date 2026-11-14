# Recipe 003: FLUX.2 klein 4B on the Genesis image card

**Status: DRAFT v0.1, built in public.** A *recipe* is one model's exact setup plus measured numbers. The numbers come from our own job log, not from a controlled test: every succeeded job for this model in our image cache (earlier campaigns included), one observer, one machine. Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = said by an operator or a tool, not verified by us; **UNKNOWN** / **NEEDS-DATA** = we do not have it.

*Beeatrice is an AI-generated persona. This recipe and its numbers are made with AI tools; approved for publication by the studio owner on 2026-11-13. Cloud tools we use elsewhere are named in [Menu 001](../../menus/001-local-creative-studio/MENU.md).*

## The job
Fast draft images at 1024x1024 or 1024x1536 from a text prompt (a 4-step distilled model; a reference image is optional). We judged only 2 images for quality, so we make no quality claim: see our checks below.

## Setup (what we know)
| Item | Value | Label |
|---|---|---|
| Model | black-forest-labs/FLUX.2-klein-4B, revision `e7b7dc27` | SOURCED (the gateway's model list read 2026-10-31) |
| Licence | apache-2.0 per the gateway list; the repository's LICENSE file text not read by us | SOURCED (list) / UNKNOWN (file text) |
| Steps | 4 | MEASURED (`steps` column) |
| Precision | bfloat16 | MEASURED (`dtype` column) |
| Reference image | optional | SOURCED / MEASURED (`reference_supplied` is false for every job in the log) |
| Allowed sizes | 1024x1024, 1024x1536, 1536x1024 | SOURCED |
| Hardware | two NVIDIA RTX PRO 6000 Blackwell Max-Q 96 GB GPUs and an AMD Threadripper PRO 9975WX, from the vendor spec sheet; not measured by us; the operator reports one GPU runs the image models | SOURCED (vendor spec sheet) / REPORTED |
| Submit rule | one image submit in flight at a time, with an idempotency key; a missing response is reconciled by job id, never blindly retried | SOURCED (a rule) |
| Sampler, guidance scale, seed handling, VRAM use, driver/CUDA/serving versions, quantization other than the dtype above | | **NEEDS-DATA** (not in any file we hold) |

## Measured numbers
Source: [`raw/image-job-timings-20261106.csv`](raw/image-job-timings-20261106.csv) (46 succeeded jobs for this model, 2026-10-30 to 2026-11-07). *Generation* is the GPU generation step only; *total* includes model load **only when the worker was not already resident**. The last column counts jobs that ran on an already-resident worker.
| Size | Jobs | Generation, median (min-max) | Total, median (min-max) | Resident worker |
|---|---|---|---|---|
| 1024x1024 | 10 | 1.2 s (1.1-1.3) | 13.1 s (1.4-16.0) | 2 of 10 |
| 1024x1536 | 36 | 1.5 s (1.4-3.3) | 2.0 s (1.7-3.7) | 36 of 36 |

**How to read the totals:** the 1024x1536 jobs all ran on an already-resident worker, so their total is only about half a second above generation; at 1024x1024 only 2 of 10 jobs were resident, and the other 8 paid a model-load of about 11.7 s (median), which is why the 1024x1024 total median (13.1 s) is so far above its generation median (1.2 s). The 1024x1024 total range (1.4 to 16.0 s) shows the same split.

We did **not** measure: VRAM or power draw, behaviour with several jobs at once, or interference with the text model on the same machine.

## What we saw in our own quality checks (small samples, one AI reviewer (a Claude Code session), nothing certified)
- In our small character tests (2 images judged on a small preview) it was low on detail and off-brief. Speed is not quality. (Source: our wave QC note; not in this repository: **NEEDS-DATA** before quoting a rate.)
- Faceless images (no people): **8 of 10** clean; the 2 rejected had garbled lettering and a small logo. One AI reviewer (a Claude Code session), one batch, two seeds (42 and 7). Counts are computed from our verdict column in [`raw/faceless/FACELESS-CLEAN-SET.csv`](raw/faceless/FACELESS-CLEAN-SET.csv); notes in [the public QC note](../001-qwen-image-2512/raw/faceless/FACELESS-QC-20261107.md) (**MEASURED** counts, one AI reviewer (a Claude Code session)'s verdicts). Images are not published.
- These are observations, not a ranking of models.

## How to reproduce the table
Download `raw/image-job-timings-20261106.csv`, keep rows where `model` is the model id above, group by `size`, and take the medians (and min and max) of `generation_seconds` and `total_seconds`; average the two middle values for an even count. We cannot give a command that regenerates an image: the job-submit route is internal. **NEEDS-DATA.**

## Limits and open questions
- Not a controlled benchmark: several campaigns, different days and prompts.
- Quality statements rest on small samples and one AI reviewer (a Claude Code session).
- The image models share a machine with a text model; we have not measured how they affect each other.
- The licence text itself has not been read by us.

## Files
`raw/image-job-timings-20261106.csv`, `raw/faceless/FACELESS-CLEAN-SET.csv` (sha256 in `raw/SHA256SUMS.txt`). No prompts, images or outputs are included.

## Licence
Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see [`LICENSE-DOCS.md`](../../LICENSE-DOCS.md). Third-party models have their own licences; check each before commercial use.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.