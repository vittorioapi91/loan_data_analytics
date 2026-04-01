import unittest
from pathlib import Path

from loan_analytics.lib.load_data import load_loans_from_csv
from loan_analytics.lib.loans_factory import create_loan
from loan_analytics.lib.loans import FixedRateLoan, InterestOnlyLoan


class TestFixedRateLoan(unittest.TestCase):
    def test_monthly_payment_positive_rate(self) -> None:
        loan = FixedRateLoan(principal=10000, term=12, rate=0.12, loan_id=1)
        self.assertAlmostEqual(loan.monthly_payment(), 888.49, places=2)

    def test_monthly_payment_zero_rate(self) -> None:
        loan = FixedRateLoan(principal=12000, term=12, rate=0.0, loan_id=2)
        self.assertAlmostEqual(loan.monthly_payment(), 1000.00, places=2)

    def test_schedule_shape_and_terminal_balance(self) -> None:
        loan = FixedRateLoan(principal=10000, term=12, rate=0.12, loan_id=3)
        schedule = loan.amortization_schedule()

        self.assertEqual(len(schedule), 12)
        self.assertEqual(schedule[0]["month"], 1)
        self.assertAlmostEqual(schedule[-1]["balance"], 0.0, places=2)

    def test_balance_at(self) -> None:
        loan = FixedRateLoan(principal=10000, term=12, rate=0.12, loan_id=4)
        self.assertEqual(loan.balance_at(0), 10000.00)
        self.assertAlmostEqual(loan.balance_at(12), 0.0, places=2)
        with self.assertRaises(ValueError):
            loan.balance_at(13)


class TestInterestOnlyLoan(unittest.TestCase):
    def test_monthly_payment(self) -> None:
        loan = InterestOnlyLoan(principal=50000, term=6, rate=0.06, loan_id=5)
        self.assertAlmostEqual(loan.monthly_payment(), 250.0, places=2)

    def test_schedule_interest_only_then_balloon(self) -> None:
        loan = InterestOnlyLoan(principal=50000, term=6, rate=0.06, loan_id=6)
        schedule = loan.amortization_schedule()

        self.assertEqual(len(schedule), 6)
        self.assertEqual(schedule[0]["principal"], 0.0)
        self.assertEqual(schedule[0]["balance"], 50000.0)
        self.assertEqual(schedule[-1]["principal"], 50000.0)
        self.assertEqual(schedule[-1]["balance"], 0.0)


class TestFactory(unittest.TestCase):
    def test_create_fixed_rate_loan(self) -> None:
        loan = create_loan({"type": "fixed_rate", "principal": 10000, "term": 12, "rate": 0.1, "loan_id": 10})
        self.assertIsInstance(loan, FixedRateLoan)

    def test_create_interest_only_loan(self) -> None:
        loan = create_loan({"type": "interest_only", "principal": 10000, "term": 12, "rate": 0.1, "loan_id": 11})
        self.assertIsInstance(loan, InterestOnlyLoan)

    def test_reject_unsupported_loan(self) -> None:
        with self.assertRaises(ValueError):
            create_loan({"type": "unknown", "principal": 10000, "term": 12, "rate": 0.1, "loan_id": 12})

    def test_reject_missing_fields(self) -> None:
        with self.assertRaises(ValueError):
            create_loan({"type": "fixed_rate", "principal": 10000, "term": 12})


class TestCsvInput(unittest.TestCase):
    def test_load_valid_csv(self) -> None:
        csv_path = Path(__file__).resolve().parent / "data" / "input" / "loans.csv"
        loans = load_loans_from_csv(str(csv_path))
        self.assertEqual(len(loans), 2)
        self.assertIsInstance(loans[0], FixedRateLoan)
        self.assertIsInstance(loans[1], InterestOnlyLoan)
        self.assertIsNotNone(loans[0].loan_id)
        self.assertIsNotNone(loans[1].loan_id)


if __name__ == "__main__":
    unittest.main()
