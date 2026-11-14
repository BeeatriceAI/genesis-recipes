# Recipe 007: Qwen3.8-27B-FP8 on one RTX PRO 6000 Max-Q: 262,144 context, native vision, MTP-2 + fp8 KV, 1,024-token prefill batches, thermal scheduler

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1105; v2 2026-1106.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

> **Warning: one lab's settings, not a recommendation.** The temperatures, pause lines and power figures in this recipe are guardrails this lab chose for its own cooling and room. They were not checked against a vendor limit, depend on your cooling and ambient temperature, and may void a warranty. Do not copy them; use your vendor's documented limits.

> **Not reproducible yet:** the code this recipe depends on is not published in this repository, and the launch or steps below cannot run as written.

## Headline

Read with recipe 006: it holds the per-request decode speed measured on the serving card from live counters (19.1 tokens/s median, ESTIMATE, not throughput). The STAGING figures below are short harness-paced runs on a different card and are not comparable with it. Per recipe 006 the per-request decode median on the primary server was 19.1 tokens/s over 2026-11-08 to 2026-11-13, but which serving profile that process ran is UNKNOWN, so this recipe's production speed stays UNKNOWN (no clean-window run).

| What | Number | Run state | Receipt |
|---|---|---|---|
| Promotion of vision + MTP-2 + fp8 KV in one restart | PASS, ready after 171.2 s; 1 request undrained; no rollback | n/a | [Q-24 · REPORTED] |
| KV cache pool on the serving card after the restart | 464,709 tokens (1.77x of 262,144), up from 319,800 | governed | [Q-25 · REPORTED] [Q-03 · REPORTED] |
| Post-restart: 1-token probe, red/blue image through the production endpoint, MTP counters live | PASS, 0.65 s for the probe | n/a | [Q-26 · REPORTED] |
| Lab post-restart check suite | 31 of 31 (reported from the lab record; raw output not found) | n/a | [Q-27 · REPORTED] |
| Vision fixture on production (error screenshot) | PASS, 6.08 s | n/a | [Q-28 · REPORTED] |
| Decode speed on production | UNKNOWN. One loaded short request: about 26.7 tokens/s, INCONCLUSIVE | n/a | [Q-29 · REPORTED] |
| STAGING decode, same flags, second card, 1 / 4 / 16 streams | 92.5 / 329.9 / 930.9 tokens/s aggregate | harness-paced, short sample | [Q-30 · REPORTED] |
| STAGING decode before vision (language-model-only), same flags | 88.5 / 312.1 / 911.0 tokens/s | governed, short sample | [Q-04 · REPORTED] |
| Same model without MTP and fp8 KV (reference) | 42.8-43.9 / 120.5-123.8 / 453-608 tokens/s | ungoverned, two boots | [Q-05 · REPORTED] |
| 258,886-token retrieval | STAGING: 324.8 s. Production after promotion: not run | harness-paced | [Q-30 · REPORTED] [Q-31 · NOT RUN] |

One limitation next to the headline: the promotion is measured, the speed gain on the serving card is not. Every tokens-per-second figure above except the 26.7 is a staging figure from short samples on a second card with nothing else attached. The one production speed reading is a loaded 5-token request that came out slower than the previous profile's chat throughput [Q-29 · REPORTED]. Do not read 92.5 or 930.9 as what a client sees through the gateway.

## 1. What this recipe is

A dense 27-billion-parameter hybrid model (16 full-attention and 48 linear-attention layers) served from one 96 GB workstation card at its native 262,144-token context, with four changes layered on a working profile: native image and video input, speculative decoding with the model's own multi-token-prediction head (2 draft tokens), an fp8 KV cache, and a custom vLLM scheduler class that pauses scheduling at a temperature line. Prefill batches stay at 1,024 tokens on purpose, so every scheduler step is short and a thermal pause can take effect between steps.

Status: staged on the lab's second card with the same flags and memory fraction as the serving card, then promoted to the serving card on 2026-11-05 in one restart [Q-24 · REPORTED]. v1 of this recipe, written before the promotion, said STAGED [Q-22 · REPORTED]. The speed numbers in sections 6 and 7 are still staging numbers; what the promotion changed is the memory and the checks in section 6.1.

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro. Two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition cards (97,887 MiB visible each, compute capability 12.0, no NVLink), AMD Threadripper PRO 9975WX, about 251 GiB RAM, Ubuntu 24.04.
- Power and clocks: stock. The power limit is the card default of 300 W and was not changed; clocks are stock. There is no artificial clock cap in this recipe.
- Driver 570 (open kernel module); CUDA 12.9 wheels run through minor-version compatibility.
- vLLM 0.32.0+cu129 (release wheel, unpatched), torch 2.13.0+cu129, transformers 5.19.0, FlashInfer 0.7.0.post1 with the sm120f ahead-of-time cache, Triton 3.7.1, Python 3.12.
- Attention backend: Triton (`--attention-backend TRITON_ATTN`). The default FlashAttention-2 path fails on this card and driver ("unsupported toolchain").

