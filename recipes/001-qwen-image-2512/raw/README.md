# raw/ (batch 2 v2, 2026-11-07)
- image-job-timings-20261106.csv: one row per succeeded Genesis image job in the OpenCode image cache (268 jobs): model, size, steps, dtype, resident_worker, load_seconds, generation_seconds, total_seconds, reference supplied (true/false), job_id. No prompts, no images. generation_seconds = GPU generation only; total_seconds includes model load unless a worker was already resident. Same sha256 as Menu 001's raw/.
- faceless/FACELESS-CLEAN-SET.csv: 26 faceless images (no people) with model, seed, verdict (CLEAN, CLEAN-BEST, CLEAN-OK, REJECT), stray-text note, approval status. One AI reviewer (a Claude Code session). faceless/FACELESS-QC-20261107.md: the AI reviewer's notes. The images are not published.
- SHA256SUMS.txt: sha256 of each file listed here (LF line endings).

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
