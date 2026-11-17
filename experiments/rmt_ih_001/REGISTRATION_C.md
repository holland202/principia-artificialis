# RMT-IH-001 part C registration: a tiny transformer that really learns in-context copying

**Status:** REGISTERED, NOT RUN on the seeds below. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-16). Design and code: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## Why

Parts A and B's models learned a shortcut: copy from exactly 32 tokens back. Part C's job is to build the thing
those parts assumed existed: a model that copies by *content*. It should find the earlier occurrence of the current
pattern and continue it, at any distance, including distances it never trained on. This is an engineering goal
with a pass/fail bar.

## Design (frozen)

- **Model:** same model as parts A and B (`tinyih.py`: 2 layers, 2 heads, d_model 256, attention only).
- **Data:** BOS, then a random segment of length L repeated to fill 64 tokens (`explore_c2.periodic`).
- **Periods:** L is drawn from 6–24, **except 9, 13, 17 and 21, which are never trained on**.
- **Training:** learning rate 1e-3, batch 64, 3,000 steps (`train_v2.py`).
- **Seeds:** 1–6. The exploration used seed 900 only.

## Exploration disclosed (seed 900, C-EXPLORE)

- **The task that failed:** a single copied segment hidden in random noise. At lr 1e-4 and 3e-4 over 4,000 steps,
  copy accuracy stayed at 0.01–0.05. That task is too sparse for this model to learn in that time.
- **The task adopted:** the periodic task. At lr 1e-3, accuracy reached 1.00 at trained periods and 0.96 at the
  held-out periods by step 3,000.
- **Transfer:** that model scored 0.80 on the noise task at distances it never saw, a task it was never trained on.

## Pass/fail bar (each seed, final weights)

| ID | Test | Pass if | Why |
|---|---|---|---|
| Q1 | copy accuracy at the 4 never-trained periods | ≥ 0.90 in ≥ 5 of 6 seeds | rules out a fixed-distance shortcut |
| Q2 | copy accuracy on a *different* task: one segment copied once inside random noise, at distances never trained on | ≥ 0.70 in ≥ 5 of 6 seeds | content-based copying transfers |
| Q3 | anti-vacuity | the same Q2 test on a randomly initialised model gives < 0.05 | the test can say "no" |

Spectral traces (edge ⟨r̃⟩, top_norm, stable rank, every 50 steps) are saved for a later registered question. No
prediction about them is made here.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) → human validation: not performed → human editing/curation:
direction by Chad Holland, 2026-11-16 → human responsibility: Chad Holland. Review level: direction only.*
