"""Finance and debt-control calculations for the Airbnb business unit."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FinanceSnapshot:
    gross_revenue: Decimal
    platform_fees: Decimal
    operating_expenses: Decimal
    net_operating_result: Decimal
    outstanding_obligation: Decimal
    cash_available_for_debt: Decimal
    debt_clearing_nights: int
    break_even_nights: int


def ceiling_div(amount: Decimal, per_night: Decimal) -> int:
    if amount <= 0:
        return 0
    if per_night <= 0:
        raise ValueError("per_night must be positive")
    return int((amount / per_night).to_integral_value(rounding="ROUND_CEILING"))


def build_snapshot(
    *,
    gross_revenue: Decimal,
    platform_fees: Decimal,
    operating_expenses: Decimal,
    outstanding_obligation: Decimal,
    nightly_contribution: Decimal,
    fixed_costs: Decimal = Decimal("0"),
) -> FinanceSnapshot:
    values = [gross_revenue, platform_fees, operating_expenses, outstanding_obligation, nightly_contribution, fixed_costs]
    if any(value < 0 for value in values):
        raise ValueError("finance amounts cannot be negative")

    net = gross_revenue - platform_fees - operating_expenses
    cash_for_debt = max(Decimal("0"), net - fixed_costs)
    debt_nights = ceiling_div(outstanding_obligation, nightly_contribution)
    break_even_nights = ceiling_div(fixed_costs, nightly_contribution)
    return FinanceSnapshot(
        gross_revenue=gross_revenue,
        platform_fees=platform_fees,
        operating_expenses=operating_expenses,
        net_operating_result=net,
        outstanding_obligation=outstanding_obligation,
        cash_available_for_debt=cash_for_debt,
        debt_clearing_nights=debt_nights,
        break_even_nights=break_even_nights,
    )
