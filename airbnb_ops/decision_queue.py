"""Bridge operational approval items into TIMEŒ decisions."""

from dataclasses import dataclass
from datetime import date

from .approval_queue import ApprovalItem
from .decision_engine import Decision, evaluate
from .temporal_engine import extract_temporal_features


@dataclass(frozen=True)
class ScoredApproval:
    approval_id: str
    decision: Decision

    def as_dict(self) -> dict:
        payload = self.decision.as_dict()
        payload["approval_id"] = self.approval_id
        return payload


def score_approval(item: ApprovalItem, as_of: date) -> ScoredApproval:
    temporal = extract_temporal_features(as_of, item.task.due_date)
    return ScoredApproval(
        item.approval_id,
        evaluate(item.task.task_type, temporal, item.task.priority),
    )


def rank_approvals(items: list[ApprovalItem], as_of: date) -> list[ScoredApproval]:
    scored = [score_approval(item, as_of) for item in items]
    return sorted(scored, key=lambda item: item.decision.risk_score, reverse=True)
