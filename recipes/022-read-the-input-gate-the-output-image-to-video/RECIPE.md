# Recipe 022: Read the input, gate the output: two image-to-video faults from one bake-off start

**Status: DRAFT v0.1, 2026-11-21. FIELD NOTE FROM THE FIRST CANARY CLIPS OF A VIDEO BAKE-OFF; ONE CHARACTER, ONE STILL, ONE CLIP PER CASE; QUALITY JUDGED BY AI READERS FROM FRAMES; NOTHING HERE RANKS A MODEL.** Times are ET.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named public record; **REPORTED** = from a record that is not in `raw/` (the number is transcribed in `raw/receipts.public.json` with its basis, date and caveat, but the clips and reader notes behind it are not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Receipt |
|---|---|---|
| First two canary clips, one conditioning still | the still was a two-panel composite (two views of one face, a black divider); both models animated it as a split-screen video | [V-01 · REPORTED] |
| Same character, fixed single-panel still, one model | face and accessories held, but the mouth opened at 0.5 s and stayed open and talking for roughly 90 percent of the clip (reader's estimate, not a frame count) | [V-02 · REPORTED] |
| Same clip, other faults | camera pulled back from 0.5 s; the model invented a sleeveless jacket and an arm tattoo that are not in the still | [V-02 · REPORTED] |
| Clip formats observed | model A: 1280x704, 24 fps, 121 frames, 5.04 s, no audio; model B: 768x512, 25 fps, 125 frames, 5.00 s, audio 16 kHz mono | [V-03 · REPORTED] |

One limitation next to the headline: one still, one clip per case, judged by AI readers from sampled frames; no human has watched the clips with sound, and we ran no repeat seeds yet [V-06 · NOT RUN].

## 1. What this recipe is

Two cheap checks that would have saved a render batch:

1. **Read the conditioning input before the batch.** Open the image the model is actually given, at full size, and confirm it is what you think it is. Ours was cropped from a character sheet and passed in as a two-panel composite. The reader traced the split-screen output to the input; the models did what they were asked [V-01 · REPORTED].
2. **Gate the output, not only the prompt.** Image-to-video models tend to animate speech. Even with a clean single-panel still, the mouth opened at 0.5 s and talked for most of the clip. For a film that must not look like unsynced speech, every output needs a mouth-closed check on sampled frames, and a clip that fails is rejected whatever the prompt said [V-02 · REPORTED].

## 2. Hardware and software pins

Run on the studio's two-GPU Linux workstation through the lab's job runner; the reader notes do not record which GPU. Output sizes and frame counts are in the headline [V-03 · REPORTED]. Heat, memory and wall-clock times were not recorded for these two clips [V-06 · NOT RUN].

## 3. Models

Model A: Wan2.2 TI2V-5B (Apache-2.0 on its model card, per our public-use table). Model B: LongCat-Video-Avatar-1.5 (MIT, same table) [V-05 · SOURCED]. Licences are read from the model cards, not from memory; check the card again before you use either model commercially.

## 4. The method

```
Before a batch:
  1. Open every conditioning still at full size. One face, one panel, the right crop, the right aspect.
  2. Record the file hash of the still and of any audio file given to the model; confirm both are present next to the clip.
  3. Run one canary clip per model and have a reader (not the person who built the batch) look at it.

For every output:
  4. Sample frames (we used 0, 0.5, 1, 2, 3, 4 s and the last frame) and check: one shot or a split screen; mouth closed or open;
     framing drift; invented clothing or marks.
  5. Reject or trim a clip that fails; do not trust the prompt to have prevented it.
```

## 5. Patches and workarounds

Prompt changes we made next, **all INFERENCE and not yet shown to work** [V-04 · INFERENCE]:
- Put mouth behaviour in the positive prompt ("lips gently closed, mouth stays closed, silent, not speaking, not singing") and "talking, speaking, open mouth, teeth, lip movement, singing" in the negative prompt.
- Add the outfit as an explicit line to stop invented clothing.
- Try 2.5 to 3 s clips and 2 to 3 seeds; talking and framing drift grow with duration. A trim to the first 0.5 to 1 s is a fallback.

A mouth-shut gate (a script that checks sampled frames for an open mouth) was in build when this was written. The 30-second proof cut that followed passed it, but 9 of its 12 shots were held closed-mouth frames used as placeholders, so it does not show that the prompt changes work [V-04 · REPORTED].

## 6. Results and how they were measured

Two readers, both AI, looked at the clips and at frames sampled from them. The first checked file hashes against the expected ones (model A matched; model B had no expected hash, so it is recorded only) and described the two-panel still [V-01 · REPORTED] [V-03 · REPORTED]. The second watched the single-panel clip at the sample times above and scored identity 3, motion 4, mouth-closed 1 and cleanliness 4 on a 1 to 5 scale. Those scores are one reader's opinion on one clip [V-02 · REPORTED].

Model B's audio was a 16 kHz mono track muxed into the clip; the reader's advice was to re-mux the original full-band audio over the video for release [V-03 · REPORTED].

## 7. Thermal behaviour

Not measured.

## 8. What did not work

- **The first batch on a bad input.** Two models, one wasted comparison: any judgement of the models from those clips would have been about our crop.
- **Trusting the model to stay quiet.** The positive prompt did not ask for a closed mouth; the model filled the gap with speech.
- **Judging from the clip file name.** The first reader found the audio file the clip was meant to be checked against was not in the folder; the reader measured the audio muxed into the clip instead.

## 9. Not measured

Which model keeps its mouth closed more often (one clip each); frame-accurate mouth-open time; behaviour with other characters, other lengths or other seeds; audio-driven sync; speed and heat; whether the prompt changes in section 5 work.

## 10. Reproduction steps (draft: the stills, clips and reader notes are not published)

1. Pick one still of one face; crop to a single panel at the aspect your model expects.
2. Generate one clip per model, same seed and length.
3. Sample six frames per clip; write down: one shot or split, mouth state, framing, invented details.
4. Repeat with the prompt changes in section 5 and compare the mouth-open frames.

**How to measure whether it works (to do):** over at least 3 seeds per model and 2.5 to 3 s clips, report mouth-open frames per clip as a count of sampled frames, and publish the table.

## 11. Licence and credits

Recipe text CC BY 4.0. Model A: Apache-2.0. Model B: MIT. Third-party models have their own licences; read each card before commercial use.

## 12. Changelog

- 2026-1121 v1: first write-up from two reader notes of 2026-11-21.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Reproduction steps marked draft are drafts: the material behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on [APPROVAL DATE: fill when Danny approves].
