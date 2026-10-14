# Experiment #001 — Morning field record (2026-10-14)

**Provenance:** operator-reported Termux outputs, not independently reproduced. Original CSVs remain on the device and have NOT been uploaded. All temperature conversions (raw/1000) are candidate, uncalibrated measurements.

## Instrument
Samsung Galaxy S25 Ultra / Termux. Inventory: 68 thermal zones; 63 candidate readings; five `-273000` suspected sentinel readings (sdr0_pa, mmw0–3). Selected: zone17 cpu-1-0-1, zone16 cpu-1-0-0, zone23 gpuss-0, zone60 battery, zone52 sys-therm-5. Sensor identity and scale not independently verified. Five synthetic tests previously passed locally. GitHub PR #45 introduces sentinel classification; initial CI failed due to escaped newline source defects; fixes pushed as commits 6b1d7eebe7ed17f8e6421ce3d6caff5213e9ebaa and 6e3ef89c892aa8a8ae2cdf29efb1634efd21ad69. Do not assume PR #45 green or merged.

## R1
File `exp001_baseline_20261014.csv`, 151 lines = header + 150 readings (30 per sensor), target 2-second cadence, elapsed ~58.11 s, all candidate_unverified.
SHA256 `d63bdc1dae45a653260214d397aec5d53bcd0bd123929c5d1017ddf5b05cca1a`.

## R2
File `exp001_baseline_R2_20261014.csv`, 151 lines; metadata `exp001_baseline_R2_20261014_metadata.json`, calibration_verified false.
SHA256 `391dfffffbf6bcd060d89dadf40dd964710259b02c070c4d6593448989411e53`.
Comparison script reported hash matches True for both R1 and R2. Operator reports phone was not charging during either run; interactive ChatGPT/GitHub work was concurrent with R2, but local CPU effect is unmeasured.

| Sensor | R1 mean | R1 range | R1 SD | R2 mean | R2 range | R2 SD |
|---|---:|---|---:|---:|---|---:|
| battery | 33.070 | 33.0–33.1 | 0.047 | 33.383 | 33.2–33.6 | 0.160 |
| cpu-1-0-0 | 40.133 | 38.4–45.3 | 1.614 | 43.937 | 38.0–64.2 | 7.399 |
| cpu-1-0-1 | 40.383 | 38.4–46.9 | 1.763 | 45.223 | 38.0–74.2 | 9.990 |
| gpuss-0 | 39.477 | 38.0–42.3 | 1.001 | 40.860 | 38.0–51.1 | 3.171 |
| sys-therm-5 | 25.494 | 25.486–25.501 | 0.004 | 25.494 | 25.481–25.512 | 0.006 |

Temperatures in candidate degrees Celsius. Thermal stability was not reproduced; workload causation unverified.

## R3
File `exp001_R3_idle_20261014.csv`, 151 lines, 150 candidate_unverified readings, 30 per sensor.
SHA256 `4fd26df79f7bbe5d28386c8103bc55f62b607e4de425f86b1df64b68d4682bd9` (operator-reported; no second hash verification).
CPU utilization values 0/150, battery status unavailable 150/150: attempted /proc/stat and /sys/class/power_supply/battery/status channels did not yield usable readings. No CPU-workload correlation established.
Wall-clock span 285.641 s versus monotonic span 58.122 s; discrepancy 227.519 s, cause unknown (suspension or clock change are hypotheses).

| Sensor | R3 min | R3 max | First | Last |
|---|---:|---:|---:|---:|
| battery | 32.9 | 34.2 | 34.2 | 32.9 |
| cpu-1-0-0 | 36.1 | 66.5 | 41.1 | 36.1 |
| cpu-1-0-1 | 36.1 | 74.9 | 41.5 | 36.1 |
| gpuss-0 | 35.7 | 41.1 | 39.6 | 35.7 |
| sys-therm-5 | 25.476 | 25.507 | 25.491 | 25.481 |

## Clock diagnostic
10-second test: wall 10.002475 s, monotonic 10.0025061420165 s, boottime 10.00267082900973 s. Both CLOCK_MONOTONIC and CLOCK_BOOTTIME available; clocks agreed in short test. This does NOT explain R3 discrepancy.

## Shizuku and next steps
Operator reports Shizuku is installed but NOT running. No Shizuku-assisted measurement was performed. Shizuku is a proposed route to investigate Android service data, not a guarantee of /proc/stat or sysfs access.
Next: preserve original CSVs; instrument UTC + monotonic + boottime simultaneously, detect timing gaps; independently record charging, screen and CPU workload where permissions allow; use pre-registered, repeated controlled conditions before causal claims. Do not infer entropy, heat capacity or safety thresholds from these temperatures alone.

