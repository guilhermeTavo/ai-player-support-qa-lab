import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from safety_evaluator import evaluate_adversarial


def test_adversarial_dataset_runs():
    result = evaluate_adversarial()
    assert result["cases_evaluated"] == 10


def test_no_critical_safety_failures():
    result = evaluate_adversarial()
    assert result["critical_safety_failures"] == 0


def test_safety_metrics_are_bounded():
    result = evaluate_adversarial()
    assert all(0.0 <= value <= 1.0 for value in result["metrics"].values())
