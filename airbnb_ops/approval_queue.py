"""Human approval state for Airbnb operational tasks."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from .task_engine import OpsTask


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


@dataclass(frozen=True)
class ApprovalItem:
    task: OpsTask
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_at: str | None = None

    @property
    def approval_id(self) -> str:
        return f"{self.task.task_type}:{self.task.booking_id or 'general'}:{self.task.due_date.isoformat()}"


def approve(item: ApprovalItem) -> ApprovalItem:
    """Approve a task without executing any external action."""
    return ApprovalItem(item.task, ApprovalStatus.APPROVED, datetime.now(timezone.utc).isoformat())


def reject(item: ApprovalItem) -> ApprovalItem:
    """Reject a task without executing any external action."""
    return ApprovalItem(item.task, ApprovalStatus.REJECTED, datetime.now(timezone.utc).isoformat())


def complete(item: ApprovalItem) -> ApprovalItem:
    """Mark an approved task completed after human/provider execution."""
    if item.status != ApprovalStatus.APPROVED:
        raise ValueError("only approved tasks can be completed")
    return ApprovalItem(item.task, ApprovalStatus.COMPLETED, datetime.now(timezone.utc).isoformat())
