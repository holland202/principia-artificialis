# Sovereign Evolution: A Record of the Work

Chad Edward Holland · 2026-10-03

Status: **DRAFT — historical reconstruction — not yet publication-ready.** A history of the program, not a research
result. Not promoted or announced. Each person credited below was shown their exact line on 2026-10-03 and
replied "Ok sounds good" (replies relayed by the author). Drafted by Claude (Claude Opus 5.5) at the
author's request from the repositories and session records; not yet reviewed line by line by the author (see
Provenance). Where a number here disagrees with a repository, the repository wins.

## Abstract

In eight months I went from AI instruction sets that reported success they never measured to instruments that report failures they did measure. This paper is the record of that change, kept honestly.

I started in February 2026 with no software background. I build oilfield workover rigs for a living, and I did all of this on a Samsung Galaxy S25 Ultra under Termux. I worked with AI models (Claude, ChatGPT, Gemini, Grok, Kimi, Perplexity) as instruments. The early work, February to May, was prompt documents and code that could not fail: a governance oracle that refused only when the literal word "hallucination" appeared, and a thermal fallback that invented a safe temperature. From July on, every claim had to be registered before it was run, carry a control that could return null, and keep its failures.

The main products today are research prototypes, not products:

- **sovereign-veritas**: a fail-closed permission gate for AI actions. It conforms to 4,690 contract vectors and catches 19 of 19 planted bugs. It also verifies a fully consistent rewrite, and no one else has reproduced it yet.
- **evidence-ledger**: evidence-state semantics. 10 of 11 predictions held; one was refuted and kept.
- **Principia-Artificialis**: 87 indexed notes, 12 of them with refuted claims kept on purpose.
- **Detection baselines on public industrial benchmarks**: SENTINEL scored S = 0.432 on BATADAL, below every published entry. That was published as a negative result.

No result here has been independently reproduced. No human-subjects data exists. The most useful thing this program has produced is a way of working that catches its own errors, including the AI's.

## Why I started

I started because someone in my family became seriously ill. I wanted to understand the illness better, keep track of results, and get answers I could trust, so that we were prepared when we sat down with the doctors.

Ordinary chatbots gave confident answers I had no way to check. In that situation, a wrong answer that sounds sure is worse than no answer. It can send you into an appointment with the wrong questions, or the wrong fears. So the requirement came first, before any architecture: **the tool must not mislead me, and when it does not know, it must say so.** The doctors make the medical decisions. What I wanted was to understand, and to ask better questions.

Two more requirements came from the same place:

- **Private.** Personal information should not leave the phone. That is why everything runs on-device, on a Samsung Galaxy S25 Ultra under Termux, with no cloud dependency.
- **Checkable.** I could not judge a medical claim myself. So I needed a system whose answers carry the evidence behind them, and that refuses when the evidence is missing.

### What I brought to it

I am not a trained programmer. I have been a machine builder in OEM manufacturing since 2012, building oilfield workover rigs, leading OSHA toolbox talks and training new builders. Before that I was a pumper operator, 2009 to 2012. I hold a DOL Machine Builder certification (2019).

That background shaped the work more than any software habit. On a rig, you do not trust a gauge you have not checked against a known reference. A safety check that cannot fail is not a safety check. You write down what broke, because the next person will meet it again. Those three shop rules later became the program's core method rules: anti-vacuity, verification before claims, and keeping failures.

### What it was not, at the start

My early instruction sets did not achieve any of this. I did not yet know how to tell a system that sounds rigorous from one that is. An early whitepaper even listed clinical monitoring as a target use. It was never fit for that, and it is not now. Nothing in this program is a medical device or gives medical advice.

## Timeline

| Phase | Dates | What happened |
| --- | --- | --- |
| Instruction sets | Feb to May 2026 | Gemini prompt systems; whitepapers with no tests; checks that cannot fail |
| Runtimes | Jul to Aug 2026 | SLC, SKN, QUASAR; BATADAL S = 0.432; public claims refuted |
| Method | 2026-07-26 to 2026-09-22 | Vacuity finding; registration first; HAI, VERA, Principia |
| Evidence tools | 2026-09-22 to 2026-10-03 | SWAY adopted; Sovereign Veritas; evidence-ledger, EACE |

