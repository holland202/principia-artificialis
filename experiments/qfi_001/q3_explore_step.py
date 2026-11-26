#!/usr/bin/env python3
"""QFI-001 Q3, EXPLORATORY (C-EXPLORE, not registered; written after the registered run was seen).

Question: why does F_Q at trained layers >= 1 change by up to 90% between h = 1e-4 and h = 1e-3 (registered item 6)?
Instrument: F_Q against the central-difference step h in {1e-3, 1e-4, 1e-5, 1e-6} at the four points named below
(the registered run's largest rel_h at layer 6, and pair 2 theta 0.4 at layers 4-6), twice:
  - as registered (transformers' eager GPT-NeoX attention, whose softmax is computed in float32 and cast back);
  - with that softmax kept in float64 (the dtype argument dropped, patched in memory only).
If float32 rounding inside the forward pass is the cause, the first arm's F_Q should not settle as h shrinks and the
second arm's should. Author: Claude (Anthropic, Opus 5.5). SELF-TESTED.

Usage:  python -I experiments/qfi_001/q3_explore_step.py [--softmax64]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q3_run as q  # noqa: E402
import qfi_ref  # noqa: E402

POINTS = [(2, 0.4, 6), (0, 0.0, 6), (2, 0.4, 5), (2, 0.4, 4)]
STEPS = (1e-3, 1e-4, 1e-5, 1e-6)


def main():
    sm64 = "--softmax64" in sys.argv
    if sm64:
        import torch
        import transformers.models.gpt_neox.modeling_gpt_neox as g
        orig = torch.nn.functional.softmax

        class _F:  # module-local stand-in for nn.functional with the float32 cast removed
            def __getattr__(self, k):
                return getattr(torch.nn.functional, k)

            @staticmethod
            def softmax(x, dim=None, dtype=None, **kw):
                return orig(x, dim=dim, **kw)

        class _NN:
            functional = _F()

            def __getattr__(self, k):
                return getattr(torch.nn, k)

        g.nn = _NN()
    models, tok, ok = q.load_models(os.path.expanduser("~/.cache/qfi001_q3"))
    if not ok:
        print("identities MISMATCH")
        return 1
    pairs = {i: (ia, ib) for i, ia, ib in q.chosen_pairs(tok)}
    lab = list(models)[0]
    f = q.Forward(models[lab])
    print(f"arm: {'softmax kept in float64 (patched)' if sm64 else 'as registered (eager softmax in float32)'}")
    for pi, th, L in POINTS:
        ia, ib = pairs[pi]
        A = f(ia, ib, th)[L]
        out = []
        for h in STEPS:
            dA = (f(ia, ib, th + h)[L] - f(ia, ib, th - h)[L]) / (2 * h)
            out.append(qfi_ref.qfi_split_ex(*q.rho_drho(A, dA))["F_Q"])
        print(f"{lab} pair {pi} theta {th} layer {L}: F_Q at h=1e-3,1e-4,1e-5,1e-6: "
              + " ".join(f"{x:.6e}" for x in out)
              + f" | rel(1e-4 vs 1e-5) {abs(out[1] - out[2]) / out[2]:.2e} rel(1e-5 vs 1e-6) "
              f"{abs(out[2] - out[3]) / out[3]:.2e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