## 3. Model

- `Qwen/Qwen3.8-27B-FP8`, revision `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`, Apache-2.0 (card front matter). Base model `Qwen/Qwen3.8-27B`, architecture Qwen3_5ForConditionalGeneration, loaded with its vision tower (v1 loaded language-model-only). The checkpoint ships the MTP head (`mtp.safetensors`).
- Weights in memory: 27.99 GiB with the MTP head, 27.55 GiB without [Q-20 · REPORTED].

## 4. Launch

```
# thermal pause settings (lab guardrails, see the warning at the top): pause 90 C, resume 86 C, hard stop 91 C, 1 C margin,
# 120 s maximum pause, 4 confirmation samples, 2 s minimum hold; the card is selected by its UUID
PYTHONPATH=<dir containing the thermal scheduler module> <thermal pause settings as environment variables> \
python -m vllm.entrypoints.cli.main serve Qwen/Qwen3.8-27B-FP8 --revision 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a \
  --served-model-name <name> --tensor-parallel-size 1 --attention-backend TRITON_ATTN \
  --max-model-len 262144 --max-num-seqs 64 --gpu-memory-utilization 0.51 --max-num-batched-tokens 1024 \
  --limit-mm-per-prompt '{"image":16,"video":2}' --mm-encoder-attn-backend TORCH_SDPA --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3 \
  --default-chat-template-kwargs '{"enable_thinking":false}' \
  --scheduler-cls <thermal scheduler module>.ThermalScheduler --no-async-scheduling \
  --speculative-config '{"method":"mtp","num_speculative_tokens":2}' --kv-cache-dtype fp8
```

Bind to loopback and put authentication in front of it. v2 removes `--language-model-only` and adds the two vision flags: the vision encoder's default attention path fails on this card and driver (a PTX version error), and `--mm-encoder-attn-backend TORCH_SDPA` fixes it; the decoder's `--attention-backend TRITON_ATTN` does not cover the encoder. The memory fraction 0.51 leaves room for other resident models on the serving card; on an exclusive card a larger fraction gives a larger KV pool (70% gave 545,105 tokens with MTP alone [Q-08 · REPORTED]).

## 5. Patches and workarounds

- vLLM source patches: 0. The engine is the release wheel.
- One added module, the thermal scheduler (about 290 lines), loaded with `--scheduler-cls`. It subclasses the vLLM scheduler and sets the token budget to zero while the card is hot (see the recipe 008 for the design). Two guards remain: it refuses async scheduling and more than one in-flight batch.
- The module refused speculative decoding until this staging work lifted that guard after reading the vLLM 0.32.0 scheduler code [Q-18 · NOT RUN]. The unit tests include a zero-budget hold with two drafts in flight.
- Publication gap: the lab's copy of the module allow-lists two card identifiers; the public copy must read the identifier from the environment instead. Not yet done, so this recipe is not yet a one-command reproduction (draft reproduction steps).

## 6. Results and how they were measured

Method for decode: 256 output tokens per request, temperature 0, short prompts, loopback client, 2 / 8 / 16 requests at 1 / 4 / 16 concurrency, aggregate tokens over wall time. Method for long prompts: three random key-value phrases planted at three positions in filler text, ask for all three back, record wall time and server-reported prompt tokens.

### Decode

| Config | 1 stream | 4 streams | 16 streams | Receipt |
|---|---|---|---|---|
| Reference: no MTP, default KV, 70% fraction, boot 1 | 42.8 | 120.5 | 453.2 | [Q-05 · REPORTED] |
| Reference, boot 2 | 43.9 | 123.8 | 608.4 | [Q-05 · REPORTED] |
| fp8 KV alone | 43.4 | 138.9 | 371.3 | [Q-09 · REPORTED] |
| b12x linear backend | 44.1 | 119.4 | 515.9 | [Q-21 · REPORTED] |
| MTP-1 alone (acceptance 0.875) | 67.5 | 258.7 | 841.9 | [Q-08 · REPORTED] |
| MTP-2 alone (acceptance 0.797) | 84.2 | 297.1 | 871.4 | [Q-08 · REPORTED] |
| STAGING: MTP-2 + fp8 KV + scheduler, language-model-only, 51% | 88.5 | 312.1 | 911.0 | [Q-04 · REPORTED] |
| STAGING: the promoted flags (adds vision) | 92.5 | 329.9 | 930.9 | [Q-30 · REPORTED] |

