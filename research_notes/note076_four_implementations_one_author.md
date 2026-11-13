# Note #076 — Four implementations, one author: what agreement between AI-written ports can show

**Status:** Speculative — one case observation plus a literature intake. No experiment registered or run for this
note. The case's own results are self-tested and live in Sovereign Veritas.
**Theme:** Verification / Independence / N-version programming
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's direction (2026-11-06). Review level: direction
only.
**Builds on:** [[note073_repair_verification_intake]] (a passing check is evidence only about what it can see),
[[note044_circularity_test]] (a test built under the tested system's assumptions carries little evidence).
**Method:** [METHOD.md](../METHOD.md) at commit `46034aa`.

## What went wrong, first

- **Update 2026-11-13, read first ([below](#update-2026-11-13)).** This note missed two facts that were already on
  record when it was written. A fifth implementation, by another family (OpenAI Codex), already existed. And it had
  already exposed a defect two of the Claude-written implementations shared (OVF-1). Also, a registered run
  (NOTE076-X1) found that two Claude-written ports differ off the vectors. The text below is kept as written.
- **The case's evidence is weaker than its result looks.** On 2026-11-06 a Rust port of the Sovereign Veritas
  Gate contract (`sv.gate/0`) matched all 4690 contract vectors on its first run (C7 in
  [`docs/GATE_CONTRACT.md`](https://github.com/holland202/sovereign-veritas/blob/main/docs/GATE_CONTRACT.md)). It is the
  fourth implementation to do so. All four were written by the same model family (Claude), and the Rust port's
  author had read the Go port's first 60 lines before writing it. Agreement among them is not the independent
  check it resembles.
- Nothing in this note was run for it. The C7 numbers are Sovereign Veritas's, self-tested.

## The claim

When every implementation of a specification comes from one author family, their agreement mostly measures how
consistently that family reads the specification, not whether the specification, or any one implementation, is
right. The claim is precisely wrong if implementations written from the same contract by *different* families
(other AI families, or people) agree with the same-family set at the same rate, including on the cases the
contract names as traps.

## Epistemic status (read first)

- **Established, not ours:** independently written versions fail together far more often than independence would
  predict (Knight and Leveson 1986). Different language models are wrong in the same way much more often than
  chance (Kim et al. 2025).
- **Observed here, one case:** four same-family implementations, zero disagreements on 4690 vectors, first-run
  conformance for both ports written from the contract (Go, C6; Rust, C7).
- **Ours, not tested:** that a different-family port would disagree on the contract's named traps more often
  than same-family ports do. Novelty is not claimed: this is N-version correlation applied to AI-written code.

## Known mathematics / prior art (verified 2026-11-06)

| Work | Verified | What it reports | Bearing |
|---|---|---|---|
| Knight and Leveson, *An Experimental Evaluation of the Assumption of Independence in Multiversion Programming*, IEEE Transactions on Software Engineering 12(1):96–109, 1986 | Yes (author PDF) | 27 versions written independently from one specification, each passing a 200-case acceptance test, run on one million inputs. "The number of tests in which more than one program failed was substantially more than expected" under independence. | Agreement between versions is not independent evidence even when the authors are different people |
| Kim, Garg, Peng and Garg, *Correlated Errors in Large Language Models*, arXiv 2506.07962 (v1, 2025-06-09); ICML 2025, PMLR 267:30038–30066 | Yes for the title, authors, venue, "over 350" models and the 60% sentence (PMLR abstract page, rechecked 2026-11-06). The 0.423 figure is from the paper's body and was **not** rechecked | Over 350 models. On one leaderboard dataset (Helm), "models agree 60% of the time when both models err"; on the Hugging Face leaderboard data, mean pairwise agreement when both are wrong is 0.423 | Different model families share errors too, so a cross-family port is more independent, not fully independent |

## The case (Sovereign Veritas, engineering evidence)

| Implementation | Written from | Result on 4690 vectors | Evidence label |
|---|---|---|---|
| Kernel Gate (`decision.py`) | itself (CONTRACT.md's rules were taken from it) | conforms | SELF-TESTED |
| `replay_gate` (`tools/verify_package.py`) | the same codebase | conforms | SELF-TESTED |
| Go port (C6) | CONTRACT.md (author had read the Python `replay_gate`) | conforms on first run | SELF-TESTED |
| Rust port (C7) | CONTRACT.md (author had read the Go port's first 60 lines) | conforms on first run | SELF-TESTED |

The contract's checker can fail a port: a one-line mutant of the Rust port gave `4 of 4690 vectors differ` (C7d),
and a mutant of the Go port gave 1 (C6). So the agreement above is not a blind checker. What it cannot show is
how a reader who does not share the author's habits would read the same text.

## The experiment (or: what one would look like) — proposed, not registered

Give `CONTRACT.md` (and nothing else from the repository) to authors from at least two other families (for example
ChatGPT, Gemini, and a person), each writing a port in a language of their choice. Run each port through
`tools/gate_contract.py` once, unchanged. Record per port: first-run conformance, and which vectors differ, grouped
by the contract's named traps (truthiness, `1` and `"true"` for `true`, `2.0` as a non-integer, Python equality,
`repr` and four-place rounding).

Candidate prediction (not frozen): at least one cross-family port differs on a named trap on its first run, while
both same-family ports did not. If every cross-family port also conforms on the first run, the contract is clearer
than this note's claim assumes, and the claim is refuted for this specification.

## Reference code

None for this note. The case's code is in Sovereign Veritas (`ports/go`, `ports/rust`, `tools/gate_contract.py`).

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes, for the proposed experiment: the number of willing cross-family authors bounds it |
| Noise | C-NOISE | No: the checker is deterministic on fixed vectors |
| Statistics | C-STAT | Yes, if a rate is ever claimed. None claimed here; one case |
| Evidence | C-EVID | No |
| Independence | C-INDEP | Yes: the whole note is about it. Every implementation in the case is same-family |
| External | C-EXT | Yes: two external works, checked against their pages |
| Device | C-DEVICE | No |
| Verdict code | C-BUILD | No new verdict code here |
| Exploration | C-EXPLORE | Yes: the question came from looking at the C7 result after the fact, so C7 cannot confirm it |
| Method comparison | C-METHCOMP | No |
| People's data | C-PRIVATE | No |
| Design | C-DESIGN | Yes: a single case; its strongest claim is that this happened once |
| Held-out | C-HOLDOUT | Yes, for the proposed experiment: the vectors are fixed and public; cross-family authors must not see the checker's output before their first run |
| Generated inputs | C-SYNTH | No |

## Falsifiable next predictions (M15)

- **Unrun:** a port of `sv.gate/0` written from `CONTRACT.md` alone by a non-Claude author differs from the
  conformance digest on its first run. If it conforms first time, the claim above loses its main support for this
  contract.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) checked the sources and drafted this note → human validation: not
performed → human editing/curation: direction by Chad Edward Holland, 2026-11-06 → human responsibility: Chad Edward
Holland. Review level: direction only.*

## Update 2026-11-13

Appended (M12). Status stays **Speculative**: nothing below tests the claim prospectively.

### What this note got wrong

1. **"All four were written by the same model family" left out a fifth implementation.** A port from another
   family was on Sovereign Veritas `main` when this note was written:
   `ports/python_independent/independent_gate.py`. It was written by OpenAI Codex at Putluru Sandeep's direction
   (SV PR #86, opened 2026-10-20, merged 2026-10-24). It was written from `CONTRACT.md` at `d3a9a88`, and it
   CONTRIBUTOR REPORTED 4,690/4,690 conformance. Its first run was not recorded, so it cannot score the prediction
   below.
2. **The note missed the case that bears most on its claim.** DIFF-001 (SV, registered 2026-10-22) compared the
   kernel Gate (K), the verifier (V) and that port (I) beyond the vectors. K and V raised `OverflowError` when the
   quality floor was an integer too large for a double, and I decided. K and V are both Claude-written, and they
   never disagreed with each other (DIFF-001 P2, 0 in 3,360,000 cases). They shared the defect, the vectors did not
   contain it, and the cross-family port exposed it. It was fixed as OVF-1 (SV PR #89, 2026-10-22). This is one
   instance of the claim's mechanism, found after the fact. Recording it does not confirm the claim.

### A same-family common-mode case outside this contract

Sovereign Memory Layer PDX-001 (SML PR #19, 2026-11-13). Three implementations, the Python reference and the Rust
and TypeScript ports, all Claude-written, shared two defects. Protected records decayed. And "current evidence not
retrieved" was reported as "insufficient evidence". The cross-implementation differential CI passed at `6262dbe`,
before the fix, while all three were wrong in the same way. A behavioural test written against the stated intent
caught it (MEM-DECAY-001 S1, in this repository). That test is also Claude-written, so this case shows agreement is
not correctness. It does not show that another family would have caught it.

### NOTE076-X1: registered and run on 2026-11-13

[Registration](../experiments/note076_x1/REGISTRATION.md) · [Results](../experiments/note076_x1/RESULTS.md).
Five implementations, six probes with out-of-range numbers, scored against the fixed kernel.

- **A2 REFUTED.** The Go port prints `0.2000<+Inf` where K, V, the Rust port and the Codex port print
  `0.2000<inf`. It does so on two probes, a floor of `10**400` and of `2**1024`. All five conform on the 4,690
  vectors. `CONTRACT.md` does not say how an infinite floor prints to four places, so the text does not decide
  between them.
- A1, A3 and A4 held. Controls held: the kernel before the fix crashes on the probe (C1), an always-ALLOW
  program differs (C2), and all five arms conform (C3).

**What this changes here.** Two Claude-written ports read one gap in the contract differently, each taking its
language's default. So "one family reads the contract one way" is too strong as stated. A better version, still
untested: same-family implementations share failures where they share *code or reasoning* (K and V; the three SML
implementations). Where the contract is silent they can still diverge on language defaults. And a check on fixed
vectors sees neither.

### Door (M15), replacing the candidate prediction above

The candidate prediction is now frozen as Part B of
[NOTE076-X1](../experiments/note076_x1/REGISTRATION.md) (B1–B3), with a fixed prompt
([PROMPT.md](../experiments/note076_x1/PROMPT.md)) so that a cross-family port's first run is recorded. **Unrun.**

*Provenance of this update (M13): Claude (Anthropic, Opus 5.5) found the omissions, registered, ran and wrote
NOTE076-X1, and drafted this update → human validation: not performed → human editing/curation: direction by Chad
Holland, 2026-11-13 → human responsibility: Chad Holland. Review level: direction only.*
