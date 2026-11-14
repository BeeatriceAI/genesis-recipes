# Recipe 016: Five image models on one 300 W card: seconds per image, generation against load

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1108 v1; MEASURED FROM 253 SUCCEEDED JOBS; TIMINGS, NO QUALITY CLAIM.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| FLUX.2-klein-4B, 1024x1024, 4 steps | generation 1.2 s; 13.1 s total when the model had to load | governed | [M-01 · MEASURED] |
| Z-Image, 1024x1024, 50 steps | generation 39.7 s; 51.8 s total with load | governed | [M-02 · MEASURED] |
| MOSS-Image-SFT, 1024x1024, 50 steps | generation 31.3 s; 52.7 s total with load | governed | [M-03 · MEASURED] |
| Qwen-Image-2512, 1024x1024, 50 steps | generation 42.2 s; 68.7 s total with load | governed | [M-04 · MEASURED] |
| Qwen-Image-Edit-2511, 1024x1024, 40 steps, reference image required | generation 97.8 s; 118.0 s total with load | governed | [M-05 · MEASURED] |

One limitation next to the headline: these are timings, not quality. The jobs come from a real queue over nine days, mixed campaigns and prompts, and the thermal state of each job was not recorded, so the numbers are medians of what the service did, not a controlled test [M-07 · MEASURED] [M-08 · NOT RUN].

## 1. What this recipe is

A table of how long each image model took on the lab's media card, with the model load separated from generation. Load costs 12-25 s per job unless a resident worker already holds the model, which is the same lesson as recipe 011: for a 4-step model, loading dominates (13.1 s total against 1.2 s of generation).

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro, two NVIDIA RTX PRO 6000 Blackwell Max-Q cards (97,887 MiB each, no NVLink), power limit stock 300 W, clocks stock. The jobs ran on the second card through the image service, with a pause line that was 88/84 C and became 90/87 C on 2026-11-06 [M-07 · MEASURED].
- Driver 570 (open kernel module), CUDA 12.9 wheels. All jobs in bfloat16 [M-06 · REPORTED].

## 3. Models

| Model | Repository | Licence field on the model card (read 2026-11-10; the LICENSE files themselves were not read) | Steps | Reference image |
|---|---|---|---|---|
| FLUX.2-klein-4B | black-forest-labs/FLUX.2-klein-4B, revision e7b7dc27f91deacad38e78976d1f2b499d76a294 | Apache-2.0 | 4 | optional |
| Z-Image | Tongyi-MAI/Z-Image | Apache-2.0 | 50 | unsupported |
| MOSS-Image-SFT | OpenMOSS-Team/MOSS-Image-SFT | Apache-2.0 | 50 | unsupported |
| Qwen-Image-2512 | Qwen/Qwen-Image-2512 | Apache-2.0 | 50 | unsupported |
| Qwen-Image-Edit-2511 | Qwen/Qwen-Image-Edit-2511 | Apache-2.0 | 40 | required |

The revisions of the last four were not recorded in full in the source files: revision pin UNKNOWN for those four [M-06 · REPORTED]. Models with other licences or no verified sample are not in this recipe.

## 4. Job parameters

```
allowed sizes   1024x1024, 1024x1536, 1536x1024
precision       bfloat16 for every job
steps           4 (FLUX.2-klein-4B), 40 (Qwen-Image-Edit-2511), 50 (the other three)
seeds, prompts  not recorded in the timing file
```

## 5. Patches and workarounds

None to the models or the library. The timing file records, per job: model, size, steps, precision, whether a resident worker already held the model, load seconds, generation seconds, total seconds, and whether a reference image was supplied. Prompts and images are not in it [M-07 · MEASURED].

## 6. Results and how they were measured

Method: median of `generation_seconds` (GPU generation alone), median of `load_seconds` over jobs that had to load, and median of `total_seconds` (includes load unless a worker was resident). Medians are recomputed from the file for this recipe; ranges are minimum to maximum generation.

