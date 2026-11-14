# Menu 001: Local creative studio (mostly local)

**Status: DRAFT v0.4, built in public.** (v0.4 aligns this menu with recipes 002, 004, 006, 007, 008 and 010; where it differs from them, the recipe is newer.) A *recipe* is one model's exact setup plus measured numbers. A *menu* is a combination of models plus routing and workflow that does a job, published with the same receipts. This menu describes how our studio makes illustrated content on one workstation. Labels: **SOURCED** (read from a config or doc we hold), **MEASURED** (a number from a receipt file in `raw/`), **REPORTED** (stated by an operator or a controller, not verified by us), **UNKNOWN**.

*Beeatrice is an AI-generated persona. This menu and its images are made with AI tools; approved for publication by the studio owner on 2026-11-13.*

## The job
Turn a creative brief into reviewed images (and the words around them) with the studio owner approving every public release.

## Hardware
Two NVIDIA RTX PRO 6000 Blackwell Max-Q 96 GB GPUs and an AMD Threadripper PRO 9975WX in one server (from the vendor spec sheet; not measured by us). GPU 0 serves the text model and GPU 1 runs the image models (recipes 006 and 010). Driver and CUDA pins are in the recipes that need them.

## The lineup
Image times below are **generation time only, model load excluded**; the total including model load is shown beside it. They come from all succeeded jobs in our image cache (268 jobs, earlier campaigns included), not from a controlled test. Raw file: [`raw/image-job-timings-20261106.csv`](../../raw/image-job-timings-20261106.csv).

| Role | Model | 1024x1024 median: generation / total with load | Jobs | Notes |
|---|---|---|---|---|
| Agent text model | Qwen3.8-27B-FP8 (recipes 006 and 007), served under a gateway alias | per-request decode median 19.1 tokens/s over 2026-11-08 to 2026-11-13, an ESTIMATE from live counters (recipe 006) | | profile of that process UNKNOWN; context 262,144 |
| Reference-image edit | Qwen-Image-Edit-2511 | 97.8 s / 118.0 s (40 steps) | 21 | needs reference images |
| Text-to-image | Qwen-Image-2512 | 42.2 s / 68.7 s (50 steps) | 19 | |
| Text-to-image | Z-Image | 39.7 s / 51.8 s (50 steps) | 12 | |
| Text-to-image | MOSS-Image-SFT | 31.3 s / 52.7 s (50 steps) | 8 | |
| Draft | FLUX.2 klein 4B | 1.2 s / 13.1 s (4 steps) | 10 | only 2 of 10 jobs ran on an already-loaded worker; model load was about 12 s per job otherwise |
| Draft | FLUX.3 klein distilled | 4.5 s / 18.0 s (16 steps) | 4 | licence is the FLUX Kommunity License, not Apache; not tested by our QC |

Licences: the gateway's model list (2026-10-31) shows Apache-2.0 for the other models; check each model repository's licence before commercial use.

### What we saw in our own QC (small samples, one AI reviewer (a Claude Code session), some judged from small previews; nothing certified)
- In our small tests, Qwen-Image-Edit held a character's identity from approved reference images better than the text-only models. It added an extra or wrong-arm tattoo often enough to matter; recipe 002 has the counts (1 of 8 edit images clean in wave 6) and we do not quote an overall rate.
- Qwen-Image-2512 (text only) drifted to an older look and added a hair bun across 3 test waves.
- Z-Image added a hair bun in our character tests; recipe 004 has the counts.
- MOSS-Image-SFT: one plausible character shot, one that read very young, one cartoon-styled banner.
- FLUX.2 klein: low detail and off-brief in the 2 images we judged on a small preview.

## Routing
1. The agent (text model) writes the brief and calls the image tools. **SOURCED.**
2. Our rule for the gateway: one image submit in flight at a time; every submit carries an idempotency key; a missing response is treated as UNKNOWN and reconciled by job id, never blindly retried. **SOURCED** (a rule, not a measured limit).
3. The image controller reports guards (details withheld). **REPORTED by the controller; we have not tested them.** Thermal behaviour is covered in recipes 008 and 010.
4. Roles are split: the agent session generates and fetches only; a separate Claude Code session copies files, hashes them, opens them at full size, runs QC and writes the manifest; the studio owner approves and picks. **SOURCED.**

## Cloud tools we use (named, always)
Claude Code (Anthropic Claude) for driving, review and writing; the ChatGPT image UI in a signed-in account for some Beeatrice image candidates; OpenAI image tools for some book covers; Cloudflare for the website and radio; APIFrame (Suno) for music; fal.ai (Seedance) for video; Shopify and Printful for the shop; GitHub for this repository; X for posts; and Google Fonts' GitHub repository for the Chakra Petch font (OFL) used on images.

## What we measured, and what we did not
**Measured:** image generation and total times (table above); the step times of our agent session. In the 40 steps in [`raw/opencode-step-durations-20261106.csv`](../../raw/opencode-step-durations-20261106.csv) the median step took 495 s (range 313 to 1070 s). In the split file [`raw/opencode-step-times-split-20261107.csv`](../../raw/opencode-step-times-split-20261107.csv) (80 steps) the step time is almost all model time: median 484 s of model time and 0.0 s of tool time. We have not measured tokens per second, so we do not say why the steps are slow; the cause is unknown and under investigation.
**Measured since this menu was first written:** the text model's per-request decode speed and time to first token from live counters (recipe 006, not a designed run). **Not measured yet:** behaviour with several streams at once, power draw, cooling or reliability, the actual quantization and configured context, the share of time spent loading models, any speed-up from a small fast model, any slowdown of image jobs when the text model shares a card, any workflow-versus-recipe test.

## Failure modes we have seen
- Text-only image models drift the character's apparent age and add props (see samples above).
- Reference-edit adds extra or wrong-arm tattoos in our small sample (counts in recipe 002).
- Faces on some outputs read older than intended; any age or text defect needs a human look.
- A thermal-cooldown flag read true for 10+ hours while jobs still ran; GPU readings we saw ranged 68 to 88 C. We have not measured cooling or reliability and make no claim about either.

## Not built yet
A small fast text model for routine agent work (planned, nothing installed), automatic evaluators, and a designed run of the text model (recipe 006 is live-traffic counters, not a designed run).

## How to rerun
Not yet published. Rerun steps will be added with the first measured run.

## CHANGELOG
- v0.4: aligned with recipes 002, 004, 006, 007, 008 and 010 (hardware roles, model name, tattoo and bun counts, text-model speed, thermal pointers); removed guard text and the gateway alias; the human-review wording now says what happened (AI agents wrote and checked; the studio owner approves).
- v0.3: step-time numbers now cite the raw files (median 495 s over 40 steps; split file: 484 s model time, 0.0 s tool time over 80 steps; cause unknown), added the split CSV, licence wording fixed.
- v0.2: driver check applied: generation vs load times, softer wording, REPORTED labels, raw files added, cloud list extended.
- v0.1: first draft from our studio inventory.

## CREDITS
Models by their respective authors: Qwen (Alibaba), Tongyi-MAI (Z-Image), OpenMOSS (MOSS-Image-SFT) and Black Forest Labs (FLUX; FLUX.3 klein uses the FLUX Kommunity License, see Black Forest Labs' model page). Check each licence before commercial use. See the root `LICENSE-DOCS.md` for this repository's own licences.
