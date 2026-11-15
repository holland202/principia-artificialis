# CST-001 feasibility, second model: Qwen2.5-7B-Instruct (4-bit, llama.cpp)

**State:** gate written 2026-11-15, before any 7B output was scored. Chad Holland chose a larger model run on this
machine (2026-11-15). Dev split only; the test split stays sealed. Self-tested.
**Model:** `Qwen/Qwen2.5-7B-Instruct-GGUF` revision `bb5d59e`, Q4_K_M, files `…00001-of-00002.gguf` (SHA-256
`dfce12e3…72db`) and `…00002-of-00002.gguf` (SHA-256 `539cf93f…d72a`). llama-cpp-python 0.3.37, temperature 0,
top-k 1, 2 CPU threads. The Q4 quantization is part of what is tested: results describe this file, not the
full-precision model.

## Gate, fixed before any 7B result is seen

Arms E (explicit instruction) and D (none) run first on the 64 dev pairs. Arms A, B and C run only if **both** hold:

1. E gets at least 16 of 64 pairs right (25%), so the assay can see the behaviour at all;
2. E gets more pairs right than D.

If the gate fails, CST-001 stops for this model too, and the result is recorded the same way as for the 1.5B model.
Two timing calls (arm D, first dev pair) were made before this gate was written. Their outputs were discarded and
not scored. Greedy decoding reproduces them.
