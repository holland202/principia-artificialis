# TINY-ENGINE-004 exploration - pre-mortem and predictions (written before running, 2026-11-20)
Exploration only. All three arms use the SAME seed (903), so arms differ only by their config.
A = CFG3 (version 3). B = CFG3 + answer-segment label. C = B + position coupling in the rotary layer 0.
Released weights untouched. Same eval as 003 (eval3.evaluate3 + engine.evaluate) but case seeds +20000 (fresh).
Predictions:
 X1 C tf_alpha8_k127 >= 0.95 (coupling makes copy offset-free in id space, so repeats stop mattering)
 X2 B tf_alpha8_k127 within 0.05 of A (the label alone does not fix repeats: SEP already marks the boundary)
 X3 C free_alpha8_k63 > 0.5 (A and B expected ~0.00)
 X4 C keeps periodic_heldout_L1024 and recall_L1024 >= 0.99 (coupling only touches rows that contain SEP)
Pre-mortem: (1) the coupled ids make layer 0's previous-token head see the answer token i-1 and source token i at
offsets 1 and 0 at once - could confuse it; (2) C may learn a 1-layer copy and stop using layer 1, harming recall
- X4 checks; (3) coupling uses SEP at inference: a test whose prefix lacks SEP silently runs uncoupled - free-run
prefixes always include SEP; (4) a bug in answer_layout would make C behave like B - X1 vs X2 would then tie.
Off-ramp: if C does not beat B by >= 0.10 on tf_alpha8_k127, coupling as built does not help here; stop, record.
