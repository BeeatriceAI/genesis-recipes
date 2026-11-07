# Recipe 002: Qwen-Image-Edit-2511 with approved reference images

**Status: DRAFT v0.2, built in public.** A *recipe* is one model's exact setup plus measured numbers. The numbers come from our own job log, not from a controlled test: every succeeded job for this model in our image cache, one observer, one machine. Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = said by an operator or a tool, not verified by us; **UNKNOWN** / **NEEDS-DATA** = we do not have it.

*Beeatrice is an AI-generated persona. This recipe and its numbers are made with AI tools and reviewed by a human before release. Cloud tools we use elsewhere are named in [Menu 001](../../menus/001-local-creative-studio/MENU.md).*

## The job
Edit or generate an image of a known character from one or more approved reference images, so that the character's identity carries over. This model **requires** a reference image.

## Setup (what we know)
| Item | Value | Label |
|---|---|---|
| Model | Qwen/Qwen-Image-Edit-2511, revision `6f3ccc0b` | SOURCED (gateway model list read 2026-10-31) |
| Licence | apache-2.0 per the gateway list; the repository's LICENSE file text not read by us | SOURCED (list) / UNKNOWN (file text) |
| Steps | 40 | MEASURED |
| Precision | bfloat16 | MEASURED |
| Reference image | REQUIRED (all 43 jobs in the log supplied one) | SOURCED / MEASURED |
| Allowed sizes | 1024x1024, 1024x1536, 1536x1024 | SOURCED |
| Hardware | two NVIDIA RTX PRO 6000 Blackwell Max-Q 96 GB GPUs and an AMD Threadripper PRO 9975WX, from the purchase invoice; not measured by us; the operator reports one GPU runs the image models | SOURCED (invoice) / REPORTED |
| Submit rule | one image submit in flight at a time, with an idempotency key; a missing response is reconciled by job id, never blindly retried | SOURCED (a rule) |
| Number of reference images per job, prompt text, guidance scale, sampler, seed handling, VRAM use, driver/CUDA/serving versions | | **NEEDS-DATA** (prompts are private; the rest is not in any file we hold) |

## Measured numbers
Source: [`raw/image-job-timings-20261106.csv`](raw/image-job-timings-20261106.csv) (43 succeeded jobs for this model, 2026-11-05 to 2026-11-07). *Generation* is the GPU step only; *total* includes model load. None of the jobs ran on an already-resident worker, so every total includes loading the model (median about 20 s).
| Size | Jobs | Generation, median (min-max) | Total with load, median (min-max) |
|---|---|---|---|
| 1024x1024 | 21 | 97.8 s (94.3-100.5) | 118.0 s (113.5-120.7) |
| 1024x1536 | 8 | 120.7 s (119.8-126.1) | 140.9 s (139.7-147.6) |
| 1536x1024 | 14 | 127.1 s (119.9-128.6) | 147.3 s (139.9-148.9) |
We did **not** measure: VRAM or power draw, behaviour with several jobs at once, or interference with the text model on the same machine.

## What we saw in our own quality checks (small samples, one reviewer, nothing certified)
- **Identity:** by eye, in waves 3 to 6 of our character tests, the reference-edit route carried the approved identity (copper-red curls, purple braids, glasses) better than the text-only Qwen model. A later one-pair score sweep (one reference pair, one character) disagreed: it scored MOSS-Image-SFT highest and gave the edit route 0.0 on the face metric, and that scorer's reliability has not been tested. **So we publish no ranking of models.** (Sources: our wave QC notes and the sweep note, neither in this repository.)
- **Tattoos are the weak spot.** Our character has one heart tattoo on one arm. In wave 6 only **1 of 8** edit images was clean. In wave 4 the heart appeared on both arms in three images and on the wrong arm in one; in wave 5 on both arms in one image and on the wrong arm in another. One reviewer, small samples, some judged from small previews. We do not quote an overall rate because our notes do not support one. (Sources: wave 4, 5 and 6 QC notes, not in this repository.)
- **Faces** read about 30 to 40 in our reviewer's judgment (by eye, some from small previews), older than the character's stated adult age. We therefore state adult ages and anchors explicitly in prompts and check every image by hand.
- **A wrong character description** (a different braid colour and arm) was used in our first two test waves. Those waves ran the text-only models (Qwen-Image-2512 and Z-Image), **not this edit model**; the error was caught by comparing against the approved files and then corrected everywhere it had been copied. (Source: wave 1 and 2 QC notes and our identity-anchor notes; not in this repository.)

## How to reproduce the table
Download `raw/image-job-timings-20261106.csv`, keep rows where `model` is `qwen-image-edit-2511`, group by `size`, and take the medians of `generation_seconds` and `total_seconds` (average the two middle values for an even count). We cannot give a command that regenerates an image: the submit route is internal, the reference images are not published, and no outputs are included. **NEEDS-DATA.**

## Limits and open questions
- Not a controlled benchmark; several campaigns, different days, different prompts.
- Quality statements rest on small samples and one reviewer, and one later sweep disagreed.
- The reference images and all outputs are withheld: they are pending human approval.
- The licence text has not been read by us.

## Files
`raw/image-job-timings-20261106.csv` (sha256 in `raw/SHA256SUMS.txt`). No prompts, no reference images, no outputs are included.

## Licence
Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see [`LICENSE-DOCS.md`](../../LICENSE-DOCS.md). Third-party models have their own licences; check each before commercial use.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools and reviewed by a human before release.
