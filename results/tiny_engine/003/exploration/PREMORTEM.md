# TINY-ENGINE-003 exploration — pre-mortem and predictions (written before running, 2026-11-20)
Exploration only: seeds 901 (arm A) and 902 (arm B), never used for confirmation. Released weights untouched.
Arm A = CFG2, original training mix (v2 baseline, fresh seed).
Arm B = CFG2, copy task changed: half of copy examples use a per-example alphabet of a random size in 2..127
        (symbols drawn with replacement), half stay distinct-symbol. Everything else identical.
Eval (teacher-forced per-token copy accuracy, 256 cases each): families distinct / alpha32 / alpha8 at k = 63 and 127,
plus the 002 periodic/recall checks at L128 and L1024; free-run whole-answer exact rate for alpha8 k=63 (100 cases).
Predictions:
 E1 arm A alpha8 k=63 teacher-forced < 0.50 (content-only matching is ambiguous when symbols repeat)
 E2 arm A distinct k=127 >= 0.99 (reproduces 002)
 E3 arm B alpha8 k=63 above arm A, but < 0.90 at k=127 (2 layers x 2 heads cannot hash long enough contexts)
 E4 arm B keeps periodic_heldout_L1024 and recall_L1024 >= 0.99
Pre-mortem: (1) alpha8 copy may be unsolvable for a 2-layer NoPE matcher -> E3 failing is a capacity finding, not a
bug; (2) arm B may lose the 002 length win -> E4 checks it; (3) mask: only positions after SEP are scored, the
source never is; (4) a scorer that cannot fail: untrained model must score near 1/alphabet or lower.
Off-ramp: if arm B does not beat arm A on alpha8 by >= 0.10, stop tuning; next is a 3rd layer or a copy tool.
