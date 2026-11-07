# PA-C7 — Red-team the instruments

**Status: OPEN (pilot), added 2026-11-06.** Part of the [entry challenge menu](../entry/README.md). Take it through an
[entry-challenge issue](../../.github/ISSUE_TEMPLATE/entry_challenge.yml) and register before you run anything.

The repository's verdicts come from a few small checkers. This challenge asks you to make one of them give the wrong
verdict:

- a **false pass**: it accepts an input that breaks the rule it enforces; or
- a **false fail**: it rejects an input that is honest.

PA-C2 asks whether an instrument *can* say no. PA-C7 asks whether someone trying to get past it can make it say the
wrong thing. A failed attack counts too: an instrument that holds against a registered attack has more evidence behind it.

No defect is asserted here. While building the [Liar's Note](liars_note/README.md) judge, Claude found two candidate
false passes in `check_numbers.py` and reported them to the owner privately; it did not try to break the other
instruments. There is no sealed answer.

**Want a quick game first?** [PA-C8, the Liar's Note](liars_note/README.md), is the same idea aimed at one checker,
with a judge that tells you in under a second whether you won.

## Targets

| Instrument | Rule it serves | What a win looks like |
|---|---|---|
| [`scripts/check_numbers.py`](../../scripts/check_numbers.py) | M6: numbers come from code | A note and reference-script pair where a measured number in the prose differs from the script's output, yet the report says FOUND. Or the reverse: a matching number reported NOT FOUND. |
| [`scripts/method_lint.py`](../../scripts/method_lint.py) | M17: one definition per rule | An edit to the method documents that breaks the consistency it checks, yet it reports 0 violations. |
| [`scripts/doc_evidence_check.py`](../../scripts/doc_evidence_check.py) | Documentary integrity | A broken in-repo link, or a scientific claim without review, that it does not flag. |
| [`scripts/make_index.py`](../../scripts/make_index.py) | M7: honest labels | A status string that the Tier column maps to a higher tier than its words support. |
| [`scripts/make_dashboard.py --check`](../../scripts/make_dashboard.py) | Generated views match their sources | A difference between `dashboard.html` and its sources that `--check` misses. |
| `sovereign_core/` | Governance suite | Use [PA-C5](../entry/README.md) instead. |

## Baseline: each instrument's own tests

Run by Claude (Anthropic, Opus 5.5) on 2026-11-06, at commit `100d1e0`, in a Linux x86_64 container with Python 3.13.18.
Not run on the S25 (see CONTROLS.md C-DEVICE).

```
python3 scripts/test_check_numbers.py         Ran 11 tests ... OK
python3 scripts/test_doc_evidence_check.py    Ran 13 tests ... OK
python3 scripts/test_make_dashboard.py        Ran 15 tests ... OK
python3 scripts/mutate_check_numbers.py scripts    mutants killed: 7/7
python3 scripts/method_lint.py                method_lint: 0 violation(s)
```

These show what the instruments' own tests cover. They do not show that the instruments can't be fooled; that is the
question this challenge asks.

## Rules of engagement

1. **Register first.** In the issue, name the instrument, the rule, the wrong verdict you predict, and your control.
   Pin the commit.
2. **Two arms, both run.** Run an attack input and an honest control that differs from it in one way. The instrument
   must give the right verdict on the control and the wrong one on the attack. Paste both commands and their full output.
3. **Work on a copy.** Make synthetic notes and scripts in your own clone or a temporary directory. Do not edit real
   notes, their numbers or their status labels to build an attack.
4. **Documented limits are not new defects.** For example, `check_numbers.py` skips integers and one- or two-digit
   decimals, and `doc_evidence_check.py` does not inspect external URLs. An attack that only uses a stated limit is
   not a win. Showing that a stated limit hides a real mismatch in an existing note is welcome; report it as PA-ENTRY-01-style evidence.
5. **A fix is optional and separate.** Send it as its own PR, with a test that fails before the fix and passes after
   it. The owner decides whether to merge it.
6. **Report misses.** If the instrument held, say so in the same issue, with the attempts you made.

**Out of scope:** GitHub Actions and CI secrets; anyone's account; the owner's device; other repositories (for example,
[sovereign-veritas](https://github.com/holland202/sovereign-veritas) has its own CHALLENGE.md); denial of service; and
social engineering. These instruments are public, read-only tools with no secrets. If you come across anything that
would expose credentials or private material, do not post it: open an issue that says only that you have a private
report, and wait for the owner to arrange a channel.

## What counts

A win is a false pass or false fail that a maintainer reproduces from your registered commands. Credit follows the
[menu's terms](../entry/README.md): public credit in your own words, if you consent; unpaid; no automatic access.

Provenance: drafted by Claude (Anthropic, Opus 5.5) → human validation: not performed → human direction: Chad Holland,
2026-11-06 → human responsibility: Chad Holland. Review level: direction only.