The runtime work and the method overlapped. The vacuity finding on 2026-07-26 is where the program turned from describing systems to measuring them.

## Phase 1: the instruction-set era (February to May 2026)

The first phase produced documents and prompt systems that described a working system. None of them measured one. I record them here as specimens, because the rest of the program is a reaction to them.

### What it was

The first artifact was "Sovereign Suite (v.2026.02)", a system prompt written with Gemini. It ran three agent personas and used named mathematics as decoration: Cauchy, Ramanujan-Sato, Black-Scholes, S = k ln W, FFT. It required a "Hidden Layer" insight on every response. Whitepapers followed in April and May, with code attached.

The content worth keeping from this phase is the goal and a few distinctions. Separating what a system knows from what it assumes is one of them. The mechanisms were not real.

### What was wrong with it, measured later

In July and August I went back through the archive with a sorting rule. A note was pulled if it had a number the system reported about itself, a check that can only pass, a capability claim it does not have, or code presented as working.

| Specimen | Date | Defect, as measured |
| --- | --- | --- |
| Sovereign Suite system prompt | Feb 2026 | A mandatory "Hidden Layer" insight is an instrument that can never return null. Its MSE > 0.15 self-audit cannot run. |
| Epoch 1 Manifest (turns 1–500) | Feb 2026 | Every number is confabulated (MSE 0.22 / 0.18 / 0.19 "RECOVERED"). A story, not a measurement. |
| Sovereign-Omega v2026.04.11 | Apr 2026 | The gate refuses only if the literal string "hallucination" appears. Maths is "verified" by grep for "GAUSS-BONNET". |
| Thermal script | spring 2026 | Raises AttributeError on battery read; the echo-redirect writes nothing; logic inverted. |
| Parallel Engine v1.4.0-ULTRA | 2026-05-16 | No threading. 4 of 6 kernels dead. A 64-character SCADA report and 64 letter a's give byte-identical output. |
| Hyperbolic Manifold Engine v1.1.0 | 2026-05-16 | A weight is never updated yet exported as "Final Converged". Thermal fallback returns 34.2 + random noise: a fabricated safe temperature. |
| SIC v10.3 | measured 2026-08-08 | Raises on the first call. The rejection branch is unreachable. Identity check accepted 647 of 1,000 strangers. |
| Sovereign Suite Master Archive v0.1.5 | 2026-05-24 | Governance appears in no code. The governor sends one hardcoded control vector forever. |
| Sovereign Topological Kernel whitepaper | May 2026 | Asserts unimplemented mechanisms and names a clinical target. Not published; its claims must be stripped before it goes anywhere. |

One artifact from this era was real: a llama.cpp Android build log. BUILD SUCCESSFUL in 21 seconds, real ARM feature detection, ggml 0.9.4.

### Why it went wrong

The instruction sets rewarded output that sounded deep. The models complied and produced it, and I could not yet tell that from output that was correct. Thresholds disagreed across documents. Only one constant from the era survived as something real and tested: a 38.5 °C thermal limit, and later work found even that miscalibrated for this device.

This was not bad faith. It was what happens when the one person checking the work cannot check it, and the tools are rewarded for sounding right.

## Phase 2: runtimes and public benchmarks (July to September 2026)

In July the work moved from documents to code that runs, and from my own claims to public benchmarks scored by other people's metrics. Most of the results were negative. They are published that way.

### SLC v12: admission control for model memory

SLC sits between a language model's output and persistent memory and decides what is admitted. It generates nothing and contains no model.

- **Announced before it ran.** On 2026-08-09 I announced it on LinkedIn with Gibbs ΔG < 0 enforcement and Langevin dynamics. The same day, `core/engine.py` could not import: all six dependencies differed. Fixing five defects took cycles from 0 of 20 to 20 of 20.
- **Two public claims refuted.** ΔG was negative at every reachable temperature, so the gate could never refuse. The "Langevin" update ignored temperature. Both were later rebuilt and measured. The thermodynamic gate now admits 1 of 10 at scar_alpha 3.0, and the update is an Ornstein-Uhlenbeck process.
- **First real-model calibration (TinyLlama-1.1B).** At n = 8 the gate was inert (J = 0.000). At n = 30, P1 held (28 wins, 1 tie, 1 loss), and P2 was refuted: the best threshold was 0.348, outside the registered 0.40–0.60.
- **The device cannot run its own defense profile.** One CPU zone idles at 44.8 °C and passes 65 °C under load, against a 36.5 °C profile cap. P0 fails, and the README says so.

