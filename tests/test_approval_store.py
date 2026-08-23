import sqlite3
from datetime import date

from airbnb_ops.approval_queue import ApprovalItem, ApprovalStatus, approve
from airbnb_ops.approval_store import ApprovalStore
from airbnb_ops.task_engine import OpsTask


def test_approval_store_survives_reopen():
    connection = sqlite3.connect(":memory:")
    store = ApprovalStore(connection)
    item = ApprovalItem(OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-1", "high"))

    store.save(item)
    store.save(approve(item))

    restored = store.get(item.approval_id)
    assert restored is not None
    assert restored.status == ApprovalStatus.APPROVED
    assert restored.task.booking_id == "BK-1"


def test_store_upserts_same_approval():
    connection = sqlite3.connect(":memory:")
    store = ApprovalStore(connection)
    item = ApprovalItem(OpsTask("check_in", "Prepare", date(2026, 8, 25), "BK-2", "high"))
    store.save(item)
    store.save(approve(item))
    assert len(store.list_all()) == 1