## Claim boundaries
**Verified from supplied transcript:** scripts completed; R1/R2 local hash checks True; row counts; descriptive statistics; R3 timing anomaly; clock test. **Not independently verified:** sensor identity/calibration, causes of CPU spikes, source of clock discrepancy, physical repeatability, workload correlation. No physical CSVs or device metadata were published with this note.


## Addendum — Shizuku-assisted diagnostic, 2026-10-14

**Status: device-reported measurement and derived check; independent reproduction not performed.** This addendum supersedes the earlier statement above that Shizuku had not been used; that statement accurately described the earlier phase. Shizuku was subsequently started and used for a separate diagnostic. Do not retroactively assign these readings to R1, R2, or R3.

### Access and acquisition
- Termux resolved both `rish` and `adb`. A direct `rish -c 'id'` returned `uid=2000(shell)`, context `u:r:shell:s0`.
- A direct shell read of `/proc/stat` returned aggregate and per-core counters. `dumpsys battery` showed no AC/USB/wireless/dock power, `status: 3` (discharging), level 77%, and `temperature: 337` (33.7°C under Android battery convention); `dumpsys power` included `mWakefulness=Awake`.
- Initial Python subprocess counter test raised `IndexError: list index out of range`. This is a **retained negative result**, not proof of a permission denial.
- Subsequent read-only multi-probe collection succeeded with process exit code 0 for identity, CPU counters (two samples), battery, power, thermalservice, and cpuinfo. Captured stdout lengths: identity 0 bytes, CPU first 144, CPU second 144, battery 4307, power 30000 (truncated by collector), thermalservice 1495, cpuinfo 8192. The identity subprocess's empty stdout is unexplained despite exit 0; direct identity check had succeeded.
- Private device evidence: `exp001_shizuku_probe_20261014.json`, SHA-256 reported by device `bbbc0988e11375df963ddd6be8d5573312d3a3fd40dd2daa7a1f6e7c390da56b`. **The raw JSON is not in this repository**, and this digest is not an independent checksum of uploaded bytes.

### Offline derivation from preserved CPU counter snapshots
A follow-up Python script read the two aggregate `cpu` lines from the saved JSON, rather than invoking Shizuku again. Aggregate total delta = 4294 ticks; idle+iowait delta = 4107 ticks; calculated busy fraction = `(4294 - 4107) / 4294 * 100 = 4.35%` (rounded). Sampling delay was nominally five seconds; exact timestamps of the two shell reads were not separately logged. This validates the *calculation pathway* for one interval, not CPU-to-thermal causality, individual-core usage, or idle workload conditions.

### Android service excerpts and interpretation limits
- Battery service snapshot: AC/USB/wireless/dock `false`; `status: 3`, `level: 77`, `voltage: 4054`, `temperature: 342` (34.2°C by Android convention). The service also contained historical battery-change events with differing levels, voltages and temperatures. **Do not treat historical event values as simultaneous with the snapshot.**
- Thermal service: `Thermal Status: 0`, cached `AP=48.4`, `PA=46.3`, `BAT=26.6`, `SUBBAT=0.0` (service-reported °C). No identity mapping or calibration to the sysfs zones used in R1–R3 has been established. In particular, `BAT=26.6` differs from the battery-service 34.2°C; neither value should be silently substituted for the other. `SUBBAT=0.0` is not assumed to be a physically validated temperature.
- `dumpsys cpuinfo` showed historical load averages 10.69/10.71/10.86 and process-level percentages for a window described as 229167 to 177017 ms before the dump, including `com.openai.chatgpt` 31%, `system_server` 17%, and `surfaceflinger` 13%. These are **not simultaneous** with the 4.35% aggregate counter interval, and the percentage denominators may differ. They do not establish a causal explanation for R2 or R3 spikes.
- `dumpsys power` stdout was truncated to 30,000 characters; no conclusion about its completeness is warranted. Exit 0 indicates process completion, not semantic validity of every field.

### Current evidence boundary and follow-up
**Supported:** Shizuku's shell identity worked in a direct test; CPU counters could be collected twice and yielded a valid positive-delta aggregate utilization calculation; Android battery and thermal services were accessible; one snapshot reported discharging. **Unresolved:** earlier Python `IndexError`, identity subprocess empty stdout, physical sensor calibration, cross-interface sensor identity, R3 clock discrepancy, workload attribution, time synchronization, and independent reproduction.

Future R4 collection should preregister controls and log timestamps per channel (UTC, MONOTONIC, BOOTTIME), shell exit codes, parsing validity, and missing-data reasons. Do not publish the raw service dump without privacy review. No new live Shizuku run is needed for this addendum.
