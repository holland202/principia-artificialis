# Lesson: when every prediction holds, ask how hard they were

*Teaching note, kept separate from the evidence. Written by Claude (Anthropic, Opus 5.5) at Chad Holland's
direction, 2026-11-14.*

MEM-DECAY-002 registered seven predictions, and all seven held. That sounds strong, and mostly it isn't. Sort each
prediction by what could have made it fail:

- **By construction** (Q1). Critical records are never used, so a decay based on use cannot save them. This only
  checks the instrument.
- **By arithmetic on the definitions** (Q3, Q4, Q7). A pinned record is kept by definition, and a missed label is
  an unpinned record. Getting these right shows the code does what it says.
- **By mechanism** (Q2, Q5, Q6). These could have failed because of how the pieces interact: floors against six
  fresher look-alikes, and use-based decay against stale values. These carry the findings.

The most useful result was not a prediction at all. Critical recall came out *exactly* equal to label recall:
166/200 and 129/200. Seeing that turns "which decay curve?" into "who decides what is important, and how often are
they wrong?"

Habit to keep: next to each prediction, write the reason it could fail. If the reason is "only if my code is
wrong", call it a control, not a prediction.
