# Recipe 012: One 4096x4096 image held a vision slot for 166 seconds: a red-team finding and the router cap

**Status: DRAFT v0.1, built in public from the studio's staged recipe 2026-1106; v2 2026-1110.** Times are UTC.

Labels: **MEASURED** = computed from a raw file in this repo; **SOURCED** = read from a named record; **REPORTED** = from a record that is not in `raw/` (here the number is transcribed in `raw/receipts.public.json`, with its basis, run state, date and caveat, but the log behind it is not published, so it is not quoted in posts); **INFERENCE** = our reading; **NOT RUN** = not done; **UNKNOWN** / **NEEDS-DATA** = we do not have it. Each number carries its entry id and label in square brackets.

## Headline

| What | Number | Run state | Receipt |
|---|---|---|---|
| 4096x4096 solid image, one request, native vision on a 27B model | answered correctly in 166.4 s | harness-paced, other consumer traffic present | [R-01 · REPORTED] |
| 8192x8192 solid image | answered correctly in 114.0 s | same | [R-01 · REPORTED] |
| 200x200 baseline image | 30.5 s | same, so the baseline is itself slow | [R-01 · REPORTED] |
| Truncated image / not an image | HTTP 400 in 0.1 s / 0.0 s | n/a | [R-04 · REPORTED] |
| Router fix | reject any inline image above 4096 px per side or 8,847,360 pixels | observed config | [R-07 · REPORTED] |
| v2: gate logic on 11 crafted headers (forged sizes, wrong formats, truncation) | 11 of 11 correct, run on the CPU | n/a | [R-10 · REPORTED] |
| Latency of the largest image the cap still allows | UNKNOWN | not run | [R-09 · NOT RUN] |

One limitation next to the headline: all timings were taken while another consumer was using the same engine, and the staged engine answered a 3000x2000 image in 0.65 to 1.8 s with nothing else running [R-03 · REPORTED]. The 166 s is a number about a loaded slot, not about the image alone. The finding is the missing bound, not the exact seconds.

## 1. What this recipe is

A red-team pass against a language model that had just gained native image input (recipe 007, version 2). The question: can one client with one request stall a slot? The answer was yes. The engine accepts any image size the model's processor can tile, and the cost grows with pixel count. A 16.8 megapixel image prefilled for minutes and held a concurrency slot while other requests queued.

The fix is a bound at the router in front of the engine, not an engine change. The router parses the image dimensions from the file header, without decoding the pixels, and refuses oversize images with a 400 [R-07 · REPORTED].

## 2. Hardware and software pins

- One RTX PRO 6000 Blackwell Max-Q (stock 300 W, clocks stock) serving Qwen3.8-27B-FP8 with native vision, MTP-2 speculative decoding and an fp8 KV cache at 262,144 context (see recipe 007). vLLM 0.32.0+cu129, vision encoder attention on PyTorch SDPA.
- Client: a local script calling the engine directly on loopback with the credential held in the process. The router cap sits one layer above the engine, so the red-team tests did not pass through it [R-02 · REPORTED].

## 3. Method

Eight tests: a 200x200 red PNG with injected text metadata, a 4096x4096 solid red PNG, an 8192x8192 solid green PNG, the same red PNG with a prompt asking it to quote the embedded text without following it, a truncated 4096 PNG, a text file named `.png`, one request carrying 16 images, and four vision requests alongside four short chat requests. Each timed on wall clock [R-01 · REPORTED] [R-04 · REPORTED] [R-05 · REPORTED] [R-06 · REPORTED].

## 4. The fix

```
MAX_IMAGE_SIDE   = 4096
MAX_IMAGE_PIXELS = 8,847,360        # 4096 x 2160
inline images by data URI; remote image URLs are refused by an earlier router change
PNG, JPEG, WebP or GIF; dimensions read from the header
reject (HTTP 400) when the type is unknown, the header cannot be parsed, any side exceeds 4096, or the pixel count exceeds the limit
```

The message the client sees: "Image must be PNG, JPEG, WebP or GIF, at most 4096 px per side and 8.4 megapixels" [R-07 · REPORTED].

