from pathlib import Path

from airbnb_ops.approval_runtime import ApprovalRuntime


def test_runtime_uses_configured_database_path(tmp_path: Path):
    path = tmp_path / "data" / "airbnb_ops.sqlite3"
    runtime = ApprovalRuntime(path)
    assert runtime.database_path == path
    runtime.store.connection.execute("SELECT 1")
    runtime.close()
    assert path.exists()


def test_runtime_reopens_persistent_store(tmp_path: Path):
    path = tmp_path / "data" / "airbnb_ops.sqlite3"
    first = ApprovalRuntime(path)
    first.close()
    second = ApprovalRuntime(path)
    assert second.store.list_all() == []
    second.close()
