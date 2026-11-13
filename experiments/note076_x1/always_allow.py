#!/usr/bin/env python3
"""Control C2 (REGISTRATION.md): answers ALLOW with no reasons for every case."""
import json
import sys

for line in sys.stdin:
    if line.strip():
        print(json.dumps({"id": json.loads(line)["id"], "decision": "ALLOW", "reasons": []}))
