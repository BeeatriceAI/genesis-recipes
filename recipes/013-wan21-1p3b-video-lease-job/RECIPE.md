# Recipe 013: Wan 2.1 1.3B video on a Max-Q card via a lease-holding job

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1105 v1; WORKING FOR SHORT B-ROLL CLIPS; quality not evaluated.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| 21-frame clip (1.31 s at 16 fps), 480x832, 30 steps | median 26.0 s per clip, 22 clips, 0 failures | harness-paced, no pause occurred | [V-01 · REPORTED] |
| 41-frame clip (2.56 s, the runner maximum) | 77.3 s and 51.7 s (two clips) | harness-paced | [V-02 · REPORTED] |
| Video per GPU minute, warm | about 3 s | derived | [V-04 · REPORTED] |
| Larger 14B model, 9 frames | 112.5 s cold, 0.3 s of video per GPU minute | ungoverned, one run | [V-05 · REPORTED] |

One limitation next to the headline: these are short clips from fixed prompts and one seed each. A frame per clip was checked by image inspection on the production-path run and none on the 22-clip job, so this recipe says nothing about video quality [V-12 · NOT RUN].

## 1. What this recipe is

A job that renders text-to-video clips on the lab's second card while sharing that card with other workloads. The job does not call a media service. It runs under an exclusive lock on the card (held by a job scheduler for the whole run), starts the Wan runner itself as a child process on a private loopback port, renders a fixed list of prompts with fixed seeds, writes the clip, a receipt and a poster frame for each, stops the child and exits. Because the child is in the job's process group, the scheduler's thermal pause (stop signal at 88 C, continue at 84 C) pauses the video model too. A media service that holds its own lease cannot pause a running request; it can just kill it [V-05 · REPORTED] [V-10 · REPORTED].

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro, two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition cards (97,887 MiB each, compute capability 12.0, no NVLink). The job runs on the second card; power limit stock 300 W, clocks stock.
- Driver 570 (open kernel module), CUDA 12.9 wheels; the runner's environment has torch 2.11.0+cu129, diffusers 0.42.1, transformers 5.22.1, Python 3.12.
- The Wan reference loader, with attention routed through PyTorch SDPA because no FlashAttention wheel exists for this card in this stack.

## 3. Model

- Wan 2.1 T2V 1.3B (`Wan2.1-T2V-1.3B` weights: DiT, UMT5-XXL encoder in bf16, Wan VAE), Apache-2.0. The pull was by repository name with a checksum manifest; the commit id was not recorded [V-11 · REPORTED]. Fix this before pinning a public revision.
- For comparison, the 14B model was run once [V-05 · REPORTED].

## 4. Job parameters

```
frames          21 (1.31 s) or 41 (2.56 s); frame count = 4 x duration + 1, duration 2..10 in the runner
size label      request 480x832 to get a landscape 832x480 clip (the runner's label is swapped, see below)
steps / fps     30 steps, 16 fps (fixed by the runner)
seed            fixed per prompt id; a prompt already rendered at this frame count and seed is skipped
negative prompt the runner's default (text, watermark, still frames); no control exposed
admission       start a clip when the card is at or below 76 C (21 frames) or 72 C (41 frames); wait up to 300 s for that;
                at least 10 s between clips
exit codes      0 complete | 3 runner failure | 4 time budget reached | 5 cooling-limited | 143 terminated
```

On SIGTERM the job keeps a clip that is within 4 s of completing and abandons otherwise; the child is always killed. A re-run after a hand-over resumes at the next unfinished prompt [V-09 · REPORTED]. The prompt list is 24 plain scenic and technical b-roll prompts, none with faces, lettering or brands; it will be published as a JSON file after review.

## 5. Patches and workarounds

- The runner is the upstream Wan loader with an SDPA attention patch (no FlashAttention). The 14B entry in the lab's runner is an uncommitted local patch and is not part of this recipe.
- Start the runner as the job's own child, with the lease proof passed by environment, instead of calling the lab's media service: the service answers HTTP 429 "lease busy" when another job holds the lock, which parked a request for 10 s [V-10 · REPORTED].
- Do not trust the runner's own memory figure (13 GB): it under-reports the real peak by 4 to 5x [V-07 · REPORTED].
- The width and height labels are swapped in the runner: asking 832x480 gives a portrait clip [V-06 · REPORTED].

## 6. Results and how they were measured

Method: wall time per clip from the job's receipt (request to file written), GPU temperature and power at 2 s by card identifier, whole-card memory from the driver. Fixed seeds and prompts; one resolution (the sole one the runner serves).

