"""Core loan domain objects and amortization logic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from math import isclose
from typing import Dict, List


@dataclass
class Loan(ABC):
    """Abstract base class for loans."""

    principal: float
    term: int
    rate: float
    loan_id: int
    _schedule_cache: List[Dict[str, float]] | None = field(
        default=None, init=False, repr=False
    )

    @abstractmethod
    def monthly_payment(self) -> float:
        """Return the regular monthly payment amount."""

    @abstractmethod
    def amortization_schedule(self) -> List[Dict[str, float]]:
        """Return month-by-month schedule dictionaries."""

    def balance_at(self, month: int) -> float:
        """Return balance after ``month`` months; ``ValueError`` if out of range."""
        if month < 0 or month > self.term:
            raise ValueError(f"month must be between 0 and {self.term}")
        if month == 0:
            return round(self.principal, 2)
        return self.amortization_schedule()[month - 1]["balance"]


@dataclass
class FixedRateLoan(Loan):
    """Fully amortizing fixed-rate loan."""

    def monthly_payment(self) -> float:
        """Return level payment that fully amortizes principal over `term` months."""

        monthly_rate = self.rate / 12.0
        if isclose(monthly_rate, 0.0):
            return self.principal / self.term

        numerator = self.principal * monthly_rate
        denominator = 1 - (1 + monthly_rate) ** (-self.term)
        return numerator / denominator

    def amortization_schedule(self) -> List[Dict[str, float]]:
        """Return one dict per month: payment, interest, principal, balance."""
        if self._schedule_cache is not None:
            return self._schedule_cache

        schedule: List[Dict[str, float]] = []
        payment = self.monthly_payment()
        balance = self.principal
        monthly_rate = self.rate / 12.0

        for month in range(1, self.term + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest

            # Ensure numerical stability in the final month.
            if month == self.term:
                principal_paid = balance
                payment = principal_paid + interest

            balance = balance - principal_paid
            if balance < 0 and isclose(balance, 0.0, abs_tol=1e-8):
                balance = 0.0

            schedule.append(
                {
                    "month": month,
                    "payment": round(payment, 2),
                    "interest": round(interest, 2),
                    "principal": round(principal_paid, 2),
                    "balance": round(balance, 2),
                }
            )
        self._schedule_cache = schedule
        return self._schedule_cache

@dataclass
class InterestOnlyLoan(Loan):
    """Interest-only loan: pay interest each month, then repay full principal on the last month."""

    def monthly_payment(self) -> float:
        """Return monthly interest on principal (before the final principal payment)."""

        monthly_rate = self.rate / 12.0
        return self.principal * monthly_rate

    def amortization_schedule(self) -> List[Dict[str, float]]:
        """Return monthly rows; the last month repays all principal plus interest."""
        if self._schedule_cache is not None:
            return self._schedule_cache

        schedule: List[Dict[str, float]] = []
        monthly_interest = self.principal * (self.rate / 12.0)

        for month in range(1, self.term + 1):
            if month < self.term:
                payment = monthly_interest
                principal_paid = 0.0
                balance = self.principal
            else:
                payment = monthly_interest + self.principal
                principal_paid = self.principal
                balance = 0.0

            schedule.append(
                {
                    "month": month,
                    "payment": round(payment, 2),
                    "interest": round(monthly_interest, 2),
                    "principal": round(principal_paid, 2),
                    "balance": round(balance, 2),
                }
            )
        self._schedule_cache = schedule
        return self._schedule_cache


