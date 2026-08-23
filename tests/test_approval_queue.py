from datetime import date

import pytest

from airbnb_ops.approval_queue import ApprovalItem, ApprovalStatus, approve, complete, reject
from airbnb_ops.task_engine import OpsTask


def task():
    return OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-1", "high")


def test_approval_lifecycle():
    item = ApprovalItem(task())
    approved = approve(item)
    assert approved.status == ApprovalStatus.APPROVED
    completed = complete(approved)
    assert completed.status == ApprovalStatus.COMPLETED


def test_rejection():
    rejected = reject(ApprovalItem(task()))
    assert rejected.status == ApprovalStatus.REJECTED


def test_only_approved_can_complete():
    with pytest.raises(ValueError):
        complete(ApprovalItem(task()))
