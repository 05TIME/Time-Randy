"""In-memory approval workflow adapter for the Command Center."""

from .approval_queue import ApprovalItem, approve, reject, complete


def transition(item: ApprovalItem, action: str) -> ApprovalItem:
    """Apply a safe UI action; no external provider side effects."""
    if action == "approve":
        return approve(item)
    if action == "reject":
        return reject(item)
    if action == "complete":
        return complete(item)
    raise ValueError(f"unsupported approval action: {action}")
