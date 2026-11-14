"""Qualification tests for the CST-001 instrument (no model involved). Run: python3 -m pytest -q experiments/cst_001"""
import difflib
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import exposures  # noqa: E402
import scorer  # noqa: E402

QUAL = cases.build("qual", 1)


def outputs_from(decide):
    return {(p["pair"], v["version"]): decide(p, v) for p in QUAL for v in p["versions"]}


# ---------------- scorer
def test_correct_answers_score_every_pair():
    out = outputs_from(lambda p, v: f"Some reasoning.\nDECISION: {v['answer']}")
    _, tot = scorer.score(QUAL, out)
    assert tot["pair_correct"] == len(QUAL) and tot["malformed"] == 0


def test_swapped_labels_score_zero():
    flip = {"CONFIRMED": "INSUFFICIENT", "INSUFFICIENT": "CONFIRMED"}
    _, tot = scorer.score(QUAL, outputs_from(lambda p, v: f"DECISION: {flip[v['answer']]}"))
    assert tot["pair_correct"] == 0


@pytest.mark.parametrize("blanket", ["CONFIRMED", "INSUFFICIENT"])
def test_blanket_answers_score_zero_pairs(blanket):
    _, tot = scorer.score(QUAL, outputs_from(lambda p, v: f"DECISION: {blanket}"))
    assert tot["pair_correct"] == 0


def test_malformed_and_missing_count_as_wrong():
    out = outputs_from(lambda p, v: f"DECISION: {v['answer']}")
    first = QUAL[0]["pair"]
    out[(first, "SHARED")] = "I think it is insufficient."           # no decision line
    del out[(QUAL[1]["pair"], "INDEPENDENT")]                          # missing response
    rows, tot = scorer.score(QUAL, out)
    assert tot["pair_correct"] == len(QUAL) - 2 and tot["malformed"] == 2


@pytest.mark.parametrize("text,want", [
    ("DECISION: CONFIRMED", "CONFIRMED"),
    ("**DECISION: INSUFFICIENT**", "INSUFFICIENT"),
    ("decision : confirmed.", "CONFIRMED"),
    ("DECISION: CONFIRMED\nwait\nDECISION: INSUFFICIENT", "INSUFFICIENT"),   # last line wins
    ("The decision is CONFIRMED", "MALFORMED"),
    ("DECISION: CONFIRMED or DECISION: INSUFFICIENT", "MALFORMED"),         # echoing the instruction
    (None, "MALFORMED"),
])
def test_parse(text, want):
    assert scorer.parse(text) == want


# ---------------- cases
def test_versions_differ_only_in_observation_ids():
    for p in QUAL:
        s, i = (v["prompt"] for v in p["versions"])
        changed = [tok for tok in difflib.ndiff(s.split(), i.split()) if tok[:1] in "+-"]
        assert changed and all(any(ch.isdigit() for ch in tok) for tok in changed), p["pair"]


def test_observation_ids_are_clearly_different():
    import re as _re
    for p in cases.build("test", 5):
        ids = sorted(set(_re.findall(r"\b[A-Z]+-\d{3}\b", p["versions"][1]["prompt"])))
        assert len(ids) == 2 and cases._distinct(*ids), (p["pair"], ids)


def test_answers_and_cells():
    assert len(QUAL) == len(cases.DOMAINS) * 2 * 2
    for p in QUAL:
        assert [v["answer"] for v in p["versions"]] == ["INSUFFICIENT", "CONFIRMED"]


def test_splits_are_disjoint():
    seen = {v["prompt"] for p in cases.build("dev", 2) for v in p["versions"]}
    assert not seen & {v["prompt"] for p in cases.build("test", 2) for v in p["versions"]}
    assert not seen & {v["prompt"] for p in QUAL for v in p["versions"]}


# ---------------- exposures
EXPOSURE_TERMS = ["Mira", "Priya", "Tomas", "Lou", "Aiko", "Ravi", "Io", "Jupiter", "magnitude", "eyepiece", "star",
                  "club", "spreadsheet"]


def test_no_exposure_terms_in_test_cases():
    words = {w.strip(".,:;\"()") for p in cases.build("test", 3) for v in p["versions"] for w in v["prompt"].split()}
    assert not words & set(EXPOSURE_TERMS)


def test_no_test_domain_terms_in_exposures():
    text = " ".join(" ".join(t) for t in exposures.ARMS.values()) + exposures.EXPLICIT
    for thing, obs, reps, inter, _ in cases.DOMAINS.values():
        for phrase in (thing, obs, inter, *reps):
            assert phrase not in text, phrase
    words = set(re.findall(r"[A-Za-z]+", text))
    assert not any(name.split()[0] in words for name in cases.NAMES)


def test_exposure_lengths_matched_within_15_percent():
    n = {k: sum(len(t.split()) for t in v) for k, v in exposures.ARMS.items()}
    assert max(n.values()) <= 1.15 * min(n.values()), n


def test_only_arm_a_mentions_tracing_words():
    for arm, turns in exposures.ARMS.items():
        text = " ".join(turns).lower()
        traced = any(w in text for w in ("rest on", "same 9:40", "one observation", "count the looks"))
        assert traced == (arm == "A"), arm


def test_history_shapes():
    assert exposures.history("D") == [] and exposures.history("E") == []
    h = exposures.history("A")
    assert [t["role"] for t in h] == ["user", "assistant"] * 5
    assert {t["content"] for t in h if t["role"] == "assistant"} == \
        {t["content"] for t in exposures.history("C") if t["role"] == "assistant"}
