# Recipe 014: LongCat Avatar presenter + SeedVR2 on one card

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1105 v1; WORKS END TO END ON A 15-SECOND PIECE; slow, and judged by stills.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

> **Warning: one lab's settings, not a recommendation.** The temperatures, pause lines and power figures in this recipe are guardrails this lab chose for its own cooling and room. They were not checked against a vendor limit, depend on your cooling and ambient temperature, and may void a warranty. Do not copy them; use your vendor's documented limits.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| Presenter stage: 15.0 s of speech to 375 frames, 832x480, 25 fps | 707.3 s wall = 593 s active + 111 s paused | harness-paced | [P-01 · REPORTED] |
| Super-resolution to 1264x720 | 404.7 s, no pauses | harness-paced | [P-02 · REPORTED] |
| Card time per second of finished video | about 36 s (presenter) + 27 s (upscaler) | derived, paced by cooling | [P-03 · REPORTED] |
| Whole 15 s piece, GPU stages | 1,111.8 s (18.5 min) to a 1920x1080 file | harness-paced | [P-04 · REPORTED] |

One limitation next to the headline: this is roughly an hour of one card per minute of presenter video, and the judgement of quality rests on extracted frames. Nobody had played the clip with sound when this was written [P-05 · REPORTED].

## 1. What this recipe is

A talking-presenter pipeline that fits on one 96 GB card shared with other jobs: take a voice recording and a still image, generate a speaking video (LongCat-Video-Avatar-1.5, 8-step distilled, bf16, 480p, continued segment by segment), upscale it with SeedVR2-7B, then assemble a 1080p file with captions. Each GPU stage takes the exclusive card lease, runs as a child process with an external thermal pacer, and releases the lease; three hand-overs per run [P-11 · REPORTED].

The avatar is a synthetic still made with a local image model. It is not a real person. The voice is a 15-second voice-over recording that is not shared.

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro, two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition cards (97,887 MiB each, compute capability 12.0, no NVLink). The pipeline uses the second card; power limit stock 300 W, clocks stock. The other card was at 87 C serving language models during the run.
- Driver 570 (open kernel module); CUDA 12.9 wheels; torch 2.13.0+cu129; Python 3.12; a separate environment per model (the two stacks pin different transformers and diffusers versions).
- Peak whole-card memory: 70,596 MiB for the presenter stage, 79,478 MiB for the upscaler stage [P-01 · REPORTED] [P-02 · REPORTED].

## 3. Models and licences

| Model | Revision | Licence |
|---|---|---|
| LongCat-Video-Avatar-1.5 | `92016c71d5d318d0f5d84e4db30015a571484ab6` | MIT |
| LongCat-Video (base text encoder, tokeniser, VAE) | `03b55529b1d1d4045f5fbe14d65c8c6e8116b278` | MIT (licence file in the repository) |
| SeedVR2-7B | `eb0c4281d41ba3767d4f14370f0e37e9e9180c16` | Apache-2.0 |

The pipeline also uses a speech-separation model, a transcription model and a voice-synthesis model; their licences are not covered here [P-10 · REPORTED]. Weights were pulled at pinned revisions and every large file was checked against the repository's published hash (zero mismatches); the 8-step distilled path needs the distillation LoRA.

## 4. How it is run

```
stage 1  audio prep      noise-floor and SNR check; vocal separation applied when the recording is noisy
stage 2  transcript      word timestamps, caption lines
stage 3  presenter       official LongCat demo script (audio+image to video, 8 steps, --use_distill, avatar-v1.5,
                         480p, reference frame index 10, mask range 3), 93 frames for the initial segment and 80 new
                         frames per continuation, 25 fps; trimmed to the voice length; re-encoded at crf 10
stage 7  upscale         SeedVR2-7B on chunks of 4k+1 frames sized to a fixed pixels-times-frames budget
                         (41 frames at 1264x720), one process for all chunks, joined at crf 12
stage 6  assemble        lanczos to 1920x1080, burned captions, -17 LUFS audio
each GPU stage: take the card lease, wait for no other compute owner, cool to 78 C, run as a child with
CUDA_VISIBLE_DEVICES set by card identifier, offline model hub, minimal environment, release the lease at once
```

Pacing for the child: stop signal at 88 C, continue at 84 C, stop the run at 91 C, thermal margin 1 C or less, active slowdown, three missing telemetry samples or 85 C CPU; a cumulative pause budget turns a cooling-limited run into an INCOMPLETE result instead of a pass.

## 5. Patches and workarounds

- 3 shims plus a one-line patched script, because the upstream code hard-imports packages with no wheel for this card [P-08 · REPORTED]: FlashAttention calls go to PyTorch SDPA, the fused RMSNorm goes to a plain fp32 implementation, and the video reader goes through PyAV. The numerics are therefore not those of the reference kernels.
- The demo resolves its base components through the parent of the checkpoint directory, through a symlink target: place the base repository next to the real avatar repository, not next to the link.
- The demo fixes its seed at 42; the command-line seed does not reach it [P-09 · REPORTED].
- Pause signals must reach the whole process tree. The launcher (torchrun) starts its worker in a new session, so a stop sent to the launcher's group left the GPU busy: 98.7% utilisation and 297 W during 77 "paused" samples [P-06 · REPORTED].
- The SeedVR2 attention shim has no sm_120 FlashAttention; memory is managed with checkpoint offload on.

