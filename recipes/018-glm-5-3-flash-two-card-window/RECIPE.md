# Recipe 018: One evening with a 150 GB-class open model on two GPUs: GLM-5.3-Flash (UD-IQ4_XS) on llama.cpp

**Status: DRAFT v0.1, built in public.** Times in this text are UTC; the raw files may use the studio's local time. Labels: **MEASURED** = computed from a raw file in this repo (the file is named in square brackets); **REPORTED** = from a record that is not in `raw/`; **ESTIMATE** = arithmetic from a raw file, basis shown; **INFERENCE** = our reading of a measurement; **READ** = read from a file header or a log; **SOURCED** = read from a named public page; **UNKNOWN** / **NOT RUN** = we do not have it. It is one evening, one quantisation, one engine, one machine and five timed text jobs. It is not a benchmark and not a verdict on the model.

> **Warning: one lab's settings, not a recommendation.** The settings here are what this lab ran on its own machine; they were not checked against a vendor limit. Use your vendor's documented limits.

## Headline

| What | Number | Label | File |
|---|---|---|---|
| Download, six files | 157,986,121,376 bytes (147.14 GiB); every file's sha256 equals the Hugging Face listing; MIT licence on the listing; not gated | MEASURED | `download_receipt.json` |
| Model load | 47.4 s from process start to "model loaded" | MEASURED | `glm-server-log-excerpt.txt` |
| Decode, one request, idle server | 52.9, 51.2 and 48.9 tokens/s at 26, 29,962 and 125,739 prompt tokens | MEASURED | `glm-smoke-summary.csv` |
| Prefill, idle server | 1,605 tokens/s at 29,962 tokens; 1,428 tokens/s at 125,739 tokens (88.7 s wall) | MEASURED | `glm-smoke-summary.csv`, `glm-smoke-wall-times.txt` |
| Prefill of a 240k-token prompt, server busy with a second request in the other slot | 221.1 to 226.8 s for 239,912 to 239,999 tokens, about 1,058 to 1,085 tokens/s | MEASURED | `server_log_extra_lines.txt` |
| Five timed text jobs while sharing the server | by job in the order of the section 7 table (T1, T2, T6, T4, T5): completion tokens per wall second 15.8, 38.5, 7.8, 27.3 and 27.4; first content token after 115.7, 5.2, 244.5, 23.7 and 13.7 s | MEASURED | `glm-text-task-metrics.jsonl` |
| Pool-exhaustion episodes 2 to 5 | the largest request ended 242.3, 243.1, 243.3 and 242.3 s after launch; at that moment the server logged "Context size has been exceeded" (a server `send_error`) for both slots and cancel lines for both tasks | MEASURED | `glm-server-log-excerpt.txt`, `server_log_extra_lines.txt` |
| Cause of those episodes | the two requests together needed more than the 262,144-token pool (the second request's full size is UNKNOWN; the progress field suggests about 120k); no client time limit is evidenced and any client limit is UNKNOWN | INFERENCE | same |
| Memory after load | 80,492 and 79,775 MiB used on the two GPUs of 97,887 MiB each; 17,395 and 18,112 MiB free (34.7 GiB across both) | READ | `glm-kv-and-context-arithmetic.md` |
| Memory after the start-up checks | 80,636 and 80,093 MiB used; 34.2 GiB free across both | MEASURED | `gpu_after.csv` |

One limitation next to the headline: the per-job speeds are not decode speeds. They divide the completion tokens (including reasoning tokens) by the whole wall time, which includes the wait for the first content token. The decode speeds measured on an idle server are the three in the smoke table. The speeds under load are single runs taken while coding-agent sessions used the same server [`glm-contention-timeline.md`; REPORTED]. All speeds and outputs here are at reasoning effort "low", which was the server default we set; the model card lists a higher default (our own review read it as "max"; not re-read by us), so a run at the card default would differ.

## 1. What this recipe is

We loaded a 147.1 GiB mixed-quantisation build of GLM-5.3-Flash across both GPUs of one workstation for about two hours, ran a short start-up check, and let five text jobs and coding-agent sessions share it. The window ended early; the operator's notes give repeated "Context size has been exceeded" errors on the shared cache as the reason [REPORTED]. This recipe records the flags, the measurements and what went wrong, including the parts that were our configuration.

## 2. Hardware and software

- Workstation: Digital Storm Aventum Pro with two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition GPUs (97,887 MiB each), an AMD Threadripper PRO 9975WX and about 251 GiB of RAM. Stock power limit and clocks as the machine is normally run [REPORTED; not re-read for this window]. The model was split by layer across both GPUs.
- Engine: llama.cpp tag v1.0.0, commit b1b770d, built from source for compute capability 12.0 with CUDA 12.8 (nvcc 12.8.93), no patches, no third-party forks; 347 of 347 build steps ran, about 10 minutes, with the build paused if the CPU reached 81 C [`build_receipt.json`; REPORTED, from the build receipt; the build log is not published]. The llama.cpp licence was not read by us for this recipe.
- Model: `unsloth/GLM-5.3-Flash-GGUF` at revision `a38483c8cd5df544f53d70fb281afe97369d5ab6`, file set UD-IQ4_XS (five shards) plus the BF16 vision projector. MIT per the Hugging Face listing; the licence file text itself was not read by us [`download_receipt.json`; SOURCED].

## 3. The model, as read from the file

Architecture `glm5-next`, 46 blocks, 288 experts with 8 used per token, size label "288x10B", declared context length 1,048,576 tokens with no rope-scaling fields [`glm-model-metadata-excerpt.txt`; READ]. Eleven attention layers carry one KV head each, which is why the cache is small (the file lists twelve entries with one KV head; our arithmetic treats the last, a next-token-prediction block, as unused) [`glm-kv-and-context-arithmetic.md`, `glm-model-metadata-excerpt.txt`; READ / ESTIMATE]. The model card (read 2026-11-14 by the author of an earlier note, not re-read for this recipe) gives 320B total and 18B active parameters, quotes evaluations at 164K, 300K, 400K and 1M context and states no recommended maximum [SOURCED].

## 4. Launch line

```
llama-server -m <UD-IQ4_XS shard 1 of 5> --mmproj <mmproj-BF16.gguf> -ngl 999 --split-mode layer --tensor-split 1,1 \
  -c 262144 --kv-unified -np 2 -b 2048 -ub 512 --jinja --reasoning-format deepseek \
  --chat-template-kwargs '{"reasoning_effort":"low"}' --alias glm-5.3-flash --host <loopback address> --port <port> --metrics
```

KV cache type: the default (f16); no cache-type flag [`launch_flags.txt`; REPORTED, transcribed from the start script]. Reasoning effort "low" was the server default for every job; sampling settings were the server defaults and were not recorded. We chose `-c 262144` from memory arithmetic, not from tuning (section 6).

## 5. Start-up check on an idle server

| Check | Result | File |
|---|---|---|
| Text answer, 26 prompt tokens | 52.9 tokens/s decode; 1.7 s wall | `glm-smoke-summary.csv`, `glm-smoke-wall-times.txt` |
| Image with text and two shapes | 52.6 tokens/s decode; answer matched | same |
| Streamed tool call | parsed (true) | same |
| 30k-token needle question | 1,605 prefill and 51.2 decode tokens/s; answer correct; 19.2 s wall | same |
| Cold 126k-token prompt | 1,428 prefill and 48.9 decode tokens/s; 88.7 s wall | same |

After the checks the two GPUs read 72 and 73 C [`gpu_after.csv`; MEASURED]. Each check is one run, and the decode speeds rest on short outputs: 79 tokens (text), 50 (image), 26 (30k needle) and 23 (126k prefill) [`glm-smoke-summary.csv`]. The text check's note in that file calls the answer "200-token"; the same file shows 79 tokens generated.

## 6. Context and memory arithmetic

- Weights plus projector: 147.14 GiB (the six file sizes; the arithmetic file says 147.2). Memory used after load: 80,492 and 79,775 MiB on the two GPUs, leaving 17,395 and 18,112 MiB free; after the start-up checks 80,636 and 80,093 MiB (157.0 GiB together). A desktop used about 3.1 GiB before load, and the second GPU carries about 2.9 GiB of it [`glm-kv-and-context-arithmetic.md`, `gpu_after.csv`; READ / MEASURED].
- Cache cost: 11 layers x 1 KV head x (512 + 512 values) x 2 bytes = 22,528 bytes per token, which is 22.0 KiB. Our first note wrote 22.5 KiB; that was a rounding error of ours (22.5 would be kB, not KiB) [`glm-kv-and-context-arithmetic.md`; ESTIMATE].
- At 262,144 tokens that is 5.5 GiB; at the declared 1,048,576 it is 22.0 GiB, against 34.7 GiB free after load (34.2 GiB after the checks), so a 1M window f16 would fit in memory on paper [ESTIMATE; never loaded].
- Time is the other limit. Prefill ran at 1,605 and 1,428 tokens/s on an idle server at 30k and 126k prompt tokens, and at about 1,085 tokens/s at 240k with another request running, so a cold 240k prompt took 221 to 227 s. A cold 1,048,576-token prompt would take about 16 minutes at a flat 1,085 tokens/s (a floor, because the rate fell as the prompt grew) and about 43 minutes (42.8 on that basis, 44.7 if the 30k point is included) if the time grows as a quadratic through the 126k and 240k prefills; both are ESTIMATES that mix idle and busy conditions [`glm-smoke-summary.csv`, `server_log_extra_lines.txt`]. Quality at 262k or 1M on our tasks is UNKNOWN: just a 30k needle and a 126k prefill were run. Whether this engine version supports a quantised cache for this model is UNKNOWN.

## 7. Under load

Five text jobs (T1, T2, T4, T5, T6) ran while coding-agent sessions were active. T3 and T7 ran inside a coding-agent session and have no timing row [`review_scoreboard.csv`].

| Job | Prompt tokens | Completion tokens | First content token | Wall | Completion tokens per wall second |
|---|---|---|---|---|---|
| T1 | 17,017 | 2,629 | 115.7 s | 166.5 s | 15.8 |
| T2 | 4,125 | 1,125 | 5.2 s | 29.2 s | 38.5 |
| T6 | 6,377 | 2,810 | 244.5 s | 358.3 s | 7.8 |
| T4 | 5,645 | 1,754 | 23.7 s | 64.2 s | 27.3 |
| T5 | 12,699 | 1,554 | 13.7 s | 56.6 s | 27.4 (the file's value; 1,554 / 56.6 is 27.46) |

[`glm-text-task-metrics.jsonl`; MEASURED]. The first content token follows the model's reasoning, and the reasoning length varied from 126 to 5,101 characters across the five jobs [`glm-text-task-metrics.jsonl`], so the spread in waiting time is partly contention (T6 had a small prompt, 6,377 tokens, and the longest wait) and partly reasoning length; we did not separate them. The sessions, from the contention note [`glm-contention-timeline.md`; REPORTED]: a 220k to 238k-token conversation in one session, which at one point sent a second request in parallel, and later a different session of 117k to 129k tokens with a warm cache, one request every 8 to 10 s. The note covers events up to about 02:29 UTC; the log shows both slots in use at about 114k to 149k tokens each in episodes 6 to 14 (about 03:13 to 03:51 UTC), so the note does not describe that later period.

## 8. What went wrong: the pool

`--kv-unified` makes both slots share one cache of 262,144 tokens. In four episodes (the second to the fifth in the log) the largest request ended 242.3, 243.1, 243.3 and 242.3 s after launch. In each, the server logged "failed to find free space in the KV cache" warnings, then ended both requests with "Context size has been exceeded" (a server `send_error`), released both slots and logged cancel lines for both tasks within 0.1 s of each other [`glm-server-log-excerpt.txt`, `server_log_extra_lines.txt`; MEASURED, uptime stamps]. The large request was a conversation of about 240k tokens; its prefill alone took 221.1 to 226.8 s.

What the log supports about the second request, and what it does not. When the errors came, the large slot held 239,924, 239,953, 239,981 and 240,009 tokens (the release lines). The second slot's last progress line shows 21,696 tokens processed at "progress = 0.18" in each of episodes 2 to 5, and its release lines show 23,743, which is 2,047 more: about one batch (`-b 2048`) that did not fit [INFERENCE]. If the progress field is the fraction of the prompt processed, the second prompt was about 117,000 to 124,000 tokens long [ESTIMATE: 21,696 / 0.185 and 21,696 / 0.175]; its true length is UNKNOWN. So the 263,667 to 263,752 token totals in the release lines (239,924 + 23,743 and so on) are held tokens plus a batch that did not fit. They are not prompt sizes, and an earlier note that called the second request "about 23.7k tokens" was a misreading by us. At the moment of failure the two slots held about 261,620 to 261,705 tokens, which left 439 to 524 tokens of the 262,144 pool, and the next batch did not fit [ESTIMATE].

The first pair, 20 min 53 s into the uptime, came after 41 s and 29 s of running, with 238,477 and 23,747 tokens in the release lines; the second request there had processed 21,699 tokens at progress 0.18, the same pattern. In total the full server log, which is not published, shows 14 groups of such errors (an episode here means two Context-size errors less than 5 s apart) between about 02:12 and 03:51 UTC. The main excerpt holds the first five; the error, release and cancel lines of episodes 6 to 14 are in `server_log_extra_lines.txt` (for example 114,679 and 148,235 tokens in the release lines of episode 12) [READ].

The reported manual interrupt (operator's notes, about 02:28:44 UTC) is not the cause of the fifth episode: by the clock offset of the other four episodes the server error came about 10 s before it [`glm-contention-timeline.md`; REPORTED; ESTIMATE].

No client time limit is evidenced; any client limit is UNKNOWN. The log shows cancel lines but not which side initiated each; the server errors precede them. Our notes first recorded the cancels as a client giving up at exactly 240 s (cancel times 02:11:58, 02:16:03, 02:20:10 and 02:24:22 UTC on 2026-11-14, which are episodes 1 to 4; episode 1 lasted 41 s, and the four 242 s episodes are 2 to 5) [REPORTED]. The log does not show that. We blame no product. Each retry took a full prefill of the large prompt (221 to 227 s, MEASURED); that the cache could not be reused is our reading (INFERENCE).

What would help, in our reading (INFERENCE, none tested): one slot per agent, or `-np 1` with a warm cache; compacting a session before it approaches half the pool; request time limits, if you set any, above the cold prefill time. A larger context would have held both requests on the arithmetic above: about 240k plus about 120k is about 360k, against a declared 1,048,576, whose f16 cache would be about 22.0 GiB (section 6). That is an ESTIMATE; we never loaded 1M, and the cost is a longer cold prefill (section 6).

## 9. Output quality, as one AI review agent saw it

An independent review agent read each output and checked at least five claims per output against source files; we report its table and notes, not our own judgement [`review_scoreboard.csv` holds the table and word counts; the ratings, the claim checks and the three misses come from the reviewer's notes, which are not published; REPORTED]. Ratings: USEFUL for T1 and T4, PARTLY for T2, T3, T5, T6 and T7; no invented file, row, id or number found. It found three misses in the outputs we counted: T6 flagged a number the article had right, T5 ignored its own input and used a wrong date, and T3 made two false repository-wide claims. This is one AI review agent, seven outputs, no listening or taste test, and no baseline from another model.

**Word limits.** Three of the five timed outputs went over their word limits. Counted by the metrics file: T2 751 against 700 (+7.3%), T4 846 against 800 (+5.8%), T5 938 against 900 (+4.2%). Counted by the reviewer with `wc -w` on the saved files: 770 (+10.0%), 865 (+8.1%) and 957 (+6.3%). In each of the five jobs that have both counts, the `wc` count is exactly 19 words higher than the metrics-file count (the reason is UNKNOWN), and the two agree on which outputs went over. T2 ended with a self-reported count of about 640 words against 751 or 770 counted [REPORTED, from the reviewer's notes].

## 10. Timeline and restore

Window: start of the stop sequence 01:50 UTC on 2026-11-14, server live about 01:51, GLM stopped 03:55, the main text service healthy again 03:57:50, 2 min 25 s after the start command; 2 h 05 min of a planned 4 h 15 min [REPORTED, from the operator's receipts; the receipts are not published]. The load time of 47.4 s is MEASURED from the log excerpt. One restore step cost about 20 s because another service had been masked with a runtime option and a plain unmask failed [REPORTED]. The operator's notes give the reason for stopping early as repeated "Context size has been exceeded" errors that left the agent work not paying [REPORTED]; the raw files do not show that cost. Errors continued until about 03:51 UTC (section 8).

## 11. What we got wrong

1. We ran a ~240k-token conversation and a second large request in parallel against one unified cache of 262,144 tokens. The configuration set the ceiling; we published the arithmetic after, not before.
2. We first told the 240 s cancels as a client timeout. The log shows the server ending both requests when the pool ran out, 242 to 243 s in; no client time limit is evidenced and any client limit is UNKNOWN. We then called the second request "about 23.7k tokens"; that was held tokens plus a batch, and its true length is UNKNOWN (about 120k by the progress field).
3. Our cache arithmetic rounded 22.0 KiB per token to 22.5 KiB.
4. Our notes called completion tokens per wall second "tokens per second". They are not decode speeds.
5. We did not test the restore path (unmask with the same flag used to mask) before the window.
6. We cut the window short; most of the planned agent work did not run on this model.

## 12. Not measured

Output quality beyond seven outputs and one reviewer; behaviour at 400k or 1M tokens (including whether 1M would have held both requests); a quantised cache; `-np 1` or any per-slot cap; a second quantisation; a second engine; any comparison with another model on the same jobs (recipe 006 measures a different model, a different engine and real traffic, so the two are not comparable); energy use; a clean-room repeat.

## 13. Reproduce

1. Build llama.cpp at the tag and commit in `build_receipt.json` for your GPU architecture.
2. Download the file set at the revision in `download_receipt.json` and compare each file's sha256 with the listing.
3. Run the launch line in section 4 with your own model path and a loopback address. Expect about 47 s to load across two cards of this size.
4. Run the five start-up checks of section 5 on an idle server and publish the server's own timings.
5. To look for the same failure, with `-c 262144 --kv-unified -np 2`, start a very long prompt (we saw about 240k tokens) in one slot and, while it is still being processed, send a second long prompt (we saw one of about 120k tokens by the progress field; its exact size is UNKNOWN) to the other slot, and watch the log for "failed to find free space in the KV cache" and "Context size has been exceeded". We saw this during the window, not in a clean-room repeat, so this step is untested as written. Do it on a machine where nothing else is running.
6. Repeat with `-np 1`, and separately with a larger `-c`, and compare. Neither has been run.

The text jobs' prompts are internal and are not published, so jobs T1 to T7 cannot be rerun exactly; steps 4 to 6 can.

## 14. Licence and credits

Recipe text and data: CC BY 4.0, per the repository's LICENSE-DOCS.md. Model: GLM-5.3-Flash, MIT per the Hugging Face listing; quantised build by Unsloth; engine llama.cpp (MIT). Not affiliated with or endorsed by any of them.

## 15. Changelog

- v0.1: first write-up from the window's receipts, the server log, and the independent review.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-14.
