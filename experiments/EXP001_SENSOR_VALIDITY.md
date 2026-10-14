# Exp001 sensor inventory and thermodynamic validity gate

This experiment addresses a physical measurement gap in Exp #001. On Linux/Android, `thermal_zoneN` indices are not globally meaningful sensor identifiers. A plausible numerical reading is not proof of CPU temperature, calibration, or even the units assumed. The inventory records the kernel-reported `type`, raw temperature, and a **candidate** millidegree-Celsius conversion without silently upgrading it to a calibrated measurement.

Run on the actual device:
```sh
python experiments/exp001_sensor_inventory.py --out sensor_inventory.json
python -m unittest discover -s experiments -p 'test_exp001_sensor_inventory.py' -v
```
The inventory creates a new output file exclusively; keep original evidence unchanged. No automatic publishing, network transfer, or sensor control. Synthetic tests do not validate device measurements.

## Preregistered follow-up
1. Identify which thermal zone corresponds to the physical quantity of interest from kernel/vendor documentation, not numeric ordering.
2. Establish units, sensor response time, quantization, calibration or a reference thermometer where physically feasible, uncertainty budget, ambient conditions, and timestamp source.
3. Run repeated baseline/load/cooldown series with a fixed sampling interval and missing-data counts. Record device, kernel, zone type, workload, power state, ambient, and clock synchronization.
4. Compare independent observations and controls; report failure cases, not only successful runs.
5. Test a thermal dynamic model such as `C dT/dt = P_in - hA(T - T_ambient)` only with separately justified power and thermal parameters. Do not claim measured entropy production or Gibbs free energy from a temperature-only proxy.
6. Explicitly separate thermodynamic inference from action authorization. Never trigger hardware actions from this experiment.

## Claim status
Sensor identity: **unverified**. Scale: **candidate**. Calibration: **unverified**. Physical validation: **not performed**. The existing Gibbs-inspired proxy is not a measurement of Gibbs free energy. This branch does not alter the legacy monitor or historical data.