Derived: about 2.0x at one stream and 2.6x at four against the reference; 1.5x to 2.0x at 16, depending on which reference boot is used [Q-06 · REPORTED]. The configurations differ in memory fraction and scheduler, so this is not a controlled A/B. Single runs; differences under about 15% at 16 streams are noise [Q-05 · REPORTED].

Sustained: sixteen back-to-back streams for six minutes at the 300 W limit gave 1,373 requests and 350,436 output tokens with no errors, 810-1,100 tokens/s per ten-second bucket and a mean near 973 tokens/s; acceptance over that load was 0.76 [Q-17 · REPORTED] [Q-07 · REPORTED].

### 6.1 Production receipts (after the promotion)

| Check | Result | Receipt |
|---|---|---|
| Restart | PASS, readiness 171.2 s, 1 request undrained when the 120 s drain window closed | [Q-24 · REPORTED] |
| KV pool | 464,709 tokens (1.77x at full context), previously 319,800 | [Q-25 · REPORTED] |
| 1-token probe; red and blue image through the production endpoint; draft counters | PASS; 0.65 s; 4 drafted, 4 accepted | [Q-26 · REPORTED] |
| Lab post-restart suite | 31 of 31, reported | [Q-27 · REPORTED] |
| Vision fixture (error screenshot) | PASS, 6.08 s; the 1x1 control answered "I" | [Q-28 · REPORTED] |
| Decode | UNKNOWN; one loaded short request about 26.7 tokens/s, INCONCLUSIVE | [Q-29 · REPORTED] |
| 258,886-token retrieval | not run | [Q-31 · NOT RUN] |
| Image input | inline data URIs (no remote URLs); image size is bounded before the engine; 16 images and 2 videos per prompt | [Q-32 · REPORTED] |

The formal 12-case regression did not run after the promotion (HOLD) [Q-28 · REPORTED]. That is the reason the production speed in this recipe is UNKNOWN.

### Memory

| Config | KV pool | Receipt |
|---|---|---|
| PRODUCTION after promotion (vision + MTP-2 + fp8 KV, 51%) | 464,709 tokens | [Q-25 · REPORTED] |
| Vision alone, no MTP, default KV (STAGING) | 279,056 tokens: FAIL against the 303,810 floor | [Q-33 · REPORTED] |
| Previous serving profile, 51% | 319,800 tokens | [Q-03 · REPORTED] |
| Staged MTP-2 + fp8 KV, language-model-only, 51%, warm compile cache | 536,203 tokens | [Q-01 · REPORTED] |
| Staged, 51%, cold compile cache | 469,178 tokens | [Q-02 · REPORTED] |
| fp8 KV alone, 70% | 1,120,891 vs 571,950 for default KV | [Q-09 · REPORTED] |

### Long prompts

| Prompt tokens | Config | Wall time | Rate (derived) | Receipt |
|---|---|---|---|---|
| 258,886 | staged, harness-paced, 87 pauses | 346.75 s | 747 tokens/s | [Q-10 · REPORTED] [Q-15 · REPORTED] |
| 258,886 | staged, no scheduler class, 35 pauses | 305.74 s | 847 tokens/s | [Q-11 · REPORTED] [Q-15 · REPORTED] |
| 258,886 | current profile, production endpoint, 2026-10-29 | 468.94 s | 552 tokens/s | [Q-12 · REPORTED] |
| 199,888 | staged, 24 pauses / 6 pauses (two runs) | 191.79 s / 168.44 s | 1,042 / 1,187 tokens/s | [Q-13 · REPORTED] |
| 160,045 | fp8 KV, no MTP, ungoverned | 125.88 s | 1,271 tokens/s | [Q-14 · REPORTED] |
| 160,045 | default KV, no MTP, ungoverned | 169.59 s | 944 tokens/s | [Q-14 · REPORTED] |

The rates divide prompt tokens by the whole request wall time (including 66 output tokens and any pauses), so they are wall-clock averages, not a prefill kernel rate, and they fall as the prompt grows. The staged probes carry external pauses that were not timed separately. The 468.94 s line is a different card state, shared with other resident models and other jobs, under lower pacing lines: do not read the three 258,886-token rows as a like-for-like speed-up. An identical prompt repeated from the prefix cache returns in 0.55-0.63 s [Q-14 · REPORTED]; that is cache reuse, not prefill speed.

### Quality gates

- Twelve-case fixture (format, arithmetic, tool call, needle retrieval at 8K and 32K, over-context rejections): 11 of 12 at three samples. The miss is an arithmetic case that the serving profile answers identically [Q-16 · REPORTED]. Tool-call fixture 3 of 3.
- The engine warns that the fp8 KV cache runs with scale 1.0 and uncalibrated attention scales because the checkpoint ships none [Q-19 · REPORTED]. The fixtures pass, but they do not measure fp8 attention quality; no perplexity or long-context quality comparison was run.

## 7. Thermal behaviour

