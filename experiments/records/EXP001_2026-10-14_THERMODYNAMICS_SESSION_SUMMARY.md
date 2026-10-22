# EXP001 — Thermodynamics session synthesis (2026-10-14)

**Status:** exploratory, operator-reported; physical calibration and independent reproduction outstanding.

**Canonical numerical evidence:** [Morning field record](./EXP001_2026-10-14_MORNING_FIELD_RECORD.md), including R1–R3 descriptive statistics, file names and SHA-256 digests, clock diagnostics, Shizuku access checks, battery and Android thermal-service excerpts, and retained failures. **Do not copy numbers from this synthesis in place of that record.** The original CSV and Shizuku JSON evidence remain private on the operator's handset; they have not been uploaded or independently rehashed.

## Scientific question
Can a handset provide sufficiently reliable, time-aligned temperature and activity measurements to support later controlled investigation of computation-related thermal response? This session addressed **instrument observability**, not a thermodynamic law.

We did not measure electrical power input, heat flux, system boundaries, ambient reference temperature, calorimetric energy change, or entropy production. Consequently, neither first-law energy balance nor second-law entropy-production rate can be inferred from the available observations.

## What the morning established
1. **Thermal channel availability:** five candidate sysfs sensors could be sampled repeatedly. Raw/1000 °C is a hypothesis; sensor identity and calibration remain unverified. The inventory also exposed five suspected `-273000` sentinel readings.
2. **Control sensitivity:** R1 and R2 showed substantially different CPU-labeled temperature variance. Unmeasured interactive handset activity is a possible confounder, not an established cause. R3 still showed elevated CPU-labeled maxima under a nominal idle label, with CPU utilization and battery state missing from that run.
3. **Clock integrity problem:** R3 wall and monotonic elapsed time disagreed by 227.519 seconds. A later ten-second triple-clock check agreed within milliseconds. Neither device suspension nor wall-clock adjustment has been established as the explanation.
4. **Shizuku instrumentation path:** Android shell access exposed aggregate CPU counters and battery/power/thermal services unavailable through the earlier Termux-only route. Two stored counter snapshots supported a calculated 4.35% aggregate busy fraction across a nominal five-second delay. This observation was **not simultaneous with R1–R3**.
5. **Cross-interface ambiguity:** Android battery service and thermalservice returned materially different BAT-labeled temperatures. There is no established mapping to the sysfs thermal zones, and `SUBBAT=0.0` must not be assumed to represent a valid physical temperature.
6. **Failure preservation:** the initial Python CPU parser raised an IndexError; the later multi-probe subprocess identity returned empty stdout despite exit code 0 and earlier direct identity success. These failures remain unresolved and should not be rewritten as successful checks.

## Implications for thermodynamic inference
Temperature trajectories alone cannot establish a heat-transfer coefficient, power dissipation, entropy generation, or computational efficiency. The observed run-to-run differences are a reason to improve instrumentation and experimental controls—not evidence that a specific thermal mechanism has been identified.

The Android thermal-service status of 0 and the battery charging status of discharging describe device-service states at their own acquisition times. They do not prove that a controlled thermal equilibrium or steady state was achieved.

## Next protocol: proposed R4 (not executed)
- Preregister idle versus defined workload conditions, repetitions, randomization/counterbalancing, exclusion criteria, and cooling periods.
- Timestamp each channel with UTC, CLOCK_MONOTONIC and CLOCK_BOOTTIME; retain source, acquisition latency, exit code, missing-data reason and unexpected gaps.
- Pair thermal sampling with delta-based aggregate CPU activity and battery/power/screen state **at comparable times**, rather than combining historical process reports with new measurements.
- Validate sensor identity and scaling, or restrict claims to named raw channels. Keep independent calibration and external replication as open milestones.
- Preserve immutable raw data, SHA-256 manifests, script revisions and negative outcomes. Review Android service dumps for sensitive metadata before any public release.

## Repository status
Earlier thermal tooling PRs #41–#44 were merged. PR #45 concerns suspected-sentinel classification and synthetic regression; its CI status must be evaluated independently. This synthesis and its canonical field record are part of PR #46. Neither a green CI check nor a merged documentation PR constitutes physical or scientific validation.

**Bottom line:** a promising measurement pathway was demonstrated, but the instrument is not yet validated for causal thermodynamics experiments.
