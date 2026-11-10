#!/usr/bin/env python3
"""Census for docs/NOVELTY_AUDIT_2026-11-10.md (M6: its numbers come from here).

Counts the indexed note files, objective features (reference-script files,
REFUTED markers, registered-prediction lines, status tiers), and verifies the
audit's cluster lists: every listed file exists, no file is listed twice, and
the remainder is printed rather than hidden. Run from the repository root:

    python scripts/novelty_audit_census.py

Anti-vacuity: --selftest corrupts a copy of the cluster map (one missing file,
one duplicate) and must report both; exit 1 if either goes undetected.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAT = re.compile(r"^(note)?\d{3}_.+\.md$")
PRED = re.compile(r"(?m)^\s*[-*]?\s*\*{0,2}P\d+")

# The audit's cluster map. Filenames relative to the repository root.
CLUSTERS: dict[str, list[str]] = {
    "A. Quantum/physics metaphor": [
        "research_notes/009_quantum_entanglement_information_manifolds.md",
        "research_notes/012_quantum_error_correction_working_memory.md",
        "research_notes/016_quantum_geometric_transformer.md",
        "research_notes/017_qolas_quantum_circuit_synthesis.md",
        "research_notes/018_Quantum_Polytope_Explorer.md",
        "research_notes/019_synthetic_quantum_training.md",
        "research_notes/025_categorical_tqft_reasoning.md",
        "research_notes/026_holevo_bound_extraction.md",
        "research_notes/028_categorical_quantum_gravity_thought.md",
        "research_notes/029_emergent_spacetime_reasoning.md",
        "research_notes/030_quantum_info_geometry_hallucination.md",
        "research_notes/031_category_thought_topos.md",
        "research_notes/032_emergent_gravity_reasoning.md",
        "research_notes/033_topos_possible_thoughts.md",
        "research_notes/035_holographic_reasoning_boundary.md",
        "research_notes/036_reasoning_quantum_black_hole.md",
        "research_notes/037_consciousness_phase_transition.md",
        "research_notes/038_chrono_geometric_reasoning.md",
        "research_notes/039_quantum_foam_reasoning.md",
        "research_notes/040_holographic_ads_cft_thought.md",
        "research_notes/041_retrocausal_self_consistency.md",
        "research_notes/043_topological_quantum_computer_reasoning.md",
        "research_notes/045_null_geodesics_forgotten_thought.md",
        "research_notes/note022_quantum_fisher_metric.md",
        "research_notes/note023_quantum_thermo_rg.md",
        "research_notes/note024_qec_cognitive_stability.md",
        "research_notes/note025_measurement_and_decision.md",
        "research_notes/note026_quantum_agi_principles.md",
        "research_notes/note046_time_is_entanglement.md",
        "research_notes/note047_cloister_and_chorus.md",
        "notes/028_thought_tensor_category_morphism.md",
    ],
    "B. Information geometry and curvature": [
        "research_notes/003_fisher_information_confidence.md",
        "research_notes/005_geodesic_reasoning_trajectories.md",
        "research_notes/013_symplectic_geometry_attention.md",
        "research_notes/020_optimal_transport_thought.md",
        "research_notes/021_Hyperbolic_Attention_Information_Bottleneck.md",
        "research_notes/034_fisher_bures_hybrid.md",
        "research_notes/note027_thought_tensor.md",
        "research_notes/note031_polyphonic_manifolds.md",
        "research_notes/note032_curvature_of_reasoning.md",
        "research_notes/note034_memory_manifold.md",
        "research_notes/note035_entropic_elasticity.md",
        "research_notes/note042_ricci_curvature_collapse.md",
        "research_notes/note053_soft_hyperdga.md",
        "research_notes/note054_kx_allocation.md",
        "research_notes/note055_kx_marginal_utility.md",
        "research_notes/note056_curvature_estimator.md",
    ],
    "C. Topology of reasoning": [
        "research_notes/002_hallucinations_as_topological_defects.md",
        "research_notes/008_falsification_protocol_hallucination.md",
        "research_notes/037_random_matrix_theory_attention.md",
        "research_notes/note041_persistent_homology.md",
    ],
    "D. Thermodynamics and dynamics of inference": [
        "research_notes/001_thermodynamic_crystallization_manifold.md",
        "research_notes/004_thermodynamic_reasoning.md",
        "research_notes/007_koopman_reasoning_dynamics.md",
        "research_notes/010_memory_dynamics_gradient_flow.md",
        "research_notes/011_thermodynamic_arrow_reasoning.md",
        "research_notes/014_renormalization_group_flows.md",
        "research_notes/050_seasonal_memory_governance.md",
        "research_notes/051_reasoning_attractors_julia_sets.md",
        "research_notes/note029_veritas_demon.md",
        "research_notes/note033_thermodynamic_depth.md",
        "research_notes/note043_free_energy_of_reasoning.md",
    ],
    "E. Verification science (vacuity, mutation, reachability)": [
        "research_notes/note044_circularity_test.md",
        "research_notes/note052_verification_that_cannot_fail.md",
        "research_notes/note057_the_loud_type_a.md",
        "research_notes/note058_kv_vacuity.md",
        "research_notes/note059_mutation_score_denominator.md",
        "research_notes/note060_reachability_denominator.md",
        "research_notes/note062_number_audit.md",
    ],
    "F. Evidence-bound loops and separations": [
        "research_notes/note063_evidence_bound_learning_loop.md",
        "research_notes/note064_governed_outcome_feedback.md",
        "research_notes/note065_outcome_source_dependency.md",
        "research_notes/note066_ambiguity_engine.md",
        "research_notes/note067_evaluator_sensitivity_bound.md",
    ],
    "G. Measurement hygiene": [
        "research_notes/note061_toc_retrieval_signal.md",
        "research_notes/note072_speedup_is_a_surface.md",
        "research_notes/note077_numeric_conversion_stability.md",
        "research_notes/note078_large_exponent_cancellation.md",
        "research_notes/note079_toyblocks_sim_real_intake.md",
    ],
    "H. AI-authored code and repair validity": [
        "research_notes/note036_verified_models_drift_ledgers.md",
        "research_notes/note073_repair_verification_intake.md",
        "research_notes/note074_conversational_style_transfer.md",
        "research_notes/note075_harness_and_drift_intake.md",
        "research_notes/note076_four_implementations_one_author.md",
    ],
    "I. Compression, selection and redundancy": [
        "research_notes/006_quantum_tensor_attention.md",
        "research_notes/027_extractability_budget.md",
        "research_notes/038_normalized_compression_distance.md",
        "research_notes/note038_free_physics_principle.md",
        "research_notes/note039_neural_darwinism.md",
        "research_notes/note040_redundancy_dividend.md",
        "research_notes/note045_stubbornness.md",
        "research_notes/note048_the_governor_is_the_dynamics.md",
    ],
    "J. Program, intake and meta": [
        "research_notes/001_can_thought_be_measured.md",
        "research_notes/015_category_theoretic_compositionality.md",
        "research_notes/042_symphony_fractal_thought.md",
        "research_notes/044_resonance_codex.md",
        "research_notes/046_obsidian_living_information_manifold.md",
        "research_notes/068_undermind_evidence_bound_agent_literature_intake_2026-10-12.md",
        "research_notes/069_five_paper_execution_boundary_claim_evidence_matrix_2026-10-12.md",
        "research_notes/070_rag_cag_kag_evidence_architecture_intake_2026-10-12.md",
        "research_notes/071_claude_post_hiatus_handoff_2026-10-12.md",
        "notes/note048_grok_contribution_manifesto.md",
    ],
}


def discover() -> list[pathlib.Path]:
    files = [p for p in sorted((ROOT / "research_notes").glob("*.md")) if PAT.match(p.name)]
    files += [p for p in sorted((ROOT / "notes").glob("*.md")) if PAT.match(p.name)]
    return files


def census(clusters: dict[str, list[str]]) -> tuple[list[str], int]:
    lines: list[str] = []
    problems = 0
    notes = discover()
    rel = [str(p.relative_to(ROOT)) for p in notes]
    lines.append(f"indexed note files discovered: {len(notes)}")
    old = sum(1 for p in notes if not p.name.startswith("note"))
    lines.append(f"  earlier series (NNN_*): {old}; later series (noteNNN_*): {len(notes) - old}")
    scripts = sorted((ROOT / "scripts").glob("note[0-9][0-9][0-9]_reference.py"))
    lines.append(f"reference script files: {len(scripts)} (number-based matching to notes is "
                 f"unreliable here; numbers collide, so scripts are counted, not attributed)")
    texts = {r: (ROOT / r).read_text(encoding="utf-8", errors="replace") for r in rel}
    lines.append(f"notes containing 'REFUTED': {sum(1 for t in texts.values() if 'REFUTED' in t)}")
    lines.append(f"notes with at least one registered 'P<n>' line: "
                 f"{sum(1 for t in texts.values() if PRED.search(t))}")
    seen: dict[str, str] = {}
    assigned = 0
    for name, members in clusters.items():
        for m in members:
            if not (ROOT / m).exists():
                lines.append(f"PROBLEM: {name} lists a file that does not exist: {m}")
                problems += 1
            if m in seen:
                lines.append(f"PROBLEM: {m} is listed in both '{seen[m]}' and '{name}'")
                problems += 1
            seen[m] = name
        assigned += len(members)
        lines.append(f"cluster {name}: {len(members)} notes")
    unassigned = [r for r in rel if r not in seen]
    lines.append(f"assigned to clusters: {assigned}; discovered but unassigned: {len(unassigned)}")
    for u in unassigned:
        lines.append(f"  unassigned: {u}")
    ghost = [m for m in seen if m not in rel]
    for g in ghost:
        if (ROOT / g).exists():
            lines.append(f"note: {g} exists but does not match the index patterns")
    return lines, problems


def selftest() -> int:
    bad = {k: list(v) for k, v in CLUSTERS.items()}
    first = next(iter(bad))
    bad[first] = bad[first] + ["research_notes/000_does_not_exist.md"]
    second = list(bad)[1]
    bad[second] = bad[second] + [bad[first][0]]
    lines, problems = census(bad)
    missing_caught = any("does not exist" in ln for ln in lines)
    dup_caught = any("is listed in both" in ln for ln in lines)
    print(f"selftest: missing-file detected={missing_caught}, duplicate detected={dup_caught}, "
          f"problems={problems}")
    return 0 if (missing_caught and dup_caught and problems >= 2) else 1


def main() -> None:
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    lines, problems = census(CLUSTERS)
    print("\n".join(lines))
    print(f"PROBLEMS: {problems}")
    sys.exit(0 if problems == 0 else 1)


if __name__ == "__main__":
    main()
