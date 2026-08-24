"""Provider-neutral market-data ingestion with strict OHLCV validation."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from .signals import MarketBar


@dataclass(frozen=True)
class RawBar:
    timestamp: str
    open: str
    high: str
    low: str
    close: str
    volume: str = "0"


def parse_bars(rows: list[RawBar]) -> list[MarketBar]:
    """Convert provider rows into trusted engine bars; reject malformed data."""
    result: list[MarketBar] = []
    previous_timestamp = None
    for row in rows:
        if previous_timestamp is not None and row.timestamp <= previous_timestamp:
            raise ValueError("market bars must have strictly increasing timestamps")
        try:
            values = [Decimal(value) for value in (row.open, row.high, row.low, row.close, row.volume)]
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("market bar contains a non-numeric value") from exc
        open_, high, low, close, volume = values
        if min(open_, high, low, close) <= 0 or volume < 0:
            raise ValueError("OHLC prices must be positive and volume non-negative")
        if high < max(open_, close) or low > min(open_, close) or high < low:
            raise ValueError("invalid OHLC relationship")
        result.append(MarketBar(row.timestamp, open_, high, low, close, volume))
        previous_timestamp = row.timestamp
    return result
