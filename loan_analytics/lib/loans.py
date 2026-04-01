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
    _schedule_cache: List[Dict[str, float]] | None = field(
        default=None, init=False, repr=False
    )

    @abstractmethod
    def monthly_payment(self) -> float:
        """Return the regular monthly payment amount."""

    def amortization_schedule(self) -> List[Dict[str, float]]:
        """Return month-by-month schedule dictionaries."""
        return self._amortization_schedule_up_to_n(self.term)

    @abstractmethod
    def _amortization_schedule_up_to_n(self, upto_month: int) -> List[Dict[str, float]]:
        """Incrementally extend cached schedule up to ``upto_month``."""

    def balance_at(self, month: int) -> float:
        """Return balance after ``month`` months; ``ValueError`` if out of range."""

        if month < 0 or month > self.term:
            raise ValueError(f"month must be between 0 and {self.term}")
        if month == 0:
            return round(self.principal, 2)
        return self._amortization_schedule_up_to_n(month)[month - 1]["balance"]


@dataclass
class FixedRateLoan(Loan):
    """Fully amortizing fixed-rate loan."""

    def _amortization_schedule_up_to_n(self, upto_month: int) -> List[Dict[str, float]]:
        """Incrementally extend cached schedule up to ``upto_month``."""

        if self._schedule_cache is None:
            self._schedule_cache = []

        if len(self._schedule_cache) >= upto_month:
            return self._schedule_cache

        payment = self.monthly_payment()
        monthly_rate = self.rate / 12.0
        balance = (
            self.principal if not self._schedule_cache else self._schedule_cache[-1]["balance"]
        )
        start_month = len(self._schedule_cache) + 1

        for month in range(start_month, upto_month + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest

            if month == self.term:
                principal_paid = balance
                payment = principal_paid + interest

            balance = balance - principal_paid
            if balance < 0 and isclose(balance, 0.0, abs_tol=1e-8):
                balance = 0.0

            self._schedule_cache.append(
                {
                    "month": month,
                    "payment": round(payment, 2),
                    "interest": round(interest, 2),
                    "principal": round(principal_paid, 2),
                    "balance": round(balance, 2),
                }
            )

        return self._schedule_cache

    def monthly_payment(self) -> float:
        """Return level payment that fully amortizes principal over `term` months."""

        monthly_rate = self.rate / 12.0
        if isclose(monthly_rate, 0.0):
            return self.principal / self.term

        numerator = self.principal * monthly_rate
        denominator = 1 - (1 + monthly_rate) ** (-self.term)
        return numerator / denominator

@dataclass
class InterestOnlyLoan(Loan):
    """Interest-only loan: pay interest each month, then repay full principal on the last month."""

    def _amortization_schedule_up_to_n(self, upto_month: int) -> List[Dict[str, float]]:
        """Incrementally extend cached schedule up to ``upto_month``."""
        if self._schedule_cache is None:
            self._schedule_cache = []

        if len(self._schedule_cache) >= upto_month:
            return self._schedule_cache

        monthly_interest = self.principal * (self.rate / 12.0)
        start_month = len(self._schedule_cache) + 1

        for month in range(start_month, upto_month + 1):
            if month < self.term:
                payment = monthly_interest
                principal_paid = 0.0
                balance = self.principal
            else:
                payment = monthly_interest + self.principal
                principal_paid = self.principal
                balance = 0.0

            self._schedule_cache.append(
                {
                    "month": month,
                    "payment": round(payment, 2),
                    "interest": round(monthly_interest, 2),
                    "principal": round(principal_paid, 2),
                    "balance": round(balance, 2),
                }
            )

        return self._schedule_cache

    def monthly_payment(self) -> float:
        """Return monthly interest on principal (before the final principal payment)."""

        monthly_rate = self.rate / 12.0
        return self.principal * monthly_rate

