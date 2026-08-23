"""Command Center view model for ranked TIMEŒ approval decisions."""

from datetime import date

from .approval_queue import ApprovalItem
from .decision_queue import rank_approvals


def build_decision_panel(items: list[ApprovalItem], as_of: date) -> list[dict]:
    """Return UI-safe ranked recommendations without executing any action."""
    return [item.as_dict() for item in rank_approvals(items, as_of)]
