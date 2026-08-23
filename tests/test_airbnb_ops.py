import unittest
from datetime import date
from decimal import Decimal

from airbnb_ops.service import AirbnbOpsService, Booking, Expense, PropertyConfig


class AirbnbOpsServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = AirbnbOpsService(
            PropertyConfig(
                property_name="Lekki Phase 1 — 2BR",
                nightly_rate=Decimal("150000"),
                outstanding_obligation=Decimal("450000"),
            )
        )

    def test_booking_revenue_and_nights(self):
        booking = Booking(
            "B1",
            date(2026, 8, 1),
            date(2026, 8, 4),
            Decimal("150000"),
            Decimal("22500"),
        )
        self.service.add_booking(booking)
        self.assertEqual(booking.nights, 3)
        self.assertEqual(booking.gross_revenue, Decimal("450000"))
        self.assertEqual(booking.net_revenue, Decimal("427500"))

    def test_month_summary(self):
        self.service.add_booking(
            Booking("B1", date(2026, 8, 1), date(2026, 8, 4), Decimal("150000"))
        )
        self.service.add_expense(
            Expense("E1", "cleaning", Decimal("30000"), date(2026, 8, 4))
        )
        summary = self.service.summary(date(2026, 8, 1), date(2026, 9, 1))
        self.assertEqual(summary["booked_nights"], 3)
        self.assertEqual(summary["gross_revenue"], Decimal("450000"))
        self.assertEqual(summary["operating_expenses"], Decimal("30000"))
        self.assertEqual(summary["net_operating_result"], Decimal("420000"))

    def test_debt_clearing_nights_rounds_up(self):
        self.assertEqual(self.service.nights_to_clear(Decimal("450001")), 4)
        self.assertEqual(self.service.nights_to_clear(Decimal("450000")), 3)


if __name__ == "__main__":
    unittest.main()