- In-engine scheduler lines: pause 90 C, resume 86 C, latch 91 C or 1 C thermal margin, debounced over four samples. The card's own hardware protections are untouched; we did not verify their values against a vendor document, so none are published here.
- While staging, an external test harness paused the engine at 88 C and resumed at 84 C so the scheduler stayed a backstop. The staging card peaked at 88 C during the long probes and 86 C during decode, with 111 pauses totalling 136.6 s in the governed run, longest 2.1 s [Q-23 · REPORTED] [Q-10 · REPORTED].
- Under six minutes of 16-stream decode with no harness pacing, the card rose from 73 C to 86 C in a minute and then sat at 87-88 C, monitor peak 89 C. The 90 C line was not reached, so the scheduler never held [Q-17 · REPORTED].
- Production temperature after the promotion was not recorded for this recipe.
- Not observed: a real hold-and-resume with MTP drafts pending. It is covered by a unit test and a code trace, and is unknown live [Q-18 · NOT RUN].

## 8. What did not work or did not help

- Initial boot with the scheduler as it stood: refused speculative decoding at start-up (a deliberate guard); fixed after code inspection [Q-18 · NOT RUN].
- The b12x linear backend for the fp8 weights: no gain, slower to start (126 s) [Q-21 · REPORTED].
- fp8 KV alone does not speed up decode; its benefit is memory and some cold-prefill time [Q-09 · REPORTED] [Q-14 · REPORTED].
- MTP-1 is slower than MTP-2 at 1 and 4 streams despite higher acceptance [Q-08 · REPORTED].
- A prefix-caching flag changes nothing; it is already on [Q-14 · REPORTED].
- Vision alone did not fit: with no MTP and default KV the pool dropped to 279,056 tokens, under the floor. The combined profile fits because fp8 KV and MTP-2 give the memory back [Q-33 · REPORTED].
- The initial production speed reading came out slower than the previous profile (about 26.7 against 46.4 tokens/s). It is confounded and tiny, and it is the reason this recipe does not claim a production speed-up [Q-29 · REPORTED].
- The initial staging run was cut at 85 s when the other card reached 90 C under another job; the harness was corrected [Q-23 · REPORTED].

## 9. Not measured

Long-run (hours) stability; output quality of fp8 attention; vision output quality beyond fixtures; throughput on the production endpoint after promotion (UNKNOWN, a clean-window re-baseline is open [Q-29 · REPORTED]); the 258,886-token probe on the promoted production profile [Q-31 · NOT RUN]; hold-and-resume with drafts; 32-stream or higher concurrency with this profile; any comparison on a cooler or hotter room. The pauses cost time: the long probes would finish sooner on a card that never paused, and by how much was not measured.

## 10. Reproduction steps (draft: not reproducible until the code is published)

0. Read the v1 file for the language-model-only variant if you do not want vision; its flags differ by the two vision options.
1. Install the unpatched vLLM 0.32.0 CUDA 12.9 wheel in a fresh environment with the pins above; confirm the card is visible and Triton attention starts a small model.
2. Download the model at the revision above and check the file hashes against the Hugging Face listing.
3. Add the scheduler module (draft reproduction steps: the sanitised module is not in this repository yet) and start with the command in section 4 on an otherwise idle card.
4. Wait for the log line giving the KV pool; compare with [Q-25 · REPORTED].
5. Run the decode sample (the decode sample script is not included in this repository) for 1, 4 and 16 streams three times each; compare medians with the staging rows, expecting a spread of 15% at 16 streams. Publish your own number: the production one is UNKNOWN here.
6. Run the retrieval probe at 200K tokens; compare against [Q-13 · REPORTED] when your pacing lines match.
7. Record the clock state, power limit and temperature next to every number you publish.

## 11. Licence and credits

Model: Apache-2.0 (Qwen; read on the model card on 2026-11-06). Engine: vLLM, Apache-2.0 (read on its repository on 2026-11-06), unmodified. Recipe text CC BY 4.0; code MIT. Trademark terms of the engine and the model family were not reviewed by a lawyer: see LICENSE-DOCS.md. Thanks to the vLLM maintainers for the release notes that made the scheduler code trace possible.

## 12. Changelog

- 2026-1105 v1: initial write-up from the lab's staging receipts. Status STAGED.
- 2026-1106 v2: the profile was promoted on 2026-11-05 (21:12Z) with native vision added to the flags. Production receipts added (Q-24 to Q-33): restart, KV pool 464,709, post-restart checks, vision fixture. Speed stays labelled STAGING; production decode is UNKNOWN. Launch command changed: `--language-model-only` removed, `--limit-mm-per-prompt` and `--mm-encoder-attn-backend TORCH_SDPA` added. No v1 number was withdrawn; v1 numbers are relabelled STAGING.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
