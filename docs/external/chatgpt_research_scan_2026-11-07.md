### Principia Artificialis — research evidence scan

November 7, 2026 · Public research sources · Read-only

One meaningful new candidate passed the intake threshold. A second release is worth tracking, but its direct relevance and computational requirements make it lower priority.

New discovery · High priority

### 1\. [ToyBlocks: A Controlled World for Robot Learning and Evaluation](https://huggingface.co/blog/allenai/toyblocks?utm_source=chatgpt.com)

Allen Institute for AI (Ai2) · Article by Kyle Wiggers / Ai2 Communications · November 6, 2026

Evidence level: Public research framework with author-reported simulation and physical-robot experiments; independent reproduction not established.

ToyBlocks provides controlled physics simulation, automated task and demonstration generation, held-out evaluations, and measurements beyond task success. The authors report 55.5% success over 200 simulated episodes versus 50% over 30 physical-robot episodes for one hierarchical system. They also report agent-written skill descriptions improving task success from 24% to 63%. Hugging Face

Reproducibility: Strong potential. Simulation assets, generators, training and evaluation code, model artifacts, and validation data are publicly described. No independent execution was performed. GPU requirements and sim-to-real limitations remain important.

License caveat: The article announces multiple released components, but their individual licenses and redistribution terms require artifact-level verification.

Suggested PA fit: High-value reference for SWAY, falsifiable generalization tests, negative controls, independent task scoring, and separating observed effects from agent-reported success. Especially relevant to GROWTH methodology and experimental task custody.

Newly identified release · Lower priority

### 2\. [NVIDIA Cosmos 3 — Interactive World Simulation](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation?utm_source=chatgpt.com)

NVIDIA Cosmos team · November 5, 2026

Evidence level: Public engineering release with open-weight checkpoints and author-described demonstrations; no independent verification here.

Four action- or control-conditioned world-model checkpoints support simulated driving scenes, RGB/LiDAR generation, and robot manipulation. The technical documentation explicitly distinguishes physics-derived state from generated visual observations and discusses error accumulation across long rollouts. Hugging Face

Reproducibility: Weights, examples, and post-training recipes are available, but the published setup uses NVIDIA GPU infrastructure. This is not presently a practical S25 Ultra benchmark candidate.

License caveat: OpenMDW1.1 terms apply to the model releases; open weights do not automatically imply unrestricted redistribution.

Suggested PA fit: Reference architecture for simulation fidelity, observation independence, and testing whether synthetic observations preserve ground-truth physical events. Defer hands-on testing.

Intake decision: Prioritize ToyBlocks for a read-only methodology comparison. Keep Cosmos 3 as a lower-priority reference, not an authorized experiment.

Previously reported CWE-bench v2, IBM's harness comparison, livenerf, HarnessJevBench, and Phonon TTS were excluded as duplicates. The public search also surfaced older MLCommons benchmarks and an earlier arXiv reproduction benchmark, but no additional sufficiently verified new publication. Codeberg and exhaustive peer-reviewed-venue coverage remain incomplete.

No repositories were changed, experiments launched, private research accessed, or contributors contacted.
