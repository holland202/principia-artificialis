# NOTE076-X1 results, Part A: the Go port prints `+Inf` where the other four print `inf`

**State:** Part A RUN and scored against [REGISTRATION.md](REGISTRATION.md) (commit `135e891`). The scorer was
committed after it, at `057423a`, before any probe was sent. Part B NOT RUN. Self-tested (M10).
**Authors:** Direction: Chad Holland (2026-11-13). Design, code, run and write-up: Claude (Anthropic, Opus 5.5).
Human review level: direction only.
**Raw outputs:** [results/note076_x1/](../../results/note076_x1/), unedited: `c3_vectors.txt`, `probes_*.txt`,
`compare.txt`, `environment.txt`, `tests.txt`.

## Failures first

1. **A2 REFUTED.** The Go port (G) disagrees with the kernel (K) on two of the six probes, Q1 and Q3: the quality
   floor is an integer too large for a double. All five arms decide DEFER, for the same reason, but the reason
   string differs in how it prints the infinite floor:

   | Arm | Q1 and Q3 outcome |
   |---|---|
   | K, V, R, I | `DEFER ["evidence_quality_below_threshold:0.2000<inf"]` |
   | G | `DEFER ["evidence_quality_below_threshold:0.2000<+Inf"]` |

   G's `fixed4` (`ports/go/main.go:193`) is `strconv.FormatFloat(f, 'f', 4, 64)`, and that is what Go prints for
   +Inf. The Go port is from 2026-09-27. K and V learned to print `inf` here in the OVF-1 fix (SV PR #89,
   2026-10-22). Before that they raised `OverflowError` (control C1, below). The fix did not touch the Go port, and
   OVF-1 listed it as not covered. All 4,690 vectors still pass for G (C3), because no vector has an infinite floor.
2. **Fault assignment, from reading `CONTRACT.md` at `7be4909`: the contract does not decide this case.** Rule 10
   says an integer too large for a double is ±infinity and that the floor is printed to four places. Formatting says
   four-place values are fixed-point with exactly four decimals. It says what `<q>` prints for infinity (`inf`,
   `-inf`). It says nothing for an infinite *floor* printed to four places. So `inf` is the fix's choice, not a rule
   the text states, and G is not wrong by the text. The text is incomplete.

## Scoring

| ID | Prediction | Belief | Result |
|---|---|---|---|
| A1 | V equals K on all six probes | 0.9 | **HELD**: 6 agree, 0 differ |
| A2 | G equals K on all six probes | 0.55 | **REFUTED**: 4 agree, 2 differ (Q1, Q3; `+Inf` vs `inf`) |
| A3 | R equals K on all six probes | 0.5 | **HELD**: 6 agree, 0 differ |
| A4 | I equals K on all six probes | 0.8 | **HELD**: 6 agree, 0 differ |

## Controls

| ID | Control | Expected | Result |
|---|---|---|---|
| C1 | K before the OVF-1 fix (`7a8578a`) on Q1 | CRASH | **HELD**: `exit 1, 0 lines; stderr: OverflowError: int too large to convert to float`. It also crashes on Q3 and agrees with fixed K on Q2, Q4, Q5, Q6 |
| C2 | Always-ALLOW command | differs from K on at least one probe | **HELD**: 1 agrees (Q2), 5 differ |
| C3 | All five arms on the 4,690 vectors | each CONFORMS, digest `44823d0f…0628` | **HELD**: all five `L=0 S=0 X=0`, digest `44823d0ff707213ae8bc310ed8b21e135f8e742fd8834e8f9474743d3a250628` |

Scorer tests: `7 passed`. They include a port sabotaged on `X:` vectors, a crashing port and a probe-file
comparison that must say DIFFER.

## The six outcomes K gives

| Probe | Floor | Quality | K |
|---|---|---|---|
| Q1 | `10**400` | 0.2 | `DEFER ["evidence_quality_below_threshold:0.2000<inf"]` |
| Q2 | `-(10**400)` | 0.2 | `ALLOW []` |
| Q3 | `2**1024` | 0.2 | `DEFER ["evidence_quality_below_threshold:0.2000<inf"]` |
| Q4 | `10**308` | 0.2 | `DEFER ["evidence_quality_below_threshold:0.2000<1000…0336.0000"]` (the double's exact value, 309 digits, in `probes_K.txt`) |
| Q5 | `10**400` | `10**400` | `DEFER ["evidence_quality_invalid:inf"]` |
| Q6 | 0.5 | `-(10**400)` | `DEFER ["evidence_quality_invalid:-inf"]` |

All five arms agree on Q4: the 309-digit exact value of the double nearest `10**308`, to four places.

## What this does and does not show

Following the registered interpretation:

- **Two same-family ports differ off the vectors.** G and R are both Claude-written from `CONTRACT.md`, and they print
  this case differently. This weakens note076's "one family reads the contract one way". On a gap the contract leaves
  open, each port took its language's default. Go's default is `+Inf`. Rust's matched Python's here.
- **It is not a common-mode crash.** G never crashed where pre-fix K did. So in this class the family's shared failure
  (K and V raising `OverflowError`) belonged to the Python code, not to every port the family wrote.
- **What the vectors measure.** Five implementations conform on all 4,690 vectors and still disagree here. Off the
  vectors, the conformance digest says nothing. That is CONTRACT.md's own caveat ("not on every possible input"),
  now with an instance.
- **Limits.** This is one input class, chosen after OVF-1 (C-EXPLORE), with six probes. It is descriptive and cannot
  confirm note076's claim. Only the cross-family port I is from another family, and it agrees with K. Its file is
  unchanged since PR #86 (2026-10-20), so it printed `inf` before the fix existed. The fix's choice of `inf` may
  have followed it; the OVF-1 records do not say.

## Doors

- **Part B (NOT RUN):** fresh cross-family ports with first runs recorded, per the frozen [PROMPT.md](PROMPT.md).
- **SV (not done here, needs a decision there):** either `CONTRACT.md` states how an infinite floor prints (and a
  vector pins it, which changes the vectors file and the digest), or the Go port's `fixed4` maps ±Inf to `inf` and
  `-inf`. Both are changes to Sovereign Veritas under its own change control.
- Input classes other than out-of-range numbers are unrun.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, wrote and ran this and wrote it up → human validation: not
performed → human editing/curation: direction by Chad Holland, 2026-11-13 → human responsibility: Chad Holland.
Review level: direction only.*
