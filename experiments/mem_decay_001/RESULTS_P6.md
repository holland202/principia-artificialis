# MEM-DECAY-001 P6: results (run 2026-11-13)

**Status:** run as registered at `1fe8549` ([REGISTRATION_P6.md](REGISTRATION_P6.md)). SELF-TESTED. **4 of 4
predictions held, and NC2 held.**

- **Seal:** matched `c2a17dc7…e583`.
- **Determinism:** a second run gave byte-identical output, digest
  `ac1923037a22ea20fd844b9e4fc6fb0644fe5eb88cd8f93564db7f47dda87ddc`.
- **Raw output:** [`results/mem_decay_001/p6.txt`](../../results/mem_decay_001/p6.txt).

## What failed or is weaker than it looks (M8)

- **Nothing registered failed.** But P6d was registered as partly true by construction: the analytic estimate
  predicted where critical records would come back. It confirms the arithmetic and the instrument, not a fact about
  memory.
- **A2 (LRU) is not comparable with the first run.** Its kept count is now matched to TTL (7,211 records), not half
  the store.
- **With 8,000 random filler, recall of ordinary facts dropped for every deletion arm.** For example, TTL current
  recall was 0.435 here against 0.145 in the first run. Different T values make this a different regime, not a
  comparison.

## What held

- **P6a.** Even with the half-life set from background ages (T = h = 182.1826 days), pure decay kept no old critical
  record: A3 0/200, against 200/200 for pinned TTL (A4). **So the first run's P3 was not an artifact of its short T.**
- **P6b.** At this longer half-life, decay suppressed stale values as well as TTL: both 198/200 (0.990). **So the
  first run's P2 refutation was a short-half-life effect.** The finding there was "decay at h ≈ 49 days hurts new
  values", not "decay is worse than TTL".
- **P6c.** Decay still cost recall of old ordinary facts: A3 current 0.270 against A0 0.995.
- **P6d and the sweep.** No single half-life does both jobs:

| h | Critical kept | Stale suppressed | Current recall |
|---|---|---|---|
| 1 × T = 182.2 days | 0.000 | 0.990 | 0.270 |
| 2 × T = 364.4 days | 0.000 | 0.980 | 0.505 |
| 4 × T = 728.7 days | 0.000 | 0.700 | 0.885 |
| 8 × T = 1457.5 days | 0.005 | 0.505 | 0.985 |
| 16 × T = 2914.9 days | 0.720 | 0.495 | 0.990 |
| 32 × T = 5829.8 days | 0.985 | 0.495 | 0.990 |

  - Stale suppression is good only up to about a one-year half-life.
  - Critical records come back only from about eight years up.
  - By then decay no longer suppresses stale values: 0.495, the same as no decay (A0 0.490).
  - **There is no window where both are good.**
- **NC2.** At h = ∞, A3's rankings were identical to A0's on all 1,200 queries.

## Pinned TTL against the alternatives (P6 split, guard G1)

| Arm | current | stale | contradictory | critical | revoked leak | adversarial | kept |
|---|---|---|---|---|---|---|---|
| A0 no decay | 0.995 | 0.490 | 0.985 | 1.000 | 0.000 | 1.000 | 1.000 |
| A1 TTL | 0.435 | 0.990 | 0.265 | 0.000 | 0.000 | 0.130 | 0.591 |
| A2 LRU | 0.445 | 0.845 | 0.285 | 0.000 | 0.000 | 0.275 | 0.591 |
| A3 rank decay | 0.270 | 0.990 | 0.100 | 0.000 | 0.000 | 0.000 | 1.000 |
| A4 pinned TTL | 0.435 | 0.990 | 0.265 | 1.000 | 0.000 | 0.130 | 0.607 |

- **Pinned TTL** is the only policy that got critical (1.000) and stale (0.990) together. It paid for that in old
  ordinary facts (0.435), contradictions (0.265) and old targets with newer look-alikes (0.130).
- **No decay plus the guard** had the best recall everywhere except stale values (0.490). That is the half without
  supersession links.

## What the two runs together support (C-DESIGN)

The scope is this generator, these synthetic vectors, and top-5:

1. **Pure rank decay cannot keep critical records and suppress stale ones at the same time.** The half-life that does
   one breaks the other. The claim that decay as "reversible rank demotion" fixes both is not supported here.
2. **Pinning is what protects critical records.**
3. **The retrieval-time status filter is what stops revoked records**, in every policy, in both runs.
4. **Supersession links do the stale work that no-decay retrieval cannot.** The guard alone suppressed exactly the
   linked half: 0.490 here, 0.500 in the first run.

**The design these point to is a question, not a result:** no decay for ranking, a status filter at retrieval,
supersession links for updates, and pins for critical records. That is roughly what SML already has. Whether SML's
retrieval decay undoes its pins is the next test.

## Doors (M15), unrun

- **Decay with pins:** critical records exempt from decay, against A4 at equal storage.
- **Competitor count:** fewer than 6 fresh related records per critical record.
- **NC1 done right:** decay on real ages against decay on shuffled ages.
- **SML as an external arm:** the next registered step, authorized by Chad Holland on 2026-11-13.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) registered, ran and wrote this on 2026-11-13, at Chad Holland's direction (direction
only). Human validation: not performed. Human responsibility: Chad Holland.
