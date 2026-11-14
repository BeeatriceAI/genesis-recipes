# Recipe 010: Pegging a 300 W card: moving the pause line from 88/84 C to 90/87 C on a resident image pool

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1106; v2 2026-1110.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| Pause 88 C / resume 84 C: 435 windows, 2026-11-04 to 2026-11-06 | median 51.0 images/min (range 44.0-56.7), median 19 pauses per window, 261.5 W median average draw, 78.6% median utilisation | cooling-limited | [G-01 · REPORTED] |
| Pause 90 C / resume 87 C: 14 windows, one hour of 2026-11-06 | median 60.1 images/min (range 59.0-61.7), 13 windows with 0 pauses, 98.2% median utilisation, 300.0 W median average draw | governed, line reached once | [G-02 · REPORTED] |
| Difference of the two medians | about 1.18x | derived, not a controlled A/B | [G-03 · REPORTED] |
| v2: all 66 windows at 90/87 C over 8.6 hours | 2 pauses in total (4.3 s), both at 90 C; 64 windows with none; peak 89 C in 64 windows | governed | [G-09 · REPORTED] |
| v2: 48 later windows with another model resident on the card | median 63.7 images/min (cause of the higher figure UNKNOWN) | governed | [G-08 · REPORTED] |
| Earlier ungoverned ceiling, cool card, 30-36 s windows | 61.2 images/min | ungoverned | [G-05 · REPORTED] |

One limitation next to the headline: the two sets were measured on different hours and days with the room temperature unrecorded. The v1 comparison rests on 14 windows; v2 adds 52 more windows, which agree on the pause count and move the median up, not down. The gain is large and consistent inside the set. It is not proof of the size of the gain on another day [G-03 · REPORTED] [G-06 · NOT RUN].

## 1. What this recipe is

A policy change, not a code change. The resident image pool (see recipe 011) holds new work when the card reaches a pause line and resumes when it cools to a resume line. At 88 C / 84 C the governor held the card back a median of 19 times per window, and the card spent its time at 78.6% utilisation and 261.5 W of its 300 W budget [G-01 · REPORTED]. The owner ordered the card pegged: pause at 90 C, resume at 87 C. The same workload then held 98.2% utilisation and 300 W, and 13 of 14 windows never paused [G-02 · REPORTED].

The stop line stays at 91 C. The hardware protections (92 C maximum operating point, slowdown at margin -2 C, shutdown at -5 C) are not touched, and neither are the stock 300 W power limit and stock clocks [G-04 · REPORTED].

## 2. Hardware and software pins

- Workstation: Digital Storm Aventum Pro, two NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition cards (97,887 MiB each, no NVLink). The image pool owns the lab's second card; the other serves language models.
- Power limit stock 300 W, clocks stock, no clock cap. Average SM clock fell from a median 1,763 MHz in the 88/84 windows to 1,664 MHz in the 90/87 windows: the card held a higher temperature at lower clocks, with the power cap doing the limiting [G-01 · REPORTED] [G-02 · REPORTED].
- Driver 570 (open kernel module), CUDA 12.9 wheels, torch 2.11.0+cu129, diffusers 0.42.1, Python 3.12.

## 3. Model and workload

`black-forest-labs/FLUX.2-klein-4B`, 1024x1024, 4 steps, fixed prompt and seeds, one resident worker per window (see recipe 011 for the pins and licence). Median latency per image 1.00 s at p50 and 1.02 s at p95 in the 90/87 windows, because nothing waited on a pause [G-02 · REPORTED].

## 4. The change

```
chain governor (jobs that run between real image jobs):
  pause   88 C -> 90 C
  resume  84 C -> 87 C
  admit   a job when the card is at or below: light 86 -> 88 C, medium 86 -> 88 C, hot 84 -> 86 C
  stop    91 C (unchanged), 85 C CPU, missing telemetry (unchanged)
image pool policy:
  hold    88 C -> 90 C
  resume  84 C -> 87 C
  admit   below 85 C
  stop    91 C (unchanged)
a configuration check refuses a pause line above 90 C and a stop line above 91 C
```

The change is two policy values and the permitted ceiling in the configuration check; no model or scheduler code was edited [G-04 · REPORTED].

## 5. Patches and workarounds

None to the model, the diffusion library or the driver. The test that exercises a pause was changed to inject 90.5 C instead of 89 C so that it still crosses the new line [G-04 · REPORTED].

## 6. Results and how they were measured

Method: the soak harness runs back-to-back windows of one resident worker and records, per window, images per minute (jobs finished inside the window), p50 and p95 latency, average and maximum GPU utilisation and board power, average SM clock, temperature at start, maximum and end, CPU temperature, throttle-reason bits, pause count and paused seconds. A window is `complete` when the governor never engaged and `complete_but_cooling_governed` when it did.

