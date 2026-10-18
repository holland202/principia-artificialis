# Entry challenges — menu

**Status: ACTIVE — optional, public open challenges C0–C4.** Sealed/blind challenges PA-C6 are **NOT OPEN**. Read the [recruitment protocol](../../RECRUITMENT_PROTOCOL.md) for the separately consented evaluation record and evidence requirements.

**Challenges are optional.** Anyone can instead [begin their own research immediately](../../JOIN_RESEARCH.md), open an issue or submit a forked PR without a challenge or assignment.

For a **new** entry-challenge test, open an [entry-challenge issue](../../.github/ISSUE_TEMPLATE/entry_challenge.yml) with a claim and falsifier before running **that challenge check**. Earlier independent work is welcome if labeled retrospective rather than preregistered. A reviewed challenge may later support a separate role discussion, but the [Contributor Trust Path](../../CONTRIBUTOR_TRUST_PATH.md) is still a proposal and no roles or access are conferred by a challenge.

**The deal:** submit one checkable piece of work. A designated reviewer may reproduce it as time allows and must label the actual evidence and gaps. The issue itself is public on submission; any separate curated evaluation record requires written consent and your chosen credit wording. Participation is voluntary and unpaid, with no guaranteed review, role, or access. Negative and null results count fully.

Future challenge rounds may carry **sealed answers** under the commitment procedure in [SEALED.md](SEALED.md), including null-answer cases. **No items have been sealed or made available yet**; the open challenge rows below are not secretly graded.

None of these items asserts that a defect currently exists. Check the source at the commit you pin.

## Principia Artificialis (default home)

| ID | Challenge | Effort | Sealed? |
|---|---|---|---|
| PA-C1 | **Numbers vs code.** Take one research note that has a `scripts/noteNNN_reference.py`. Run the script, then show whether every number in the note's prose matches its output (rule M6). Check that the script's docstring names that note: numbers collide in this repo. | 1–3 h | open |
| PA-C2 | **Can the instrument say no?** Pick one checker or gate in `scripts/`. Build the smallest admissible input that should make it fail, and show whether it does (rule M3). | 1–4 h | open |
| PA-C3 | **Label honesty.** Pick one note whose status label claims more than Speculative. Show whether the evidence in the repo supports that label (rule M7). | 1–2 h | open |
| PA-C4 | **Walk through a door.** Pick one note's open, unrun prediction. Register it in your issue, then run it in your own environment and report it whichever way it comes out (M2, M15). This is not an official PA study unless authorized through WORKFLOW W2. | 3–10 h | open |
| PA-C5 | **Break the governance suite.** Run `python sovereign_core/test_sovereign.py`. Find a change to the governance engine that the suite does not catch (a surviving mutant), or show that each guard is load-bearing. | 2–6 h | open |
| PA-C6 | **Sealed items — NOT OPEN.** Future optional challenge, after independent construction and a separate owner gate; see [SEALED.md](SEALED.md). | future | inactive |

## Other public repositories (welcome; the record lives in that repo, with a pointer here)

**Public visibility verified on 2026-10-18:** each listed repository returned `public` and not archived. Each repository's own challenge rules and rights still govern; this list does not authorize running security tests outside those rules.

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
