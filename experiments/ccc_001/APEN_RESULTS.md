# CCC-001 A-penalty: results

**Status:** 4 of 4 as registered, SELF-TESTED, development-only (C-EXPLORE). Registration
[APEN_PREREG.md](APEN_PREREG.md) at `f58daf6` (committed alone), run at `568ecff`, outcome pinned in the next
commit. No model was loaded. **No earlier verdict changes** (M12).

## What could have gone wrong, first

- **Self-tested, not blind.** Claude designed, wrote, ran and reads this. ChatGPT's rules (relay turns 028 and 030)
  are design input, not review. No human reviewed it.
- **The accept aggregates were known before registration.** Claude derived pen₁, pen₂, pen₃ and I_acc by hand from
  published ACCBIAS numbers while writing the registration, and disclosed approximate values there
  (≈ −0.136, −0.344, −0.257; I ≈ +0.165). The code reproduces them: `-0.135780 -0.344463 -0.256645`, I `+0.164775`.
  So only the item counts (P1, P2) and the reject and not-enough penalties (P3) were open.
- **P1 and P2 thresholds are a simple majority** with no decision behind them. 17 of 24 and 15 of 24 pass it;
  15 of 24 is not far above it.
- **A registered statistic turned out uninformative.** The shuffle null's "fraction |I| ≥ |observed|" compares
  magnitudes, but the shuffled I is not centred on zero (p50 `-0.260425`), so 1929/2000 says nothing about accept.
  Recorded, not replaced.
- **Model-derived only:** one unqualified 1.5B model, 24 development items, one instruction wording. Nothing here is
  about conversations, and nothing can confirm CCC-001.
- Deviations from the registration: none known.

## Raw output (`results/ccc_001/apen_run.txt`, verbatim)

```
P0a 27 rebuilt cell means vs accbias.json: max |diff| 4.89e-07 (<= 1e-6)
P0b identity E:=D: 432 per-item and 18 aggregate contrasts exactly 0: True
P0c synthetic additive: want I +0.00 J12 +0.00 J13 +0.00; max |err| over 24 items 5.55e-17 (<= 1e-12)
P0c synthetic A1+k: want I +0.05 J12 +0.05 J13 +0.05; max |err| over 24 items 9.71e-17 (<= 1e-12)
P0c synthetic A2+k,A3-k: want I +0.00 J12 -0.05 J13 +0.05; max |err| over 24 items 6.94e-17 (<= 1e-12)
P0d linearity: |I from cells - mean item I| max 5.55e-17 (<= 1e-12)
P0 HELD rebuild, identity, synthetic and linearity gate (a-d all required)
P1 HELD accept items with I > 0: 17 of 24 (>= 13); negative 7, tied 0
P2 HELD accept items with J12 > 0: 20 of 24, J13 > 0: 15 of 24 (each >= 13)
P3 HELD pen-bar < 0 for all three meanings: accept -0.245629, reject -0.254875, notenough -0.185967
REPORT accept: pen1 -0.135780 pen2 -0.344463 pen3 -0.256645 pen-bar -0.245629 | J12 +0.208684 J13 +0.120866 I +0.164775
REPORT   accept item counts +/-/tied: pen1 9/15/0 pen2 3/21/0 pen3 5/19/0 J12 20/4/0 J13 15/9/0 I 17/7/0
REPORT   accept item I range: min -0.259209 (item 3) max +0.665810 (item 8)
REPORT   accept within-row first-slot contrast d(L,1) - mean(d(L,2), d(L,3)): A +0.254245 B +0.146669 C +0.032273
REPORT reject: pen1 -0.682118 pen2 -0.090502 pen3 +0.007994 pen-bar -0.254875 | J12 -0.591616 J13 -0.690111 I -0.640864
REPORT   reject item counts +/-/tied: pen1 0/24/0 pen2 9/15/0 pen3 10/14/0 J12 0/24/0 J13 0/24/0 I 0/24/0
REPORT   reject item I range: min -1.010893 (item 10) max -0.129716 (item 3)
REPORT   reject within-row first-slot contrast d(L,1) - mean(d(L,2), d(L,3)): A -0.219795 B +0.379887 C +0.462250
REPORT notenough: pen1 -0.387914 pen2 -0.161180 pen3 -0.008807 pen-bar -0.185967 | J12 -0.226734 J13 -0.379107 I -0.302920
REPORT   notenough item counts +/-/tied: pen1 6/18/0 pen2 6/18/0 pen3 10/14/0 J12 10/14/0 J13 8/16/0 I 9/15/0
REPORT   notenough item I range: min -1.119419 (item 9) max +0.470215 (item 19)
REPORT   notenough within-row first-slot contrast d(L,1) - mean(d(L,2), d(L,3)): A -0.144497 B +0.204091 C +0.112755
REPORT shuffle null (2000 shuffles, seed 20261122, same draw for E and D; 2000 with all 9 cells): observed I_acc +0.164775; shuffled I p5 -0.351842 p50 -0.260425 p95 -0.173460; fraction |I| >= |observed| 1929/2000
REPORT no equivalence margin is registered, so 'I ~ 0' is not decided
VERDICT 4 of 4 as registered
DIGEST 287867ed9f92920fc3d513e151f6a1efa3c227610ca0f7526148a4e51a89c01c
```

