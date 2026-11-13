# NOTE076-X1 Part B: the prompt, frozen

Paste everything between the two lines below into a fresh chat. Then paste the full text of `CONTRACT.md` from
Sovereign Veritas at commit `7be4909ea6bd960e41cdb0b5ce87cd20758b5aa2` directly after it. Change nothing.

---

Below is a specification called `sv.gate/0`. Write one program that implements it, in a language of your choice.

Requirements:

- It reads one JSON object per line on standard input, `{"id": ..., "input": {...}}`, and writes one JSON object per
  line on standard output, `{"id": ..., "decision": ..., "reasons": [...]}`, in the same order.
- Use the language's standard library only.
- Work from the specification text alone. Do not look anything up and do not run code. The specification mentions
  test vectors and a checker; you do not have them.
- Give the complete source in fenced code blocks, and the exact command to build it (if needed) and to run it.

This is a test of how clearly the specification is written. Your program will be run once, exactly as you give it.

---
