# P10 hand-check: one clarification made during the hand-check, before strata were unsealed (deviation 3)

Amendment 2's TP rule 2 says a finding is TP if "no input makes the check report failure through a nonzero exit, a
raised exception, or a pytest/unittest failure". Read literally, almost any script can raise *something* (a missing
module, an empty input). The rule was applied as follows:

- An exception counts as a fail path **only if it is how the check reports that the thing it checks is wrong.**
  An unrelated error (missing dependency, empty input, division by zero on no data) does not count.
- So an import-only test file counts as able to fail (the import *is* the check), while a script that compares
  results and only prints "failed" counts as unable to fail.
- UNPARSEABLE findings (files that do not parse under Python 3) are FP: no vacuity can be established from a file
  the tool cannot read.

Applied to all 137 findings before `strata.json` was read. Verdicts: 8 TP, 129 FP.
