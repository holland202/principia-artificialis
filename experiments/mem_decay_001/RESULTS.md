# MEM-DECAY-001: results (test split, run 2026-11-13)

**Status:** run as registered at `dfbad55` (REGISTRATION.md). SELF-TESTED: Claude wrote the generator, the arms,
the scorer and the predictions. Nobody else has run it.

**Outcome:**

- 3 of 5 predictions held. **P2 and P4 were REFUTED (kept).**
- **Control NC1 FAILED**, so the run exits 1, as registered.
- The registered sabotage check was met only in part.

Raw output: [`results/mem_decay_001/test.txt`](../../results/mem_decay_001/test.txt) (with the dev smoke run and the
sabotage run beside it). The seal matched `7753da04…b338`. A second run gave byte-identical output, digest
`b94971e4dcfb25b14306d7f85d55c5730af345f7b6e2e335d3b5d2e8644ed53d` (C-NOISE).

## Failures first (M8)

1. **P2 REFUTED.** Reversible rank decay suppressed stale values *worse* than TTL deletion: A3 stale 0.580 against
   A1 0.770. The registered margin was 0.05.

   Why: at h = T ≈ 49 days, even the *new* values (0–60 days old) are decayed. Young, unrelated filler then outranks
   them, so the new value drops out of the top-5. Decay does not only push down the old; it pushes down everything
   not brand new.
2. **P4 REFUTED (one half).** I predicted that without a guard, A3 would leak revoked records more than half the
   time. It leaked 0.090 (18/200).

   Decay pushed old revoked records out of the top-5 along with everything else old. The other half held: with the
   guard (G1), every arm leaked 0/200. The dev smoke run (0.120) had already pointed this way. The prediction was
   left as registered.
3. **NC1 FAILED: the control was wrong, not the arms.** I registered that shuffling ages would erase A3's stale
   advantage over A0 (|gap| ≤ 0.05). The gap went from +0.0800 to −0.1200.

   Decay applied to random ages does not become neutral. It reorders results at random, which costs accuracy. So
   this control cannot isolate "the advantage comes from age". A correct version would compare decay on real ages
   with decay on shuffled ages; that is left as a door. Because it failed, the run exits 1, as registered.
4. **Sabotage check partly unmet.** I registered that `--sabotage` (guard disabled) must make NC3 report FAILED.
   NC3 HELD, because under sabotage it compares two runs that are both unguarded. That is a defect in how the control
   was written.

   The sabotage was still visible: G1 leaked 200/200 (A0), 12/200 (A1), 32/200 (A2), 18/200 (A3) and 12/200 (A4),
   where the real run leaked 0/200. That breaks P4's G1 clause. P4 was already refuted, though, so the sabotage did
   not change the verdict line. See [`sabotage.txt`](../../results/mem_decay_001/sabotage.txt).

## What held

- **P1** (instrument check). TTL lost every old critical record, and the pin kept every one: A1 critical 0/200,
  A4 critical 200/200.
- **P3** (the discriminating prediction). Pure decay lost every old critical record to newer related records, and
  pinning did not: A3 critical 0/200, A4 200/200.

  So the reason to keep everything and only down-rank did not show up at retrieval in this setting. A record that is
  never returned is, for retrieval, the same as a deleted one. Only the pin protected the critical constraints.
- **P5.** No decay found every old target despite newer look-alikes (A0 adversarial 200/200). Decay found none
  (A3 0/200).
- **NC2** (h = ∞ gave A0's rankings on all 1,200 queries), **NC3** (the real run) and **NC4** (recent criticals
  survive TTL, 1.0000) held.

## The table (test, guard G1, top-5; rates from `test.txt`)

| Arm | current | stale | contradictory | critical | revoked leak | adversarial | store kept |
|---|---|---|---|---|---|---|---|
| A0 no decay | 0.995 | 0.500 | 0.995 | 1.000 | 0.000 | 1.000 | 1.000 |
| A1 TTL | 0.145 | 0.770 | 0.015 | 0.000 | 0.000 | 0.000 | 0.500 |
| A2 LRU | 0.235 | 0.655 | 0.020 | 0.000 | 0.000 | 0.095 | 0.500 |
| A3 rank decay | 0.115 | 0.580 | 0.010 | 0.000 | 0.000 | 0.000 | 1.000 |
| A4 pinned TTL | 0.145 | 0.770 | 0.015 | 1.000 | 0.000 | 0.000 | 0.532 |

Without the guard (G0), the revoked leak was:

| A0 | A1 | A2 | A3 | A4 |
|---|---|---|---|---|
| 1.000 | 0.060 | 0.160 | 0.090 | 0.060 |

## What this supports (C-DESIGN)

The strongest claim it carries is about this generator, these synthetic vectors, T = h ≈ 49 days and top-5:

- **Rank decay behaved like deletion for retrieval.** It kept the records stored, but it lost the same old critical
  records as TTL, and it suppressed stale values worse.
- **Pinning critical records was what protected them.** That is the cheaper fix the proposal's rival arm was there
  to test.
- **The retrieval-time status filter (G1), not decay or deletion, stopped revoked records being returned.**
- **No decay plus the guard** had the best recall on everything except stale values, where it got 0.500. That is
  exactly the unlinked half, so supersession links matter.

None of this says anything about real embeddings, real stores, or a longer half-life.

## What it means for SML (nothing changed; for owner review)

In `sml/memory.py` at `6262dbe`, the `recency`, `importance` and `protected` retrieval methods all multiply the score
by the same exponential decay (default half-life 30 days). The `protected` flag shields records from `compact()`,
not from decay at retrieval. By this result, an old protected record could fall out of the top-k under those
methods. That is a concrete question to test against SML as an external arm. It is not a defect claim yet.

## Doors (M15), unrun

- **P6** (registered). T from background ages only, plus filler ×4. Does P3 survive a long half-life?
- **NC1 done right.** Decay on real ages vs. on shuffled ages, as its own registered comparison.
- **A decay floor or pin inside A3** (decay, but critical records exempt) against A4 at equal storage.
- **SML as an arm**, through its public API, unchanged. Needs owner authorization.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) ran the registered build and wrote these results on 2026-11-13, at Chad Holland's
direction to take the growth-and-decay line forward. Human validation: not performed. Human editing and curation:
direction only. Human responsibility: Chad Holland.