Current label: 8 of 10 probes on the device, 5 of 10 modules wired, integration against a real GGUF not verified.

### SENTINEL on BATADAL: a published negative result

SENTINEL's detection method (Jensen-Shannon divergence over sensor windows) was scored on BATADAL, a public water-network attack benchmark.

| Configuration | F1 | Official S score |
| --- | --- | --- |
| Conservative | 0.251 | 0.379 |
| Balanced | 0.225 | 0.432 |
| Aggressive | 0.023 | 0.351 |

The best S, 0.432, is **below every published entry** (the lowest, Aghashahi, scored 0.534). It detects 4 of 7 attacks. The configuration ranking flips between F1 and S, so shipping on the F1 headline would have shipped the wrong configuration. The scoring code was cross-checked against an independent implementation (ipal_evaluate) and agrees within 0.003. My novelty claim was retracted when that prior art turned up. The repository says to read it as a reproducible baseline, not a working detector.

A follow-up detector, VERA, reached S = 0.796 at the pre-committed α = 0.01. An earlier "always-alarm" finding was retracted as prior art.

### SENTINEL and VERA on HAI

The HAI benchmark repo opened with the registration as commit #1. SENTINEL's precondition P0a **failed** (breach rate 0.042402 on 61,861 ticks, against a registered band of 0.05–0.2), so P1 and P3 are void. VERA's P0a passed (0.115845), the first P0 gate to pass in that repo. Two of its other predictions were refuted. A later audit found the verification script had read the held-out set's label columns. The defensible claim was narrowed to "no detector has scored test1".

### SKN: a swarm controller in simulation

SKN controls a formation of simulated nodes. The "natural gradient" was always a scalar times the identity: its step had cosine 1.000000000000 with the plain gradient over 1,200 measurements. The published figures were synthetic: hand-written exponentials and typed-in literals. They were regenerated from real output. A public ε = 0.05 m figure turned out to be the dt argument. Status: 5 of 9 subsystems implemented and tested, simulation only, no hardware.

### QUASAR: geometric attention

QUASAR tested whether a geometric (Bures) attention beats dot-product attention. The founding premise was refuted: geometry beat dot in 0 of 5 seeds. The cause was found: attention was dead, entropy 2.0782 against a maximum of 2.0794. Later runs that seemed to favour geometry were voided by a temperature confound. The "recursive self-improvement" extension (RSI-1) was closed as not admissible: the evolved genome lost 8 of 15 at matched seeds.

## Phase 3: the method

The method came from the failures, not before them. Each rule exists because a specific failure happened without it.

### The finding that started it: verification that cannot fail

On 2026-07-26 I found that four of my codebases had verification that could not fail. Some printed `[FAIL]` and exited 0. Others had a fail branch that nothing could reach. A script printed "MATH IS WRONG - STOP" and exited 0. I named this vacuous verification and built a linter for it, `vacuity_lint.py`.

The linter's own record is mixed, and it is published that way:

- It catches the first type (no fail path) and misses the second (a fail path that cannot fire). It found 2 of the 4 known cases.
- I registered that at least half of my repos would be affected. Refuted: 6 of 13.
- Against a control group of other people's repositories it found 0 true positives in 347 files, and 2 of 15 in mine. The bigger difference was volume: 34.7 verification-shaped files per repo in mine against 1.2 in the control, 28 times as many.
- A third type it cannot see turned up in September: a test whose verdict is redrawn on every run. One gate's count ranged 31 to 62 over 60 runs.

### SWAY (adopted 2026-09-22)

SWAY is the binding method across the program ([METHOD.md](../METHOD.md)). It is rigorous where a claim is promoted, and it bends where exploration needs room. Its index has 18 core rules (M1–M18), 9 workflow steps (W1–W9) and a set of triggered controls. The ones that matter most:

