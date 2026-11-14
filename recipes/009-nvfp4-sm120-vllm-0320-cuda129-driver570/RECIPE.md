# Recipe 009: NVFP4 on SM120 with vLLM 0.32.0 and CUDA 12.9: what works with driver 570

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1105 v1; WORKS FOR A DENSE 8B MODEL IN A SMOKE TEST; 27B and quantisation NOT DONE.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

> **Warning: one lab's settings, not a recommendation.** The temperatures, pause lines and power figures in this recipe are guardrails this lab chose for its own cooling and room. They were not checked against a vendor limit, depend on your cooling and ambient temperature, and may void a warranty. Do not copy them; use your vendor's documented limits.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| vLLM 0.32.0 (CUDA 12.9 wheels) on driver 570 | runs; NVFP4 dense model serves | measured | [N-01 · REPORTED] [N-06 · REPORTED] |
| vLLM 0.33.0 (CUDA 13.0 wheels, torch 2.14) on driver 570 | does not start: "driver too old" | measured | [N-01 · REPORTED] |
| NVFP4 8B decode, 1 / 4 / 16 streams, default backend | 130.4 / 436.9 / 487.8 tokens/s | ungoverned, short sample | [N-06 · REPORTED] |
| Same, b12x linear backend | 173.6 / 476.9 / 615.9 tokens/s | ungoverned, one run | [N-07 · REPORTED] |
| Local NVFP4 quantisation of the 27B | failed 3 times (Triton "device kernel image is invalid"), no checkpoint | measured | [N-11 · REPORTED] |

One limitation next to the headline: the model is an 8B checkpoint from the vendor, at 8192 context and at most 4 sequences in flight; the 27B NVFP4 checkpoint was not run, and there is no accuracy comparison against a higher-precision baseline, so nothing here says what NVFP4 costs in quality.

## 1. What this recipe is

A record of what runs and what does not when you try NVFP4 (4-bit floating-point weights and activations for the linear layers) on an RTX PRO 6000 Blackwell Max-Q (compute capability 12.0) with the driver the machine already had, 570, and the newest vLLM that driver can run, 0.32.0 built for CUDA 12.9. It lists the kernel choices, the two environment workarounds that were needed, the speed of each linear backend on a dense 8B model, and the failures when we tried to produce our own NVFP4 checkpoint.

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro, two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition cards (97,887 MiB each, no NVLink); tests ran on the second card; power limit stock 300 W, clocks stock.
- Driver 570, open kernel module, reports CUDA 12.8; the system compiler is the 12.8 toolkit; the CUDA 12.9 wheels run through minor-version compatibility [N-02 · REPORTED].
- vLLM 0.32.0+cu129 (release wheel, checksum matched the release listing), torch 2.13.0+cu129, transformers 5.19.0, FlashInfer 0.7.0.post1 with the cubin and sm120f ahead-of-time cache, b12x 1.5.1, Triton 3.7.1, Python 3.12 [N-14 · REPORTED].
- NVIDIA Model Optimizer 0.48.0 in a second environment (transformers 5.18.0, because it pins below 5.19) for quantisation attempts.

## 3. Model

- `nvidia/Qwen3-8B-NVFP4`, revision `ccd10a893cbca613259517c3efe08e151ddf2b8e`, Apache-2.0 (card front matter); 5.98 GiB in memory; the safetensors hashes matched the repository listing.
- Not run: the vendor's `nvidia/Qwen3.8-27B-NVFP4` (Apache-2.0, 21.95 GB). Its card claims accuracy within about 1.5 points of BF16 on six tests and says it was tested on a datacentre part; that is a publisher claim, not verified here [N-10 · SOURCED].

## 4. Launch

```
FLASHINFER_CUDA_ARCH_LIST=12.0f \
python -m vllm.entrypoints.cli.main serve nvidia/Qwen3-8B-NVFP4 --revision ccd10a893cbca613259517c3efe08e151ddf2b8e \
  --served-model-name <name> --tensor-parallel-size 1 --attention-backend TRITON_ATTN \
  --max-model-len 8192 --max-num-seqs 4 --gpu-memory-utilization 0.3 --max-num-batched-tokens 8192 \
  --default-chat-template-kwargs '{"enable_thinking":false}' \
  --no-enable-flashinfer-autotune
# variants: add --linear-backend b12x   or   --linear-backend cutlass
```

## 5. Patches and workarounds (the useful part)

1. `FLASHINFER_CUDA_ARCH_LIST=12.0f`: FlashInfer asks the system compiler for its version and rejects SM12.x below 12.9; this tells it to use the ahead-of-time sm120f kernels in the wheel [N-05 · REPORTED].
2. `--no-enable-flashinfer-autotune`: with the default 8192-token buckets the autotune warm-up grew to 92 GiB, ran for 3.7 minutes and the start exited with rc=1 after 225 s; with the flag, start-up took 25 s [N-05 · REPORTED].
3. `--attention-backend TRITON_ATTN`: the default FlashAttention-2 path fails on this card and driver ("unsupported toolchain"); the vision tower needed `--language-model-only` for the same reason as of 2026-11-04; recipe 007 (version 2) later fixed it with `--mm-encoder-attn-backend TORCH_SDPA` and runs vision [N-04 · REPORTED].
4. Pin torch 2.13.0+cu129 and torchcodec 0.16.0+cu129: an unpinned resolver picked a CUDA 13 build of torchcodec that cannot load.
5. vLLM source patches: 0.

