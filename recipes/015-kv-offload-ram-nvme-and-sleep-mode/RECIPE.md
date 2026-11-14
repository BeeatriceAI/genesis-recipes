# Recipe 015: Stop recomputing long prompts: KV offload to RAM and NVMe, and sleep mode instead of a kill

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1107 v1; STAGED ON THE SECOND CARD; production promotion on HOLD.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| Revisit round over 2.7 M prompt tokens (34 long sessions), no offload | 1,687 s, 4% local cache hits, 185.8 kJ of GPU energy per million tokens | governed | [O-01 · REPORTED] |
| Same round, 112 GiB RAM tier | 80 s then 77 s, 96% tier hits, 8.4 / 8.1 kJ per million tokens | governed | [O-02 · REPORTED] |
| Same round, 48 GiB RAM tier + NVMe behind it | 78 s then 77 s, 96% tier hits, 8.4 / 8.2 kJ per million tokens | governed | [O-03 · REPORTED] |
| Same round, tier smaller than the working set (64 GiB RAM) | 1,314 s then 850 s, 27% then 43% hits | governed | [O-04 · REPORTED] |
| First-touch prefill, any configuration | unchanged: about 1,670 s at about 1,620 tokens/s, 300 W | governed | [O-05 · REPORTED] |
| Engine sleep / wake (level 1) | 0.67-0.70 s / 0.74-0.90 s, outputs identical after every wake, against about 55 s to boot after a kill | governed | [O-11 · REPORTED] |
| Promotion to the serving engine | HOLD: prepared and dry-run, never executed | n/a | [O-13 · REPORTED] |

One limitation next to the headline: this is a synthetic replay with idealised revisits (every session comes back and extends the same prefix exactly), one card, one model, one run per configuration, and the lab's real revisit rate is UNKNOWN [O-15 · NOT RUN]. Offload does not make the initial computation of a prompt faster. It removes the recomputation, and the 20x in the table is the favourable case for that.

## 1. What this recipe is

The lab's prompts are long: a mean near 72,000 tokens, with a prefix-cache hit rate near 1.3% in service [O-14 · REPORTED]. The card therefore recomputed huge prefixes it had already computed, at 300 W, for the whole prefill. vLLM 0.32 can park finished KV blocks in CPU RAM (`--kv-offloading-size`) and, with its tiering spec, on NVMe behind the RAM. When a long prompt comes back, the blocks are copied in instead of recomputed.

The second half of the recipe is sleep mode: put an engine to sleep (weights to RAM, KV freed) instead of killing it, so a card shared with image jobs can be handed over in under a second and taken back in under a second.

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro, two NVIDIA RTX PRO 6000 Blackwell Max-Q cards (97,887 MiB each, no NVLink), power limit stock 300 W, clocks stock; AMD Threadripper PRO 9975WX; about 251 GiB RAM; a fast NVMe drive (13.9 GB/s direct read and 8.3 GB/s write, measured). The second card was the staging card.
- Driver 570 (open kernel module), CUDA 12.9 wheels. vLLM 0.32.0+cu129, unpatched engine; the thermal scheduler class from the recipe 008 was on.
- Engine for every run: memory fraction 0.51, concurrency 128, prefill batches of 1,024 tokens. KV pool 452,794 tokens without offload and 451,304 with it [O-01 · REPORTED].

## 3. Model

`Qwen/Qwen3.8-27B-FP8` at revision `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a` (Apache-2.0, read on the model card 2026-11-06), with MTP-2 speculative decoding, fp8 KV cache and native vision on, 262,144-token context. See recipe 007 for the flags.

## 4. Configuration

```
RAM tier, no NVMe: --kv-offloading-size 64                               # GiB of host RAM
RAM + NVMe tier:   --kv-transfer-config '{"kv_connector":"OffloadingConnector","kv_role":"kv_both",
                     "kv_connector_extra_config":{"spec_name":"TieringOffloadingSpec","cpu_bytes_to_use":51539607552,
                     "secondary_tiers":[{"type":"fs","root_dir":"<nvme directory>"}]}}'
sleep mode:        --enable-sleep-mode, environment VLLM_SERVER_DEV_MODE=1 (loopback, behind your authentication),
                   POST /sleep?level=1, POST /wake_up, GET /is_sleeping
```

