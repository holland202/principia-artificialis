# Lesson: what MEM-DECAY-001 teaches about building experiments

This is teaching material, kept apart from the evidence. The evidence is in REGISTRATION.md and RESULTS.md.

**1. A record that is never returned is, for retrieval, deleted.** "Reversible" decay keeps the bytes. But if the
score sinks below fresher noise, the reader never sees the record. Reversibility only matters if something can lift
the score back up: an "as-of" query, a pin, a floor. Ask what *restores* access, not only what keeps storage.

**2. Decay hits everything that is not brand new.** The half-life was about 49 days. A 30-day-old *correct* value
then scores about 0.65 of a fresh one, so fresh irrelevant records can outrank it. That is why decay did worse than
TTL on stale values (0.580 vs 0.770). The knob (h) and the age mix decide the outcome, which is why P6 exists.

**3. Controls can be wrong too, and a wrong control still fails loudly.** NC1 assumed that shuffled ages make decay
neutral. In fact, decay on random ages reorders results at random, which costs accuracy. The failure is kept and the
run exits 1. You fix a control with a new registration, never by editing the old threshold.

**4. Sabotage has to break something that would otherwise pass.** The sabotage run disabled the guard. But the one
control meant to catch that (NC3) compared two unguarded runs, so it could not fail. The guard break still showed up
in the raw table (G1 leaks went from 0/200 to as many as 200/200), but not in the verdict line. Design each sabotage
against a check that holds in the real run.

**5. Equivalent mutants exist.** Mutant M8 (one Wilson guard removed) survived because a second guard did the same
job. Removing both (M8b) was caught. A surviving mutant is a question, not automatically a weak test.

**6. Look at generated inputs before trusting them.** The young competitor records pulled the median age down to
about 47–49 days. That changed what "TTL" meant, and it was visible before any scoring. It was disclosed in the
registration, not discovered afterwards.
