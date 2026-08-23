"""Deterministic temporal feature extraction for TIMEŒ decisions."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class TemporalFeatures:
    days_to_due: int
    urgency: Decimal
    horizon: str


def extract_temporal_features(as_of: date, due_date: date) -> TemporalFeatures:
    days_to_due = (due_date - as_of).days
    if days_to_due <= 0:
        urgency = Decimal("1.00")
        horizon = "due"
    elif days_to_due <= 2:
        urgency = Decimal("0.85")
        horizon = "near"
    elif days_to_due <= 7:
        urgency = Decimal("0.60")
        horizon = "short"
    elif days_to_due <= 30:
        urgency = Decimal("0.30")
        horizon = "medium"
    else:
        urgency = Decimal("0.10")
        horizon = "long"
    return TemporalFeatures(days_to_due, urgency, horizon)
