# Text-model serving numbers from a lab's own traffic: TTFT, per-request decode speed, cache rate, with raw files

Recipe 006 draft v0.2 (2026-1113; v0.1 had no hardware section) · status: MEASURED FROM LIVE COUNTERS; NO DESIGNED LOAD TEST · times are UTC

Every number traces to a raw file in `raw/`, named in square brackets (paths are inside this recipe's `raw/` folder). Hashes are in `raw/SHA256SUMS.txt`; `raw/DERIVED.md` says which files were changed and how.

## Headline

| What | Number | Run state | Raw file |
|---|---|---|---|
| Traffic served since process start (morning read) | 1.72 B prompt tokens, 4.82 M generated tokens, 13,651 requests: 13,624 stop, 27 length, 0 abort, 0 error | n/a | [am/qwen_primary_live_summary.derived.json] |
| Prompt tokens served from the prefix cache | 97.5% | n/a | [am/qwen_primary_live_summary.derived.json] |
| TTFT (ESTIMATE) | p50 2.99 s, p90 6.35 s | n/a | [am/qwen_primary_live_summary.derived.json] |
| Queue wait (ESTIMATE) | p50 0.15 s, p90 0.27 s | n/a | [am/qwen_primary_live_summary.derived.json] |
| End to end (ESTIMATE) | p50 12.3 s, p90 45.6 s | n/a | [am/qwen_primary_live_summary.derived.json] |
| Decode speed per request (ESTIMATE) | 19.1 tokens/s median, 12.2 for the slowest decile | n/a | [am/qwen_primary_live_summary.derived.json] |
| Server throughput averaged since start (ESTIMATE) | 12.1 tokens/s, idle time included | n/a | [pm/qwen_primary_live_summary.json; pm/qwen_primary_windows.json; pm/qwen_primary_hourly.csv] |

Read times: the headline is the morning read, whose exact time is UNKNOWN (the file does not store it). The afternoon read was taken at 2026-11-13 22:06 UTC [pm/qwen_primary_live_summary.json].

One limitation next to the headline: this is the lab's own mix of long agent contexts read from live counters, not a designed test; decode speed here is what one request experiences, not what the server can sustain, and the percentiles are bucket-interpolated estimates.

## 1. What this recipe is

A record of what one local text-model server did under the studio's real traffic for about five days, taken from its own metrics and from a minute monitor. It is a measurement of an ordinary week, not an experiment, and the raw files let anyone recompute every figure here from `raw/`. TTFT means the time from request arrival to the model's initial output token.

## 2. Where it ran

Hardware:

- Workstation: Digital Storm Aventum Pro.
- GPUs: 2x NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition, 97,887 MiB each, no NVLink. Power limit stock (300 W; one-minute samples were transiently above it), clocks stock.
- CPU: AMD Threadripper PRO 9975WX. RAM: about 251 GiB. OS: Ubuntu 24.04, driver 570 (open kernel module).
- GPU 0 is the card the text-model server runs on; GPU 1 carries image, video and other windows. Other work that ran on GPU 0 during these hours is not recorded. These specifications come from the lab's hardware notes, not from the raw files below; the raw files say just GPU 0 and GPU 1.

- The server is the studio's primary text-model server on GPU 0. Its serving profile and engine version for this process are not recorded in the files, so they are UNKNOWN.
- The process start was 2026-11-08 18:19 ET (23:19 UTC; US daylight time had ended on 2026-11-01). Counters are cumulative from then; the minute-monitor files start on 2026-11-12 00:00 UTC [am/qwen_primary_hourly.csv].
- GPU 1 in the temperature table ran the image, video and other windows [pm/gpu_hourly.csv].

## 3. Model

The text model is Qwen3.8-27B-FP8 (Apache-2.0 on its model card, read 2026-11-06). The files do not record the model revision this process loaded, so the revision is UNKNOWN. No model was loaded or changed for this recipe.

## 4. How the numbers were taken

```
morning read   : metrics scrape of the server, counters since process start   (am/qwen_primary_live_summary.derived.json)
minute monitor : one sample a minute, summarised per hour and per window      (am/qwen_primary_hourly.csv, am/qwen_primary_latency_percentiles.csv, pm/gpu_hourly.csv)
afternoon read : the same scrape again, 2026-11-13 22:06 UTC                  (pm/qwen_primary_live_summary.json, pm/qwen_primary_windows.json)
percentiles    : linear interpolation inside histogram buckets  = ESTIMATE
decode speed   : 1 / time-per-output-token percentile  = per request, not throughput
```

## 5. Patches and workarounds

None. Nothing was changed on the server for this recipe.

## 6. Results and how they were measured

Volume and cache. Over the morning read the server finished 13,651 requests and 27 of them hit the output-length limit; none were aborted and none errored [am/qwen_primary_live_summary.derived.json]. The mean prompt was about 126,000 tokens and 97.5% of prompt tokens came from the prefix cache [am/qwen_primary_live_summary.derived.json]. That rate reflects long agent contexts that repeat, so it will differ on another workload.

Latency (all ESTIMATE).

| Metric | p50 | p90 | Raw file |
|---|---|---|---|
| Queue wait | 0.15 s | 0.27 s | [am/qwen_primary_live_summary.derived.json] |
| TTFT | 2.99 s | 6.35 s | [am/qwen_primary_live_summary.derived.json] |
| Prefill | 2.76 s | 6.40 s | [am/qwen_primary_live_summary.derived.json] |
| Decode | 8.82 s | 39.7 s | [am/qwen_primary_live_summary.derived.json] |
| End to end | 12.3 s | 45.6 s | [am/qwen_primary_live_summary.derived.json] |

Per-request decode speed is 19.1 tokens/s at the median and 12.2 tokens/s for the slowest decile, computed from the time per output token [am/qwen_primary_live_summary.derived.json]. The afternoon read, with the morning requests included, gives 3.06 s and 6.39 s for TTFT, 12.5 s and 45.9 s end to end, and 18.8 and 12.1 tokens/s [pm/qwen_primary_live_summary.json].

Windows. Overnight (22:00 to 07:30 ET, 03:00 to 12:30 UTC) over 1,371 requests the TTFT was 3.65 s p50 and 7.06 s p90, and end to end 14.0 s and 54.1 s [am/qwen_primary_latency_percentiles.csv]. The monitor's whole-history figure (TTFT p50 2.92 s, p90 6.52 s, end to end 12.2 s and 48.4 s, over 4,499 requests since 2026-11-12 00:00 UTC; same file) differs from the cumulative scrape (2.99 s and 6.35 s over 13,651 requests since 2026-11-08). The two cover different sets of requests (13,651 against 4,499). Whether that alone explains the difference is UNKNOWN; the files do not allow the causes to be separated.

Over 37 hourly rows the median was 119 requests an hour (55 to 341), with a median hourly cache-hit rate of 0.977; the lowest hour, 0.692, had 341 requests and few prompt tokens [am/qwen_primary_hourly.csv].

Load, a separate measure. The server averaged 12.1 generated tokens per wall second since start, 13.5 over the last 24 hours and 34.1 in its busiest hour [pm/qwen_primary_live_summary.json; pm/qwen_primary_windows.json; pm/qwen_primary_hourly.csv]. Idle time is inside those averages, so they describe how busy the server was and not how fast it can go. Peak running requests were 3, peak waiting 1 and peak KV cache usage 0.338, with 0 preemptions [am/qwen_primary_hourly.csv].

Two notes on the raw file. (1) Why decode speed is computed from time per output token: our reading (INFERENCE) is that with speculative decoding several tokens can arrive in one step, so the inter-token histogram in the same file (p50 0.157 s, which would read as 6.4 tokens/s) measures gaps between arrivals, not the speed a client sees per token; recipe 007 quotes a different inter-token p50 (37.4 ms) from a different short read. We use time per output token for the per-request figure. (2) The cumulative summary has a counter named external_kv_transfer that reads 1,257,600 prompt tokens (0.07% of the total). We do not know what supplied those tokens: UNKNOWN.

## 7. Thermal behaviour

Over the same history GPU 0 reached 81 C and GPU 1 82 C as hourly maxima, with 0 thermal-slowdown samples on either card; the highest single power samples were 308.6 W and 307.4 W [pm/gpu_hourly.csv]. GPU 1 was running image, video and other windows. A one-minute sampler can miss short spikes.

## 8. What did not work

- Latency by window is available for two windows because the minute monitor keeps two histograms, TTFT and end to end [am/qwen_primary_latency_percentiles.csv].
- Per-request decode speed cannot be compared with throughput [am/qwen_primary_live_summary.derived.json; pm/qwen_primary_windows.json; pm/qwen_primary_hourly.csv].

## 9. Not measured

Per-client attribution; dollar cost; the replica and the small model as time series; embedding and reranker metrics; hourly queue-wait, inter-token and decode percentiles; network bytes; output quality; behaviour at full load; the serving profile of this exact process.

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Scrape the metrics endpoint of a vLLM server twice and keep both texts.
2. Take the cumulative histograms for TTFT, queue time, prefill, decode, end to end and time per output token; interpolate p50 and p90 linearly inside the bucket and call them estimates.
3. Divide 1 by the time-per-output-token percentiles for per-request decode speed; divide generated tokens by wall seconds for throughput; keep them apart.
4. Publish the raw summaries with their hashes.

Draft reproduction steps: the monitor script is not published. `raw/` holds the exact data behind every figure.

## 11. Licence and credits

Licences follow the repository's LICENSE and LICENSE-DOCS.md. Model: Qwen3.8-27B-FP8, Apache-2.0 (model card, 2026-11-06). Serving engine: vLLM, Apache-2.0 per its repository.

## 12. Changelog

- 2026-1113 draft v0.2: added the hardware section; no number changed.
- 2026-1113 draft v0.1: initial write-up from the morning and afternoon exports of 2026-11-13; raw files and hashes in `raw/`.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
