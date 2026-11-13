# genesis-recipes

Recipes and menus from the Genesis studio, by Beeatrice (an AI-generated persona, reviewed by humans). We run a mostly-local AI production studio (local text and image models, plus cloud tools we name) and publish what we measure.

- **Recipe**: one model's exact setup plus measured numbers (config, versions, raw files, how to rerun).
- **Menu**: a combination of models plus routing and workflow that does a job, with the same receipts.

## Rules
Every number traces to a raw file in [`raw/`](raw/). No raw file, no number. Cloud tools we use are named. Failures are published. Posts are checked and human-approved. Small samples are labelled as small samples. Where a number comes from a record that is not in `raw/`, it is labelled REPORTED and we do not quote it in posts until the record is added.

## Menus
- [001 Local creative studio](menus/001-local-creative-studio/MENU.md) (draft v0.3)
- [002 Keeping an agent alive through compaction (the deterministic brief)](menus/002-compaction-brief/MENU.md) (draft v0.2; numbers MEASURED from raw/compaction-records-20261107.csv; brief quality not reviewed)

## Recipes
- [001 Qwen-Image-2512 on the Genesis image card](recipes/001-qwen-image-2512/RECIPE.md) (draft v0.2; MEASURED from our job log: 87 jobs; faceless batch counts added)
- [002 Qwen-Image-Edit-2511 with approved reference images](recipes/002-qwen-image-edit-2511/RECIPE.md) (draft v0.2; MEASURED from our job log: 43 jobs; quality notes are small samples, one reviewer, and a later sweep disagreed)
- [003 FLUX.2 klein 4B on the Genesis image card](recipes/003-flux2-klein-4b/RECIPE.md) (draft v0.1; MEASURED from our job log: 46 jobs; faceless batch counts added)
- [004 Z-Image on the Genesis image card](recipes/004-z-image/RECIPE.md) (draft v0.1; MEASURED from our job log: 36 jobs; faceless batch counts added)
- [005 MOSS-Image-SFT on the Genesis image card](recipes/005-moss-image-sft/RECIPE.md) (draft v0.1; MEASURED from our job log: 41 jobs; small-sample quality notes only)
- [006 Qwen3.8-27B-FP8 text-model serving statistics on the Genesis text card](recipes/006-text-model-serving-stats/RECIPE.md) (draft v0.1; MEASURED from live counters: 13,651 requests since 2026-11-08 (morning read; read time UNKNOWN), with an afternoon read of 14,679 requests; percentiles are bucket-interpolated ESTIMATES, per-request decode speed is not server throughput, and there was no designed load test)

## Licence
Documentation and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio" and link the licence). Any code: MIT. Beeatrice images are AI-generated; we claim no rights beyond what the law allows and grant none. Third-party models have their own licences. Details in [`LICENSE-DOCS.md`](LICENSE-DOCS.md).

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools and reviewed by a human before release.
