"""Request-safe SQLite approval runtime."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .approval_store import ApprovalStore


class ApprovalRuntime:
    """Open short-lived SQLite connections instead of sharing one globally."""

    def __init__(self, database_path: str | Path = "data/airbnb_ops.sqlite3") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def store(self) -> Iterator[ApprovalStore]:
        connection = sqlite3.connect(self.database_path)
        try:
            yield ApprovalStore(connection)
        finally:
            connection.close()
