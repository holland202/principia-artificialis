# NOTE076-X1: do the five `sv.gate/0` implementations agree just past the vectors' edge? And a frozen cross-family arm

**State:** REGISTERED, NOT RUN. Committed before the scorer exists and before any probe below has been sent to any
implementation.
**Authors:** Direction: Chad Holland (2026-11-13, "pick a subject … and let's work on it"). Design: Claude
(Anthropic, Opus 5.5). Human review level: direction only. Everything run here is **self-tested** (M10).
**Note:** [note076](../../research_notes/note076_four_implementations_one_author.md).
**Method:** [METHOD.md](../../METHOD.md).
**Code under test:** Sovereign Veritas `main` at `7be4909ea6bd960e41cdb0b5ce87cd20758b5aa2`, which also pins
`CONTRACT.md` and `contract/gate_vectors.jsonl`. One control uses `7a8578a140492a31774f42e226c7300caf5bf303`, which is
`main` before the OVF-1 fix.

## Why

note076 says the four `sv.gate/0` implementations agree because one author family wrote them. While picking it up on
2026-11-13 I found two things it missed, both older than the note:

1. A fifth implementation, by a different family, already existed: `ports/python_independent/independent_gate.py`
   (OpenAI Codex, directed by Putluru Sandeep, SV PR #86, 2026-10-20).
2. Comparing it with the Claude-written kernel (K) and verifier (V) beyond the vectors found a defect K and V shared:
   an integer quality floor too large for a double made both raise `OverflowError`. The Codex port decided instead
   (OVF-1, fixed by SV PR #89 on 2026-10-22).

The Go port (G, 2026-09-27) predates that fix and has not changed since. The Rust port (R, 2026-11-06) postdates it.
OVF-1 lists the Go port as not covered. This experiment asks whether the five implementations agree on a small, fixed
set of inputs of the same class: out-of-range numbers in the quality floor and the quality.

**Exploration disclosure (C-EXPLORE).** I chose this input class after reading OVF-1's results, and I know it
separated K and V from the Codex port once. So Part A can describe this one class; it cannot confirm note076's claim.
What I do not know: whether G, R or the Codex port agree with the fixed K on these six probes. I have not read the
Codex or Rust port's number handling. I have seen four lines of the Go port's number helpers, in a search result: the
signatures of `isNum`, `isIntLiteral` and `toFloat`, and a comment saying `toFloat` keeps `ParseFloat`'s ±Inf on
overflow.

## Part A: runnable now

### Implementations

| Arm | What | Author family | Command |
|---|---|---|---|
| K | kernel Gate, `sovereign_veritas/decision.py` | Claude | `serve_kernel.py <sv root>` (this directory) |
| V | `replay_gate`, `tools/verify_package.py` | Claude | `python3 tools/gate_contract.py --serve verifier` |
| G | Go port, `ports/go` | Claude | `ports/go` binary built with `go build` |
| R | Rust port, `ports/rust` | Claude | `ports/rust/target/release/svgate` |
| I | independent Python port, `ports/python_independent/independent_gate.py` | OpenAI Codex | `python3 ports/python_independent/independent_gate.py` |

### Probes, fixed now

Base input: the first vector in `contract/gate_vectors.jsonl` whose expected decision is ALLOW, with
`record.evidence_quality` set to `0.2`. This is the base OVF-1's regression test uses. Each probe changes one or two
fields of the base:

| Probe | `capability.min_evidence_quality` | `record.evidence_quality` |
|---|---|---|
| Q1 | `10**400` | 0.2 |
| Q2 | `-(10**400)` | 0.2 |
| Q3 | `2**1024` (the smallest power of two a double cannot hold) | 0.2 |
| Q4 | `10**308` (an integer a double can hold, approximately) | 0.2 |
| Q5 | `10**400` | `10**400` |
| Q6 | 0.5 | `-(10**400)` |

Each probe goes to each implementation as its own process: one line `{"id": "Qn", "input": …}` on stdin, in canonical
JSON (sorted keys, no spaces, as `gate_contract.py` writes). The outcome is the `(decision, reasons)` pair printed,
or `CRASH`, which covers a non-zero exit, no output line, or an output line that is not a decision.

Two outcomes are the same when the decision and the reasons list are identical, order included.

### Predictions

| ID | Prediction | My belief, for calibration only |
|---|---|---|
| A1 | V's outcome equals K's on all six probes | 0.9 |
| A2 | G's outcome equals K's on all six probes | 0.55 |
| A3 | R's outcome equals K's on all six probes | 0.5 |
| A4 | I's outcome equals K's on all six probes | 0.8 |

### Controls (anti-vacuity, M3)

| ID | Control | Registered expectation | If it fails |
|---|---|---|---|
| C1 | K at `7a8578a` (before the OVF-1 fix) on Q1 | `CRASH` (OVF-1 R1 recorded an `OverflowError`) | The probe runner cannot see the defect this class is known for; Part A is void |
| C2 | A command that prints `ALLOW` with no reasons for every case | differs from K on at least one probe | The comparison cannot say "differ"; Part A is void |
| C3 | All five arms on the 4,690 vectors through the scorer | each `CONFORMS` with digest `44823d0f…0628` | The build or the runner is wrong; scoring stops until fixed |

C3 also checks the scorer's vector path. A scorer that never reports a mismatch would pass C3, so its tests must
include a sabotaged port that it reports as differing (C-BUILD).

### Interpretation, fixed now

- A disagreement says at least one implementation, or the contract text, is wrong or unclear for that input. It does
  not say which. Fault is assigned only by reading `CONTRACT.md`'s rules for that input, reported probe by probe.
- If G or R disagrees with K, then same-family ports can differ off the vectors. That weakens note076's "one family
  reads the contract one way" and has to be written up as such.
- If G or R crashes where pre-fix K crashed, that is a common-mode failure within the family on this class.
- If all of A1–A4 hold, the class no longer separates anyone after the fix. Six probes say nothing about other classes.
- n is one input class with six probes. No rate is claimed (C-STAT).

## Part B: frozen, needs Chad (not run)

This replaces the candidate prediction in note076. A cross-family port is only informative if its first run is
recorded. PR #86 reports the Codex port's final conformance, not its first run.

**Procedure.** Chad opens a fresh chat in each of at least two non-Claude assistants (for example ChatGPT, Grok,
Kimi). He turns web browsing and code execution off where the product allows, and records the product, model and
version it shows, and whether tools were on. He pastes [PROMPT.md](PROMPT.md) followed by `CONTRACT.md` at
`7be4909`. He saves the whole reply unedited as `ports_received/<assistant>/reply.md` and commits it before anything is
run. The code is taken from the reply's fenced code blocks, unchanged. If it needs building, the reply's own build
command is tried once. Nothing in the code is edited. The first run is this one run. A second run is never counted.

**Predictions (frozen):**

| ID | Prediction |
|---|---|
| B1 | At least one received port does not conform on its first run (`VERDICT N of 4690 vectors differ`, or `COULD NOT RUN`) |
| B2 | Of the received ports that run, at least one has a mismatch with an `X:` id (the 20 cases pinning the traps `CONTRACT.md` names) |
| B3 | Every received port that runs gives K's outcome on all six Part A probes |

**Refutation of note076's claim on this contract:** if every received port conforms on its first run and B3 holds, the
claim loses its support for `sv.gate/0`. That outcome is recorded as such.

**Holdout (C-HOLDOUT).** Authors see `CONTRACT.md` and the prompt only. They see no vectors, no checker output and no
other port. Nobody tells them how they did before their first run is recorded.

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Part A: yes, Go and Rust toolchains are present here. Part B: bounded by Chad's time and which assistants he uses |
| Noise | C-NOISE | No: all five implementations are deterministic; each probe can be re-sent |
| Statistics | C-STAT | No rate is claimed; six probes, one class |
| Evidence | C-EVID | Self-tested engineering evidence (M10) |
| Independence | C-INDEP | Yes, it is the subject. Four of five arms are Claude-written. The scorer and the probes are also Claude-written |
| External | C-EXT | The Codex port is outside material. It is run as published at `7be4909`, unchanged |
| Device | C-DEVICE | No: run in a Linux x86_64 container, not on the S25 |
| Verdict code | C-BUILD | Yes: the scorer fails closed (a crash or bad line is `CRASH`, never agreement) and its tests include a sabotaged port |
| Exploration | C-EXPLORE | Yes, disclosed above |
| Method comparison | C-METHCOMP | No |
| People's data | C-PRIVATE | No |
| Design | C-DESIGN | Part A: fixed probes on existing code; descriptive for one class |
| Held-out | C-HOLDOUT | Part B, above |
| Generated inputs | C-SYNTH | Six hand-fixed probes. Each is printed in full in the results |

## Door (M15)

Part B is unrun. So is any input class other than out-of-range numbers.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed and wrote this registration → human validation: not
performed → human editing/curation: direction by Chad Holland, 2026-11-13 → human responsibility: Chad Holland.
Review level: direction only.*