## 6. Results and how they were measured

Method: one run, one synthetic still, one 15-second voice-over, 2 s telemetry by card identifier, per-stage receipts with wall, active and paused seconds, memory, temperatures, power, hashes.

| Stage | Wall | Peak GPU | Memory (whole card) | Notes | Receipt |
|---|---|---|---|---|---|
| Voice clean-up (separation) | 16.2 s | 79 C | 3.9 GB | noise floor -34.6 to -60.5 dBFS, SNR 17.9 to 43.6 dB | [P-04 · REPORTED] |
| Presenter, 5 segments | 707.3 s (593 active, 111 paused, 53 pauses) | 89 C, margin 3 C | 70,596 MiB | 375 frames at 832x480, 25 fps | [P-01 · REPORTED] |
| Upscale, 10 chunks | 404.7 s, 0 paused | 83 C | 79,478 MiB | 375 frames in and out, 832x480 to 1264x720 | [P-02 · REPORTED] |
| Assembly | 1.6 s | CPU | - | 1920x1080, 25 fps, 15.0 s, -17.0 LUFS | [P-04 · REPORTED] |

Derived: 593 s over 16.52 s of generated video is 35.9 GPU-seconds per video-second; the upscaler is 26.6; together about 62, so a minute of presenter video is about an hour of card time at the day's ambient [P-03 · REPORTED]. The presenter layer's native detail is 720p-class and is resized 1.52x to 1080p; the 1080p-class upscaling path exists and is unmeasured [P-04 · REPORTED].

An upscaler smoke test on a separate 41-frame clip took 91.9 s wall cold (about 40 s of that is loading the 33 GB checkpoint) at 74.9 GB, 80 C [P-07 · REPORTED].

Visual gate, from frames extracted at four times, twelve join frames and mouth crops [P-05 · REPORTED]: identity stable across the four segment joins; no visible seam; the luma step at the upscaler joins at most 0.89 against 3.34 between ordinary frames; mouth shapes looked plausible in four still frames; motion was not reviewed. Artifacts: a pink cast on the lips in wide-open frames, slightly over-sharpened skin and hair, hands entering at the bottom edge in the last two seconds.

## 7. Thermal behaviour

- Presenter stage: the card entered at 73 C, reached 89 C (margin 3 C) and was paused 53 times for 2-4 s each, 16% of the wall time (111 s of 707.3 s). The pacer's lines are the lab's own guardrails; the card's hardware protections are untouched [P-01 · REPORTED].
- Upscaler stage: peak 83 C, no pauses [P-02 · REPORTED].
- A cooling-limited run does not count as a pass. This run finished within the pause budget (600 s) and the stop lines never fired.
- An earlier smoke test of the same presenter model reported 9.8 s per video-second with 157 s of "pause". That was wrong: the worker had not paused (P-06 above). The corrected pace is about 33 s per video-second at 640x608. If you see the 9.8 figure in an older note, it is retracted [P-06 · REPORTED].

## 8. What did not work

- Stopping the launcher's process group to pause the GPU [P-06 · REPORTED].
- Running the presenter demo offline with the base components missing: the base repository is required and an early run used components rebuilt from local files; the official files were later hash-verified and swapped in [P-08 · REPORTED].
- Upstream attention and norm kernels: no wheels for this card; replaced with shims [P-08 · REPORTED].
- Judging pace from the earlier smoke test; retracted [P-06 · REPORTED].

## 9. Not measured

Pieces longer than about 17 s (identity drift across many segments), vertical 9:16 output, the 720p presenter bucket, the INT8 variant, 1080p-class upscaling, a listening test, lip-sync scoring, a pass on a cooler room [P-12 · NOT RUN]. The visual gate is one AI reviewer (a Claude Code session) looking at stills.

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Create two environments (presenter and upscaler) with torch 2.13.0+cu129 and the pins in each model's requirements; apply the shims in section 5.
2. Download the three repositories at the revisions above; verify hashes.
3. Make a 1824x1024 conditioning still from the avatar (blurred extension for 16:9) and a 16 kHz mono voice file.
4. Run the official demo with the flags in section 4 for 5 segments; confirm 375 frames at 25 fps; time active and paused seconds separately, signalling the whole process tree to pause.
5. Upscale in 4k+1-frame chunks at the 41-frame 1264x720 budget; confirm frames in equal frames out.
6. Compare timings with the table when your pause lines and room temperature match; record them.

The pipeline script is lab code with paths; publish it sanitised before calling this a reproduction.

## 11. Licence and credits

LongCat (Meituan LongCat team, MIT) and SeedVR2 (ByteDance Seed, Apache-2.0) are credited as the model authors; licences as read on the model cards on 2026-11-06 and listed above. Recipe text CC BY 4.0; code MIT. A real person's likeness is not used here; do not adapt the pipeline to a real person without that person's written consent. See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1105 v1: initial write-up from the 15-second qualification run and the smoke tests behind it.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
