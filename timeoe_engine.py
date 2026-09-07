"""TIMEŒ Command Engine v1: event-driven temporal execution graph.

This module is provider-agnostic. It provides the real execution/state model
for the dashboard; external agents/providers can be attached later.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any, Callable
from uuid import uuid4


class State(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    RETRY = "RETRY"
    COMPLETED = "COMPLETED"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Event:
    type: str
    task_id: str
    agent_id: str | None
    state: str
    timestamp: str = field(default_factory=now)
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    name: str
    agent: str
    dependencies: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    state: State = State.QUEUED
    result: Any = None
    attempts: int = 0


class ExecutionGraph:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.events: list[Event] = []
        self._lock = Lock()

    def add(self, task: Task) -> Task:
        with self._lock:
            self.tasks[task.id] = task
            self.emit("TASK_CREATED", task, None, {"name": task.name})
        return task

    def emit(self, event_type: str, task: Task, agent: str | None,
             payload: dict[str, Any] | None = None) -> None:
        self.events.append(Event(event_type, task.id, agent, task.state.value,
                                 payload=payload or {}))

    def ready(self, task: Task) -> bool:
        return all(self.tasks[d].state == State.COMPLETED for d in task.dependencies)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "tasks": [{**asdict(t), "state": t.state.value} for t in self.tasks.values()],
                "events": [asdict(e) for e in self.events[-100:]],
            }


class TimeoeEngine:
    """Small deterministic orchestration kernel with injectable workers."""
    def __init__(self) -> None:
        self.graph = ExecutionGraph()
        self.workers: dict[str, Callable[[Task], Any]] = {}

    def register_worker(self, agent: str, worker: Callable[[Task], Any]) -> None:
        self.workers[agent] = worker

    def command(self, objective: str, plan: list[dict[str, Any]]) -> dict[str, Any]:
        root = Task("COMMAND: " + objective, "command")
        self.graph.add(root)
        previous: list[str] = []
        for item in plan:
            task = Task(item["name"], item.get("agent", "general"), list(previous))
            self.graph.add(task)
            previous.append(task.id)
        self.graph.emit("COMMAND_RECEIVED", root, "command", {"objective": objective})
        return self.graph.snapshot()

    def run_ready(self) -> dict[str, Any]:
        # Execute all currently ready tasks; repeat so dependency chains advance.
        progressed = True
        while progressed:
            progressed = False
            for task in list(self.graph.tasks.values()):
                if task.state != State.QUEUED or not self.graph.ready(task):
                    continue
                progressed = True
                task.state = State.RUNNING
                task.attempts += 1
                self.graph.emit("TASK_RUNNING", task, task.agent)
                try:
                    worker = self.workers.get(task.agent, lambda t: {"status": "completed"})
                    task.result = worker(task)
                    task.state = State.VERIFIED
                    self.graph.emit("RESULT_RECEIVED", task, task.agent, {"result": task.result})
                    self.graph.emit("VERIFIED", task, task.agent)
                    task.state = State.COMPLETED
                    self.graph.emit("TASK_COMPLETED", task, task.agent)
                except Exception as exc:  # noqa: BLE001
                    task.state = State.RETRY if task.attempts < 3 else State.FAILED
                    self.graph.emit("TASK_FAILED", task, task.agent, {"error": str(exc)})
                    if task.state == State.RETRY:
                        task.state = State.QUEUED
        return self.graph.snapshot()