| Rule | What it requires | The failure it answers |
| --- | --- | --- |
| M2 Register before observing | Predictions committed alone, before any code runs | Phase 1 numbers chosen after the fact |
| M3 Anti-vacuity | Every instrument has a control showing it can return the other answer; a `--sabotage` run must exit 1 | Checks that could only pass |
| M6 Numbers come from code | Prose numbers are pasted from output | 71 of 216 prose numbers in Principia not found in any script output |
| M8 Failures lead and are kept | Refuted predictions stay, at the top | The urge to quietly drop a bad result |
| M10 Nothing certifies itself | A model's explanation of its own work is not validation | AI reviews agreeing with AI work |
| M11 Confirmation is fresh | Re-run before claiming | Stale copies reporting green |
| M13 AI provenance | Name the model; state only the review that happened | Overstated "validated" claims |
| M15 Every inquiry ends with a door | At least one prediction left unrun | Write-ups that sound finished |

The working pattern on every experiment:

1. Commit the registration alone, with exact pass criteria.
2. Build the smallest instrument against the real code.
3. Run it; the probe prints HELD or REFUTED per prediction, `VERDICT n of m as registered`, and a digest.
4. Pin the recorded outcome, so a later run passes only on that outcome.
5. Run the sabotage arm and confirm it fails.
6. Write the results with failures first, and append corrections rather than edit.

On 2026-10-03 one more working rule was added. When a question is about system behavior, answer it with a small executable test against the real code, not an explanation.

### What the method is not

SWAY is adopted, not validated. Whether it produces better research than a simpler practice is an open question. A comparison has been registered but not run, because it needs an outside task builder and scorer.

## Sovereign Veritas: the permission gate

Sovereign Veritas (created 2026-09-23) is the program's main artifact. It is a fail-closed permission gate for AI actions. Every decision can be packaged, signed and re-verified by a separate verifier. Its label: **PROTOTYPE, NOT PRODUCTION-READY, self-tested.**

### How it works

1. An AI proposes an action, with recorded inputs: runtime state, thermal status, authorization, budgets.
2. A deterministic Gate applies 13 rules and returns ALLOW, DEFER or REFUSE. Missing runtime state means REFUSE.
3. The decision and its inputs are written to an evidence package with digests.
4. A separate verifier, which does not import the kernel, recomputes the decision and checks the package.
5. Optionally, an SSH Ed25519 signature proves which key signed it, and a witness log proves its order among published packages.

### What a valid package proves, and what it does not

A valid package proves the package is well-formed, its digests match, and the recorded inputs produce the recorded decision. It does **not** prove the inputs were true. A fully consistent rewrite verifies: change the inputs and the decision together, recompute the digests, and every check passes. A signature proves who signed, not that the world was as described. This limit is stated at the top of the README.

### Measured

| Check | Result |
| --- | --- |
| Kernel and verifier against the gate contract | 4,690 vectors, both conform, one digest |
| Deliberate bugs planted in the Gate | 19 of 19 caught |
| Verifier guards switched off one at a time | 22 of 22 make a test fail |
| Contract rules switched off one at a time | 22 of 23 fail a vector; the 23rd cannot be reached |
| Truncations and bit flips accepted | 0 of 17,157 and 0 of 200 |
| Real package made on the S25 | 16 of 16 checks, CONSISTENT |
| CI | Linux, macOS, Windows × Python 3.10, 3.12, 3.14 |
| Reproduction by anyone else | none yet |

### What broke, and what it taught

