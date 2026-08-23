"""Cross-business-unit prioritization for TIMEŒ Chief of Staff v2."""

from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Priority(IntEnum):
    ESCALATE = 100
    CRITICAL = 90
    HIGH = 70
    MEDIUM = 50
    LOW = 20


class DecisionType(StrEnum):
    ESCALATE = "escalate"
    ACTION = "action"
    MONITOR = "monitor"


@dataclass(frozen=True)
class BusinessUnitSignal:
    unit: str
    headline: str
    priority: int
    decision: DecisionType
    action: str | None = None
    escalation: str | None = None

    def normalized_priority(self) -> int:
        return max(0, min(100, int(self.priority)))


@dataclass(frozen=True)
class ChiefOfStaffDecision:
    priority: str
    headline: str
    unit: str
    action: str | None
    escalation: str | None


def rank_signals(signals: list[BusinessUnitSignal], limit: int = 5) -> list[ChiefOfStaffDecision]:
    """Rank signals by urgency while preserving unit-level accountability."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    ranked = sorted(
        signals,
        key=lambda signal: signal.normalized_priority(),
        reverse=True,
    )
    return [
        ChiefOfStaffDecision(
            priority=(
                "escalate" if signal.decision == DecisionType.ESCALATE
                else "action" if signal.decision == DecisionType.ACTION
                else "monitor"
            ),
            headline=signal.headline,
            unit=signal.unit,
            action=signal.action,
            escalation=signal.escalation,
        )
        for signal in ranked[:limit]
    ]