| Model | Size | Jobs | Generation median (range) | Load median (cold jobs) | Total median | Receipt |
|---|---|---|---|---|---|---|
| FLUX.2-klein-4B | 1024x1024 | 10 (2 resident) | 1.2 s (1.1-1.3) | 11.7 s | 13.1 s | [M-01 · MEASURED] |
| FLUX.2-klein-4B | 1024x1536 | 36 (all resident) | 1.5 s (1.4-3.3) | none | 2.0 s | [M-01 · MEASURED] |
| Z-Image | 1024x1024 | 12 (4 resident) | 39.7 s (38.9-43.1) | 12.1 s | 51.8 s | [M-02 · MEASURED] |
| Z-Image | 1024x1536 | 24 (all resident) | 67.0 s (66.3-71.3) | none | 67.4 s | [M-02 · MEASURED] |
| MOSS-Image-SFT | 1024x1024 | 8 | 31.3 s (30.9-33.6) | 21.3 s | 52.7 s | [M-03 · MEASURED] |
| MOSS-Image-SFT | 1024x1536 | 32 | 50.2 s (49.1-52.1) | 21.3 s | 71.8 s | [M-03 · MEASURED] |
| Qwen-Image-2512 | 1024x1024 | 19 | 42.2 s (40.9-45.2) | 25.0 s | 68.7 s | [M-04 · MEASURED] |
| Qwen-Image-2512 | 1024x1536 | 60 | 64.8 s (64.2-68.9) | 25.0 s | 90.3 s | [M-04 · MEASURED] |
| Qwen-Image-Edit-2511 | 1024x1024 | 21 | 97.8 s (94.3-100.5) | 20.1 s | 118.0 s | [M-05 · MEASURED] |
| Qwen-Image-Edit-2511 | 1024x1536 | 8 | 120.7 s (119.8-126.1) | 19.8 s | 140.9 s | [M-05 · MEASURED] |
| Qwen-Image-Edit-2511 | 1536x1024 | 14 | 127.1 s (119.9-128.6) | 20.0 s | 147.3 s | [M-05 · MEASURED] |

Reading it: generation time scales with step count and pixel count. A 50-step model costs 30-70 s per image, the 4-step model about 1.5 s. FLUX.2-klein-4B and Z-Image at 1024x1536 were the mostly or fully resident rows; their total is therefore close to generation. The FLUX.2-klein-4B generation median here (1.2 s) is consistent with the 0.98 s of recipe 011, which was measured with a different harness and without process overhead; the two are not like-for-like [M-01 · MEASURED].

## 7. Thermal behaviour

Not recorded per job. Pause lines changed from 88/84 C to 90/87 C on 2026-11-06, in the middle of the window, so the same model may have been paced differently in different jobs. The ranges in section 6 are the one trace of that in the data [M-07 · MEASURED].

## 8. What did not work or does not follow

- Do not read the table as a speed ranking of quality: a fast model is not a good model, and no quality evaluation was run [M-08 · NOT RUN].
- Qwen-Image-Edit-2511 needs a reference image; its row is an edit workload, not a text-to-image workload, and is not comparable to the other four rows.
- Resident and cold jobs are mixed inside a row for the two models that were sometimes resident.

## 9. Not measured

Image quality or prompt adherence; concurrency (the file does not say how many jobs overlapped); thermal state per job; tokens or steps per second as a separate series; fixed prompts and seeds; cold-disk loads [M-08 · NOT RUN].

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Serve each model with its published pipeline in bfloat16 and a fixed prompt and seed list.
2. Time load, generation and total separately for 20 jobs per size, once cold and once with the model resident.
3. Record temperature, power and the pause line beside the times.
4. Report medians with the job count, not means.

Draft reproduction steps: the lab's job queue and timing export are not published.

## 11. Licence and credits

Recipe text CC BY 4.0, code MIT. Models are credited to Black Forest Labs, Tongyi-MAI, OpenMOSS, and the Qwen team; each is Apache-2.0 as declared on its model card on 2026-11-10. See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1108 v1: initial write-up from the job timing export of 2026-11-06 (253 succeeded jobs, 2026-10-30 to 2026-11-07).

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