Sabotage (`apen_run_sabotage.txt`): P0 HELD, P1–P3 REFUTED (0 of 24, all tied; pen-bar `+0.000000` for each
meaning), `VERDICT 1 of 4 as registered`, digest `b6ec2997…a0`, exit 1. After pinning, the normal run exits 0.

## Predictions

| ID | Prediction | Outcome |
|---|---|---|
| P0 | Rebuild, identity, synthetic, linearity | HELD |
| P1 | Accept I > 0 in ≥ 13 of 24 items | HELD, 17 of 24 |
| P2 | Accept J12 > 0 and J13 > 0, each in ≥ 13 items | HELD, 20 and 15 of 24 |
| P3 | pen̄ < 0 for accept, reject and not-enough | HELD, `-0.245629`, `-0.254875`, `-0.185967` |

## What this shows, and what it does not

**Implementation (SELF-TESTED):** the contrast code returns 0 on additive tables, κ on an injected (A, 1) effect,
and separates the cancelling case (I 0, J12 −κ, J13 +κ). The rebuild matches ACCBIAS within `4.89e-07`.

**Empirical, this model and these items only:**
- On average over slots, each meaning's instruction shift is smaller when it is printed as A (P3). This is about the
  change from D to E, not about which answer is most probable in either arm.
- For accept, the A-penalty is smaller in slot 1 than in slots 2 and 3, in most items (P1, P2).

**Post-hoc reading, not registered:**
- The slot interaction **reverses by meaning**. For reject, I is `-0.640864`, negative in 24 of 24 items. For
  not-enough it is `-0.302920` (15 of 24 negative). So "A-avoidance that weakens in first place" holds for accept
  only. A single meaning-free letter × slot effect does not describe all three tables.
- Within each accept row the first-slot contrast is positive for every letter (A `+0.254245`, B `+0.146669`,
  C `+0.032273`). For reject and not-enough it is negative for A and positive for B and C.
- The three meanings share each condition's probability, so these tables are not independent. A large drop for
  reject at (A, 1) is, by bookkeeping, a gain for accept or not-enough at their letters and slots. A model fitted
  per condition, not per meaning, is needed before reading a mechanism.

## Open (M15)

- PROPOSED / NOT RUN: fit each pair's three Δ values with shared letter and slot terms plus one semantic term per
  meaning, and report what the meaning × letter × slot residual leaves. It would need its own registration.
- A fresh letter × slot crossing at REF length; the same contrast on GPU7B outputs (not in `37fe6ac`).

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no endorsement or validation by
him. Design: Claude (Anthropic, Opus 5.5) and ChatGPT (OpenAI) in relay turns 027–030. Code, run and this document:
Claude, in a fresh scheduled session. Human validation: not performed. Human responsibility: Chad Holland. Review
level: none.
