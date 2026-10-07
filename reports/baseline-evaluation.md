# Baseline Evaluation Report

**System:** Eclipse Realms deterministic player-support classifier  
**Dataset:** `datasets/tickets.json`  
**Tickets evaluated:** 30  
**CI run:** #1  
**Overall quality gate:** PASS

## Results

| Metric | Result | Gate | Status |
|---|---:|---:|---|
| Language Accuracy | 96.7% | >= 95% | PASS |
| Category Accuracy | 100.0% | >= 90% | PASS |
| Priority Accuracy | 100.0% | >= 85% | PASS |
| Escalation Recall | 100.0% | >= 95% | PASS |

Automated tests: **4 passed**.

## Observed mismatches

### TICKET-017 — Language detection

Expected: `pt-BR`  
Actual: `en`

The Portuguese gameplay question was classified correctly for category and priority, but the baseline language detector did not recognize enough Portuguese markers. This exposes the limitation of keyword-based language detection.

### TICKET-024 — Escalation decision

Expected: `false`  
Actual: `true`

A player asking whether a previously reported user was banned should not trigger a new escalation. The system must avoid disclosing moderation outcomes, but the baseline currently treats the presence of a report-related keyword as an escalation signal.

## QA interpretation

Passing the quality gates does **not** mean the baseline is perfect. Two behavioral mismatches remain and are intentionally documented instead of hidden.

The first baseline establishes a reproducible reference point for later comparison with an LLM-powered implementation. Future iterations should improve generalization without overfitting individual golden cases.

## Next steps

- Add dedicated adversarial/safety evaluation.
- Improve language detection beyond brittle keyword matching.
- Separate moderation privacy behavior from escalation logic.
- Introduce an LLM-backed classifier and compare it against this deterministic baseline.
