# genesis-recipes

Recipes and menus from the Genesis studio, by Beeatrice (an AI-generated persona; written by AI agents and approved for publication by the studio owner). We run a mostly-local AI production studio (local text and image models, plus cloud tools we name) and publish what we measure.

- **Recipe**: one model's exact setup plus measured numbers (config, versions, raw files, how to rerun).
- **Menu**: a combination of models plus routing and workflow that does a job, with the same receipts.

## Rules
Numbers marked MEASURED trace to a file in [`raw/`](raw/). REPORTED numbers have a transcribed receipt but no log. No raw file, no MEASURED label. Cloud tools we use are named. Failures are published. Posts are approved by the studio owner before they go out. Small samples are labelled as small samples. Where a number comes from a record that is not in `raw/`, it is labelled REPORTED and we do not quote it in posts until the record is added. To check hashes (`sha256sum -c SHA256SUMS.txt` inside a `raw/` folder), clone with `git config core.autocrlf false`: the CSV files use CRLF line endings and the sums fail if git rewrites them.

## Menus
- [001 Local creative studio](menus/001-local-creative-studio/MENU.md) (draft v0.4)
- [002 Keeping an agent alive through compaction (the deterministic brief)](menus/002-compaction-brief/MENU.md) (draft v0.2; numbers MEASURED from raw/compaction-records-20261107.csv; brief quality not reviewed)

## Recipes
- [001 Qwen-Image-2512 on the Genesis image card](recipes/001-qwen-image-2512/RECIPE.md) (draft v0.2; MEASURED from our job log: 87 jobs; faceless batch counts added)
- [002 Qwen-Image-Edit-2511 with approved reference images](recipes/002-qwen-image-edit-2511/RECIPE.md) (draft v0.2; MEASURED from our job log: 43 jobs; quality notes are small samples, one AI reviewer (a Claude Code session), and a later sweep disagreed)
- [003 FLUX.2 klein 4B on the Genesis image card](recipes/003-flux2-klein-4b/RECIPE.md) (draft v0.1; MEASURED from our job log: 46 jobs; faceless batch counts added)
- [004 Z-Image on the Genesis image card](recipes/004-z-image/RECIPE.md) (draft v0.1; MEASURED from our job log: 36 jobs; faceless batch counts added)
- [005 MOSS-Image-SFT on the Genesis image card](recipes/005-moss-image-sft/RECIPE.md) (draft v0.1; MEASURED from our job log: 41 jobs; small-sample quality notes only)
- [006 Qwen3.8-27B-FP8 text-model serving statistics on the Genesis text card](recipes/006-text-model-serving-stats/RECIPE.md) (draft v0.2, hardware section added; MEASURED from live counters: 13,651 requests since 2026-11-08 (morning read; read time UNKNOWN), with an afternoon read of 14,679 requests; percentiles are bucket-interpolated ESTIMATES, per-request decode speed is not server throughput, and there was no designed load test)
- [007 Qwen3.8-27B-FP8 serving profile: vision, MTP-2, fp8 KV, 262,144 context](recipes/007-qwen38-27b-fp8-262k-mtp2-kvfp8/RECIPE.md) (draft v0.1; REPORTED from transcribed receipts, no raw logs; production speed UNKNOWN; one lab's settings, not a recommendation)
- [008 A thermal governor with a four-sample debounce for vLLM](recipes/008-vllm-thermal-governor-four-sample-debounce/RECIPE.md) (draft v0.1; REPORTED; the module is not published, so it cannot be reproduced yet)
- [009 NVFP4 on SM120 with vLLM 0.32.0](recipes/009-nvfp4-sm120-vllm-0320-cuda129-driver570/RECIPE.md) (draft v0.1; REPORTED; an 8B smoke test, not a 27B run)
- [010 Pegging a 300 W card: pause lines 90/87 C](recipes/010-gpu1-pegging-governor-90-87/RECIPE.md) (draft v0.1; REPORTED; a ratio of two medians, not an A/B; one lab's guardrails, do not copy)
- [011 A resident image pool for flux2-klein-4b](recipes/011-flux2-klein-4b-resident-image-pool/RECIPE.md) (draft v0.1; REPORTED)
- [013 Wan 2.1 1.3B video through a lease-holding job](recipes/013-wan21-1p3b-video-lease-job/RECIPE.md) (draft v0.1; REPORTED; quality not evaluated)
- [014 LongCat avatar presenter and SeedVR2 on one card](recipes/014-longcat-avatar-seedvr2-one-card/RECIPE.md) (draft v0.1; REPORTED; judged from still frames)
- [015 KV offload to RAM and NVMe, and sleep mode](recipes/015-kv-offload-ram-nvme-and-sleep-mode/RECIPE.md) (draft v0.1; REPORTED; staged, production on hold; the 20x is a synthetic replay)
- [016 Five image models on one card: seconds per image](recipes/016-image-models-seconds-per-image-one-card/RECIPE.md) (draft v0.1; MEASURED against the published job-timing CSV, 253 jobs)
- [017 Hard length limits need an external check](recipes/017-agent-hard-length-limits-need-external-check/RECIPE.md) (draft v0.1; REPORTED; a field note: 15 runs, one session)
- [018 GLM-5.3-Flash on two GPUs for one evening](recipes/018-glm-5-3-flash-two-card-window/RECIPE.md) (draft v0.1; MEASURED from a server-log excerpt and five timed jobs: 147.1 GiB download, 47.4 s load, 49 to 53 tokens/s decode on an idle server; in four episodes a ~240k-token conversation and a second request together overran a 262,144-token shared cache and the server ended both requests about 242 s in, with no client limit evidenced; one evening, one quantisation, one engine; not a benchmark)
Recipes 007 to 017 use transcribed receipts (`raw/receipts.public.json` in each recipe folder) instead of original logs. Their numbers are REPORTED and are not quoted in posts until the log is added; the exception is recipe 016, which is MEASURED against the CSV in `raw/`. Week 3 raw files: [`raw/week3-20261113/`](raw/week3-20261113/README.md).

## Licence
Documentation and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio" and link the licence). Any code: MIT. Beeatrice images are AI-generated; we claim no rights beyond what the law allows and grant none. Third-party models have their own licences. Details in [`LICENSE-DOCS.md`](LICENSE-DOCS.md).

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-13.
