# Exp #001 measurement limitations (2026-10-14)

This note accompanies the revised thermal-monitor implementation. The monitor reads candidate Linux thermal-zone files, but **thermal_zone0/1/2 are not guaranteed to be SoC sensors**. Device-specific zone identity, calibration, units and placement must be established independently before any SoC-temperature claim. A readable value alone does not establish measurement traceability.

No sensor reading: append `state=unavailable`, `event=sensor_unavailable`, and blank temperature/proxy values. This is not a zero reading, not a stable observation, and not grounds to authorize an action. Existing historical CSV records remain unchanged and should not be retrospectively relabeled as validated measurements.

The `delta_g_proxy` is a parameterized illustrative expression, **not a measured Gibbs free-energy difference**. Its sign does not determine thermal safety; the configured temperature ceiling is a demonstration threshold, not a device-manufacturer limit. The script is a research prototype and does not enforce hardware throttling or independent fail-safe shutdown.

Suggested independent tests before deployment: simulate absent, malformed, NaN, infinite and out-of-range sensor values; verify blank fields and explicit unavailable state; test known sensor-zone identity on each device; compare against a calibrated reference and report uncertainty; test a ceiling crossing without relying on the proxy sign. Preserve all negative results.

References: NIST, *Traceability Considerations for the Characterization and Use of Measuring Systems* (2016), https://www.nist.gov/publications/traceability-considerations-characterization-and-use-measuring-systems-0 ; NIST, *Research Data Framework v1.5*, https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1500-18r1.pdf .
