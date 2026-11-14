# Recipe 001: Qwen-Image-2512 on the Genesis image card

**Status: DRAFT v0.2, built in public.** A *recipe* is one model's exact setup plus measured numbers. The numbers below come from our own job log, not from a controlled test: every succeeded job in our image cache (earlier campaigns included), one observer, one machine. Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = said by an operator or a tool, not verified by us; **UNKNOWN** / **NEEDS-DATA** = we do not have it.

*Beeatrice is an AI-generated persona. This recipe and its numbers are made with AI tools; approved for publication by the studio owner on 2026-11-13. Cloud tools we use elsewhere are named in [Menu 001](../../menus/001-local-creative-studio/MENU.md).*

## The job
Turn a text prompt into one still image at 1024x1024, 1024x1536 or 1536x1024 on a local image model. Text only: this model does not take a reference image.

## Setup (what we know)
| Item | Value | Label |
|---|---|---|
| Model | Qwen/Qwen-Image-2512, revision `25468b98` | SOURCED (the gateway's model list read 2026-10-31) |
| Licence | apache-2.0 per the gateway list; we have not read the repository's LICENSE file | SOURCED (list) / UNKNOWN (file text) |
| Steps | 50 | MEASURED (`steps` column) |
| Precision | bfloat16 | MEASURED (`dtype` column) |
| Reference image | unsupported | SOURCED |
| Allowed sizes | 1024x1024, 1024x1536, 1536x1024 | SOURCED |
| Hardware | two NVIDIA RTX PRO 6000 Blackwell Max-Q 96 GB GPUs and an AMD Threadripper PRO 9975WX, from the vendor spec sheet; not measured by us. The operator reports one GPU runs the image models | SOURCED (vendor spec sheet) / REPORTED |
| Submit rule | one image submit in flight at a time, with an idempotency key; a missing response is reconciled by job id, never blindly retried | SOURCED (a rule, not a measured limit) |
| Sampler, guidance scale, seed handling, VRAM use, GPU driver, CUDA and serving-stack versions, quantization other than the dtype above | | **NEEDS-DATA** (not in any file we hold; the operator would have to supply them) |

## Measured numbers
Source: [`raw/image-job-timings-20261106.csv`](raw/image-job-timings-20261106.csv) (87 succeeded jobs for this model, 2026-10-30 to 2026-11-07). *Generation* is the GPU generation step only; *total* includes model load. None of the 87 jobs ran on an already-resident worker, so every total here includes loading the model (median about 25.0 s).
| Size | Jobs | Generation, median (min-max) | Total with load, median (min-max) |
|---|---|---|---|
| 1024x1024 | 19 | 42.2 s (40.9-45.2) | 68.7 s (64.2-76.0) |
| 1024x1536 | 60 | 64.8 s (64.2-68.9) | 90.3 s (89.1-97.9) |
| 1536x1024 | 8 | 65.0 s (64.2-65.6) | 90.6 s (89.4-93.8) |
We did **not** measure: tokens per second (not applicable), VRAM or power draw, behaviour with several jobs at once, or how the image jobs slow down when the text model shares the machine.

## What we saw in our own quality checks (small samples, one AI reviewer (a Claude Code session), nothing certified)
- **Age drift went both ways in our character tests.** In an early test (wave 1) a text-only face from this model read soft and youthful, "could read under 25", with a top-knot bun; in a later test (wave 3) the text-only faces read about 40 to 45, one with a bun. A bun appeared in some images. These are the reviewer's by-eye reads on small samples, for a character whose stated age is an adult; age direction matters, so every image is checked by hand. (Sources: our wave QC notes, which are not in this repository: **NEEDS-DATA** before anyone quotes a rate.)
- **Faceless images (no people): clean in 10 of 10.** In our faceless batch this model produced 10 images (5 cover directions plus the "138 lightning" cover run in a later retry, and 4 textures) and the reviewer found no stray text, logos or faces in any of them. For comparison, across all three models 21 of 26 faceless images were clean: FLUX.2 klein 8 of 10 and Z-Image 3 of 6; the 5 rejected images had garbled lettering or logos, and a small cartoon face icon appeared twice. One AI reviewer (a Claude Code session), one batch, two seeds (42 and 7). Counts are computed from our verdict column in [`raw/faceless/FACELESS-CLEAN-SET.csv`](raw/faceless/FACELESS-CLEAN-SET.csv); the AI reviewer's notes are in [`raw/faceless/FACELESS-QC-20261107.md`](raw/faceless/FACELESS-QC-20261107.md) (**MEASURED** counts, one AI reviewer (a Claude Code session)'s verdicts). The images themselves are not published (pending human approval).
- These are observations, not a ranking of models.

## How to reproduce the table
Download `raw/image-job-timings-20261106.csv`, keep rows where `model` is `qwen-image-2512`, group by `size`, and take the median of `generation_seconds` and `total_seconds` (for an even number of jobs average the two middle values, which is the rule the table uses). A short PowerShell version (code is MIT):
```powershell
Import-Csv .\raw\image-job-timings-20261106.csv | Where-Object model -eq 'qwen-image-2512' |
  Group-Object size | ForEach-Object {
    $g = $_.Group | ForEach-Object { [double]$_.generation_seconds } | Sort-Object
    [pscustomobject]@{ size = $_.Name; jobs = $_.Count; median_gen = $g[[int](($g.Count-1)/2)] } }
```
The snippet shows the lower middle value for an even count; the table averages the two middle values. We cannot give a command that regenerates an image from our setup: the job-submit route is internal. **NEEDS-DATA.**

## Limits and open questions
- Not a controlled benchmark: jobs come from several campaigns on different days and prompts.
- The image models share a machine with a text model; we have not measured how they affect each other.
- Quality statements rest on small samples and one AI reviewer (a Claude Code session).
- The licence text itself has not been read by us.

## Files
`raw/image-job-timings-20261106.csv`, `raw/faceless/FACELESS-CLEAN-SET.csv`, `raw/faceless/FACELESS-QC-20261107.md` (sha256 in `raw/SHA256SUMS.txt`). No prompts, no images, no outputs are included.

## Licence
Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code snippets: MIT; see [`LICENSE-DOCS.md`](../../LICENSE-DOCS.md). Third-party models have their own licences; check each before commercial use.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
