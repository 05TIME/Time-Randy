"""Application-scoped persistent approval store."""

import sqlite3
from pathlib import Path

from .approval_store import ApprovalStore


class ApprovalRuntime:
    def __init__(self, database_path: str | Path = "data/airbnb_ops.sqlite3") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.store = ApprovalStore(self.connection)

    def close(self) -> None:
        self.connection.close()
