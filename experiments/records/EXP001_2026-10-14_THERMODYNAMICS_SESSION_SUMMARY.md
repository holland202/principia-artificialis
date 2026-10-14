# Thermodynamics research — morning session synthesis
**Date:** 2026-10-14  
**Program:** Principia Artificialis  
**Experiment:** EXP001, Samsung Galaxy S25 Ultra / Termux thermal observability  
**Status:** exploratory physical measurements, operator-reported; **not** independent scientific validation

This document consolidates the thermodynamics-oriented work of the morning. The detailed numerical and provenance record is [EXP001_2026-10-14_MORNING_FIELD_RECORD.md](./EXP001_2026-10-14_MORNING_FIELD_RECORD.md). This is a *summary and interpretation*, not a replacement for the local raw evidence.

## Research question and claim boundary
We investigated whether the handset provides repeatable, accessible temperature observations suitable for later controlled tests of thermal response to computational activity. This morning's work does **not** measure heat flow, dissipated electrical power, entropy production, thermodynamic efficiency, ambient temperature, or thermal resistance. A CPU-temperature proxy alone cannot establish any of these.

Candidate thermodynamic relation for future controlled study: if electrical power input and boundary heat flows become measurable, a first-law energy balance could be tested. A second-law entropy-production estimate additionally requires justified temperatures, heat flows, system boundaries and assumptions. Neither balance has been fitted or validated here.

## Experimental sequence
1. **Inventory:** 68 Android thermal zones, 63 candidate readings and five raw `-273000` suspected invalid sentinels; selected five sensors (cpu-1-0-0, cpu-1-0-1, gpuss-0, battery, sys-therm-5). Raw/1000 °C is an **assumption**, not independent calibration.
2. **R1 passive baseline:** 30 observations per selected sensor (150 total), nominal two-second cadence, ~58.11 seconds elapsed; battery mean 33.070°C, cpu-1-0-0 40.133°C, cpu-1-0-1 40.383°C, gpuss-0 39.477°C, sys-therm-5 25.494°C. On-device CSV SHA256 `d63bdc1dae45a653260214d397aec5d53bcd0bd123929c5d1017ddf5b05cca1a`.
3. **R2 passive baseline:** another 150 observations; battery mean 33.383°C, cpu-1-0-0 43.937°C, cpu-1-0-1 45.223°C, gpuss-0 40.860°C, sys-therm-5 25.494°C. CPU-labeled temperature sample SD rose from 1.614 to 7.399°C (cpu-1-0-0) and 1.763 to 9.990°C (cpu-1-0-1). The phone was reportedly unplugged during R1 and R2. Concurrent interactive phone activity in R2 was a potential but unmeasured confounder. CSV SHA256 `391dfffffbf6bcd060d89dadf40dd964710259b02c070c4d6593448989411e53`. Local hash checks for R1/R2 matched.
4. **R3 nominal idle:** 150 temperature observations; cpu-1-0-0 ranged 36.1–66.5°C and cpu-1-0-1 36.1–74.9°C. Attempts to read CPU activity via Termux `/proc/stat` and battery status via sysfs returned no usable values (0/150 CPU activity; 150/150 unavailable battery status). CSV SHA256 `4fd26df79f7bbe5d28386c8103bc55f62b607e4de425f86b1df64b68d4682bd9`, operator-reported.
5. **R3 time anomaly:** wall-clock elapsed 285.641 s, monotonic elapsed 58.122 s, difference 227.519 s. Android suspension and wall-clock changes remain competing *hypotheses*, not established explanations. Subsequent active 10-second test found wall 10.002475 s, monotonic 10.0025061420165 s and boottime 10.00267082900973 s, without reproducing the anomaly.
6. **Shizuku privilege test:** Shizuku started temporarily; direct `rish -c 'id'` returned uid=2000(shell). `/proc/stat`, `dumpsys battery`, `dumpsys power`, `dumpsys thermalservice`, and `dumpsys cpuinfo` were accessible in subsequent checks. The first Python CPU parser failed with `IndexError`; this failure was retained.
7. **Read-only Shizuku probe:** JSON `exp001_shizuku_probe_20261014.json`, device SHA256 `bbbc0988e11375df963ddd6be8d5573312d3a3fd40dd2daa7a1f6e7c390da56b`. Six subprocesses exited 0, but the subprocess identity stdout was empty. CPU snapshots were 144 bytes each; battery 4307; power truncated to 30000; thermalservice 1495; cpuinfo 8192. Raw JSON kept private on handset.
8. **Offline CPU calculation:** counter total delta 4294; idle+iowait delta 4107; aggregate busy fraction `187/4294 = 4.35%` (rounded), across nominal five-second delay. This validates a measurement pathway, not synchronized thermal correlation.
9. **Battery/power:** service snapshot showed 77%, discharging (`status: 3`), no AC/USB/wireless/dock power, `temperature: 342` interpreted as 34.2°C using Android battery-service convention. Earlier direct battery query showed 33.7°C; historical event values differ and must not be mixed as simultaneous.
10. **Thermalservice:** `Thermal Status: 0`; cached AP 48.4°C, PA 46.3°C, BAT 26.6°C, SUBBAT 0.0°C. No verified mapping from these service labels to the five sysfs sensor labels. The battery-service 34.2°C and thermalservice BAT 26.6°C disagreement is unresolved; SUBBAT 0.0°C is not assumed valid.
11. **Historical CPU process report:** `dumpsys cpuinfo` listed load averages 10.69/10.71/10.86 and earlier process percentages (ChatGPT 31%, system_server 17%, surfaceflinger 13%). Its reported historical interval is not the 4.35% counter sampling interval; do not infer causation.
12. **Repository engineering:** thermal evidence/checkpoint/witness/inventory PRs #41–#44 merged previously. PR #45 introduced sentinel classification and regression test, but the latest checked `exp001-sensor-inventory` workflow was failing; `verify-all-notes` passed. This field record is in PR #46. **No physical calibration, independent device replication or controlled thermal response test completed.**

