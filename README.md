# AI Player Support QA Lab

A hands-on AI Quality Engineering project for evaluating an LLM-powered player support workflow for **Eclipse Realms**, a fictional MMORPG.

## Goal

The lab will evaluate whether an AI support system can reliably:

- detect ticket language;
- classify player issues;
- assign priority;
- decide when human escalation is required;
- follow safety and privacy policies;
- handle localization;
- generate useful support responses.

The project will use a golden dataset and automated evaluation rather than judging responses only by fluency.

## Planned quality gates

- Category accuracy >= 90%
- Priority accuracy >= 85%
- Escalation recall >= 95%
- Language accuracy >= 95%
- Critical safety failures = 0

## Stack

- Python
- pytest
- JSON datasets
- GitHub Actions (planned)

## Project structure

```text
datasets/   # tickets and golden labels
src/        # support pipeline and evaluators
tests/      # automated QA and safety tests
reports/    # generated evaluation reports
```

> Eclipse Realms and all tickets, policies, users, and scenarios in this repository are fictional and created solely for portfolio and testing purposes.
