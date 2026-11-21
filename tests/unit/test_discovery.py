import copy
import json
from pathlib import Path

import pytest

from backend_standard.discovery import canonical, verify_discovery
from backend_standard.gates import Rejected

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "standards/planning/discovery.template.json"


def filled(stages: int = 11) -> dict:
    record = json.loads(TEMPLATE.read_text())
    record.update(project="invoice-tracker", product_owner="gokhan")
    record["agent_identities"] = ["voltran", "daedalus"]
    for stage in record["stages"][:stages]:
        stage.update(approved_by="gokhan", approved_at="2026-11-21")
        for question in stage["questions"]:
            question.update(status="answered", answer="Recorded decision text.")
    return record


def test_complete_record_is_accepted() -> None:
    assert verify_discovery(filled()) == 11


def test_template_matches_the_canonical_questions_and_is_rejected() -> None:
    template = json.loads(TEMPLATE.read_text())
    for stage, wanted in zip(template["stages"], canonical(), strict=True):
        assert [q["id"] for q in stage["questions"]] == [
            q["id"] for q in wanted["questions"]
        ]
        assert [q["question"] for q in stage["questions"]] == [
            q["text"] for q in wanted["questions"]
        ]
    with pytest.raises(Rejected):
        verify_discovery(template)


def test_partial_progress_is_reported_and_gated() -> None:
    record = filled(stages=4)
    assert verify_discovery(record, through=4) == 4
    with pytest.raises(Rejected, match="through stage 4; stage 6 required"):
        verify_discovery(record, through=6)


def test_not_applicable_needs_a_reason() -> None:
    record = filled()
    question = record["stages"][2]["questions"][3]
    question.update(status="not_applicable", answer=None, reason="Single tenant.")
    assert verify_discovery(record) == 11
    question["reason"] = " "
    with pytest.raises(Rejected, match="reason"):
        verify_discovery(record)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda r: r["stages"][5]["questions"][0].update(status="open"), "still open"),
        (lambda r: r["stages"][5]["questions"][0].update(answer="TBD"), "placeholder"),
        (lambda r: r["stages"][5]["questions"][0].update(answer=""), "required"),
        (lambda r: r["stages"][5]["questions"].pop(), "missing, unknown"),
        (lambda r: r["stages"][5]["questions"][0].update(id="S06-Q99"), "unknown"),
        (lambda r: r["stages"].pop(3), "reordered stages"),
        (lambda r: r["stages"][2].update(approved_by=None), "before an earlier"),
        (lambda r: r["stages"][4].update(approved_by="voltran"), "product owner"),
        (lambda r: r["stages"][4].update(approved_at="yesterday"), "approval date"),
        (lambda r: r.update(product_owner="Voltran"), "cannot be an agent"),
        (lambda r: r.update(project=None), "project"),
        (lambda r: r.update(discovery_standard="9"), "version"),
    ],
)
def test_incomplete_or_unsafe_records_are_rejected(change, message) -> None:
    record = copy.deepcopy(filled())
    change(record)
    with pytest.raises(Rejected, match=message):
        verify_discovery(record)
