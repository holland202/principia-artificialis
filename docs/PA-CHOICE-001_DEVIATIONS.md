# PA-CHOICE-001 — Dated protocol clarification

**2026-11-13, before study inference.** Registration `4235f2ccb2b4b4e7478252515eb5a78c6ab18d07` remains the original record. The paper *Probing the Trajectories of Reasoning Traces in Large Language Models* is by Marthe Ballon, Brecht F. Verbeken, Vincent Ginis and Andres Algaba. The registration attributed it to Ma et al. in error. [Author record](https://arxiv.org/abs/2601.23163)

The frozen G3 example contained a specification error. With the leader removed, the other three probabilities are divided by 0.45. The swap moves 0.10 before normalization, so a path with two swaps has total variation `2 × 0.10 / 0.45 = 4/9`, where the original said `1/5`. Use the correctly normalized `4/9`. The original G3 benchmark would reject the correct implementation. The feature definition, numerical tolerance, cases, and P1 and P2 thresholds follow the registration. No study model outputs had been seen when this clarification was written. The gate correction was derived from the hand example, before building the runner.

**Provenance:** ChatGPT (OpenAI, GPT-6 family) checked authorship and derived the correction. Chad Holland authorized the study and holds responsibility. Human review level: direction only. Human validation and editorial review: none recorded.
