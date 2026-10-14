# PA thermodynamics documentation and integrity review — 2026-10-13

**Status:** Documentation corrections on review branch; no new experimental runs or method amendments.  
**Author:** ChatGPT (OpenAI GPT-6), directed by Chad Holland. Human review: direction only, not line-by-line.  
**Method:** Adopted `METHOD.md` on main (blob `6e4247ced1f2eef8b3c9917624d17d46d5bb80aa`), W9 documentation-correction path.  
**Scope:** Existing public research notes and draft synthesis. No physical AI thermodynamics claim is promoted.

## Files addressed

| File | Actual finding | Action |
|---|---|---|
| `research_notes/001_thermodynamic_crystallization_manifold.md` | Unsubstantiated thermal/topological hardware guarantee and invalid mixed diagram/ASCII fences | Added dated speculative-status warning; separated illustrative variance text from Mermaid fence |
| `research_notes/011_thermodynamic_arrow_reasoning.md` | Fisher–Rao path length labeled entropy production; unproven theorem and Carnot-like bound | Added dated, explicit non-validation correction; historical claims remain |
| `research_notes/note023_quantum_thermo_rg.md` | 3 unresolved Git conflict blocks and physical interpretation unsupported | Removed markers, choosing typographically updated identical-content option; added scope note |
| `research_notes/note035_entropic_elasticity.md` | With uniform prior, stated free-energy formula reduces to a monotonic entropy expression; hand-selected Goldilocks band lacks task results | Added exact algebra and explicit toy-only status; original hypotheses preserved |
| `WHITEPAPER.md` | Draft synthesis reads as validated physical law and implies confirmed independent signatures | Foregrounded hypothesis-only status; linked the Note #043 known negative result |
| `whitepapers/volume1_foundations_of_artificial_thought.md` | 16 unresolved Git conflict blocks; stray placeholder; open Python fence; unverified external citation tokens | Removed merge syntax, closed Python code block, preserved appendix content, labeled citations as unresolved |

## Bounded checks and outcomes

- Static scan of these six revised files: **0 unresolved conflict-marker lines**, **0 odd Markdown code-fence counts**, **0 matches for the screened out-of-scope project identifiers**.
- Inspected **3 distinct internal relative Markdown link destinations** referenced from the revised set; all 3 existed on the review branch. This is **not** a repository-wide link audit.
- Direct arithmetic cross-check on the exact uniform-prior toy formula from `figures/generate_note035_entropic_elasticity.py`: at alpha values `0`, `0.1`, `0.5`, `1`, `1.5`, the identity `F = log(20) - 0.5*S` held within floating-point rounding (maximum absolute difference below `1e-14`). This **does not** independently execute the repository's Python generator or validate the Goldilocks hypothesis.
- Git blob comparisons to main: `METHOD.md`, `WORKFLOW.md`, `CONTROLS.md`, and the existing negative-results Note #043 all **identical**. No experimental result overwritten.
- **NOT RUN:** complete CI, method-lint, original figure-producing Python programs, independent device or transformer evaluations, full reference-code suite, manuscript publication build. No test result for physical entropy, overfitting, Carnot efficiency, or hallucination prediction was produced in this documentation review.

## Open items for later bounded audit passes

1. Resolve remaining mathematical typesetting defects in older physics-inspired notes without silently altering definitions or historical predictions.
2. Trace unverified `[web:...]` citation tokens in the volume-I appendix to actual source references (or label them unsupported); do not fabricate sources.
3. Audit other notes, visualizations, and experiment statuses separately, distinguishing toy figures from real-model observations.
4. Independently run reference scripts and existing test harnesses in a reproducible environment before claiming full conformance.
5. No new physical-law or methodology comparison work should be inferred from these editorial repairs.

**Outcome:** Bounded documentation repair; broader repository audit remains incomplete. Retain every pre-existing negative result and preserve future failures under the existing SWAY method.

## Additional focused thermodynamics review — 2026-10-13 (pass 2)

The owner-authorized follow-up identified four additional published documents where unrun protocols or thermodynamic analogies could be read as verified findings. These are **dated W9 documentation clarifications**, not amendments to experiments or the PA methodology.

- `Exp003/protocol.md`: the original historical “Verified Benchmark” title is not evidence of a real-transformer run; projected AUC and synthetic free-energy numbers are not validation, especially given Note #043's previously recorded vacuous test and output mismatch. Labelled NOT RUN in this record.
- `experiments/exp003_veritas_thermal_correlation.md`: proposed thermal/hallucination mechanism and a temperature trigger have no empirical or physical-law derivation here. The chain-complex identity `boundary²=0` cannot be violated by adversarial text under its mathematical definition. Proposed runtime reduction is not confirmed implemented.
- `research_notes/note029_veritas_demon.md`: a topology analogy cannot establish that Betti numbers imply reasoning truth. Landauer's erasure bound is not an established heat cost per purported reasoning defect.
- `research_notes/note042_ricci_curvature_collapse.md`: the supposed first-order transition is not established; its energy-like formula simplifies algebraically to negative accumulated curvature. A previously unclosed Python code fence was repaired; real-model predictions remain unrun in this note.

**Additional bounded checks:** Static inspection of the four edited documents found no remaining unbalanced Markdown code fences or unresolved merge-marker lines in those files; no screened out-of-scope identifiers in changed content; canonical `METHOD.md`, `WORKFLOW.md` and `CONTROLS.md` unchanged by blob SHA. **No full code execution, real-device measurements, CI, or real-transformer validation performed.** Broader repository crawling and independent reproductions remain outstanding for the scheduled overnight passes.