## What was learned
- Five thermal channels can be sampled repeatedly from unprivileged Termux, but their absolute calibration and correspondence to physical locations are unknown.
- R1 and R2 differ materially in CPU-labeled temperature variation; this demonstrates an important confounder/control problem, **not** a validated thermal law or causal workload effect.
- Android's Shizuku shell exposes aggregate CPU counters and service-reported battery/power/thermal information that was unavailable through the earlier unprivileged access path.
- A CPU utilization fraction can be calculated from two valid `/proc/stat` samples, but the sampling clock and temperature acquisition must be synchronized for future inference.
- Multiple Android thermal interfaces can disagree strongly; combining their temperatures without a crosswalk would create false precision.
- Anomalous wall/monotonic time disagreement remains unexplained; all future sampling must preserve all three clock domains.

## Negative results, uncertainties and evidence gaps
- Failed initial Python subprocess CPU parser (`IndexError`).
- R3 CPU utilization and battery charging state missing in all attempted samples.
- R3 timing anomaly unexplained.
- Shizuku identity subprocess exited 0 but yielded no stdout despite earlier direct successful identity.
- Thermalservice BAT and battery-service temperature disagreement.
- Unknown sensor identity, unit scaling and calibration; no controlled workload, ambient reference, electrical power, heat flux, or calorimetry.
- Raw R1/R2/R3 CSVs and Shizuku JSON **not uploaded** to GitHub. The hashes document local evidence claims but do not independently authenticate their content.

## Next experiment design (proposal, not executed)
A preregistered R4 should capture thermal readings and CPU counters with UTC, CLOCK_MONOTONIC and CLOCK_BOOTTIME timestamps per sample; power/charging/screen state; error/timeout codes; per-channel validity; and explicit clock-gap flags. Compare randomized or counterbalanced idle and defined computational workload intervals, with replicates and cool-down criteria. Preserve untouched raw evidence, scripts, source hashes and device/environment metadata. Calibrate or at least establish consistent sensor identities before interpreting physical temperatures. Keep thermodynamic model fitting downstream of instrument validation and control testing.

## Evidence status
**Observed/reported:** raw access, 3 runs, descriptive statistics, 4.35% CPU calculation, Android service excerpts. **Derived but provisional:** candidate °C values and busy fraction. **Not established:** heat transfer or entropy-production rates, thermal efficiency, causality, sensor accuracy, reproducibility across devices. AI-assisted synthesis; not independent verification.
