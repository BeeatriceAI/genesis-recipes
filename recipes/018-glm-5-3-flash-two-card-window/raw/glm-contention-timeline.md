# What shared the model server during the GLM window (times local, evening of 2026-11-13)
Two sessions of the owner's coding-agent tool used the same server as the text jobs. All numbers are from the server log.
- 21:09-21:11 Session A (a 220k-238k-token conversation): turns finish in 1-10 s because the conversation's cache sits in one slot.
- 21:11-21:28 Session A also sent a second ~23.7k-token request in parallel. The two requests together (about 263,700 tokens) passed the 262,144-token shared cache, and the SERVER ended both with "Context size has been exceeded" (and earlier "failed to find free space in the KV cache"). Each end came about 242 to 243 s after the 240k-token request started, which is how long that prompt took to process; the log does not show a client giving up, so any client time limit is UNKNOWN. Each retry re-read the full prompt because the caches had been dropped. Error times 21:11:58, 21:16:03, 21:20:10, 21:24:22; interrupted by a person at 21:28:44.
- 21:29 onward Session B (an agent loop, prompt 117k-129k tokens and growing) used one slot with a warm cache: a request every 8-10 s.
- Text jobs run beside it: first-token time ranged from 5 s to 245 s depending on that load (see glm-text-task-metrics.jsonl).
- The unified-cache lesson: two sessions that each need more than half of the cache cannot coexist.
