import pytest

from forex.data import RawBar, parse_bars


def row(ts, close, open_=None, high=None, low=None):
    open_ = close if open_ is None else open_
    high = close if high is None else high
    low = close if low is None else low
    return RawBar(ts, str(open_), str(high), str(low), str(close), "100")


def test_parse_bars_accepts_valid_ohlcv():
    bars = parse_bars([row("2026-08-24T00:00:00Z", "100"), row("2026-08-24T00:15:00Z", "101")])
    assert bars[-1].close == 101


def test_parse_bars_rejects_bad_order():
    with pytest.raises(ValueError, match="strictly increasing"):
        parse_bars([row("2026-08-24T00:15:00Z", "100"), row("2026-08-24T00:00:00Z", "101")])


def test_parse_bars_rejects_invalid_ohlc():
    with pytest.raises(ValueError, match="OHLC"):
        parse_bars([row("2026-08-24T00:00:00Z", "100", open_="100", high="99", low="98")])
