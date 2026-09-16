# Provenance

## Identity

- **Repository**: holland202/principia-artificialis
- **Canonical URL**: https://github.com/holland202/principia-artificialis
- **Purpose**: An open research program exploring mathematical foundations relevant to artificial intelligence (information geometry, topology, dynamical systems, thermodynamics, etc.), organized as numbered notes with explicit epistemic status labels and, where possible, executable reference code.
- **License**: MIT (see LICENSE)

## Origin

Chad Holland initiated the program. Repository history supports this attribution.

## Contributions

See AUTHORS.md. Human origin and infrastructure map to Chad Holland. Substantial note content has been produced with material AI assistance, which is credited by system name in the repository documentation.

## Research Status Distinction

The repository maintains its own status vocabulary for notes (Verified, Draft, Speculative, and additional labels in actual use). Mapping to the common provenance vocabulary:

| Common Status | Meaning relative to this repository                          |
|---------------|--------------------------------------------------------------|
| IMPLEMENTED   | Notes and reference scripts exist                            |
| EXPERIMENTAL  | Numerical claims backed by runnable code in some notes       |
| VERIFIED      | “Verified” notes claim reference code prints every number; this is an internal designation, not independent external verification |
| REPRODUCED    | No independent external reproduction campaign is recorded    |
| REFUTED       | Notes that contain registered predictions that failed are retained and marked |
| UNRESOLVED    | Many notes remain Draft or Speculative                       |
| NOT TESTED    | Large portions of the speculative material                   |

Internal “Verified” status must not be read as independent scientific validation.

## Experimental / Note Lineage

- Notes are the primary unit.
- A subset (approximately note038–note058 and others) ship with reference scripts intended to print the numbers claimed.
- At least seven notes contain refuted-and-kept claims.
- Status-label drift exists (more distinct status strings in use than the documented core vocabulary); this is acknowledged in the README.

A centralized machine-readable experiment/note registry beyond the existing NOTES_INDEX.md and scripts is not yet present.

## Independent Reproduction

None recorded as external independent reproduction.

## Refutation / Failure Record

Refutations are first-class. Notes that register a prediction and later observe failure keep the original claim visible and mark the refutation. This policy is part of the repository’s explicit design.

## Corrections

Corrections to reference scripts or note text are expected to leave the history of the error visible where the error was load-bearing.

## Scope of Evidence

This repository contains research notes, some accompanied by executable reference code.

It does **not** establish:

- that any particular mathematical claim about artificial intelligence is true beyond the numerical checks present in the reference scripts
- recursive self-improvement
- general intelligence or autonomy
- independent peer-reviewed validation
- that AI-assisted notes carry the same epistemic weight as human-only work without further scrutiny

Successful execution of a reference script confirms that the script prints the claimed numbers under the conditions of the run; it does not by itself establish broader scientific conclusions.

## Relationship to Other Repositories

This repository functions as a hypothesis and theory laboratory. Instrument repositories and any higher-level research-operating layer remain separate.
