#!/usr/bin/env python3
"""Exp001: auditable temperature sensor inventory; never assumes sensor identity."""
import argparse
import json
import math
from pathlib import Path

DEFAULT_ROOT = Path("/sys/class/thermal")


def inspect(root=DEFAULT_ROOT):
    results = []
    for zone in sorted(Path(root).glob("thermal_zone[0-9]*")):
        if not zone.is_dir():
            continue
        item = {"zone": zone.name, "type": None, "raw": None,
                "temp_c": None, "status": "unavailable", "scale": "unestablished"}
        try:
            item["type"] = (zone / "type").read_text().strip()
            raw_text = (zone / "temp").read_text().strip()
            item["raw"] = raw_text
            raw = float(raw_text)
            # Explicit hypothesis, not silent heuristic.
            candidate = raw / 1000.0
            if not math.isfinite(raw):
                item["status"] = "nonfinite"
            elif raw == -273000:\n                item["status"] = "suspected_invalid_sentinel"\n            elif -40 <= candidate <= 150:
                item["temp_c"] = candidate
                item["status"] = "candidate_millicelsius"
                item["scale"] = "assumed_millicelsius_unverified"
            else:
                item["status"] = "outside_candidate_range"
        except (OSError, ValueError, UnicodeError, OverflowError) as exc:
            item["error_type"] = type(exc).__name__
        results.append(item)
    return {"schema": "pa.thermal-inventory/1",
            "source_root": str(root),
            "sensor_identity_verified": False,
            "calibration_verified": False,
            "zones": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--out", required=True, help="new output file only; no overwrite")
    args = ap.parse_args()
    result = inspect(Path(args.root))
    with open(args.out, "x", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(json.dumps({"written": args.out, "zones": len(result["zones"]),
                      "identity_verified": False, "calibration_verified": False}))


if __name__ == "__main__":
    main()
