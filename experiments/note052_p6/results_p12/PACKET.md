# P12 second-reviewer packet (note052 Amendment 6)

30 findings drawn with seed 1212 from the 137 that P10 hand-checked. The packet contains no verdicts.

## Rules (P10's, unchanged)

```
A finding is TP only if both hold:
1. the file is meant to be run as a check or test by its authors (its name, docstring, or how the project invokes
   it says so); and
2. reading the file and anything it imports from the same repository, no input makes the check report failure
   through a nonzero exit, a raised exception, or a pytest/unittest failure.

It is FP if the file is not a check (a library module, demo, benchmark, build or docs script), or if a fail path
exists that the linter does not see (for example unittest.main(), a fixture or helper that raises, or
sys.exit(main())). Each verdict carries a one-line reason.

How rule 2 was applied in P10 (results_p10/HANDCHECK_CLARIFICATION.md, committed before P10's strata were read):
- An exception counts as a fail path only if it is how the check reports that the thing it checks is wrong. An
  unrelated error (missing dependency, empty input, division by zero on no data) does not count.
- So an import-only test file counts as able to fail (the import is the check), while a script that compares
  results and only prints "failed" counts as unable to fail.
- UNPARSEABLE findings (files that do not parse under Python 3) are FP: no vacuity can be established from a file
  the tool cannot read.
```

## Findings

| id | linter category | file at the pinned commit |
|---|---|---|
| R01 | UNPARSEABLE | [csyhhu/L-OBS/PyTorch/ImageNet/generate-Hesian-Inv-VGG16BN.py](https://github.com/csyhhu/L-OBS/blob/346e67977955f34b10b0461ab4d60ef8d35dc145/PyTorch/ImageNet/generate-Hesian-Inv-VGG16BN.py) |
| R02 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/BA_40spin/train_and_test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_40spin/train_and_test_eco.py) |
| R03 | UNCOLLECTABLE_TEST | [tomdbar/eco-dqn/experiments/BA_100spin/test/test_s2v.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_100spin/test/test_s2v.py) |
| R04 | UNCOLLECTABLE_TEST | [tomdbar/eco-dqn/experiments/ER_200spin/test/test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_200spin/test/test_eco.py) |
| R05 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/ER_200spin/test/test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_200spin/test/test_eco.py) |
| R06 | UNCOLLECTABLE_TEST | [nasa/giant/unittests/utilities/test_utilities.py](https://github.com/nasa/giant/blob/2b1ceeaf5847f2829f440b21ad3ca1977589eda4/unittests/utilities/test_utilities.py) |
| R07 | UNCOLLECTABLE_TEST | [DurhamDecLab/ARBInterp/tests/test_ARBInterp.py](https://github.com/DurhamDecLab/ARBInterp/blob/56d88b1fdb28f2356c738dfe9bd34d65709ed0f8/tests/test_ARBInterp.py) |
| R08 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/BA_60spin/test/test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_60spin/test/test_eco.py) |
| R09 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/ER_60spin/test/test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_60spin/test/test_eco.py) |
| R10 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/BA_200spin/test/test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_200spin/test/test_eco.py) |
| R11 | UNCOLLECTABLE_TEST | [shailshouryya/yt-videos-list/python/tests/test_dependencies_json.py](https://github.com/shailshouryya/yt-videos-list/blob/0b81d1ce9bb2c04dd7a11e837649a73e73dbf7a2/python/tests/test_dependencies_json.py) |
| R12 | NO_FAIL_PATH | [shailshouryya/yt-videos-list/docs/preparing/checkAttrs.py](https://github.com/shailshouryya/yt-videos-list/blob/0b81d1ce9bb2c04dd7a11e837649a73e73dbf7a2/docs/preparing/checkAttrs.py) |
| R13 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/ER_200spin/train_and_test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_200spin/train_and_test_eco.py) |
| R14 | NO_FAIL_PATH | [hezhangsprinter/DID-MDN/test.py](https://github.com/hezhangsprinter/DID-MDN/blob/44bb9e84ab48cba764316bebeee0b47f5fad28a1/test.py) |
| R15 | UNCOLLECTABLE_TEST | [tomdbar/eco-dqn/experiments/ER_100spin/test/test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_100spin/test/test_eco.py) |
| R16 | NO_FAIL_PATH | [shailshouryya/yt-videos-list/python/tests/test_dependencies_json.py](https://github.com/shailshouryya/yt-videos-list/blob/0b81d1ce9bb2c04dd7a11e837649a73e73dbf7a2/python/tests/test_dependencies_json.py) |
| R17 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/ER_200spin/train_and_test_s2v.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_200spin/train_and_test_s2v.py) |
| R18 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/BA_20spin/train_and_test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_20spin/train_and_test_eco.py) |
| R19 | UNCOLLECTABLE_TEST | [shailshouryya/yt-videos-list/python/tests/test_safaridriver.py](https://github.com/shailshouryya/yt-videos-list/blob/0b81d1ce9bb2c04dd7a11e837649a73e73dbf7a2/python/tests/test_safaridriver.py) |
| R20 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/BA_200spin/test/test_s2v.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_200spin/test/test_s2v.py) |
| R21 | UNCOLLECTABLE_TEST | [tomdbar/eco-dqn/experiments/BA_40spin/test/test_s2v.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_40spin/test/test_s2v.py) |
| R22 | UNPARSEABLE | [xyj77/MCF-3D-CNN/utils/avg_roc.py](https://github.com/xyj77/MCF-3D-CNN/blob/32576a5b2132d1e41146f57cee4d3228fd1ace92/utils/avg_roc.py) |
| R23 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/BA_40spin/train_and_test_s2v.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_40spin/train_and_test_s2v.py) |
| R24 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/ER_20spin/train_and_test_s2v.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_20spin/train_and_test_s2v.py) |
| R25 | NO_FAIL_PATH | [tomdbar/eco-dqn/experiments/ER_20spin/train_and_test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/ER_20spin/train_and_test_eco.py) |
| R26 | NO_FAIL_PATH | [csyhhu/L-OBS/PyTorch/ImageNet/validate-AlexNet.py](https://github.com/csyhhu/L-OBS/blob/346e67977955f34b10b0461ab4d60ef8d35dc145/PyTorch/ImageNet/validate-AlexNet.py) |
| R27 | UNCOLLECTABLE_TEST | [NVIDIA/Dataset_Utilities/nvdu/tools/test_nvdu_visualizer.py](https://github.com/NVIDIA/Dataset_Utilities/blob/532b8c76e3d7946748a10af3398438b35383f157/nvdu/tools/test_nvdu_visualizer.py) |
| R28 | NO_FAIL_PATH | [shailshouryya/yt-videos-list/python/tests/test_safaridriver.py](https://github.com/shailshouryya/yt-videos-list/blob/0b81d1ce9bb2c04dd7a11e837649a73e73dbf7a2/python/tests/test_safaridriver.py) |
| R29 | UNCOLLECTABLE_TEST | [tomdbar/eco-dqn/experiments/BA_60spin/test/test_eco.py](https://github.com/tomdbar/eco-dqn/blob/134df732cbdc32ad840ee2c05079fb2dbb6dd6d0/experiments/BA_60spin/test/test_eco.py) |
| R30 | UNPARSEABLE | [xyj77/MCF-3D-CNN/utils/utils.py](https://github.com/xyj77/MCF-3D-CNN/blob/32576a5b2132d1e41146f57cee4d3228fd1ace92/utils/utils.py) |
