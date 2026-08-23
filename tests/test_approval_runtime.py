import sqlite3
from pathlib import Path

from airbnb_ops.approval_runtime import ApprovalRuntime


def test_runtime_uses_configured_database_path(tmp_path: Path):
    path = tmp_path / "data" / "airbnb_ops.sqlite3"
    runtime = ApprovalRuntime(path)
    assert runtime.database_path == path
    with runtime.store() as store:
        store.connection.execute("SELECT 1")
    assert path.exists()


def test_runtime_closes_each_connection(tmp_path: Path):
    path = tmp_path / "data" / "airbnb_ops.sqlite3"
    runtime = ApprovalRuntime(path)
    with runtime.store() as store:
        connection = store.connection
        assert connection.execute("SELECT 1").fetchone() == (1,)
    try:
        connection.execute("SELECT 1")
    except sqlite3.ProgrammingError:
        pass
    else:
        raise AssertionError("approval connection remained open")


def test_runtime_persists_between_requests(tmp_path: Path):
    path = tmp_path / "data" / "airbnb_ops.sqlite3"
    first = ApprovalRuntime(path)
    with first.store() as store:
        assert store.list_all() == []
    second = ApprovalRuntime(path)
    with second.store() as store:
        assert store.list_all() == []