- **GPS spoofing (V11).** A slow spoof walked a simulated ArduCopter 61 m outside its fence while every check passed. The gate checks evidence it was given, not the world.
- **Execution boundary (XB-1).** Reported by Davorin Popović and reproduced, 8 of 8 as registered. A repeated record id causes two real effects and one ledger record; a race causes two effects; a write failure leaves one effect and no record. The sequential case is fixed; the race and the effect-without-record case are open.
- **Defaults counted as healthy (F1).** A default compute budget or power status counts as if it had been declared. Measured-healthy and assumed-healthy should not be equal.
- **Fault injection.** One new defect: a NaN uncertainty value passed through. It is fixed (F3) and pinned.
- **Collapsed evidence states (EP-0, EP-1).** The Gate treats several different reasons for missing evidence the same way. Only "never searched" changes an outcome.
- **sv.gate/1 recount.** Of seven planned gate features, one (a consumed token) is built on main.
- **Duplicate JSON keys (DK).** Python keeps the last duplicate key, so a planted first value was invisible to the verifier. All 8 stored packages were vulnerable. The fix refuses duplicate keys and NaN/Infinity. It was merged on 2026-10-03 and is not yet validated on the S25.
- **External breaks.** An external review filed eleven breaks (issue #4); two are fixed. Labels like "PASS" and "authorized" are written by the caller.

### Where it stands

It is a verifiable authorization record for declared inputs. It is not proof that an action is safe or that its inputs are true. It should not control irreversible actions, money, vehicles or physical actuators without an independent enforcement layer. The two most urgent open problems are the trust boundary for inputs and the non-atomic link between execution and the ledger.

## The other instruments

The rest of the program is a set of smaller instruments. Each one tests one question. Each carries its own status label, and most report a refutation.

| Repository | The question | What was measured | Status |
| --- | --- | --- | --- |
| [evidence-ledger](https://github.com/holland202/evidence-ledger) | Can evidence states be kept apart from the claims they support? | EL-007: 10 of 11 as registered. P3 refuted (false support 0.091 vs ≥ 0.50 predicted). Ledger rollback caught 0 of 200 by the chain alone, 200 of 200 with a head witness. A canonicalizer attack showed wording steers which evidence is selected. | Experimental, not validated; unlicensed |
| [eace](https://github.com/holland202/eace) | Can an agent's containment be evaluated from evidence? | Verifier v0.1 broken by a 19-case attack corpus and frozen as the broken baseline. Core finding: integrity is not truth. Android sandbox escape not established. | Active research |
| [veritas-eval-harness](https://github.com/holland202/veritas-eval-harness) | Can an evaluation detect an agent that cheats? | It misses an agent that fakes the work; it only catches one that skips it. The second detector convicts an honest solver. | Draft, verified reference code |
| [token-veritas](https://github.com/holland202/token-veritas) | Can fewer tokens keep the answer? | At 20% of context tokens, plain top-k kept 0.825 accuracy (full context 0.975). The DPP selector hypothesis was refuted: its repulsion works on wording, not facts. | Run 2 REFUTED (kept) |
| [veritas-companion](https://github.com/holland202/veritas-companion) | Can a cheap layer save large-model tokens? | 2.67–2.86× fewer tokens on the S25 and more accurate on 3 seeds. A simpler rival did as well on 2 of 3 seeds. 0 of 60 on Loghub HPC. | Prototype |
| [veritas-holo](https://github.com/holland202/veritas-holo) | Does geometric state give reasoning an advantage? | Merges in 4.0 µs at 100 events; 8 of 8 held in E003. No equal-compute reasoning advantage found. 8 of 40 runs certified and wrong. | Research hypothesis, not shown |
| [veritas-science](https://github.com/holland202/veritas-science) | A framework for registered, adversarial experiments | Scaffolding; no headline result. | Framework |
| [Principia-Artificialis](https://github.com/holland202/principia-artificialis) | Mathematics of artificial thought | 87 notes indexed; 12 carry refuted claims kept on purpose. 145 of 216 prose numbers appear in script output; 71 do not, and are listed. | Each note labelled |
| veritas-reliance-study (private repository) | Does showing evidence states help people rely on AI appropriately? | Instrument only: 13 of 13 as registered with synthetic respondents. A post-run probe found condition C leaks the verdict through its row marks, and the chance floor is 0.5, not 0.4375. Correction appended; v0.2 registered. | Draft, self-tested; no human data |

Smaller probes sit beside these. A Forman-Ricci compute probe (K(x)) refuted two of its predictions: it was 2.15× worse than uniform. A soft-HyperDGA experiment failed P1 narrowly (gap 0.0617 against a bar of 0.05) and kept it.

All of these share the gate's lesson. Integrity, consistency and a passing test are each narrower than truth. Each instrument is built to show exactly how much narrower.

## Ledger of failures

These are the claims that broke, newest first. Every one is still in its repository. Several were Claude's own errors, and those are marked.

| Date | Claim | What happened | What it taught |
| --- | --- | --- | --- |
| 2026-10-03 | Reliance study condition C shows no verdict | Its row marks give the verdict: a glyph-only reader scores 32 of 32 (Claude's build) | A synthetic respondent that obeys the policy cannot detect a cue it ignores |
| 2026-10-03 | Evidence packages parse unambiguously | Duplicate JSON keys let a hidden first value pass in 8 of 8 packages | Canonical parsing is part of the trust boundary |
| 2026-10-02 | A ledger record means one effect | Repeated id: 2 effects, 1 record; write failure: 1 effect, 0 records | Execution and record must be bound, not sequential |
| 2026-10-02 | Separated evidence beats false support (EL-007 P3) | Worst false support 0.091, not ≥ 0.50 | The predicted effect size was wrong |
| Sep 2026 | DPP selection keeps facts with fewer tokens | Plain top-k did better; repulsion acts on wording | Test the simple rival first |
| 2026-09-16 | QUASAR self-improvement (RSI-1) | Evolved genome lost 8 of 15; verdict not admissible | Selection without matched seeds manufactures gains |
| 2026-09-11 | A gate is either vacuous or not | A count redrawn every run ranged 31–62 | Non-determinism is its own vacuity type |
| 2026-09-05 | SENTINEL fits HAI's normal data (P0a) | Breach rate 0.042 outside 0.05–0.2; P1 and P3 void | A failed precondition voids what depends on it |
| Sep 2026 | VERA drift coverage (P2) | Refuted at 0.929; the cause was Claude's windup bug | Check the harness before the hypothesis |
| Aug 2026 | QUASAR geometry wins (F21, F22) | Voided by a temperature confound | Calibrate arms before comparing them |
| 2026-08-10 | SLC threshold lies in 0.40–0.60 (P2) | Best threshold 0.348 | Registered bars can be wrong; keep them |
| 2026-08-09 | SLC enforces Gibbs ΔG < 0 (public claim) | ΔG negative everywhere; the gate could not refuse | Never announce before running |
| 2026-08-09 | SKN uses a natural gradient (public claim) | Always the identity; cosine 1.000000000000 | Inspect the metric, not its name |
| 2026-07-27 | SENTINEL competes on BATADAL | S = 0.432, below every published entry; novelty retracted | Use the benchmark's own metric |
| 2026-07-27 | Half my repos have vacuous checks | 6 of 13 | Measure your own prediction about yourself too |
| 2026-07-26 | Claude: run_all_tests.py is vacuous | Refuted: the thermal tests do exit 1 | The AI's audit is a hypothesis, not a finding |
| Feb–May 2026 | The Sovereign Suite works | Nothing measured; checks could only pass | The origin of every rule in this paper |

## What has not been shown

The limits are as much a part of the record as the results.

- **No independent reproduction.** No one outside this program has reproduced a result end to end. The kernel and the verifier agree on all 4,690 vectors, but one author wrote both.
- **Self-testing.** The code, the tests and most of the analysis were written with AI models, mostly Claude. A model reviewing a model of the same vendor is not independent review.
- **Device coverage.** Many results ran only in a cloud container and are marked "NOT VALIDATED on the S25". The device is the canonical place for runs.
- **No people.** No human-subjects data exists anywhere in the program. The reliance study has no participants and no ethics determination.
- **No real-world control.** Nothing here has controlled a real vehicle, actuator, payment or medical decision. Vehicle tests were simulation only.
- **Truth of inputs.** The gate verifies declared inputs. It cannot tell a true input from a well-formed false one.
- **Undemonstrated ideas.** I have described a faster maths model and a plasticity-weights AI. No predictions, code or numbers exist for either. Both are speculative.
- **The method itself.** SWAY is adopted, not validated against a simpler practice.
- **Stale text.** Some READMEs trail their own indexes: Principia's README says 84 notes, its index 87. The archived sovereign-suite README still states unqualified thermal and topology claims from the early era.

### Open doors

- [ ] An independent second implementation of the gate in another language, built without copying the Python
- [ ] A cross-language parse test (Go against Python) on the duplicate-key files
- [ ] Close the execution boundary: the race and the effect-without-record case
- [ ] Make defaulted inputs unable to satisfy high-risk authorization
- [ ] Build the remaining six sv.gate/1 features; decide where shared budget state lives
- [ ] A written threat model naming what is trusted: caller, sensor, OS, key, verifier, executor, clock
- [ ] Run the S25 checks for every "not validated on the S25" result
- [ ] Reliance study v0.2, then an ethics determination before any participant
- [ ] The SWAY methodology comparison, with an outside task builder and scorer

## Provenance

AI models took part in nearly everything here. I direct the work and I am responsible for it.

- **Models.** Claude (Anthropic) wrote most of the code, probes and write-ups since July. ChatGPT (OpenAI) designed the first eval-harness architecture. Gemini (Google) co-wrote the February to May material. Grok, Kimi and Perplexity wrote or critiqued Principia notes and several analyses. Every repository names the models it used.
- **Human review that happened.** I set direction, chose what to test, ran the on-device checks that this paper reports as run on the S25 (results not run there are marked "not validated on the S25"), and reviewed results and CI. I have not reviewed most of the code line by line, and the documents say so wherever it applies.
- **People credited.** Davorin Popović reported the execution-boundary defect. James Greenwood ran a Gemini-assisted audit of sovereign-veritas. Amos Tipton proposed the recovery A/B test. Graeme Randle gave the first external critique and drove the QUASAR geometry follow-ups. Dost Mushtaq asked the sharpest question about vacuity. None of these is an independent replication. Each was shown their exact line on 2026-10-03 and replied "Ok sounds good" (relayed by the author). That approves how they are credited, nothing more: not the work, the architecture or the results.
- **AI as instrument, AI as defendant.** The models were also wrong. Kimi fabricated statistics and retracted them. Claude claimed a test suite was vacuous when it was not, set prediction bars wrong, introduced the VERA windup bug, and built the reliance-study verdict leak. The method exists partly to catch these.

This paper was drafted by Claude (Claude Opus 5.5) from the repositories and my session records, at my request, on 2026-10-03. I have not reviewed it line by line. Its numbers are copied from the repositories' own output and records; where a number appears here and not in a repository, the repository wins.

## Sources

- [sovereign-veritas](https://github.com/holland202/sovereign-veritas): README and docs/*_RESULTS.md, main at d37779c (includes the duplicate-key fix, PR #33)
- [evidence-ledger](https://github.com/holland202/evidence-ledger): README and EL-007 results, main at 4852882
- [principia-artificialis](https://github.com/holland202/principia-artificialis): README and NOTES_INDEX.md, main at 36fff13
- [eace](https://github.com/holland202/eace), [veritas-eval-harness](https://github.com/holland202/veritas-eval-harness), [token-veritas](https://github.com/holland202/token-veritas), [veritas-companion](https://github.com/holland202/veritas-companion), [veritas-holo](https://github.com/holland202/veritas-holo), [veritas-science](https://github.com/holland202/veritas-science): READMEs
- [quasar](https://github.com/holland202/quasar) (with v2 merged in) and the archived [sovereign-suite](https://github.com/holland202/sovereign-suite)
- [sentinel-batadal-validation](https://github.com/holland202/sentinel-batadal-validation), [sentinel-hai-validation](https://github.com/holland202/sentinel-hai-validation), [skn-v1-](https://github.com/holland202/skn-v1-), [slc-v12-](https://github.com/holland202/slc-v12-): snapshot of 2026-10-02 (not re-read on 2026-10-03)
- veritas-reliance-study (private repository): RESULTS v0.1, Correction 1 and the v0.2 registration, main at 3a503ad
- The Feb–May 2026 archive (Drive, Keep, Samsung Notes): not public

## Changes

- 2026-10-03, after merge: status changed to "DRAFT — historical reconstruction — not yet publication-ready"; the S25 review line scoped to the checks actually run there; a note added that the credited people have not reviewed their descriptions. No number, finding or attribution changed. Edit by Claude (Claude Opus 5.5) at Chad Holland's request.
- 2026-10-03: each person credited (Davorin Popović, James Greenwood, Amos Tipton, Graeme Randle, Dost Mushtaq) was sent their exact line and asked to confirm, reword or be removed; each replied "Ok sounds good", as relayed by Chad Holland. No wording changed. James Greenwood was also asked which name he prefers; his reply did not name one, so the existing "James Greenwood" stands. Edit by Claude (Claude Opus 5.5) at Chad Holland's request.
