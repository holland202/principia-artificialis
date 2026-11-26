# QFI-001 collaboration: does the "quantum" part of representation geometry add anything?

**Status:** protocol and question, 2026-11-24. Nothing is registered, built or run. Chad Holland asked to explore
the quantum material in Principia alongside TLM-005 and left the choice of question to Claude (live chat,
2026-11-24, paraphrased). The third Claude–ChatGPT line, after the CCC-001 relay and TLM-005.

## Where it comes from

Several notes give a quantum geometry of representations, and none has a registered prediction or reference code:

- [[note022_quantum_fisher_metric]] (Speculative) defines the quantum Fisher information (QFI) of density
  matrices built from layer activations. Its proposed experiment 2 is "Compare QFI vs Fisher-Rao".
- [[030_quantum_info_geometry_hallucination]] (Draft) proposes that hallucinations sit where Bures distance is high.
- [[034_fisher_bures_hybrid]] (Draft) proposes that a hybrid Fisher-Rao / Bures metric captures mixed
  representations better.
- [QFI_THERMO_AGENDA.md](../../research_notes/QFI_THERMO_AGENDA.md) lists finishing #022 as its first next step.

## The question

Build a density matrix ρ(θ) from a model's activations (for example, the trace-normalised second moment of a
layer's token vectors) along a one-parameter path of inputs. The QFI splits exactly into two parts. The
**classical part** is the Fisher information of ρ's eigenvalues. The **rotation part** comes from ρ's eigenvectors
turning as θ changes, and it is the only part that is "quantum" (non-commuting). **Does the rotation part carry
information about the model that the classical part and simpler statistics do not?**

- **Rival 1, classical:** the eigenvalue spectrum alone. If it predicts as well as full QFI, the quantum framing
  adds nothing.
- **Rival 2, architecture:** the same measure on an untrained model of the same architecture. If it matches,
  the geometry reflects the architecture, not learning.
- **Rival 3, for #030:** output entropy. Bures distance must beat it at predicting a wrong answer to support #030.
- **Anti-vacuity (M3):** synthetic families with known answers. Commuting families must give a rotation share of
  0, pure rotations must give 1, and a qubit family must match its closed-form QFI.

## First steps (task list in the PR description)

1. Reference code for #022's stated properties: the classical limit, QFI ≥ the classical Fisher information of any
   measurement, and Bures distance ≈ QFI/4 at small steps. These are textbook results, so this is a test of the
   code, not of a claim.
2. A feasibility pass: QFI and its split on one small model at a few layers, counts and cost only.
3. A registration (W2) choosing the path, the model, the endpoint and the rivals, before any comparison is read.

## How the two work

The rules of [COLLAB_TLM005.md](https://github.com/holland202/principia-artificialis/blob/16a5bbf/experiments/tiny_lm/COLLAB_TLM005.md) (on PR #179, not yet on `main`) apply unchanged. There is one shared task list. The
author of a piece of code never writes or sees its blind tests. Each AI pushes only to its own branches
(`claude/qfi-001-*`, `chatgpt/qfi-001-*`). Notes are PR comments headed `note: qfi001/<claude|chatgpt>/<NNN>`.
Freezes, blind or confirmatory runs, merges and tags wait for Chad Holland's own words on the PR. The line stops
on `COLLAB STOP` from Chad, when it is closed (W8), or on 2026-12-15.

## Faster protocol (from 2026-11-25)

[COLLAB_FAST.md](COLLAB_FAST.md) (FAST-1) changes how the two AIs exchange notes on this line: a state block, short
note cards, executable public cases ([`cases/public.jsonl`](cases/public.jsonl), [`run_cases.py`](run_cases.py)),
batched attacks, parallel tracks and the D1 differential check. The rules above still hold where FAST-1 is silent.

## Known limits

"Quantum" here means a non-commuting matrix geometry built from classical activations. No quantum hardware or
quantum state is involved, and the result can say nothing about physics. Both AIs share Chad's standing
instructions (M10).

## Provenance (M13)

Direction: Chad Holland, 2026-11-24. Question and protocol: Claude (Anthropic, Opus 5.5). The notes it draws on
credit their own authors. Human validation: not performed. Human responsibility: Chad Holland.

## Changes (W9)

- **2026-11-25:** added the section "Faster protocol". Nothing else changed. Edit by Claude (Anthropic, Opus 5.5) on
  Chad Holland's direction.
