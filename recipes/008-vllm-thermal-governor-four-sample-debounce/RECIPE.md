# Recipe 008: Thermal governor with a four-sample debounce for vLLM

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1105 v1; IN SERVICE FOR ONE MODEL; staged and unit-tested; live pause under load not yet shown.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

> **Warning: one lab's settings, not a recommendation.** The temperatures, pause lines and power figures below are guardrails this lab chose for its own cooling and room. They depend on your cooling and ambient temperature, may void a warranty, and were not checked against any vendor limit. Do not copy them; use your vendor's documented limits.

> **Not reproducible yet:** the code this recipe depends on is not published in this repository, and the launch or steps below cannot run as written.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| Pause / resume lines | 90 C / 86 C, latch at 91 C or 1 C margin | governed | [T-01 · REPORTED] |
| Debounce | latch after 4 consecutive bad samples (about 1 s); immediate for slowdown, margin -1 C, 92 C | governed | [T-03 · REPORTED] |
| Injected-sample staging in vLLM 0.32.0 | 7 of 7 cases as designed | governed | [T-04 · REPORTED] |
| Unit tests | 37 pass at promotion, 43 after speculative decoding was allowed | n/a | [T-05 · REPORTED] |
| Live hold under load | not observed: six minutes of 16-stream decode peaked at 89 C | governed, not engaged | [T-11 · REPORTED] |

One limitation next to the headline: the pause lines are guardrails the owner chose, not manufacturer limits, and this recipe does not claim that 90 C is a safe operating point [T-13 · NOT RUN].

## 1. What this recipe is

A scheduler class for vLLM 0.32.0 that stops giving the GPU work while the card is hot, resumes when it has cooled, and fails visibly (health check fails, supervisor restarts) when the card crosses a stop line. Instead of killing a run at a temperature, it pauses token scheduling inside the engine so in-flight requests survive a pause. The recipe exists because one glitchy temperature sample once killed a healthy engine and dropped its requests, which led to the four-sample debounce [T-02 · REPORTED].

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro, two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition cards (97,887 MiB each, no NVLink); power limit stock 300 W, clocks stock.
- Driver 570 (open kernel module); vLLM 0.32.0+cu129, torch 2.13.0+cu129, Python 3.12. The module checks the vLLM version string and refuses to load on any other version, because it relies on the 0.32.0 scheduler internals [T-06 · INFERENCE].
- Telemetry: NVML through the pynvml copy that ships with vLLM; read-only calls, no subprocess and no setters; the card is selected by identifier, never by index.

## 3. Model

Not model-specific. It runs on the 27B FP8 chat model (see recipe 007) and was staged on a 9B model at 8192 context [T-04 · REPORTED].

## 4. Behaviour and configuration

```
every scheduler step (poll NVML at most every 0.25 s):
  sample = (temperature, thermal margin, thermal-slowdown flag), invalid if read fails or out of range
  invalid sample              -> hold (reason: telemetry unavailable); never reuse a last-known-good value
  slowdown, margin <= -1 C, or temperature >= stop+1 (92 C)   -> latch fault at once
  temperature >= stop (91 C) or margin <= 1 C                   -> bad_streak += 1; latch at 4 in a row; any good sample resets
  temperature >= pause (90 C)                                   -> hold (reason: cooling)
  holding and temperature > resume (86 C)                       -> keep holding
  holding and paused for less than 2 s                          -> keep holding (minimum hold)
  holding for 120 s or more                                     -> latch (never resume a hot card because a timer ran out)
  latched fault                                                 -> raise inside the engine: health fails, supervisor restarts
  hold                                                          -> sleep 0.05 s, set the step's token budget to 0, call the base scheduler, restore the budget
status JSON every second and on every transition: held, reason, latched fault, lines, bad_streak, pause_count, total pause seconds, peak, last sample
```

All lines are environment variables with conservative built-in defaults (84 / 80 / 87 C and 5 C margin); the serving profile passes 90 / 86 / 91 C and 1 C from a policy file. The constructor rejects inconsistent lines (resume at least 2 C under pause, stop at most 91 C, between 5 and 300 s maximum pause, 1 to 8 confirmation samples, 0 to 10 s minimum hold). Launch flags: `--scheduler-cls <thermal scheduler module>.ThermalScheduler --no-async-scheduling`, with the module on `PYTHONPATH` [T-01 · REPORTED] [T-03 · REPORTED].

## 5. Patches and workarounds

