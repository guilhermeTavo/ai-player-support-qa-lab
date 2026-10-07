import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from classifier import classify_ticket
from evaluator import GATES, evaluate


def test_classifier_returns_expected_schema():
    result = classify_ticket("I cannot log in to my account.")
    assert set(result) == {
        "language",
        "category",
        "priority",
        "escalation_required",
        "confidence",
    }


def test_dataset_has_unique_ids():
    tickets = json.loads((ROOT / "datasets" / "tickets.json").read_text(encoding="utf-8"))
    ids = [ticket["id"] for ticket in tickets]
    assert len(ids) == len(set(ids))


def test_metrics_are_bounded():
    result = evaluate()
    assert all(0.0 <= value <= 1.0 for value in result["metrics"].values())


def test_quality_gates_match_thresholds():
    result = evaluate()
    for metric, threshold in GATES.items():
        assert result["gates"][metric] == (result["metrics"][metric] >= threshold)
