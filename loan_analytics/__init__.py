"""Loan analytics package for amortization schedule calculations."""

from .lib.load_data import load_loans_from_csv
from .lib.loans_factory import create_loan
from .lib.loans import FixedRateLoan, InterestOnlyLoan, Loan

__all__ = [
    "Loan",
    "FixedRateLoan",
    "InterestOnlyLoan",
    "create_loan",
    "load_loans_from_csv",
]