- vLLM source patches: 0. One module of about 290 lines.
- The hold works by zeroing the step's token budget. In vLLM 0.32.0 both the running and waiting loops of the base scheduler are guarded by `token_budget > 0`, so a held step touches no request: no KV allocation, no preemption, and the draft tokens proposed by the last executed step are neither read nor cleared. An empty step returns the empty model-runner output and the engine skips drafting because no model executed. This was read from the vLLM code and confirmed by a unit test, not by a live pause with drafts pending [T-06 · INFERENCE] [T-11 · REPORTED].
- Refused on purpose: async scheduling, more than one in-flight batch, tensor/pipeline/data parallelism, external KV connectors. With overlapping batches the draft bookkeeping crosses step boundaries and was not inspected [T-06 · INFERENCE].
- Publication gap: the lab copy allow-lists two card identifiers; the public copy must take the identifier from the environment alone.

## 6. Results and how they were measured

Staging method: a real vLLM 0.32.0 engine on the second card with the module copied byte for byte plus a staging-only hook that feeds scripted samples; requests in flight to drive the scheduler [T-04 · REPORTED].

| Injected case | Observed | Receipt |
|---|---|---|
| One bad sample (88 C, margin 1.0 C) | consumed; request completed; no latch | [T-04 · REPORTED] |
| 3 bad, 1 good, 3 bad | no latch | [T-04 · REPORTED] |
| 3 bad then good | no latch | [T-04 · REPORTED] |
| One 90 C sample then 16 cool samples | cooling, then running after 2.053 s (minimum hold 2.0 s) | [T-04 · REPORTED] |
| 4 bad in a row | latched; engine raised; in-flight request got HTTP 500; health failed within 1 s | [T-04 · REPORTED] |
| Thermal-slowdown flag | latched at once; engine exited within 1 s | [T-04 · REPORTED] |

Real card peak during staging was 83 C; injected samples were synthetic and the immediate margin and 92 C latches were covered by unit tests, not by the engine run. The staging used a 9B model at 8192 context, not the 262,144-token profile [T-04 · REPORTED]. The cost of the debounce: a real 91 C condition needs 4 polls (about 0.75-1 s) to latch unless slowdown, margin -1 C or 92 C applies [T-03 · REPORTED].

## 7. Thermal behaviour in service

- Under six minutes of 16-stream decode at the 300 W limit with MTP, the card rose from 73 C to 86 C in a minute, then sat at 87-88 C (monitor peak 89 C). The 90 C pause line was not reached, so no hold happened and a live hold-and-resume with MTP drafts pending is unknown [T-11 · REPORTED].
- Test harnesses use their own lines on top: pause at 88 C and resume at 84 C, so the in-engine pause is the backstop [T-12 · REPORTED].
- The scheduler cannot interrupt a kernel already on the GPU or a blocking NVML call; an external guard is still needed for tests [T-07 · REPORTED].
- Hardware protections (92 C maximum operating point, slowdown at margin -2 C, shutdown at -5 C) are unchanged and are not part of this software.

## 8. What did not work (harness mistakes found while using the governor)

1. Stopping a run because the other card was hot. A staging run was cut at 85 s when the other card reached 90 C under another job's load; the harness had treated it like its own stop line. Fixed: the other card now stops a test at 91 C after 4 consecutive 1 Hz samples, or at once on margin 1 C or less, slowdown or 92 C [T-08 · REPORTED].
2. A pause that did not pause. Sending the stop signal to a process group missed a worker that runs in its own session; the card stayed at 98.7% utilisation and 297 W through 77 "paused" samples. Fixed by signalling the whole process tree; verified live: utilisation 100% to 4%, power 300 W to 116 W, 88 C to 83 C within about four seconds [T-09 · REPORTED].
3. A status check that matched the wrong text: "Not Active" contains the string the check looked for, so the initial launch aborted after 2 s [T-10 · REPORTED].
4. The single-sample latch that started this recipe [T-02 · REPORTED].

## 9. Not shown

Safe operation at 90 C; behaviour at another ambient temperature; a hold-and-resume under real load with drafts pending; a long-run pause count with a receipt behind it [T-13 · NOT RUN] [T-11 · REPORTED].

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Install vLLM 0.32.0; start any small model with the stock scheduler to confirm the card works.
2. Write the module from the pseudo-code in section 4 (the public copy will be published after sanitising), pin it to the exact vLLM version, and add a status file.
3. Run the unit tests with a fake clock and sensor before anything else: lone bad sample, scattered bad samples, four in a row, slowdown, minimum hold, telemetry loss, the pause deadline, and a zero-budget hold with speculative drafts in flight.
4. Stage it in a real engine on a spare card with a hook that injects scripted samples, then repeat the table in section 6.
5. After that, load it on the serving card, and watch the status file's pause count.

## 11. Licence and credits

The module is lab code subclassing vLLM's scheduler. code MIT, text CC BY 4.0. vLLM is Apache-2.0 (read on its repository 2026-11-06). The code is not in this repository yet (draft reproduction steps). See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1105 v1: initial write-up from the debounce staging receipt, the speculative-decoding update and the harness incidents.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
