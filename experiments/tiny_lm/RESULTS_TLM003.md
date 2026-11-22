# TLM-003 results: at the same data budget, 3.2M parameters beat 1M (run 2026-11-21)

**Status:** run as registered at `7ab92eb` ([REGISTRATION_TLM003.md](REGISTRATION_TLM003.md)), seed 31.
Self-tested. **P1–P5 all HELD.**

Raw output: [`results/tiny_lm/003/runs/`](../../results/tiny_lm/003/runs/) (log, JSON, checks, all 20 samples,
weight hash).

## Limits first

1. **One seed.** P1's margin was set above TLM-002's seed-to-seed gap (0.0180), and the result cleared it by 0.0475.
   But one run is not a variance estimate.
2. **The stories are still not coherent** ("The water was very impatient. In the end, there were many dolls.").
   Bits per byte improved; plots did not visibly.
3. **The copied-span rate rose with size and training:** 1.4–3.2% (1M, 20.5M bytes), 2.8–4.5% (1M, 51.2M), 5.7%
   (3.2M). It is still under the 7.8% of real held-out stories, but it is trending toward it. Larger models will need
   this checked again.
4. **Self-tested; Linux CPU only; S25 NOT VALIDATED.** `shufcheck.py` was changed only to take the model size as
   arguments, as the registration stated. It still reproduces TLM-002's seed 22 (1.1242 / 10.5605).

## Registered verdicts (seed 31)

| ID | Prediction | Result | Verdict |
|---|---|---|---|
| P1 | valid bpb < 1.1062 | 1.0587 | HELD |
| P2 | valid bpb < 1.1736 (refit 8-gram) | 1.0587 | HELD |
| P3 | known-word rate ≥ 0.90 | 0.9947 | HELD |
| P4 | copied-span rate ≤ 0.20 | 0.0568 | HELD |
| P5 | shuffled-valid bpb ≥ 4.0 | 10.3601 | HELD |

Checks, verbatim:
```
shufcheck: {"valid_bpb": 1.0587, "shuffled_valid_bpb": 10.3601}
gencheck: {"words": 2281, "known_word_rate": 0.9947, "spans": 264, "copied_span_rate": 0.0568, "valid_stories_reference": {"words": 3006, "known_word_rate": 1.0, "spans": 358, "copied_span_rate": 0.0782}}
```
Run: 3,215,872 parameters, 51,200,000 bytes, 7,805 s on 2 threads. Last validation points (step, train bpb, valid
bpb): [5500, 1.0632, 1.0661], [5750, 1.1139, 1.0609], [6000, 1.0995, 1.059], [6250, 1.0776, 1.0587].

## The tiny story model line so far (same data slice and evaluation)

| Run | Parameters | Bytes seen | Valid bpb | vs 8-gram |
|---|---|---|---|---|
| TLM-001 | 1,018,624 | 20,480,000 | 1.3633 / 1.3698 | lost (1.2075) |
| TLM-002 | 1,018,624 | 51,200,000 | 1.1422 / 1.1242 | won (1.1736) |
| **TLM-003** | **3,215,872** | **51,200,000** | **1.0587** | **won (1.1736)** |

## What this supports

- At 51.2M bytes, the 1M model was capacity-limited: a 3.2M model trained the same way scored 0.0655 bpb lower
  than the better 1M seed. That is one seed, against a gap of 0.0180 between the two 1M seeds.
- Its loss was also still falling slowly at the end (1.0609 → 1.0587 over the last 500 steps).

## Next (unrun)

- A second 3.2M seed; a word-piece tokenizer; more data per run at 3.2M (needs more than this CPU, or an overnight
  run).
- Publishing this model alongside the 1M one.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level: direction
only.*
