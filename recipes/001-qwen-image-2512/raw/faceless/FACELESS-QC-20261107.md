# Faceless image batch: AI reviewer QC notes (a Claude Code session; public version, 2026-11-07). 26 images from three local models; the reviewer saw the model names, so this is not blind; small sample; nothing certified.
Source: our gateway job log for this batch. The images themselves are not published here. Size 1024x1024 (the two 16:9 textures 1536x1024). Rule applied: no faces or figures, no stray text or logos (the prompts asked for none).

## FACELESS-01 (cover directions)
| image | verdict | note |
|---|---|---|
| 01 weather knot flux2 | USE | cloud-knot, one magenta thread, clean |
| 01 weather knot qwen | USE (reviewer preference) | braided silver rain knot, magenta accent, clean |
| 01 weather knot zimage | OK | flat saturated blue background, weaker mood |
| 07 pool flux2 | REJECT | garbled letters at top ("M E H O R") and a small logo bottom-right |
| 07 pool qwen | USE (reviewer preference) | still water, storm sky, one magenta reflection, clean |
| 07 pool zimage | REJECT | garbled title text and a cartoon face icon bottom-right; pool is cyan, not the navy palette |
| 08 cathedral flux2 | USE | lightning, open dark doors, clean |
| 08 cathedral qwen | USE (reviewer preference) | clean, strongest facade |
| 08 cathedral zimage | REJECT | garbled text across the top, flat illustration style |
| 09 road flux2 | REJECT | small text and logo bottom-right |
| 09 road qwen | USE (reviewer preference) | amber streetlight, storm wall, clean |
| 09 road zimage | REJECT | large garbled heading plus a small face-like glyph bottom-center |
| 10 knot fabric flux2 | OK | sky window reads, knot weak |
| 10 knot fabric qwen | USE (reviewer preference) | knot is clear, sky window clean |
| 10 knot fabric zimage | OK | smaller window, clean |
| 11 138 lightning flux2 | USE | digits read 138 correctly, one magenta branch, clean |
| 11 138 lightning qwen (retry) | CLEAN | digits read 138; the white bolt crosses the 3; no stray text |
| 11 138 lightning zimage (retry) | CLEAN-OK | digits read 138 but small and angular; no stray text |

## FACELESS-02 (textures)
All 8 are clean (no text, logos or figures): emerald/magenta interlace (flux2 fine weave, qwen bold weave), rain on glass (qwen warmer bokeh, flux2 darker), star field 16:9 (qwen richer Milky Way), nebula 16:9 (both good; flux2 magenta/teal fits the Orbit palette). Reviewer preference for the pages: FK02-01 flux2 (tileable-looking), FK02-04 flux2, FK02-03 qwen.

## Lessons
- z-image and flux2 add stray lettering or logos even when told "no text"; qwen-image-2512 did not in 10 of 10 here (a small sample, reviewer judgment, not a ranking; the two "retry" rows replaced earlier attempts that are not counted).
- 5 of 18 FACELESS-01 images were rejected for stray text or logos (a cartoon face icon appeared twice, a "no faces" violation in spirit): scan the corners of every image. Across all 26 images, 21 were clean.
