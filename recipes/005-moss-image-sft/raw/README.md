# raw/ (batch 3, 2026-11-07)
- image-job-timings-20261106.csv: one row per succeeded Genesis image job in the OpenCode image cache (268 jobs): model, size, steps, dtype, resident_worker, load_seconds, generation_seconds, total_seconds, reference supplied (true/false), job_id. No prompts, no images. generation_seconds = GPU generation only; total_seconds includes model load only when the worker was not already resident. Same sha256 as Menu 001's raw/.
- SHA256SUMS.txt: sha256 of each data file listed here (LF line endings).
