# Principia Artificialis — EXP001 Thermal Pacing Research Note

**Record date:** 2026-10-20 (America/Chicago)  
**Status:** EXPLORATORY / NOT REGISTERED / NOT RUN  
**Owner:** Chad Holland  
**AI drafting:** ChatGPT (OpenAI)  
**Scope:** Research idea associated with Experiment #001's thermal measurement program only. No alteration of EXP001's existing records or claim status.

## Research question for possible future registration

For a fixed, comparable AI workload on one specified edge device, does a thermal-feedback pacing strategy reduce (a) peak measured temperature and/or (b) *total* energy per completed task relative to default or fixed-delay scheduling, without exceeding independently specified latency or quality constraints?

## Candidate conceptual model

\[
P_{\mathrm{dyn}}\approx\alpha C V^2 f,\qquad E_{\mathrm{task}}=\int P(t)\,dt.
\]

A lower observed power level under slower execution is insufficient to establish lower energy. Measurements must distinguish temperature from energy, and both from computation latency and throughput.

## Connection to existing EXP001 evidence limits

The existing `experiments/records/EXP001_2026-10-14_MORNING_FIELD_RECORD.md` describes preliminary S25 Ultra/Termux thermal-zone readings whose sensor identity/calibration were not independently verified. It also records missing/incomplete CPU/charge observability and a wall-clock/monotonic discrepancy in one run. Its results do **not** establish workload-to-temperature causality, energy savings, or a verified thermodynamic law. Those limits carry into any proposed pacing work.

## Future-only minimal design alternatives

- A: default device scheduling, pinned workload and initial conditions.
- B: fixed bounded pauses between identical work batches.
- C: thermal-feedback pacing, using a validated source of temperature data.

Possible outcomes include lower peak temperature with higher task energy, less energy without a peak-temperature benefit, both, or neither. All are admissible results; do not presuppose improvement. Separate repeated-measures noise quantification, sensor calibration, clock continuity, cold-start conditions, and energy source verification are prerequisites to useful physical conclusions.

## Governance / research boundary

This is **not** an adopted experiment, frozen W2 registration, prediction, protocol update, evidence correction, run request, or authorization. A later proposed study must follow PA's current `METHOD.md`, `WORKFLOW.md`, and `CONTROLS.md`, define an independent measurement and falsification plan, state exact acceptance criteria and source revision, and obtain explicit owner approval before execution.

Do not change EGRR, PA-NS-001 or other research projects based on this note.
