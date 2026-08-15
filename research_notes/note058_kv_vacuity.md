# note058 — This has a name: vacuity detection, Kupferman & Vardi, 1999

**Status:** Draft, verified reference code
**Reference code:** `scripts/note058_reference.py`
**Contributors:** Chad Edward Holland; Claude (Anthropic) — literature search and reference code.

---

## The thing this estate has been measuring already has a name

`vacuity_lint.py`, the igar tests fixed in [[sovereign-evolution]], the Commit
Gate work in [[note054_k_x_allocation]]-adjacent SLC notes, and
[[note057_the_loud_type_a]] are all instances of one question with a 27-year
literature: **can a check pass for a reason that has nothing to do with what it
was meant to verify?**

Kupferman and Vardi named it *vacuity* in model checking (CHARME 1999; STTT
2003). Formally: a system M satisfies a formula φ vacuously iff M ⊨ φ and there
is some subformula ψ of φ such that ψ does not affect φ in M. Their motivating
example is `G(req -> F grant)` — "every request is eventually followed by a
grant" — which is satisfied vacuously in any system where `req` never fires.
The implication is true on every step, for a reason that has nothing to do
with grants ever being issued.

That is exactly the shape of every inert gate this estate has found. The
Commit Gate's Fisher threshold held at J = +0.000 not because it discriminated
correctly but because it admitted almost nothing. `test2_honest_failure.py`
exited 0 not because the answer was right but because no code path could ever
return 1. Same structure: a check whose passing condition never depended on
the thing it claimed to check.

```
G(req -> F grant) holds: True
but req fired 0 times out of 0 steps
P1: CONFIRMED
```

---

## Where this estate's method already matches the literature, and where it goes further

The literature's core technique is **mutation**: perturb the specification (or
the system) and check whether the verdict changes. If it doesn't, the check
wasn't testing that part. Kupferman, Li and Seshia (FMCAD 2008) formalize this
directly, unifying vacuity, coverage and fault tolerance under mutation theory.

`--sabotage`, added to the igar tests and `note057_reference.py` this week, is
exactly this: force the wrong branch, require exit 1. `vacuity_lint.py`'s own
`gate.yml` fix plants a known-defective file and requires the scan to reject
it before trusting a clean scan. Both are mutation testing, independently
arrived at, before either of us knew the name.

Where this estate's notes go further than the classical literature: Kupferman
& Vardi ask whether a check *can* fail. [[note057_the_loud_type_a]] asks a
question their framework doesn't have a slot for — whether a check that
correctly detects a failure still *reports* it. `test2_honest_failure.py`
printed `DANGER: returned {'Z1'}`, independently re-verified the answer was
wrong, and exited 0. To a vacuity detector this is identical to a check that
says nothing at all; to a reader of the log, it is worse, because the output
looks like diligence. This is closer to Chockler, Gurfinkel & Strichman's
"Beyond vacuity: towards the strongest passing formula" (FMCAD 2008), which
distinguishes a check that barely passes from one that passes robustly — but
even that paper is about the verdict, not about what the check *announces* on
its way to a verdict it then discards.

---

## Registered predictions

- **P1 — CONFIRMED.** The Kupferman-Vardi example reproduces exactly: a
  specification holds for a reason unrelated to its intent when its
  antecedent never fires.
- **P2 — CONFIRMED, run live against the estate.**

```
  repositories cloned      : 13
  python files scanned     : 180
  repositories with any CI : 4
  total vacuity findings   : 11
    principia-artificialis: 3 finding(s) in 58 files
    slc-v12-: 3 finding(s) in 29 files
    skn-v1-: 1 finding(s) in 19 files
    sovereign-suite: 2 finding(s) in 10 files
    polytope-explorer: 1 finding(s) in 2 files
    quasar-v2: 1 finding(s) in 27 files
  finding rate: 11/180 = 6.1%
```

Kupferman & Vardi report roughly 20% of LTL specifications register
vacuously in industrial verification. This estate's Python code registers
at 6.1% by `vacuity_lint.py`'s definition. The two numbers are not directly
comparable — different artifact type, different detector, different
population — and the note does not claim they are. What is comparable is
the *shape*: neither number is zero, and in both cases the finding was
invisible to the tool that was supposed to catch it (a model checker
returning SAT; a CI badge showing green) until someone asked the second
question.

- **P3 — PASS, after fixing a real bug the first attempts exposed.** The
  reference script's P2 block called `os.chdir(d)` inside a
  `TemporaryDirectory()` and never restored it. When that block exits, `d`
  is deleted from disk, but the process's own working directory is still
  pointed at it -- `os.getcwd()` from that state raises `FileNotFoundError`.
  P3's clone runs afterward with no `cwd=` set, so it silently inherited the
  now-deleted directory and `git clone` failed with exit 128 ("could not
  create work tree dir: No such file or directory"). `clone()` only checks
  the return code, so this printed as "could not clone -- network
  unavailable," which was false: reproduced twice, 15 seconds apart,
  immediately after a P2 run that had just cloned the identical repository
  successfully in the same process. Confirmed with a minimal repro (chdir
  into a `TemporaryDirectory`, let it close, run any subprocess with no
  `cwd=`) before touching the fix. Corrected by removing `os.chdir`
  entirely and passing `cwd=` explicitly to every subprocess call in P2.
  After the fix: scanner returns zero findings, not an error, on a
  genuinely clean file -- `findings : 0`, exit 0, process CWD confirmed
  unchanged before and after the whole run. The anti-vacuity requirement:
  an instrument that only ever reports findings is itself the defect this
  note is about -- and, it turned out, so is a diagnostic message that
  names the wrong cause.

---

## What this note does not claim

It does not claim this estate's Python heuristic (`assert`/`raise`/nonzero
exit presence) is equivalent to LTL vacuity detection, which operates over a
formal specification language with a decidable satisfaction relation. Python
source has neither. The scanner is a syntactic proxy, and a coarse one — note
that P3's clean-file check and `note057`'s false-positive discussion
(`make_index.py` matching the string "REFUTED") are both about that
coarseness. The claim here is narrower and, I think, correct: the *category*
of failure — a check whose truth value doesn't depend on the thing it was
meant to check — is the same category in both domains, has a name, has 27
years of literature, and this estate's tools reinvent pieces of that theory
independently.

---

## Open, unrun

Chockler & Strichman's "easier and more informative vacuity checks" (MEMOCODE
2007) proposes ranking vacuous results by how *trivially* the specification
could be mutated and still pass — a severity ordering, not just a binary
finding. `vacuity_lint.py` currently reports NO_FAIL_PATH / PRINTS_FAIL_ONLY
as flat categories with no severity axis. Whether their ranking method
transfers from LTL mutation to source-level heuristics (what does "trivial
mutation" mean for a Python function with no formal spec?) is unrun and may
not transfer cleanly — the formal notion of a subformula doesn't have an
obvious source-code analogue.

---

*Vincit Omnia Veritas.*
