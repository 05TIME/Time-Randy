from decimal import Decimal

from airbnb_ops.finance import build_snapshot, ceiling_div


def test_ceiling_div():
    assert ceiling_div(Decimal("300000"), Decimal("150000")) == 2
    assert ceiling_div(Decimal("1"), Decimal("150000")) == 1


def test_finance_snapshot():
    result = build_snapshot(
        gross_revenue=Decimal("1500000"),
        platform_fees=Decimal("75000"),
        operating_expenses=Decimal("300000"),
        outstanding_obligation=Decimal("900000"),
        nightly_contribution=Decimal("125000"),
        fixed_costs=Decimal("250000"),
    )
    assert result.net_operating_result == Decimal("1125000")
    assert result.cash_available_for_debt == Decimal("875000")
    assert result.debt_clearing_nights == 8
    assert result.break_even_nights == 2
