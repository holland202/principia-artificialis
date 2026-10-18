# Entry challenges — menu

**Status: DRAFT (part of [RECRUITMENT_PROTOCOL.md](../../RECRUITMENT_PROTOCOL.md)); not in effect until the owner merges.**

Pick one challenge, then open an [entry-challenge issue](../../.github/ISSUE_TEMPLATE/entry_challenge.yml) and declare
your claim and falsifier **before** you run anything. One accepted, reproduced challenge is the evidence for
[Contributor Trust Path](../../CONTRIBUTOR_TRUST_PATH.md) Stage 1.

**The deal:** you do one checkable piece of work. We reproduce it, and if you consent, we credit you publicly in your own
words. It is unpaid and there is no automatic access. Negative and null results count fully.

Some items have a **sealed answer**: its hash was committed in [SEALED.md](SEALED.md) before posting. For some sealed
items the correct answer is "no defect" or "cannot be determined". We do not say which.

None of these items asserts that a defect currently exists. Check the source at the commit you pin.

## Principia Artificialis (default home)

| ID | Challenge | Effort | Sealed? |
|---|---|---|---|
| PA-C1 | **Numbers vs code.** Take one research note that has a `scripts/noteNNN_reference.py`. Run the script, then show whether every number in the note's prose matches its output (rule M6). Check that the script's docstring names that note: numbers collide in this repo. | 1–3 h | open |
| PA-C2 | **Can the instrument say no?** Pick one checker or gate in `scripts/`. Build the smallest admissible input that should make it fail, and show whether it does (rule M3). | 1–4 h | open |
| PA-C3 | **Label honesty.** Pick one note whose status label claims more than Speculative. Show whether the evidence in the repo supports that label (rule M7). | 1–2 h | open |
| PA-C4 | **Walk through a door.** Pick one note's open, unrun prediction. Register it in your issue, then run it in your own environment and report it whichever way it comes out (M2, M15). This is not an official PA study unless authorized through WORKFLOW W2. | 3–10 h | open |
| PA-C5 | **Break the governance suite.** Run `python sovereign_core/test_sovereign.py`. Find a change to the governance engine that the suite does not catch (a surviving mutant), or show that each guard is load-bearing. | 2–6 h | open |
| PA-C6 | **Sealed items.** Posted here once the owner seals them; see [SEALED.md](SEALED.md). | varies | sealed |

## Other public repositories (welcome; the record lives in that repo, with a pointer here)

The owner must confirm this list before adoption.

| Repo | Challenge | Notes |
|---|---|---|
| [vacuity_lint.py](https://github.com/holland202/vacuity_lint.py) | Write test cases the linter gets wrong: a vacuous check it misses, or a sound check it flags. | The first independent evaluation (IE1) came from here; see the precedent in the protocol. |
| [sovereign-veritas](https://github.com/holland202/sovereign-veritas) | Its own [CHALLENGE.md](https://github.com/holland202/sovereign-veritas/blob/main/CHALLENGE.md) applies. | **Security testing is limited to that file's rules.** Anything beyond it needs a written agreement first. |
| [sentinel-batadal-validation](https://github.com/holland202/sentinel-batadal-validation) | Reproduce the published negative result from a clean clone, or find the step where it does not reproduce. | |
| [sentinel-hai-validation](https://github.com/holland202/sentinel-hai-validation) | Reproduce one registered gate result, or find a confound the registration missed. | |
| [veritas-eval-harness](https://github.com/holland202/veritas-eval-harness) | Run one of its open registered predictions and report it either way. | |
| [token-veritas](https://github.com/holland202/token-veritas) | Re-measure one claimed token-cost reduction on your own inputs. | |
| [veritas-holo](https://github.com/holland202/veritas-holo) | Attempt to falsify one stated claim with the repo's own code. | |

## Your own question

**OPEN:** state your own falsifiable question against any listed repository. If you don't name a repository, it
defaults to Principia. It is judged by reproduction alone.
