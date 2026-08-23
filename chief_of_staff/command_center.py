"""Aggregate cross-business-unit signals into an owner-ready command brief."""

from dataclasses import dataclass

from .orchestrator import BusinessUnitSignal, ChiefOfStaffDecision, rank_signals


@dataclass(frozen=True)
class CommandCenter:
    decisions: tuple[ChiefOfStaffDecision, ...]

    @property
    def escalations(self) -> tuple[ChiefOfStaffDecision, ...]:
        return tuple(d for d in self.decisions if d.priority == "escalate")

    @property
    def actions(self) -> tuple[ChiefOfStaffDecision, ...]:
        return tuple(d for d in self.decisions if d.priority == "action")

    @property
    def monitors(self) -> tuple[ChiefOfStaffDecision, ...]:
        return tuple(d for d in self.decisions if d.priority == "monitor")

    def as_dict(self) -> dict:
        return {
            "escalations": [d.__dict__ for d in self.escalations],
            "actions": [d.__dict__ for d in self.actions],
            "monitors": [d.__dict__ for d in self.monitors],
            "total": len(self.decisions),
        }


def build_command_center(signals: list[BusinessUnitSignal], limit: int = 10) -> CommandCenter:
    return CommandCenter(tuple(rank_signals(signals, limit=limit)))
