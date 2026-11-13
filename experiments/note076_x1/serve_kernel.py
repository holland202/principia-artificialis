#!/usr/bin/env python3
"""serve_kernel.py SV_ROOT - serve the kernel Gate of the Sovereign Veritas checkout at SV_ROOT.

Reads {"id", "input"} lines on stdin and writes {"id", "decision", "reasons"} lines, using that checkout's own
tools/gate_contract.py (kernel_gate and serve). An exception is not caught: the process exits non-zero, which the
scorer records as CRASH. NOTE076-X1, REGISTRATION.md.
"""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: serve_kernel.py SV_ROOT")
    path = os.path.join(os.path.abspath(sys.argv[1]), "tools", "gate_contract.py")
    spec = importlib.util.spec_from_file_location("gate_contract", path)
    gct = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gct)
    gct.serve(gct.kernel_gate())


if __name__ == "__main__":
    main()
