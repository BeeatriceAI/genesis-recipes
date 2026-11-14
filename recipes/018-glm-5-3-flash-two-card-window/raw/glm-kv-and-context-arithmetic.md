# GLM-5.3-Flash context and memory arithmetic (UD-IQ4_XS, llama.cpp v1.0.0, two GPUs)
READ = from a file or log. ESTIMATE = arithmetic.
- Declared maximum context in the model file: 1,048,576 tokens (READ). No rope-scaling or YaRN fields in the file (READ). The model card evaluates at 1M (one benchmark), 400K and 164K (READ) and states no recommended maximum.
- Run: context 262,144, 2 slots sharing one unified cache, f16 cache (defaults).
- Memory after load: about 80.5 GiB and 79.8 GiB used on the two GPUs (READ), against about 3.1 GiB used by the desktop before load. GLM total about 153.5 GiB.
- Weights plus vision projector: 147.2 GiB (READ from file sizes). So cache plus buffers is at most about 6.3 GiB at 262,144 tokens (ESTIMATE: 153.5 - 147.2).
- Per-token cache: 11 attention layers x 1 KV head x (512 + 512 values) x 2 bytes = 22.0 KiB (22,528 bytes) per token (ESTIMATE from file metadata). At 1,048,576 tokens that is about 22 to 24 GiB, so a full-length window would fit on the two GPUs (about 34 GiB was still free after load) (ESTIMATE, not loaded).
- Speeds measured (single request, idle server): decode 49-53 tokens/s; prefill 1,605 tokens/s at 30k tokens, 1,428 tokens/s at 126k, about 1,090 tokens/s at 240k (READ from server timings).

## Added with owner-cleared hardware figures
- Each GPU has 97,887 MiB of memory (the hardware block published in recipe 006 v0.2).
- After the model loaded (context 262,144, 2 slots), the two GPUs showed 80,492 MiB and 79,775 MiB used, leaving 17,395 MiB and 18,112 MiB free (READ from the GPU tool; the second GPU also carries about 2.9 GiB of desktop use).
- So a 1,048,576-token window (about 24 GiB of cache by the estimate above) needs about 18 GiB more than the 6 GiB used at 262,144, against about 34.7 GiB free: it fits on paper (ESTIMATE, not loaded).
