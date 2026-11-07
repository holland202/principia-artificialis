# PA-C8 — The Liar's Note

**Get a wrong number past the number checker.** Status: OPEN (pilot), added 2026-11-06.

This repository has one rule it treats as law: every number in a research note must match what the note's code
printed (M6). [`scripts/check_numbers.py`](../../../scripts/check_numbers.py) enforces it. It has passed its own tests and
killed all seven of its planted mutants.

Your job: write a short note whose prose reports a number the output does not support, and get the checker to report
it **FOUND**. A judge script tells you in under a second whether you won. You don't need anyone's permission, a GPU or
any knowledge of the research. All you need is Python 3.

## Play

```
git clone https://github.com/holland202/principia-artificialis
cd principia-artificialis
python3 challenges/redteam/liars_note/judge.py --selftest            # check the judge itself first
python3 challenges/redteam/liars_note/judge.py challenges/redteam/liars_note/example
```

The example is an honest entry, so it prints `NO WIN: honest`. Copy its folder and start lying:

| File | Contents |
|---|---|
| `note.md` | the prose, as a research note would write it |
| `output.txt` | what the reference script printed |
| `claim.json` | `{"line": 1, "prose": "<number as written in note.md>", "true": "<the value it should report, as printed in output.txt>"}` |

The judge runs nothing from your folder; it reads the three files.

## How the judge decides

It uses exact decimal arithmetic, not the checker's code:

1. The `true` value must be printed in `output.txt`.
2. **Honest:** if `true`, rounded to the prose number's last decimal place, gives the prose number, that is not a
   lie. Half-up and half-even rounding are both accepted.
3. **Coincidence:** if some *other* printed number rounds to your prose number, that doesn't count. The checker
   looks for a number anywhere in the output, which is a stated limit.
4. **Caught or not checked:** if the checker reports your number NOT FOUND, or skips it (it ignores integers and
   one- or two-digit decimals by design), you didn't win.
5. **WIN:** the checker says FOUND. The judge prints the relative error, |prose − true| / |true|.

The judge's self-test shows it can return both answers: it rejects an honest entry, a caught lie and a coincidence,
and it reports a WIN when it is handed a sabotaged checker that calls everything FOUND.

## The board

A win goes on the board once a maintainer reproduces it from your entry. It is ranked by **mechanism**, the reason
the checker was fooled. Each new mechanism earns a row; the first person to report one is credited for it. A second
entry that uses the same mechanism ranks above the first only by a larger relative error.

| # | Mechanism | Finder | Relative error | Checker sha256 (first 16) | Reproduced |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

*No public entries yet.* While building the judge, Claude (Anthropic, Opus 5.5) found two candidate mechanisms. It
reported them to the owner privately; they are not described here, and they are not on the board. Claude also
checked every note with a reference script at commit `100d1e0`: none of the numbers it reports FOUND is a lie of
either kind. Whether those two are published, fixed or held back is the owner's decision. If you find one of them
independently, you are credited as an independent finder.

## Submit

1. Open an [entry-challenge issue](../../../.github/ISSUE_TEMPLATE/entry_challenge.yml) with challenge ID `PA-C8`. Pin
   the commit and **say which mechanism you will try before you run it**.
2. Post your three files and the judge's full output as a comment. Misses count: report what you tried, too.
3. A fix is welcome as a separate PR, with a test that fails before the fix. The board keeps every row; a fixed
   mechanism is marked fixed, with the commit.

The [PA-C7 rules of engagement](../README.md#rules-of-engagement) apply: work in your own clone, don't edit real
notes, and nothing outside this repository is in scope.

Provenance: challenge and judge by Claude (Anthropic, Opus 5.5) → human validation: not performed → human direction:
Chad Holland, 2026-11-06 → human responsibility: Chad Holland. Review level: direction only.