Housekeeping the run needed (the lab's helper scripts are not published; the designs are in section 8):
1. Remove unmapped offload buffer files from the shared-memory filesystem before every engine start.
2. Keep the NVMe tier directory under a size quota.
3. Let the thermal scheduler accept the native offload connector and keep refusing every other connector [O-10 · REPORTED].

## 5. Patches and workarounds

- vLLM source patches: 0.
- The lab's thermal scheduler refused any external KV connector (a deliberate guard). A staging copy without that refusal ran with the governor forced to pause at 77 C and resume at 74 C: 10 pause and resume cycles while serving through the CPU tier, 0 errors, cold and late outputs identical [O-10 · REPORTED]. The production plan changes the guard to allow the native offload connector alone. Not executed in service.
- Publication gap: the helper scripts (buffer sweep, quota janitor, replay generator, analysis) are not published yet (draft reproduction steps).

## 6. Results and how they were measured

Method: a replay generator makes synthetic token-id prompts (exact lengths, exact shared prefixes, no tokenizer drift). The length mix follows the lab's own measured distribution (about 10% up to 10k tokens, 50% up to 50k, 72% up to 100k, 94% up to 200k). The 34 sessions total 2.70 M tokens (mean 79k, maximum 228k), all share a 6,000-token system prefix, and later turns append about 600 new tokens to the same history. Phases: three probe prompts (20k, 60k, 120k), a first-touch pass over every session at concurrency 8, then two revisit rounds. The GPU KV pool holds just about 450,000 tokens, so most of the working set cannot stay on the card.

### Revisit rounds (same 2.7 M prompt tokens each)

| Config | Revisit wall | Prompt tok/s | Tier hit rate | TTFT p50 / p95 | GPU energy per M tokens | Receipt |
|---|---|---|---|---|---|---|
| No offload | 1,687 s | 1,614 | 4% (local) | 295 / 587 s | 185.8 kJ | [O-01 · REPORTED] |
| RAM 64 GiB | 1,314 s, then 850 s | 2,072 / 3,225 | 27% / 43% | 169 / 98 s | 144.7 / 92.8 kJ | [O-04 · REPORTED] |
| RAM 112 GiB | 80 s, then 77 s | 34,238 / 35,855 | 96% / 96% | 12.6 / 14.9 s | 8.4 / 8.1 kJ | [O-02 · REPORTED] |
| RAM 16 GiB + NVMe | 356 s, then 522 s | 7,643 / 5,257 | 80% / 70% | 44 / 47 s | 39.0 / 56.8 kJ | [O-04 · REPORTED] |
| RAM 48 GiB + NVMe | 78 s, then 77 s | 34,792 / 35,624 | 96% / 96% | 12.8 / 16.0 s | 8.4 / 8.2 kJ | [O-03 · REPORTED] |

Heat, honestly: the card still draws 300 W while it computes and the peak temperature did not change (79-81 C in every configuration). What falls is the time spent at 300 W, from about 500 kJ to about 23 kJ per revisit round, because the card is not recomputing [O-01 · REPORTED] [O-02 · REPORTED] [O-05 · REPORTED].

Other measurements:
- Correctness: three probe prompts (20k, 60k, 120k tokens, 24 output tokens, temperature 0) gave identical text across the baseline, the 112 GiB run and the tier runs, and identical between the cold pass and the later pass served from the tier. First-token log-probabilities differ by up to about 0.1 between separate engine runs; that is run-to-run numeric jitter, not an offload effect [O-06 · REPORTED].
- Persistence: a second run that reused the NVMe directory after an engine restart served the whole 2.7 M-token working set in 66 s at about 41,000 prompt tokens/s with a 97% hit rate [O-07 · REPORTED].
- Cost of a bigger tier: engine start 56 s with no tier, 59-71 s for 8-64 GiB, 103-122 s for 112 GiB (the buffer is allocated and pinned) [O-08 · REPORTED].
- Transfer: 96 GB moved from CPU to GPU in about 78 s, 1.2 GB/s on average, far under both the PCIe link and the drive's measured read rate. Where the limit sits in the engine is UNKNOWN [O-09 · REPORTED].
- Memory per token: 33-34 KiB (16 full-attention layers, 4 KV heads, 256 dimensions, fp8, plus linear-attention state); a first-touch pass wrote 93 GB [O-09 · REPORTED].

### Sleep mode

Method: a staged engine with sleep enabled, three level-1 cycles and one level-2 cycle. After each wake: one text answer, one image answer (a red square) and one 30k-token prompt, all at temperature 0.

| Step | Measured | Receipt |
|---|---|---|
| Level 1 sleep (weights to RAM, KV freed) | 0.67-0.70 s; the initial call took 7.8-10.8 s | [O-11 · REPORTED] |
| Level 1 wake | 0.74-0.90 s; the initial request after wake took 0.07 s | [O-11 · REPORTED] |
| Card memory | 73,939 MiB awake, 27,878 MiB asleep | [O-11 · REPORTED] |
| Level 2 sleep / total wake | 0.14 s / 4.3-4.7 s (weights reload from the page cache) | [O-11 · REPORTED] |
| Outputs after every wake | text, image and long-prompt answers identical in 3 of 3 level-1 cycles and the level-2 cycle | [O-11 · REPORTED] |
| With a 32 GiB CPU tier | works; the tier buffer survives sleep; outputs identical | [O-11 · REPORTED] |

A kill-and-boot hand-over costs about 55 s of boot plus a waiting period, and drops the RAM tier [O-11 · REPORTED].

## 7. Thermal behaviour

- Peak 79-81 C on the staging card in every configuration, power 291-300 W on average [O-01 · REPORTED] [O-02 · REPORTED] [O-03 · REPORTED].
- Governor forced to 77 C / 74 C: 10 pause and resume cycles, 0 errors [O-10 · REPORTED].
- The synthetic replay is cooler than the serving card's real load; the numbers say nothing about the serving card's temperature.

## 8. What did not work or did not help

1. The shared-memory filesystem caps the RAM tier. It is half of RAM (126 GiB) and shared with every tenant: tiers of 128 and 180 GiB refused to start, 112 GiB worked. Remounting it is a system setting and was not done [O-12 · REPORTED].
2. The NVMe tier leaks its RAM buffer when an engine is killed (the plain CPU spec removes the file at creation; the tiering spec does not), and the next start fails with a "required, free" error. A sweep before every start removes unmapped buffers [O-12 · REPORTED].
3. The NVMe tier has no capacity limit or eviction in vLLM 0.32.0. A quota janitor held a 12 GiB quota at 10.8-11.8 GiB while serving with 0 engine errors; deleting files while the engine loads blocks from them is UNKNOWN [O-12 · REPORTED].
4. A tier smaller than the working set helps partly: 64 GiB of RAM for a 93 GB working set cut round time 22% to 50%, not 20x [O-04 · REPORTED].
5. PCIe is not the bottleneck in this replay (1.2 GB/s on average) [O-09 · REPORTED].
6. Pinned RAM for tiers shrinks the page cache that holds image-model weights; a 46 GB reload from a cold cache costs about 4-7 s. A cost, not a wall.
7. A warm-cache plan for the language-model weights gains nothing: they are already 100% in page cache and the 52-58 s boot is compile, graph capture and setup, not disk.

## 9. Not measured

The lab's real revisit rate and working-set size; a second run of each configuration (one run each, no variance); LMCache (not installed, not tried); sleep mode on the second language model; deleting tier files during a load; any long-horizon output-quality evaluation; any serving-card measurement [O-15 · NOT RUN].

## 10. Reproduction steps (draft, one machine)

1. Start an engine with the pins above and no tier; replay your own long-prompt sessions twice and record the revisit round time, TTFT, hit rate and GPU energy.
2. Add the RAM tier, sized to your working set, and repeat. Expect the cold pass to be unchanged.
3. Add NVMe behind a smaller RAM tier. Put a size quota on the directory and a buffer sweep before every start.
4. Compare text hashes between the cold pass and the pass served from the tier at temperature 0.
5. Start a second engine with sleep mode on, run three sleep and wake cycles, and compare answers before and after each wake.
6. Publish energy per million tokens, peak temperature and your hit rate beside the times.

Draft reproduction steps: the replay generator, analysis script, sweep and janitor are not published yet.

## 11. Licence and credits

Recipe text CC BY 4.0, code MIT. Engine: vLLM, Apache-2.0 (read on its repository 2026-11-06). Model: Qwen3.8-27B-FP8, Apache-2.0 (model card, 2026-11-06). See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1107 v1: initial write-up from the 2026-11-07 staging runs and the production plan (dry-run).

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; where a licence line below says "check upstream" we have not verified it. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools and reviewed by a human before release.
Written by AI agents and reviewed by a human before publishing.
