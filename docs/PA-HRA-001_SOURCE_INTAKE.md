# PA-HRA-001 — Hybrid Reasoning Agents: source intake and proposed falsifiable questions

**State:** SOURCE REVIEW ONLY / NOT RUN. Public conceptual intake, not a preregistration, completed experiment, security verification, or adoption of the cited architecture.  
**Prepared:** 2026-10-19. **Project:** Principia Artificialis.  
**Owner:** Chad Holland. **Assistance:** ChatGPT (OpenAI, GPT-6); owner directed the research topic; technical/line review not independently attested.  
**Method:** [METHOD.md](../METHOD.md), [WORKFLOW.md](../WORKFLOW.md), [CONTROLS.md](../CONTROLS.md) at PA main `710e575a035629287422e2175f9c1872cfd12903`.  
**Origin:** Examination of third-party published work. No contributor endorsement is implied.

## 1. Primary sources and limits

- Jiaru Zou et al., *Hybrid Reasoning Agents*, arXiv:2610.18861v1 (2026-10-13): https://arxiv.org/html/2610.18861v1
- Upstream implementation: https://github.com/togethercomputer/HybridAgent ; reviewed source commit `1b41cebbd2388d083ee1820af421b7f9e24affb5`.
- Released implementation is MIT-licensed; upstream source remains owned and credited to its authors. This file cites, but does **not** copy, its implementation.
- Inspected: `hybrid_agent/hybridlink.py`, `model.py`, `readout.py`, `engine.py`, `tools/python_tool.py`; paper sections 3, 4 and 6. Statements about measured performance below are the **authors' reports**, not independent observations here.

## 2. Source observations (not verified on our hardware)

- Model inference alternates text/token steps with continuous latent-state feedback, through an adapter and a retained Transformer KV-cache. Repeated text prompting is **not** equivalent to this method.
- In released code, `HybridLink` has pre- and post-LayerNorm around a residual MLP. The paper's displayed `h + W2 GELU(W1 h)` equation is a simplified representation, not an exact module listing.
- A latent pseudo-text view selects nearest token embeddings for inspection. It is a **derived, lossy annotation**, not the latent state itself, a verbatim reasoning transcript, a proof of intent, or an authorization credential.
- Authors' MATH500 ablation, 8B/14B: unmodified 84.6%/88.2%; nearest-token **replacement used as the continued computation** 82.6%/87.2%; latent-mode entry blocked 80.4%/78.8%. These results concern the trained models and the reported evaluation only.
- Authors' interventions: random-token replacement (reported perturbation strength 1.6) scores 41.2% at 8B; Gaussian-noise perturbation (strength 2.0) scores 66.4%. Strength alone is not a sufficient control for changed content or perturbation family. The two strength metrics are not asserted to be statistically exchangeable.
- Hybrid context includes continuous state; text-only reconstruction is insufficient for identical resumed trajectories. In-training exact replay of recorded latent inputs is **not evidence** of cross-backend, cross-precision, crash-recovery or independent replay equivalence.
- The upstream Python tool runs a subprocess with time, virtual-memory and output limits. Its own code states those limits are *guardrails, not a security sandbox*, and generated code runs as the current user with filesystem/network access. This source observation makes it unsuitable as a privileged-action boundary without additional isolation.

## 3. Public research question (concept only)

**RQ:** Can a system benefit from model-internal latent computation while keeping *external actions* mediated by an independent, explicit, reviewable request and authorization gate?

A useful boundary separates: (a) model-internal latent/text computation; (b) a structured, explicit external action request; (c) an independent authorization verdict; (d) effect observation; (e) post-hoc evidence validation. Inferences, pseudo-text readouts and model self-reports are **never** authority.

**Competing explanations:** efficiency may come from model training, better model quality, prompt/benchmark differences, tool availability, batching, or hardware rather than latent steps alone. Readout similarity may correlate with correctness yet fail to preserve semantic content.

## 4. Candidate independent research (NOT REGISTERED / NOT RUN)

1. **Readout fidelity (concept):** fix a public evaluation subset and compare live latent continuation against nearest-token *replacement*, matched random-token replacement, and the unmodified reference. Observe answer correctness, latent transition/exit behavior, and per-example divergence. Keep *readout for observation* separate from *replacement for intervention*.
2. **Mode restriction (concept):** compare a trained hybrid model with latent entry enabled versus disabled and against a separately trained text-only control. Never treat blocking latent mode as zero-cost governance.
3. **Trust-boundary control (concept):** use a **simulated** effect sink with positive authorized and negative revoked/malformed/stale authority cases. Verify through independent sink observations that arbitrary latent/readout content does not bypass the structured external action gate.
4. **Mechanism-specific falsifier:** distinguish equal-norm or equal-distance perturbations with different *content*. A larger quoted perturbation score does not inherently imply a stronger causal intervention.

**Before registering any experiment** under W2: name the code/environment, fixed inputs and admissible population, feasibility count, prediction numbers, exact primary metric and decision boundary, controls and sabotage, sampling/stopping/statistics, compatibility assumptions, costs, and responsible human review. Freeze predictions **before** observing the target outputs. The methods and bounds above are proposals, not accepted predictions.

## 5. Triggered controls and disclosure

- **C-EXT:** Applies; external paper and code are identified by exact links/revision. No externally submitted private text has been reproduced.
- **C-FEAS:** Applies if benchmark-arm eligibility is claimed; **not performed**.
- **C-NOISE / C-STAT:** Trigger if comparative stochastic claims are registered; **not performed**.
- **C-EVID:** Applies to independently validated authorization claims; **not performed**.
- **C-INDEP:** Applies to replication claims; current status **no replication**.
- **C-DEVICE:** Applies to any platform claim; **no device runs**.
- **C-BUILD:** Applies if an action-verdict harness is built; **no harness**.
- **C-EXPLORE:** Any exploratory runs that support future claims need recording; **no runs conducted**.
- **C-METHCOMP:** Applies if comparing these methods empirically; **protocol not registered**.

**Next authorized door:** independent reviewer checks source transcription, then owner separately approves an isolated registration. This document does not authorize execution, repository-level integration, publication of unpublished designs, or changes to existing trials.
