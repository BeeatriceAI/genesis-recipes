# Recipe 011: Resident image pool on a 300 W workstation card: flux2-klein-4b, 61 images/min peak, about 50 sustained

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1105 v1; IN SERVICE on the lab's media card; numbers from lab runs and live bursts.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| One resident worker, 1024x1024, 4 steps | 0.98 s/image, 61.2 images/min | ungoverned, 30-36 s windows from a cool start | [I-02 · REPORTED] |
| Same, thermal governor on | 54.7 images/min over 180 s | governed | [I-04 · REPORTED] |
| Live bursts through the production API | 737 images in 883.5 s (50.1/min); 807 in 955.7 s (50.7/min); 0 failures | governed | [I-05 · REPORTED] |
| 94 four-minute windows over about 14 h | median 51.2 images/min, range 48.5-54.2, GPU peak 89 C | cooling-limited | [I-06 · REPORTED] |

Read 61 as a peak you get for half a minute on a cool card. Plan on about 50 images a minute. The limiter is the thermal governor on a 300 W part, not the model loader, the queue or memory [I-03 · REPORTED] [I-04 · REPORTED].

## 1. What this recipe is

An image service that used to start a fresh process per image (load a 4-billion-parameter diffusion model, render, exit) and now keeps the model resident in a small pool of worker processes behind a durable queue. The card is still exclusively leased as one unit: the pool takes the lease before its initial worker boots, holds it while busy and for 120 s after, and releases it when idle, so other GPU jobs still wait their turn. Cancellation, receipts and the refusal path are unchanged.

The finding that mattered: model loading dominated a one-shot job (see recipe 003 for its job-log timings: 1.2 s generation, 13.1 s total at 1024x1024 when the model had to load). Adding workers, batching or other tricks gave nothing measurable on top of keeping the model resident [I-03 · REPORTED].

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro with two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition cards (97,887 MiB each, compute capability 12.0, no NVLink). The image pool owns the lab's second card; the other serves language models.
- Power limit stock 300 W (card range 250-325 W), clocks stock, no clock cap. In the governed windows the average board power was 263.6 W (peak 308 W) and the average SM clock 1,761 MHz [I-08 · REPORTED].
- Driver 570 (open kernel module), CUDA 12.9 wheels; torch 2.11.0+cu129, diffusers 0.42.1, Python 3.12.
- Memory: one worker is about 20.3 GiB on the card (peak allocated 17.3 GiB), card baseline 1.7 GiB; four workers use 82.8 GiB; the sixth ran out of memory at load [I-09 · REPORTED].

## 3. Model

- `black-forest-labs/FLUX.2-klein-4B`, revision `e7b7dc27f91deacad38e78976d1f2b499d76a294`, Apache-2.0 (declared on the model card, read 2026-11-06) [I-13 · REPORTED]. 1024x1024, 4 steps, fixed seeds for the measurements.
- The pool also holds one worker of a 50-step model (about 26 GiB, 36 s per image) so slow jobs do not block fast ones. Its numbers appear just in the mixed-pool row.

## 4. Configuration

A pool policy, not a command line. The shipped values:

```
pooled model A (4-step):  max 2 slots, 20.5 GiB budget each
pooled model B (50-step): max 1 slot, 26.5 GiB budget
total slots 3, total memory budget 68 GiB (about 70% of the card)
boot workers one at a time; unload and release the lease after 120 s idle
thermal: hold at 88 C, resume at 84 C, stop at 91 C (and at 85 C CPU, or missing telemetry)
queue: durable; submission cap 16; idempotency keys; cancellation of queued and running jobs
```

Models that peak above about 58 GiB are not pooled and run through the old one-shot path; submitting one drains the pool, runs it, and the pool reboots on the next fast job.

## 5. Patches and workarounds

- No change to the model code or the diffusion library. The pool is a supervisor process and a worker script that import the same pipeline the one-shot path used; five hook points in the service's dispatcher (a diff of 136 lines), with 14 CPU tests using a stub worker.
- The safety path is unchanged: the refusal result maps to a "refused" state and is not retried. Safety checks stay on.
- The pool ships disabled by default and is enabled by a policy edit and a restart. Both the apply and rollback scripts were exercised on a stand-in tree, not on the live service.

## 6. Results and how they were measured

Method: a fixed prompt, a fixed seed list, 2 s telemetry of temperature, power, utilisation and clocks by GPU identifier, waits until the card is at or below 74 C before each run, and counts jobs completed inside the window; the steady column removes window quantisation by summing images over mean job time.

