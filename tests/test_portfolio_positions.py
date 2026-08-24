from decimal import Decimal

from portfolio.positions import Position, position_summary


def test_position_summary_tracks_investment_without_execution():
    result = position_summary(Position("VOO", Decimal("9.00")), Decimal("500"))
    assert result["symbol"] == "VOO"
    assert result["invested_usd"] == "9.00"
    assert result["shares"] == "0"
    assert result["market_value"] == "0"
