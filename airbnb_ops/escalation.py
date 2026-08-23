"""Central escalation policy for Airbnb operations."""

from dataclasses import dataclass
from enum import StrEnum


class EscalationLevel(StrEnum):
    INFO = "info"
    REVIEW = "review"
    ESCALATE = "escalate"
    URGENT = "urgent"


@dataclass(frozen=True)
class Escalation:
    level: EscalationLevel
    reason: str
    action: str


def assess(*, financial_discrepancy: bool = False, damage_dispute: bool = False, urgent_maintenance: bool = False, unusual_guest_request: bool = False) -> Escalation:
    if urgent_maintenance:
        return Escalation(EscalationLevel.URGENT, "Urgent maintenance issue", "Contact physical manager immediately and pause affected inventory if necessary.")
    if financial_discrepancy or damage_dispute:
        return Escalation(EscalationLevel.ESCALATE, "Financial or damage discrepancy", "Do not auto-resolve; send to owner/Chief of Staff for decision.")
    if unusual_guest_request:
        return Escalation(EscalationLevel.REVIEW, "Unusual guest request", "Review before committing to a non-standard promise or discount.")
    return Escalation(EscalationLevel.INFO, "No escalation condition", "Continue normal workflow.")
