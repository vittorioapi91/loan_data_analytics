import unittest
from decimal import Decimal
from pathlib import Path

from loan_analytics.lib.load_data import load_loans_from_csv
from loan_analytics.lib.loans_factory import create_loan
from loan_analytics.lib.loans import FixedRateLoan, InterestOnlyLoan


class TestFixedRateLoan(unittest.TestCase):
    def test_monthly_payment_positive_rate(self) -> None:
        loan = FixedRateLoan(
            principal=Decimal("10000"),
            term=Decimal("12"),
            rate=Decimal("0.12"),
        )
        self.assertAlmostEqual(loan.monthly_payment(), 888.49, places=2)

    def test_monthly_payment_zero_rate(self) -> None:
        loan = FixedRateLoan(
            principal=Decimal("12000"),
            term=Decimal("12"),
            rate=Decimal("0.0"),
        )
        self.assertAlmostEqual(loan.monthly_payment(), 1000.00, places=2)

    def test_schedule_shape_and_terminal_balance(self) -> None:
        loan = FixedRateLoan(
            principal=Decimal("10000"),
            term=Decimal("12"),
            rate=Decimal("0.12"),
        )
        schedule = loan.amortization_schedule()

        self.assertEqual(len(schedule), 12)
        self.assertEqual(schedule[0]["month"], 1)
        self.assertAlmostEqual(schedule[-1]["balance"], 0.0, places=2)

    def test_balance_at(self) -> None:
        loan = FixedRateLoan(
            principal=Decimal("10000"),
            term=Decimal("12"),
            rate=Decimal("0.12"),
        )
        self.assertEqual(loan.balance_at(0), 10000.00)
        self.assertAlmostEqual(loan.balance_at(6), 5149.21, places=2)
        self.assertAlmostEqual(loan.balance_at(12), 0.0, places=2)
        self.assertAlmostEqual(loan.balance_at(6), 5149.21, places=2) # testing cache
        with self.assertRaises(ValueError):
            loan.balance_at(13)

    def test_rejects_rate_list_for_fixed_rate_loan(self) -> None:
        with self.assertRaises(ValueError):
            FixedRateLoan(
                principal=Decimal("10000"),
                term=Decimal("12"),
                rate=[Decimal("0.12"), Decimal("0.13")],
            )


class TestInterestOnlyLoan(unittest.TestCase):
    def test_monthly_payment(self) -> None:
        loan = InterestOnlyLoan(
            principal=Decimal("50000"),
            term=Decimal("6"),
            rate=Decimal("0.06"),
        )
        self.assertAlmostEqual(loan.monthly_payment(), 250.0, places=2)

    def test_schedule_interest_only_then_principal_repayment(self) -> None:
        loan = InterestOnlyLoan(
            principal=Decimal("50000"),
            term=Decimal("6"),
            rate=Decimal("0.06"),
        )
        schedule = loan.amortization_schedule()

        self.assertEqual(len(schedule), 6)
        self.assertEqual(schedule[0]["principal"], 0.0)
        self.assertEqual(schedule[0]["balance"], 50000.0)
        self.assertEqual(schedule[-1]["principal"], 50000.0)
        self.assertEqual(schedule[-1]["balance"], 0.0)

    def test_rejects_rate_list_for_interest_only_loan(self) -> None:
        with self.assertRaises(ValueError):
            InterestOnlyLoan(
                principal=Decimal("50000"),
                term=Decimal("6"),
                rate=[Decimal("0.05"), Decimal("0.06")],
            )


class TestFactory(unittest.TestCase):

    def test_create_fixed_rate_loan(self) -> None:
        loan = create_loan(
            {
                "type": "fixed_rate",
                "principal": Decimal("10000"),
                "term": Decimal("12"),
                "rate": Decimal("0.1"),
                "loan_id": 10,
            }
        )
        self.assertIsInstance(loan, FixedRateLoan)
        self.assertIsInstance(loan.principal, Decimal)
        self.assertIsInstance(loan.term, Decimal)
        self.assertIsInstance(loan.rate, Decimal)

    def test_create_interest_only_loan(self) -> None:
        loan = create_loan(
            {
                "type": "interest_only",
                "principal": Decimal("10000"),
                "term": Decimal("12"),
                "rate": Decimal("0.1"),
                "loan_id": 11,
            }
        )
        self.assertIsInstance(loan, InterestOnlyLoan)

    def test_reject_unsupported_loan(self) -> None:
        with self.assertRaises(ValueError):
            create_loan(
                {
                    "type": "unknown",
                    "principal": Decimal("10000"),
                    "term": Decimal("12"),
                    "rate": Decimal("0.1"),
                    "loan_id": 12,
                }
            )

    def test_reject_negative_principal(self) -> None:
        with self.assertRaises(ValueError):
            create_loan(
                {
                    "type": "fixed_rate",
                    "principal": Decimal("-10000"),
                    "term": Decimal("12"),
                    "rate": Decimal("0.1"),
                    "loan_id": 13,
                }
            )

    def test_reject_non_positive_term(self) -> None:
        with self.assertRaises(ValueError):
            create_loan(
                {
                    "type": "fixed_rate",
                    "principal": Decimal("10000"),
                    "term": Decimal("0"),
                    "rate": Decimal("0.1"),
                    "loan_id": 14,
                }
            )

    def test_reject_negative_rate(self) -> None:
        with self.assertRaises(ValueError):
            create_loan(
                {
                    "type": "fixed_rate",
                    "principal": Decimal("10000"),
                    "term": Decimal("12"),
                    "rate": Decimal("-0.1"),
                    "loan_id": 15,
                }
            )



class TestCsvInput(unittest.TestCase):
    def test_load_valid_csv(self) -> None:
        csv_path = Path(__file__).resolve().parent / "data" / "input" / "loans.csv"
        loans_by_id = load_loans_from_csv(str(csv_path))
        self.assertIsInstance(loans_by_id[1], FixedRateLoan)
        self.assertIsInstance(loans_by_id[2], InterestOnlyLoan)


if __name__ == "__main__":
    unittest.main()
