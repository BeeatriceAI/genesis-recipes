# GPU daily usage, 2026-10-29 to 2026-11-15 (UTC days)

Daily summary behind the "three weeks" GPU figures: how many minutes a day each of the studio's two GPUs spent at 50 percent utilisation or more, the mean utilisation, and energy worked out from the power samples.

All days in this folder are UTC dates, and "busy" means a minute at 50 percent utilisation or more. The Week 3 folder (`raw/week3-20261113/`) uses US Eastern days, and the hourly GPU file in recipe 006 counts minutes at 90 percent or more, so their rows do not line up one to one with these. Example: for GPU 0 on 2026-11-12 UTC this folder has 1,321 minutes at 50 percent or more, and the recipe 006 hourly file sums to 809 minutes at 90 percent or more for the same day.

| File | What it holds |
|---|---|
| `gpu_daily_usage_UTC.csv` | One row per UTC day and GPU: monitor samples, mean utilisation, minutes at 50 percent utilisation or more, mean power, energy, maximum temperature, holes in the day's record. |
| `gpu_three_week_totals.csv` | The totals and averages quoted in posts, each with the formula that produces it from the daily file. |
| `SHA256SUMS.txt` | Hashes of the two data files. |

## How the numbers were taken

- A minute monitor writes about one record a minute per GPU. The daily file is a summary of those records; the minute records themselves are not published.
- Busy hours = `minutes_util_ge_50` / 60.
- Mean utilisation over the span is weighted by the number of samples per day. It is not the share of time a GPU was busy.
- Energy = sum of the power sample x 1 minute, per day. It assumes each record stands for one minute. It is GPU power only: no CPU, no drives, no cooling, no wall meter. It is not a cost figure.
- `missing_minutes_in_day` counts holes between the first and last record of that day.
- Totals are summed from the unrounded daily values and then rounded, so the two rounded per-GPU energy figures add up to 0.1 kWh less than the both-GPU figure.
- Two per-day means are given for each GPU. One covers the whole span, per recorded day (samples / 1,440). The other covers 2026-11-07 to 2026-11-14 only, and is higher. Quote the second one with its dates.

## What is left out, and limits

- The peak memory column of the daily export is left out.
- 2026-10-29 (first record day, 515 samples) and 2026-11-15 (20 samples) are partial days, and 2026-10-30 has 64 holes. Nothing is filled in for missing minutes. Sixteen of the 18 dates have 1,380 or more samples. No date is complete to the minute.
- There are no records before 2026-10-29, so these files cover 18 calendar dates, not a full three weeks.
- On 2026-10-29 and 2026-10-30 the usual gap between records was about 65 seconds; from 2026-10-31 it is about 60. Each record still counts as one minute, so busy minutes and energy on those two days can be low by up to about 8 percent, and most of the holes on those two days come from the slower interval, not from outages. This was measured on the minute records.
- Nine dates have samples plus holes above 1,440 (up to 1,460 on 2026-10-30). The reason is records that share a clock minute with another record: 87 of 23,524 per GPU over the span, 0.4 percent, all but one of them before 2026-11-07. The cause is not recorded. Busy-hour figures can be high by up to about 20 minutes on a single day because of them.
- The monitor's record format gained fields on 2026-10-30 and 2026-11-04. The per-GPU fields summarised here come from the same monitor throughout.
- Temperature maxima before 2026-11-06 are higher than in the Week 3 folder: GPU 0 reached 91 C on 2026-10-31 and 90 C on 2026-11-02 to 2026-11-04, and 89 C appears on GPU 0 from 2026-10-29 and on GPU 1 from 2026-10-31. The cause is not recorded in these files.
- Busy minutes include the image-pool throughput windows measured in recipe 010 (from 2026-11-04). They are not separated here.
- The files do not say which job a GPU minute belonged to. Utilisation is not output: a busy minute is not a finished image, clip or answer.
- Which kind of work ran on which GPU comes from lab notes (REPORTED), not from these files.

Made with AI tools at the Genesis studio; approved for publication by the studio owner on 2026-11-14.
