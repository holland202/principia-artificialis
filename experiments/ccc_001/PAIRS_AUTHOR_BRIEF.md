# CCC-001 matched evidence pairs: brief for the independent item author

**Status:** brief committed before any item is written (M2). Not a registration of any test, endpoint or
threshold. Proposed in `ccc-relay/chatgpt/036`. Chad Holland chose an outside model as author on 2026-11-23 in a
live chat (paraphrased, not quoted). Gemini is the candidate.

The author must not see this repository, the relay or the CCC-001 development items. The brief describes only the
answer format, which the author has to know. It contains no item from `probes.py`.

## Handling

1. The author gets the brief below in a fresh session with memory and custom instructions off, no repository
   access and no browsing. It replies in chat only and writes nothing to GitHub.
2. **Set 1** (development) is committed verbatim with its SHA-256 and the author's stated model name.
3. **Set 2** (held out) stays off the repository. Chad Holland keeps the text and commits only its SHA-256. Neither
   relay AI sees it before a registered, approved run.
4. Before Set 1 is used, Chad Holland reads a named sample of pairs and confirms that each one flips (C-SYNTH). The
   key balance is counted.
5. Label: AI-authored, independent of Claude and ChatGPT and of the measured model's vendor. Not human-authored.

## The brief, verbatim

```text
You are writing test items for a research experiment. For this task, do not look at any GitHub repository,
website or earlier conversation, and do not write to GitHub or any file. Reply here, in plain text only.

Each item is a Report and a Claim. A reader answers with one letter:
A = accept the claim (the report gives direct evidence for it)
B = reject the claim (the report gives direct evidence against it)
C = not enough evidence to decide

Write matched pairs. Both items in a pair have the same Claim. Their Reports differ only in the evidence,
changed in as few words as possible, so that a different letter becomes correct. Keep length, topic and
style otherwise the same.

Rules:
1. Three pair types: AB (one item is A, the other B), AC, and BC.
2. Write two sets. Set 1: 12 pairs, 4 of each type. Set 2: 24 pairs, 8 of each type.
3. Every item must have exactly one correct letter that a careful reader would agree on. If a case is
   borderline, drop it and write another.
4. Report: one or two sentences, at most 40 words. Claim: one sentence.
5. Everyday, concrete topics, a different topic for every pair. Nothing about AI, computers or research.
6. A C report must be relevant to the claim but not enough to decide it either way.
7. The correct letter must not be guessable from length, or from a single word such as "not".

Format. First line: your exact model name and version. Then one line per item:
SET | PAIR | TYPE | KEY | Report | Claim
for example: 1 | 01 | AB | A | <report> | <claim>
Do not use the | character inside a report or claim. After the last item, write nothing else.
```

## Provenance (M13)

Brief written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-23. Design idea (matched
evidence pairs by an independent author, held out as pairs): ChatGPT (OpenAI), `ccc-relay/chatgpt/036`. Human
validation: not performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico
Talens-Alesson's. Crediting him implies no endorsement or validation by him.
