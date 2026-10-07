"""Evaluate the deterministic baseline against the golden dataset."""

from __future__ import annotations

import json
from pathlib import Path

from classifier import classify_ticket


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "tickets.json"

GATES = {
    "language_accuracy": 0.95,
    "category_accuracy": 0.90,
    "priority_accuracy": 0.85,
    "escalation_recall": 0.95,
}


def load_tickets() -> list[dict]:
    with DATASET.open(encoding="utf-8") as file:
        return json.load(file)


def evaluate(tickets: list[dict] | None = None) -> dict:
    tickets = tickets or load_tickets()
    counters = {"language": 0, "category": 0, "priority": 0}
    expected_escalations = 0
    true_positive_escalations = 0
    failures = []

    for ticket in tickets:
        expected = ticket["expected"]
        actual = classify_ticket(ticket["message"])

        for field in ("language", "category", "priority"):
            if actual[field] == expected[field]:
                counters[field] += 1

        if expected["escalation_required"]:
            expected_escalations += 1
            if actual["escalation_required"]:
                true_positive_escalations += 1

        mismatches = {
            field: {"expected": expected[field], "actual": actual[field]}
            for field in ("language", "category", "priority", "escalation_required")
            if actual[field] != expected[field]
        }
        if mismatches:
            failures.append({"id": ticket["id"], "mismatches": mismatches})

    total = len(tickets)
    metrics = {
        "language_accuracy": counters["language"] / total,
        "category_accuracy": counters["category"] / total,
        "priority_accuracy": counters["priority"] / total,
        "escalation_recall": (
            true_positive_escalations / expected_escalations
            if expected_escalations else 1.0
        ),
    }

    gates = {name: metrics[name] >= threshold for name, threshold in GATES.items()}

    return {
        "tickets_evaluated": total,
        "metrics": metrics,
        "gates": gates,
        "passed": all(gates.values()),
        "failures": failures,
    }


def main() -> None:
    result = evaluate()

    print(f"Tickets evaluated: {result['tickets_evaluated']}")
    for name, value in result["metrics"].items():
        status = "PASS" if result["gates"][name] else "FAIL"
        print(f"{name}: {value:.1%} [{status}]")

    print(f"Overall: {'PASS' if result['passed'] else 'FAIL'}")

    if result["failures"]:
        print("\nMismatches:")
        for failure in result["failures"]:
            print(f"- {failure['id']}: {failure['mismatches']}")


if __name__ == "__main__":
    main()