| Set | Windows | Images/min median (range) | Pauses per window | Utilisation median | Board power median | Peak temperature | Receipt |
|---|---|---|---|---|---|---|---|
| Pause 88 C / resume 84 C | 435 | 51.0 (44.0-56.7) | median 19, 8,314 in total | 78.6% | 261.5 W | 90 C in at least one window, median window peak 89 C | [G-01 · REPORTED] |
| Pause 90 C / resume 87 C | 14 | 60.1 (59.0-61.7) | 0 in 13 windows; 1 pause of 2.05 s at 90 C in the last | 98.2% | 300.0 W | 89 C in 13 windows, 90 C in one | [G-02 · REPORTED] |
| v2: same lines, earliest 18 windows | 18 | 60.2 (59.0-61.7) | 1 in total | 98.2% | 300.0 W | 90 C in one, 89 C in the rest | [G-07 · REPORTED] |
| v2: same lines, later 48 windows, another model resident on the card | 48 | 63.7 (61.0-64.5) | 1 in total | 97.9% | 300.0 W | 90 C in one, 89 C in the rest | [G-08 · REPORTED] |

CPU temperature peaked at 84.1 C in the 90/87 windows, under the 85 C test line. Throttle-reason bits seen: none, and the software power cap [G-02 · REPORTED]. The derived ratio is 60.1 / 51.0, about 1.18x [G-03 · REPORTED]. The 90/87 median sits within 2% of the 61.2 images/min that one worker reached ungoverned on a cool card for 30-36 s: at this line the governor stops costing throughput [G-05 · REPORTED].

## 7. Thermal behaviour

- The card peaked at 89 C in thirteen of fourteen windows and never reached the 90 C line in them. The fourteenth reached it once and paused for 2.05 s [G-02 · REPORTED].
- 90 C is a software guardrail chosen by the owner. This recipe does not claim 90 C is a safe operating point, and it does not claim anything about component life at that temperature [G-06 · NOT RUN].
- v2: across 66 windows over 8.6 hours of wall time (about 5 hours of window time) the line was reached in two windows and each paused once [G-09 · REPORTED]. The windows are about four and a half minutes apart with five gaps longer than ten minutes. Continuous multi-hour behaviour, a hotter room and a card with the other GPU also at its power limit are UNKNOWN [G-06 · NOT RUN].

## 8. What did not work or does not follow

- The earlier 88/84 line was not wrong: it was a conservative choice, and its cost was measurable. Every pause is a few seconds of idle silicon, repeated a median of 19 times per window [G-01 · REPORTED].
- Raising the line did not raise the ceiling above the ungoverned number: the gain is that the governor mostly stops engaging, not that the card got faster [G-05 · REPORTED].
- The 435-window set pools windows run under earlier pool settings; the harness file does not record the worker count per window, so the 88/84 set is a median of a mixed bag and the comparison is conservative in no known direction [G-01 · REPORTED].

## 9. Not measured

Image quality (identical seeds were not compared between lines); a continuous run longer than about four and a half minutes; the other card's temperature and throughput while this one runs at 300 W; ambient temperature; component wear; any line above 90 C [G-06 · NOT RUN].

## 10. Reproduction steps (draft, one machine)

1. Pick a resident-worker workload and a pause/resume pair; log temperature, board power, utilisation, SM clock and throttle bits every 2 s per card by identifier.
2. Run 30 windows at your current line, then 14 at 90 C / 87 C, back to back, starting each window below 77 C.
3. Report median images per minute, pauses per window and median utilisation for both sets, with the date, the hours and the room temperature.
4. Keep the stop line at your own limit and the hardware protections as shipped.
5. A one-line telemetry logger (not included in this repository) records the telemetry in step 1; the pool and chain governor code is not published (draft reproduction steps).

## 11. Licence and credits

Recipe text CC BY 4.0, code MIT. Model credit: Black Forest Labs (FLUX.2-klein-4B, Apache-2.0 as verified on its model card). See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1106 v1: initial write-up from the soak harness file and the policy change (14 windows).
- 2026-1110 v2: the file grew to 66 windows at 90/87 C over 8.6 hours (G-07 to G-09). The pause count stays at 2 in total. A later set of 48 windows with another model resident on the card measured a higher median (63.7); the cause is UNKNOWN. v1 numbers are unchanged. The synthetic windows have since stopped, so no further windows are expected.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; where a licence line below says "check upstream" we have not verified it. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools and reviewed by a human before release.
Written by AI agents and reviewed by a human before publishing.