| Scenario | Images/min | Receipt |
|---|---|---|
| 1 resident worker, ungoverned, cool start | 61.2 steady (62.0 counted) | [I-02 · REPORTED] |
| 2, 3, 4 workers | 59 to 62 (flat) | [I-03 · REPORTED] |
| Batch 2 / 4 / 8 on one worker | 59.6 / 56.7 / 57.1 | [I-03 · REPORTED] |
| 1 worker, governed, 180 s | 54.7 (duty about 91%, 14 pauses) | [I-04 · REPORTED] |
| Live burst 1, 883.5 s | 50.1 | [I-05 · REPORTED] |
| Live burst 2, 955.7 s | 50.7 | [I-05 · REPORTED] |
| 94 governed windows | median 51.2 | [I-06 · REPORTED] |

Latency in the governed windows: median p50 0.97 s, median p95 2.88 s, the tail being the 88 C pauses [I-07 · REPORTED]. Mixed pool: while a 36 s image renders in one slot, 4-step jobs in the other two keep a 3.1 s latency [I-10 · REPORTED]. CUDA MPS added 6-9% in three A/B pairs and was not adopted [I-11 · REPORTED]. The initial image after idle pays about 14 s of worker boot [I-12 · REPORTED].

The live bursts counted jobs whose final state landed in the window; monitor samples were once a minute and include ramp edges. GPU 1 ran at 68-88 C and averaged 253-263 W. Another card was serving a different workload at its power limit during the bursts, and the effect of one card on the other was not measured [I-05 · REPORTED].

## 7. Thermal behaviour

- At 300 W the card climbs from about 70 C to 88 C in 45-60 s and then sits at 87-88 C. That is the sustained ceiling; the governor holds new work at 88 C and resumes at 84 C, cooling back takes about 2 s once the load stops [I-04 · REPORTED].
- Across 94 windows the governor paused 1,645 times in total and the card peaked at 89 C once; the sole throttle-reason values seen were "none" and the software power cap [I-06 · REPORTED] [I-08 · REPORTED]. No window was a pass or fail on thermals: all are labelled cooling-governed, and they are labelled that way here too.
- Nothing about the pause lines was changed for this recipe; the hardware limits are untouched.

## 8. What did not work

- Adding workers beyond one: no throughput, higher latency and memory [I-03 · REPORTED].
- Batching 2, 4 or 8 images: slower than batch 1 and 1.2x-2.4x the memory [I-03 · REPORTED].
- Six workers: out of memory at load; five is about 103 GiB by arithmetic [I-09 · REPORTED].
- The 50-step model alone ungoverned: stopped inside 40 s at the 88 C line, an incomplete run, never a pass [I-10 · REPORTED].
- CUDA MPS: +6-9%, within what a thermal-state change could explain [I-11 · REPORTED].
- A model that peaks at 58-61 GiB cannot share the card with the pool.

## 9. Not measured

Image quality (outputs were spot-checked, not scored, and no comparison between pool and one-shot outputs was made); runs longer than about 16 minutes of continuous live burst; cold-disk model load; torch.compile, fp8 or NVFP4 transformer variants; the effect on the other card's latency [I-14 · NOT RUN].

## 10. Reproduction steps (draft, one machine)

1. Install the pins above; load the model once and render a single 1024x1024, 4-step image with a fixed seed; time load and render separately and compare with [I-12 · REPORTED] and with recipe 003.
2. Keep that process alive and render 30 s of images back to back from a card at or below 74 C; compare with [I-02 · REPORTED].
3. Repeat for 180 s with a pause at 88 C and resume at 84 C; compare with [I-04 · REPORTED].
4. Put a durable queue and a single exclusive lock in front of the workers; confirm that a second GPU job waits for the lock.
5. Publish temperature, power and clocks beside the rate.

The pool code and policy file are not published yet (they contain lab paths). Until they are, steps 1-3 reproduce the main finding and step 4 is a design to implement.

## 11. Licence and credits

Model: FLUX.2-klein-4B by Black Forest Labs, Apache-2.0 (declared on the model card, read 2026-11-06). Diffusers library: Apache-2.0 (read on its repository 2026-11-06). Recipe text CC BY 4.0; code MIT. See LICENSE-DOCS.md for trademark notes and what was not verified.

## 12. Changelog

- 2026-1105 v1: initial write-up from the lab report, the live burst receipt and 94 governed windows.
- 2026-1106 note: the pause and resume lines in section 4 (88 C / 84 C) were later raised to 90 C / 87 C; see recipe 010. The numbers in this recipe were measured at 88/84 and stay as they are.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; where a licence line below says "check upstream" we have not verified it. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools and reviewed by a human before release.
Written by AI agents and reviewed by a human before publishing.