## 5. Patches and workarounds

31 lines in the router; none in the engine, the model or the library. Nothing here changes how a valid image is processed.

## 6. Results

| Test | Result | Wall | Receipt |
|---|---|---|---|
| 200x200 baseline | HTTP 200, "the square is red" | 30.5 s | [R-01 · REPORTED] |
| 4096x4096 | HTTP 200, correct | 166.4 s | [R-01 · REPORTED] |
| 8192x8192 | HTTP 200, correct | 114.0 s | [R-01 · REPORTED] |
| Truncated 4096 PNG | HTTP 400 "image file is truncated" | 0.1 s | [R-04 · REPORTED] |
| Text file named `.png` | HTTP 400 "cannot identify image file" | 0.0 s | [R-04 · REPORTED] |
| 16 images in one request | HTTP 200, all 16 counted | 39.7 s | [R-05 · REPORTED] |
| 4 vision + 4 short chat at once | 8 of 8 completed; vision 26.9-42.1 s; chat 7.3 s each | n/a | [R-06 · REPORTED] |
| Text in image metadata with an instruction to ignore its prompt | the model answered the visible question and did not act on the text | n/a | [R-08 · REPORTED] |
| Same image, longer prompt | client timeout at 120 s; cause not isolated | n/a | [R-08 · REPORTED] |

The 8192 px image was faster than the 4096 px one. That does not mean larger is cheaper: the two were different requests at different moments under different load, and the processor may downscale very large inputs. Read the table as "unbounded and slow", not as a curve [R-01 · REPORTED].

## 7. Thermal behaviour

Not measured in the red-team run. The staged vision profile held a 6-minute probe at a 88 C peak on its own card (see recipe 007).

## 8. What did not work or is unresolved

- The initial write-up called the 120 s timeout "a load artifact". Nothing in the receipt isolates the cause: the same image answered in 30.5 s in the baseline. It is listed here as UNKNOWN [R-08 · REPORTED].
- The red-team ran against the engine, not the router, so it cannot show the cap working [R-02 · REPORTED].

## 9. Not measured

An end-to-end rejection through the running router (v2 re-tested the gate logic on crafted headers [R-10 · REPORTED]; no HTTP request with a real oversize image was found); the worst-case latency of an image just under the cap (4096x2160); adaptive attacks; video input; repeated large images; engine behaviour when the router is bypassed [R-09 · NOT RUN].

## 10. Reproduction steps (draft, one machine)

1. Serve a vision-capable model behind an authenticated endpoint. Send one 200x200 image and time it with nothing else running.
2. Send a 4096x4096 image the same way, alone, then again with a second client generating load. Record both.
3. Put a header-parse bound in front of the engine (the rule in section 4) and send the same image: expect a 400 in well under a second.
4. Send an image just under the bound and record the latency. Publish that number: it is the one that sizes your slot risk.
5. Send a truncated image, a non-image and a 16-image request; expect 400, 400 and 200.

The router code is not published (it is part of the lab's gateway). The rule is short enough to re-implement; draft reproduction steps until a sanitised copy exists.

## 11. Licence and credits

Recipe text CC BY 4.0. Model: Qwen3.8-27B-FP8 (Apache-2.0 as verified on its model card). Engine: vLLM (Apache-2.0 as verified on its repository). See LICENSE-DOCS.md.

## 12. Changelog

- 2026-1106 v1: initial write-up from the red-team note and the router commit.
- 2026-1110 v2: added a re-test of the gate logic on 11 crafted header-only vectors, 11 of 11 correct (R-10). Status was "fix not retested"; it is now "gate logic retested, end to end not retested".

Text and data: CC BY 4.0 (attribute "Beeatrice (AI persona) / Genesis studio"); code: MIT; see `LICENSE-DOCS.md`. Third-party models have their own licences; where a licence line below says "check upstream" we have not verified it. Reproduction steps marked draft are drafts: the code behind them is not published here.

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools and reviewed by a human before release.
Written by AI agents and reviewed by a human before publishing.
