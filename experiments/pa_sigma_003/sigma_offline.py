#!/usr/bin/env python3
"""Run sigma-cli with MITRE data read from local files (PA-SIGMA-003, stand-in S1).

pySigma 2.x downloads MITRE ATT&CK data (from github.com) and MITRE D3FEND data (from d3fend.mitre.org) the
first time a tag validator runs. Neither host is reachable from the container this study runs in, so this
wrapper points pySigma at local files, in a fresh cache directory for each process, and then calls sigma-cli's
own entry point with the remaining arguments:
  - ATT&CK: enterprise-attack.json from mitre-attack/attack-stix-data at a pinned commit. That is the file CI
    downloads (the default URL is that repository's master branch).
  - D3FEND: an empty JSON-LD graph. The D3FEND validator flags only tags in the d3fend namespace, and no rule
    in the scanned folders carries one (feasibility.py counts them), so its result does not depend on the data.

Usage: python -I sigma_offline.py ATTACK_JSON D3FEND_JSON <sigma-cli arguments>
"""
import os
import shutil
import sys
import tempfile


def main():
    attack, d3fend, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    from sigma.data import mitre_attack, mitre_d3fend

    cache = tempfile.mkdtemp(prefix="pa-sigma-003-pysigma-")
    try:
        mitre_attack.set_cache_dir(os.path.join(cache, "attack"))
        mitre_d3fend.set_cache_dir(os.path.join(cache, "d3fend"))
        mitre_attack.set_url(attack)
        mitre_d3fend.set_url(d3fend)
        from sigma.cli.main import main as cli

        sys.argv = ["sigma"] + args
        try:
            cli()
        except SystemExit as e:
            if e.code is None:
                return 0
            return e.code if isinstance(e.code, int) else 1
        return 0
    finally:
        shutil.rmtree(cache, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
