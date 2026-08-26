"""Request-safe SQLite approval runtime."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .approval_store import ApprovalStore


def _default_database_path() -> str:
    """Use Vercel's writable temp filesystem unless explicitly configured."""
    if os.getenv("AIRBNB_DB_PATH"):
        return os.environ["AIRBNB_DB_PATH"]
    if os.getenv("VERCEL"):
        return "/tmp/airbnb_ops.sqlite3"
    return "data/airbnb_ops.sqlite3"


class ApprovalRuntime:
    """Open short-lived SQLite connections instead of sharing one globally."""

    def __init__(self, database_path: str | Path | None = None) -> None:
        self.database_path = Path(database_path or _default_database_path())
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def store(self) -> Iterator[ApprovalStore]:
        connection = sqlite3.connect(self.database_path)
        try:
            yield ApprovalStore(connection)
        finally:
            connection.close()
