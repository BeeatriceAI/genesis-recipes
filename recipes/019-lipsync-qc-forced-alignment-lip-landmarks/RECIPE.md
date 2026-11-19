# Recipe 019: Lip-sync QC for a generated music video: forced alignment + lip landmarks

**Status: DRAFT v0.1, 2026-11-19. FIELD NOTE FROM ONE MUSIC VIDEO; THRESHOLDS SET AND CHECKED ON THE SAME CUT.** Times are ET.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named public record; **REPORTED** = from a record that is not in `raw/` (the number is transcribed in `raw/receipts.public.json` with its basis and caveat, but the run files behind it are not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Receipt |
|---|---|---|
| Known cases on one finished cut (sections with a known answer) | 37 of 37 agree: 34 sections proven in sync are not failed, 3 known bad sections fail | [Q-01 · REPORTED] |
| One of the 3 known bad sections | an older meter (envelope correlation only) had passed it at -22 ms; this tool fails it (mouth sealed while the line is rapped) | [Q-02 · REPORTED] |
| Shift control (v1 offset): picture moved -400 / -200 / +200 / +400 ms on the 28 HIGH sections | the measured offset moved by the shift (within 45 ms) in 83 of 112; HIGH was lost at +-400 ms in 27 of 28 | [Q-03 · REPORTED] |
| m/b/p closure check | closure hit rate 0.86 in sync vs 0.68-0.72 when shifted | [Q-04 · REPORTED] |
| Unit tests (synthetic data) | 19 passed | [Q-06 · REPORTED] |

One limitation next to the headline: the 37 cases come from the same cut the thresholds were tuned on, for one song, judged by eye and by one cloud vision model (Gemini, in its web app). This shows the tool reproduces known answers; it is not an independent accuracy figure [Q-07 · INFERENCE].

## 1. What this recipe is

A repeatable gate for music videos whose performance shots are generated (image or video to lip-sync models). For every section of the finished cut it answers: is the singer's mouth in sync with the voice, with HIGH confidence? It is built for rap and sung lines, where a generator can hold a closed smile through a fast bar, run 80-150 ms early or late, or put the wrong face on screen under a vocal.

It combines two independent views:
- **Audio ("spectrometer") side:** the lyrics are forced-aligned to the vocal stem letter by letter, letters become mouth-shape events (lips must close on m/b/p, mouth must open on vowels), and each m/b/p is snapped to the closure dip it leaves in the 1-4 kHz band.
- **Picture side:** a face-landmark model on every frame gives lip gap / mouth width, jaw opening and lip press per face; faces are tracked per shot and the singer's face is picked.

## 2. Software pins

No GPU is needed; everything runs on CPU. Python 3.14, torchaudio 2.11 (CPU build), mediapipe 0.10.35, librosa 0.11.0, scipy 1.17.1, numpy 2.4.4, ffmpeg [Q-08 · REPORTED].

## 3. Models

| Part | Model | Licence |
|---|---|---|
| Forced alignment | wav2vec2 base, fine-tuned on 960 h of read English (`WAV2VEC2_ASR_BASE_960H`, torchaudio pipeline) | MIT: the torchaudio page says the weights were published by the wav2vec 2.0 authors under MIT and redistributed under the same licence [Q-09 · SOURCED] |
| Face landmarks + blendshapes | MediaPipe Face Landmarker (`face_landmarker.task`: face detector, Face Mesh V2, Blendshape V2) | Apache-2.0 on each model card; the cards name AR entertainment as the primary intended use and human life-critical decisions as out of scope [Q-14 · SOURCED] |

MIT and Apache-2.0 both allow commercial use; this is our reading of the licence names, not legal advice [Q-09, Q-14 · INFERENCE].

Not part of this tool: a SyncNet-style learned sync score. The original SyncNet page says the model can be used for research purposes and says nothing about commercial use, so it is not used; a learned score with a clearer licence is a possible extra signal later, and was not run for this recipe [Q-10 · SOURCED].

## 4. How it measures

1. **Alignment, anchor-and-refine.** Word timestamps from a speech recogniser can squash a fast rap bar (one bar was stamped into 1.24 s, starting about 2.4 s after the start seen by eye) [Q-12 · REPORTED]. Every lyric line whose stamped speed is plausible (at most 9 syllables per second, coverage of at least 0.8) is an anchor and is CTC-aligned inside its own span +-0.25 s. Implausible lines are re-aligned jointly over the gap between the anchors around them. Words the recogniser heard outside every lyric line become UNSCRIPTED lines, so a sung ad-lib that is not in the lyric sheet is still checked.
2. **Mouth-shape events from spelling.** m/b/p = lips close; f/v = lower lip to teeth; vowel groups = open; o/u/w = rounded. Silent letters are skipped (climb, psych, final e).
3. **Offset per section.** Band-passed (0.8-8 Hz) cross-correlation of the voice-band envelope with lip gap and jaw opening, +-500 ms. Verified when moving the audio +-5 frames moves the reading by the same amount. Because a sung envelope repeats on the beat, a second peak one beat away can win; the v2 offset uses audio-measured anchors (m/b/p closures with a visible dip, phrase onsets) to choose between beat twins, and a whole-beat shift test marks any reading that snaps back as ambiguous (never HIGH).
4. **Event checks at the offset the viewer sees.** Every m/b/p must show a closure and every open vowel an opening within +-80 ms.
5. **Verdict per section.** HIGH (singer on screen, |offset| <= 80 ms and verified, >= 75 % vowels open, >= 60 % m/b/p closed, face tracked >= 80 %), MED, FAIL (mouth sealed or frozen under the vocal, no closures on m/b/p, a verified offset > 150 ms, or a close non-singer face with a shut mouth under the vocal), COVERED (no face big enough on screen), UNTRACKED, NO_VOCAL.
6. **Gate.** The cut passes only when every section is HIGH, COVERED or NO_VOCAL, or waived in writing with a reason. MED blocks: high confidence is the bar.

Outputs: a per-section table, a JSON of every row and event, and a timeline image per section (spectrogram, event lanes, lip-gap track).

## 5. Patches and workarounds

- A hard gate on the singer's letter spans dominated the correlation (offsets of 200-430 ms on proven sections); replaced by a smooth 80 ms mask used only when a second singer holds at least 20 % of the section [Q-11 · REPORTED].
- Joint block alignment let one rap line eat its neighbour; replaced by anchor-and-refine [Q-11 · REPORTED].
- A sparse event target normalised per lag turned a section that had lost its only anchor into amplified noise; the target is normalised once over the whole window, and at least 2 audio-measured anchors are needed before they may vote [Q-11 · REPORTED].
- Short sections (1-2 s) alias on the beat: continuous pieces of the same shot are measured together for the offset, while the event checks stay per section [Q-11 · REPORTED].

## 6. Validation

| Check | Result | Receipt |
|---|---|---|
| Known cases | 37 of 37 (28 proven sections read HIGH, 6 read MED, 3 known bad sections FAIL) | [Q-01 · REPORTED] |
| Same cases after the v2 beat-alias offset | 37 of 37 (27 HIGH, 7 MED, 3 FAIL) | [Q-05 · REPORTED] |
| Shift control (v1 offset) | offset followed the shift in 83 of 112; HIGH lost at +-400 ms in 27 of 28 | [Q-03 · REPORTED] |
| Shift control (v2 offset, 27 HIGH sections) | offset followed the shift in 85 of 108; HIGH lost at +-400 ms in 26 of 27; event hit rate best at 0 ms in 15 of 27 | [Q-15 · REPORTED] |
| Event checks under shift | m/b/p closure rate 0.86 at 0 vs 0.68-0.72 shifted (discriminates timing); open-vowel rate 0.88-0.93 at every shift (does not discriminate timing, catches sealed or frozen mouths only) | [Q-04 · REPORTED] |
| Alignment | 2 of 2 named lines land in their known windows, including the squashed rap bar (stamped about 2.4 s late, re-aligned to the window seen by eye) | [Q-12 · REPORTED] |
| Event hit rate best at 0 ms vs every shift (v1 offset) | 16 of 28 HIGH sections | [Q-03 · REPORTED] |

## 7. What did not work

- The open-vowel check as a timing signal (see the table: flat across shifts) [Q-04 · REPORTED].
- An earlier onset-locked meter on face boxes without landmarks: it could not see syllable-level mouth events [Q-11 · REPORTED].
- Letter-timed vowel spans as offset anchors: CTC letter times carried about 200 ms of bias on rap and broke 4 known cases, so only audio-measured anchors are used [Q-11 · REPORTED].

## 8. Limits

- Faces under 140 px tall in a 1280-px-wide frame (wide group shots) are COVERED, not judged.
- Mouth shapes come from spelling rules, not a pronunciation dictionary: m/b/p is reliable, vowels are approximate.
- wav2vec2 was trained on read speech; alignment confidence on processed rap vocals is low (mean letter posterior about 0.1-0.4) [Q-16 · REPORTED], which the anchor step limits but does not remove.
- Event hit rate peaks at the true offset in only 16 of 28 HIGH sections (15 of 27 with the v2 offset) [Q-03, Q-15 · REPORTED]: timing confidence comes from the verified offset plus the m/b/p check, not from the events alone.
- A non-singer face moving its mouth under someone else's vocal is MED ("needs eyes"), never an automatic FAIL.
- One cut, one song, thresholds tuned and checked on the same cut. A new song needs its own known cases before the table is trusted.

## 9. Not measured

Accuracy on a second song or another language; agreement with a learned sync score; runtime per minute of video; behaviour at frame rates other than 24 fps [Q-13 · NOT RUN].

## 10. Reproduction steps (draft: not reproducible until the code is published)

1. Export the finished cut and the isolated vocal stem with song time equal to picture time.
2. Write a timeline: each shot's start and end, who is on screen, and whether it is meant as a lip-sync shot.
3. Force-align the full lyric text to letters (anchor-and-refine as in section 4) and read the alignment report for squashed and unscripted lines.
4. Run the face landmarker on every frame (up to 4 faces), track faces per shot.
5. Measure each section (offset, shift check, beat-twin check, events), write the table, and gate.
6. Before trusting the table on a new song: pick sections whose answer you know (by eye, at full size) and require the tool to agree with every one; then move the picture by +-200 and +-400 ms and check the offset follows.

Draft reproduction steps: the code and the cut are not published.

## 11. Licence and credits

Recipe text CC BY 4.0. Models: MediaPipe Face Landmarker (Apache-2.0, per its model cards); wav2vec2 base 960h via torchaudio (MIT, per the torchaudio page). The project is not affiliated with or endorsed by Google, Meta or the PyTorch project. See LICENSE-DOCS.md.

## 12. Changelog

- 2026-11-19 v0.1: initial write-up from the tool's validation run on one finished cut and the v2 offset re-run the same day; independent scrub added licence sources, the v2 shift-control row and two missing receipts.

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; check each before commercial use. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approved for publication by the studio owner on 2026-11-19.