## 6. Results and how they were measured

Method: 256 output tokens per request, temperature 0, short prompts, 2 / 8 / 16 requests at 1 / 4 / 16 concurrency, aggregate tokens over wall time, one run per variant, loopback client. At most 4 sequences run at once (`--max-num-seqs 4`), so the 16-stream column is queue-limited.

| Linear backend | 1 stream | 4 streams | 16 streams | Start-up | Receipt |
|---|---|---|---|---|---|
| FlashInfer CUTLASS (auto-selected default) | 130.4 | 436.9 | 487.8 | 54 s | [N-06 · REPORTED] |
| b12x (native SM120 kernel) | 173.6 | 476.9 | 615.9 | 42 s | [N-07 · REPORTED] |
| CUTLASS | 122.3 | 401.5 | 431.5 | 36 s | [N-08 · REPORTED] |

Derived: b12x is about 33% faster at one stream and 26% at 16 than the default. These are single runs on a 4-sequence engine; repeat before relying on them. Kernel capability check on the real card: b12x, FlashInfer b12x, FlashInfer CUTLASS, CUTLASS, cuDNN, TensorRT-LLM and Marlin report supported; the CuTe DSL backend does not (it needs a data-centre architecture) [N-03 · REPORTED]. A capability check is not a speed or correctness result.

Quality gate: a five-case answer-format fixture; 4 of 5 pass in the default and the b12x backends. The miss is the same arithmetic case in both (the reply "1234 + 8765 = 9999" is correct but not in the expected format). This is a smoke test of the stack. No BF16 or FP8 comparison of this 8B model was run, so no accuracy-loss claim follows [N-09 · REPORTED].

For scale: the 27B FP8 model with one MTP draft token gave 72.2 tokens/s against 43.3 plain on a maximally predictable counting prompt; that is an upper bound, and recipe 007 has the real figures [N-12 · REPORTED].

## 7. Thermal behaviour

Short runs; the card stayed under 75 C in the initial start attempt and the smoke tests used a small fraction of the 300 W limit (about 100 W in the 8B smoke). No pauses and no stop lines fired. Nothing here says how NVFP4 behaves under a sustained load.

## 8. What did not work

- vLLM 0.33.0: the release wheels are built for CUDA 13.0 alone and need torch 2.14; torch 2.14.0+cu130 refuses to initialise on driver 570 ("driver too old"). A driver of 580 or newer is needed, which means a root install and a reboot; we have not done it and we do not claim that it works [N-01 · REPORTED].
- NVFP4 start without the autotune flag: 92 GiB held, rc=1 [N-05 · REPORTED].
- Local NVFP4 quantisation of the 27B model with Model Optimizer 0.48.0 and 8 calibration samples: three attempts died in the calibration forward pass with "Triton Error [CUDA]: device kernel image is invalid" raised from a PyTorch-native kernel, 15-23 s in, with 54 GB in use; a fourth attempt failed on a launcher path error (the script imports its siblings by directory, and isolated mode removes that directory from the path). No NVFP4 checkpoint was produced and the cause of the Triton error is not isolated [N-11 · REPORTED].
- The CUTLASS linear backend: slowest of the three [N-08 · REPORTED].

## 9. Not tested

NVFP4 mixture-of-experts models (community reports of broken kernels on this architecture exist; not checked here), the NVFP4 KV cache, long context, the 27B model, accuracy against a higher-precision baseline, and driver 580 or newer [N-13 · NOT RUN]. Repeats of the backend comparison.

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Confirm driver 570 and torch.cuda sees the card with compute capability 12.0.
2. Install the vLLM 0.32.0 CUDA 12.9 wheel and the pins above; install b12x 1.5.1.
3. Download `nvidia/Qwen3-8B-NVFP4` at the revision above; check hashes.
4. Start with the command in section 4; expect a ready server in under a minute.
5. Run the decode sample for each linear backend three times; compare medians with the table.
6. Run your own accuracy check against a BF16 copy before using NVFP4 for anything that matters.

## 11. Licence and credits

Model: Qwen3-8B-NVFP4 by NVIDIA (derived from Qwen3-8B), Apache-2.0 (declared on the model card, read 2026-11-06). Engine: vLLM, Apache-2.0; FlashInfer, Apache-2.0; NVIDIA Model Optimizer, Apache-2.0 (each read on its repository 2026-11-06). The licence of b12x was not verified: check upstream. Recipe text CC BY 4.0; code MIT. See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1105 v1: initial write-up from the dense-8B smoke tests, the three backend runs and the failed quantisation attempts.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
