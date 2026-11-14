# Recipe 005: MOSS-Image-SFT on the Genesis image card

**Status: DRAFT v0.1, built in public.** A *recipe* is one model's exact setup plus measured numbers. The numbers come from our own job log, not from a controlled test: every succeeded job for this model in our image cache (earlier campaigns included), one observer, one machine. Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = said by an operator or a tool, not verified by us; **UNKNOWN** / **NEEDS-DATA** = we do not have it.

*Beeatrice is an AI-generated persona. This recipe and its numbers are made with AI tools; approved for publication by the studio owner on 2026-11-13. Cloud tools we use elsewhere are named in [Menu 001](../../menus/001-local-creative-studio/MENU.md).*

## The job
Turn a text prompt into one still image at 1024x1024, 1024x1536 or 1536x1024. Text only: this model does not take a reference image.

## Setup (what we know)
| Item | Value | Label |
|---|---|---|
| Model | OpenMOSS-Team/MOSS-Image-SFT, revision `f972bd4b` | SOURCED (the gateway's model list read 2026-10-31) |
| Licence | apache-2.0 per the gateway list; the repository's LICENSE file text not read by us | SOURCED (list) / UNKNOWN (file text) |
| Steps | 50 | MEASURED (`steps` column) |
| Precision | bfloat16 | MEASURED (`dtype` column) |
| Reference image | unsupported | SOURCED / MEASURED (`reference_supplied` is false for every job in the log) |
| Allowed sizes | 1024x1024, 1024x1536, 1536x1024 | SOURCED |
| Hardware | two NVIDIA RTX PRO 6000 Blackwell Max-Q 96 GB GPUs and an AMD Threadripper PRO 9975WX, from the vendor spec sheet; not measured by us; the operator reports one GPU runs the image models | SOURCED (vendor spec sheet) / REPORTED |
| Submit rule | one image submit in flight at a time, with an idempotency key; a missing response is reconciled by job id, never blindly retried | SOURCED (a rule) |
| Sampler, guidance scale, seed handling, VRAM use, driver/CUDA/serving versions, quantization other than the dtype above | | **NEEDS-DATA** (not in any file we hold) |

## Measured numbers
Source: [`raw/image-job-timings-20261106.csv`](raw/image-job-timings-20261106.csv) (41 succeeded jobs for this model, 2026-10-30 to 2026-11-07). *Generation* is the GPU generation step only; *total* includes model load **only when the worker was not already resident**. The last column counts jobs that ran on an already-resident worker.
| Size | Jobs | Generation, median (min-max) | Total, median (min-max) | Resident worker |
|---|---|---|---|---|
| 1024x1024 | 8 | 31.3 s (30.9-33.6) | 52.7 s (52.2-58.3) | 0 of 8 |
| 1024x1536 | 32 | 50.2 s (49.1-52.1) | 71.8 s (71.6-73.6) | 0 of 32 |
| 1536x1024 | 1 | 49.6 s (49.6-49.6) | 70.9 s (70.9-70.9) | 0 of 1 |

**How to read the totals:** none of the 41 jobs ran on an already-resident worker, so every total includes loading the model (median about 21.3 s). The single 1536x1024 job is one sample, not a median to rely on.

We did **not** measure: VRAM or power draw, behaviour with several jobs at once, or interference with the text model on the same machine.

## What we saw in our own quality checks (small samples, one AI reviewer (a Claude Code session), nothing certified)
- In our small tests we judged three images: a guardian shot with a bun (reading about 30 to 35), a face that "may read about 24-26" (an age hold for an adult character), and one banner that came out cartoon-styled. Three images; no rate. (Source: our wave 3 and 4 QC notes; not in this repository: **NEEDS-DATA** before anyone quotes a rate.)
- A later one-pair score sweep (one reference pair, one character) scored this model highest; that scorer's reliability has not been tested, so we publish no ranking (REPORTED, driver's check; the sweep note is not in this repository).
- It was **not** part of our faceless batch, so we have no faceless-image result for it.

## How to reproduce the table
Download `raw/image-job-timings-20261106.csv`, keep rows where `model` is the model id above, group by `size`, and take the medians (and min and max) of `generation_seconds` and `total_seconds`; average the two middle values for an even count. We cannot give a command that regenerates an image: the job-submit route is internal. **NEEDS-DATA.**

## Limits and open questions
- Not a controlled benchmark: several campaigns, different days and prompts.
- Quality statements rest on small samples and one AI reviewer (a Claude Code session).
- The image models share a machine with a text model; we have not measured how they affect each other.
- The licence text itself has not been read by us.

## Files
`raw/image-job-timings-20261106.csv` (sha256 in `raw/SHA256SUMS.txt`). No prompts, images or outputs are included.

## Licence
Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see [`LICENSE-DOCS.md`](../../LICENSE-DOCS.md). Third-party models have their own licences; check each before commercial use.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.