| Run | Clips | Wall per clip | GPU peak | Receipt |
|---|---|---|---|---|
| 21 frames, job, 22 clips | 22 rendered, 0 failed, 0 abandoned | median 26.0 s, mean 27.0 s, range 24.9-53.1 s (the 53.1 s clip carried the model load) | 79-85 C | [V-01 · REPORTED] |
| 41 frames, job | 2 | 77.3 s and 51.7 s (mean 64.5 s) | 86-87 C | [V-02 · REPORTED] |
| 21 frames, media service, warm | 3 | 26.6-27.2 s | 80-83 C | [V-03 · REPORTED] |
| 41 frames, media service | 1 | 52.8 s | 86 C | [V-03 · REPORTED] |
| same, cold call | 1 | 56.1 s (about 29 s model load) | 80 C | [V-03 · REPORTED] |
| 14B, 9 frames, cold | 1 | 112.5 s | 85 C | [V-05 · REPORTED] |

Derived: about 3 s of video per GPU minute for the 1.3B model warm, 0.3 s for the 14B cold [V-04 · REPORTED] [V-05 · REPORTED]. Memory (whole card, includes about 1.9 GB of desktop): 14.9-20.0 GB for 21 frames, 60.3 GB for the 41-frame clip, 68.9 GB for the 14B [V-07 · REPORTED] [V-05 · REPORTED].

Sharing the card: a blocking waiter on the lock file gets the card in about 1.4 s because the scheduler yields. In two hand-overs the displaced job lost 344 s and 42 s of work and restarted its run [V-08 · REPORTED]. The 41-frame job needed 6 attempts, 5 of them interrupted by hand-overs, because other jobs held priority; the skip-if-done rule is why that cost little [V-09 · REPORTED].

## 7. Thermal behaviour

- Pacing lines for the job: pause at 88 C, resume at 84 C, stop at 91 C or 1 C thermal margin or 85 C CPU, as set by the scheduler. No pause occurred in the 22-clip job; the 41-frame clips peaked at 86-87 C, which is 1-2 C under the pause line, so expect pauses on a warmer day [V-01 · REPORTED] [V-02 · REPORTED].
- From a 68-72 C start, 21-frame clips peaked at 80-83 C and the 41-frame clip at 86 C (margin 6 C) [V-03 · REPORTED].
- In the 14B run the CPU temperature touched 85.25 C for one sample, the CPU stop line. The request could not be cancelled from the client and finished 30 s later: a completed clip with a documented excursion, not a clean pass [V-05 · REPORTED].
- Start 41-frame clips with the card at or below 72 C; the lab classes that job as hot.

## 8. What did not work

- Calling the media service from a job that already holds the lock: refused with HTTP 429 until the job stops holding the lock [V-10 · REPORTED].
- A client-side stop for the 14B run: the service cannot cancel one in-flight call; its 88 C stand-down is the sole way to end it, and the clip in flight is lost [V-05 · REPORTED].
- Using the runner's memory report for admission: 4 to 5x too low [V-07 · REPORTED].
- 81-frame clips (the model's native length): the runner does not expose them.

## 9. Not measured

Motion and prompt-adherence quality (no review of the 22 clips beyond file checks), other seeds and resolutions, warm 14B, 21-frame 14B, behaviour at the 88 C stand-down, any co-resident image workload [V-12 · NOT RUN]. These are not a quality evaluation or a long soak.

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Install the pins above and the upstream Wan loader; fetch the 1.3B weights and record the commit id and file hashes.
2. Render one 21-frame clip with a fixed seed from a card at or below 76 C; the initial call includes about 29 s of load, the next ones should land near 26 s [V-03 · REPORTED].
3. Run 22 prompts back to back under a pause-at-88 / resume-at-84 script; compare with [V-01 · REPORTED].
4. Put an exclusive lock on the card; verify that a second job requesting the lock gets it in about 1.5 s and that your job restarts cleanly [V-08 · REPORTED].
5. Record temperature, power and the pause count next to the times.

The job script and prompt file are lab code (they carry paths); publish them sanitised before calling this a reproduction.

## 11. Licence and credits

Model: Wan 2.1 T2V 1.3B by the Wan team at Alibaba, Apache-2.0 (declared on the model card, read 2026-11-06). Recipe text CC BY 4.0; code MIT. See LICENSE-DOCS.md for trademark notes and what was not verified.

## 12. Changelog

- 2026-1105 v1: initial write-up from the 22-clip job, the 41-frame job and the production-path run.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
