# Derived and transcribed files in this folder

- `build_receipt.json`: the build receipt with the build directory line removed, times converted to UTC, the name of the build log removed and an internal job description reworded. Every other field is unchanged.
- `launch_flags.txt`: transcribed from the start script with paths, the listen address and the port replaced by placeholders.
- `review_scoreboard.csv`: transcribed by hand from the reviewer's table, with the word counts from the metrics file added. The reviewer's `wc` counts are REPORTED: the saved outputs are not published.
- `server_log_extra_lines.txt`: more lines from the same server log than `glm-server-log-excerpt.txt` holds (the last prompt-processing line of each request before each error, the first KV-space warning, the fifth episode's errors), selected by a script, with paths removed and time stamps shortened to T+MM:SS.mmm. Lines already in the main excerpt are not repeated. It also holds the error, release and cancel lines of episodes 6 to 14.

Left out on purpose: the full server log, the saved outputs of the jobs, the prompts, and the start and stop scripts.

## Errata to the original files (they are kept unchanged, byte for byte)

- `glm-contention-timeline.md` and the header of `glm-server-log-excerpt.txt` call the second request in the parallel pair "about 23.7k tokens". That figure is the token count in the second slot's release line, which is held tokens plus a batch that did not fit. The second prompt's true length is UNKNOWN; the progress field suggests about 117,000 to 124,000 tokens (RECIPE.md section 8).
- `glm-contention-timeline.md` gives the time of a manual interrupt (in the studio's local time); by the clock offset of the other episodes the server error of the fifth episode came about 10 s before it.
- `glm-server-log-excerpt.txt`: its header line lists three durations (tasks 14283, 15047 and 15826). A fourth, task 16611, also ended 242.3 s after launch, so there are four episodes of that kind (2 to 5); its error lines are in `server_log_extra_lines.txt`.
- `glm-contention-timeline.md`: "two sessions that each need more than half of the cache cannot coexist" is superseded. It rests on the second request being about 23.7k tokens or about half the pool; the second prompt's true length is UNKNOWN (RECIPE.md section 8). "first-token time ranged from 5 s to 245 s depending on that load" is also superseded: the spread is partly contention and partly reasoning length, which we did not separate (RECIPE.md section 7). The note covers events only up to about 02:29 UTC.
- `glm-kv-and-context-arithmetic.md`: "147.2 GiB" for weights plus projector is 147.14 GiB by the file sizes; "80.5 GiB and 79.8 GiB used" for 80,492 and 79,775 MiB should read 78.6 and 77.9 GiB; "about 24 GiB" at 1,048,576 tokens is 22.0 GiB by the 22,528 bytes per token it also gives.
- `glm-smoke-summary.csv`: the note "200-token text answer" for the first check; 79 tokens were generated.
- `glm-text-task-metrics.jsonl`: `completion_tok_s_overall` for T5 is 27.4; 1,554 / 56.6 is 27.46 (rounding of the wall time).

Beeatrice is an AI-generated persona. Her images, words and designs are made with AI tools.
Written by AI agents; approval for publication by the studio owner is pending (the date is added after his yes).
