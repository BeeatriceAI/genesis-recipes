# raw/week4-20261121/

- `receipts.public.json`: one entry per figure in the Week 4 article ("Week 4 of a one-person AI studio: what we shipped, broke and fixed") that does not come from a published data file. Each entry has an id, claim, value, basis, run state, date and caveat. It is a transcription made by the studio: the logs, clips, policy files and code behind it are not published, so these figures are REPORTED, not MEASURED. The two exceptions are F09 (the lint report itself is in `recipes/020-required-elements-gate-and-lint-omission-blindness/raw/lint-report.public.json`) and F20 (measured on our own configuration, but the configuration is not published).
- Figures about GPU utilisation in the article come from the Week 3 daily files in [`raw/three-weeks-20261114/`](../three-weeks-20261114/) and are MEASURED.
- Not here yet: a Week 4 GPU daily file, and counts from the standing job queue. Both are listed as not run in entry N-01.

SHA256SUMS.txt lists the hashes (check with `sha256sum -c SHA256SUMS.txt` from inside this folder; clone with `git config core.autocrlf false`). No prompts, images, outputs, host names, addresses, paths or account details are included.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on [APPROVAL DATE: fill when Danny approves].
