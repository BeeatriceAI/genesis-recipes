# Week 3 raw number files (2026-11-07 to 2026-11-13)

Raw exports behind the Week 3 figures for the image, training and temperature lanes. The text-model figures have their own raw files under `recipes/006-text-model-serving-stats/raw/`.

All days are US Eastern time.

| File | What it holds |
|---|---|
| `daily_image_jobs_ET.csv` | Image-queue jobs per day and model: succeeded, refused, cancelled, other. |
| `own_worker_seconds_per_image.csv` | Pure render seconds per image (median, p90) and load seconds for the three models that run on their own worker. |
| `training_windows_aggregate.csv` | Training runs per base-model family: count, wall hours total and median, peak GPU temperature. |
| `daily_gpu_cpu_maxima_ET.csv` | Per day: monitor samples, GPU temperature and power maxima, minutes at 90 percent utilisation or more, thermal-slowdown samples, CPU sensor maximum. |
| `qwen_primary_peak_hour.json` | Busiest full hour of the primary text model: generated tokens per wall second and request count. |
| `SHA256SUMS.txt` | Hashes of the five data files. |

## What is left out, and limits

- `daily_image_jobs_ET.csv`: totals in this file are lower than the machine's full job count.
- `own_worker_seconds_per_image.csv`: the peak memory column is left out.
- `training_windows_aggregate.csv`: aggregate only. Run names, characters and sample data are withheld by design.
- `daily_gpu_cpu_maxima_ET.csv`: 2026-11-06 holds 19:00 to 24:00 only (monitor file boundary) and 2026-11-13 is a partial day. The CPU value is a sensor maximum.
- GPU temperature maxima fall from 89 C on 2026-11-06 and 2026-11-07 to 80 to 82 C from 2026-11-08. We think the synthetic pegging windows of recipe 010 explain the earlier maxima (INFERENCE); the date those windows stopped is not recorded.
- Queue times for models in the shared image queue include waiting, so they are not render speed and are not in these files.
- Nobody judged image, video or audio quality for these numbers. They are counts, seconds and temperatures only.

Made with AI tools at the Genesis studio; approved for publication by the studio owner on 2026-11-13.
