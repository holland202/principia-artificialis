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
| Kim, Garg, Peng and Garg, *Correlated Errors in Large Language Models*, arXiv 2506.07962 (v1, 2025-06-09) | Yes (arXiv page; venue not stated on the page read) | Over 350 models. On one leaderboard dataset (Helm), "models agree 60% of the time when both models err"; on the Hugging Face leaderboard data, mean pairwise agreement when both are wrong is 0.423 | Different model families share errors too, so a cross-family port is more independent, not fully independent |

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
