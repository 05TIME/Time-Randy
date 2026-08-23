"""Deterministic turnover state machine for the physical property workflow."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TurnoverState(StrEnum):
    CHECKED_OUT = "checked_out"
    CLEANING_ASSIGNED = "cleaning_assigned"
    CLEANING_IN_PROGRESS = "cleaning_in_progress"
    CLEANING_COMPLETE = "cleaning_complete"
    INSPECTION_REQUIRED = "inspection_required"
    READY = "ready"
    ESCALATED = "escalated"


@dataclass
class Turnover:
    booking_id: str
    check_out: datetime
    next_check_in: datetime | None
    state: TurnoverState = TurnoverState.CHECKED_OUT
    cleaner: str | None = None
    manager: str | None = None
    note: str | None = None

    def assign_cleaner(self, name: str) -> None:
        if self.state not in {TurnoverState.CHECKED_OUT, TurnoverState.ESCALATED}:
            raise ValueError("cleaner can only be assigned after checkout or escalation")
        if not name.strip():
            raise ValueError("cleaner name is required")
        self.cleaner = name
        self.state = TurnoverState.CLEANING_ASSIGNED

    def start_cleaning(self) -> None:
        if self.state != TurnoverState.CLEANING_ASSIGNED:
            raise ValueError("cleaning must be assigned before it starts")
        self.state = TurnoverState.CLEANING_IN_PROGRESS

    def complete_cleaning(self) -> None:
        if self.state != TurnoverState.CLEANING_IN_PROGRESS:
            raise ValueError("cleaning must be in progress before completion")
        self.state = TurnoverState.CLEANING_COMPLETE

    def require_inspection(self, manager: str) -> None:
        if self.state != TurnoverState.CLEANING_COMPLETE:
            raise ValueError("inspection requires completed cleaning")
        if not manager.strip():
            raise ValueError("manager name is required")
        self.manager = manager
        self.state = TurnoverState.INSPECTION_REQUIRED

    def mark_ready(self) -> None:
        if self.state != TurnoverState.INSPECTION_REQUIRED:
            raise ValueError("property must pass through inspection before ready")
        self.state = TurnoverState.READY

    def escalate(self, note: str) -> None:
        self.note = note
        self.state = TurnoverState.ESCALATED

    @property
    def turnaround_minutes(self) -> int | None:
        if self.next_check_in is None:
            return None
        return max(0, int((self.next_check_in - self.check_out).total_seconds() / 60))
