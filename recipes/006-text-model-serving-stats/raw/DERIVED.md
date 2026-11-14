# Derived and original files

Original, byte for byte from the lab's export (sha256 checked against the export's own SHA256SUMS before copying):
- `am/qwen_primary_hourly.csv`, `am/qwen_primary_latency_percentiles.csv`, `am/qwen_primary_resets.json` (morning export of 2026-11-13).
- `pm/qwen_primary_live_summary.json`, `pm/qwen_primary_windows.json`, `pm/qwen_primary_hourly.csv` (afternoon export, public subset).

Derived, one change each:
- `am/qwen_primary_live_summary.derived.json`: the morning summary with its `source` string replaced, because the original string named the metrics file itself. Every number is unchanged. Original file sha256: 69aa37221ec92b56a194832473049ac50461b35460ac75f1f784274fd5612173 (this file's hash is in SHA256SUMS.txt).
- `pm/gpu_hourly.csv`: the afternoon export's public subset, from which the export removed the memory-peak column before it reached this repository. The unreduced file is not published.

Left out on purpose: the raw metrics scrapes, the sampler files and per-run receipts.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
