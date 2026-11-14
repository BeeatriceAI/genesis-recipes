# raw/ for recipe 018 (GLM-5.3-Flash window)

Originals, byte for byte from the studio's sanitised export of 2026-11-14 (checked against its own SHA256SUMS.txt before copying): `glm-text-task-metrics.jsonl`, `glm-smoke-summary.csv`, `glm-smoke-wall-times.txt`, `glm-contention-timeline.md`, `glm-kv-and-context-arithmetic.md`, `glm-model-metadata-excerpt.txt`, `glm-server-log-excerpt.txt`, plus `gpu_after.csv` and `download_receipt.json` from the window's receipts.

Derived or transcribed (see `DERIVED.md`): `build_receipt.json`, `launch_flags.txt`, `review_scoreboard.csv`, `server_log_extra_lines.txt`.

- `glm-text-task-metrics.jsonl`: one line per timed text job. `completion_tok_s_overall` is completion tokens divided by wall seconds including the wait for the first content token; it is not decode speed. T3 and T7 have no row.
- `glm-smoke-summary.csv`, `glm-smoke-wall-times.txt`: start-up checks on an idle server, with the server's own speeds.
- `glm-server-log-excerpt.txt`, `server_log_extra_lines.txt`: selected lines of the model server's log. Time stamps are T+MM:SS.mmm since the server started.
- `glm-contention-timeline.md`: what shared the server, from the operator's notes.
- `glm-kv-and-context-arithmetic.md`: context and memory arithmetic with the per-GPU memory figures.
- `glm-model-metadata-excerpt.txt`: architecture fields read from the model file.
- `launch_flags.txt`, `build_receipt.json`, `download_receipt.json`: how the server was built, downloaded and launched.
- `review_scoreboard.csv`: the independent reviewer's table plus the metrics-file word counts.
- `gpu_after.csv`: GPU memory and temperature after the start-up checks.
- `SHA256SUMS.txt`: hashes of every file here. Some files use CRLF line endings: clone with `git config core.autocrlf false` before checking.

No prompts, outputs, host names, addresses, ports, paths or user names are included. Nothing here is a quality evaluation.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-14.
