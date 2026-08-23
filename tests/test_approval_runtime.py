import sqlite3

from airbnb_ops.approval_runtime import ApprovalRuntime


def test_runtime_uses_configured_database_path(tmp_path):
    path = tmp_path / "airbnb_ops.sqlite3"
    runtime = ApprovalRuntime(path)
    assert runtime.database_path == path
    runtime.store.connection.execute("SELECT 1")
    runtime.close()
    assert path.exists()
