"""Deterministic baseline classifier for the Eclipse Realms QA lab.

This is intentionally rule-based. It gives the project a reproducible baseline
before an LLM-backed implementation is introduced.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Classification:
    language: str
    category: str
    priority: str
    escalation_required: bool
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def detect_language(message: str) -> str:
    text = _normalize(message)
    pt_markers = (
        " meu ", " minha ", " nao ", " jogador", " conta", " comprei", " fui ",
        " quero ", " preciso ", " jogo", " missao", " como ", " depois ",
        " gostaria ", " ajuda ", " cartao", " cobr", " tela ", " idioma",
    )
    padded = f" {text} "
    return "pt-BR" if any(marker in padded for marker in pt_markers) else "en"


def classify_category(message: str) -> str:
    text = _normalize(message)

    rules = {
        "billing": (
            "bought", "purchase", "purchased", "payment", "charged", "refund",
            "card", "crystals", "comprei", "pagamento", "cobrado", "reembolso",
            "cartao", "passe de batalha",
        ),
        "account": (
            "log in", "login", "password", "account email", "authenticator",
            "recover", "recovery", "steam account", "conta", "senha", "e-mail",
            "email cadastrado", "autenticador",
        ),
        "abuse": (
            "insult", "harass", "cheat", "hack", "threat", "hurt me", "exploit",
            "reported", "denunc", "speed hack", "machucar", "banido",
        ),
        "technical": (
            "crash", "launcher", "error 504", "fps", "black screen",
            "tela preta", "disconnected", "update", "patch",
        ),
        "gameplay": (
            "quest", "npc", "critical damage", "critical chance", "inventory",
            "storage", "minimap", "dungeon", "missao", "dano critico",
            "chance critica", "item desapareceu",
        ),
    }

    scores = {
        category: sum(1 for keyword in keywords if keyword in text)
        for category, keywords in rules.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"


def assess_priority(message: str, category: str) -> str:
    text = _normalize(message)

    if (
        ("everyone" in text and ("disconnected" in text or "log" in text))
        or "nobody can log" in text
        or "widespread" in text
    ):
        return "P0"

    p1_patterns = (
        "didn't request", "did not request", "nao solicitei",
        "someone changed my account email", "stolen", "roub",
        "three times", "tres vezes", "duplicate",
        "coming to hurt me", "machucar", "real-world",
        "duplicate premium", "severe exploit",
    )
    if any(pattern in text for pattern in p1_patterns):
        return "P1"

    p3_patterns = (
        "how do i", "como eu", "qual e a diferenca", "what level",
        "a little", "um pouco", "where can i", "onde encontro",
        "quais idiomas", "was banned", "foi banido",
    )
    if any(pattern in text for pattern in p3_patterns):
        return "P3"

    if category in {"billing", "account", "technical", "abuse"}:
        return "P2"

    if category == "gameplay":
        material_issue = (
            "stuck", "disappeared", "desapareceu", "progress", "loss", "perda"
        )
        return "P2" if any(x in text for x in material_issue) else "P3"

    if any(x in text for x in ("delete all personal data", "suspended", "appeal", "excluir meus dados")):
        return "P2"

    return "P3"


def requires_escalation(message: str, category: str, priority: str) -> bool:
    text = _normalize(message)

    if priority in {"P0", "P1"}:
        return True

    escalation_markers = (
        "missing", "haven't appeared", "nao apareceu", "continua bloqueado",
        "refund", "reembolso", "authenticator", "recover", "recovery",
        "linking my steam", "rare quest reward", "harass", "insult",
        "cheat", "hack", "denunc", "delete all personal data",
        "suspended", "appeal",
    )
    if any(marker in text for marker in escalation_markers):
        return True

    # A simple declined payment with no charge can receive safe troubleshooting first.
    if category == "billing" and ("declined" in text or "recus" in text) and "charged" not in text:
        return False

    return False


def classify_ticket(message: str) -> dict:
    category = classify_category(message)
    priority = assess_priority(message, category)
    escalation = requires_escalation(message, category, priority)

    confidence = 0.90
    if category == "other":
        confidence = 0.72

    return Classification(
        language=detect_language(message),
        category=category,
        priority=priority,
        escalation_required=escalation,
        confidence=confidence,
    ).to_dict()
