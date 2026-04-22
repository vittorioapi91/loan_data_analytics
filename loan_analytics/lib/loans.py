"""Core loan domain objects and amortization logic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Union
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator  # pyright: ignore[reportMissingImports]


class LoanInputModel(BaseModel):
    """Validate common loan input fields."""

    model_config = ConfigDict(extra="forbid")

    principal: Decimal
    term: Decimal
    rate: Union[Decimal, List[Decimal]]

    @field_validator("principal")
    @classmethod
    def validate_principal(cls, value: Decimal) -> Decimal:
        normalized_value = Decimal(str(value))
        if normalized_value <= 0:
            raise ValueError("principal must be greater than 0")
        return normalized_value

    @field_validator("term")
    @classmethod
    def validate_term(cls, value: Decimal) -> Decimal:
        normalized_value = Decimal(str(value))
        if normalized_value <= 0:
            raise ValueError("term must be greater than 0")
        if normalized_value != normalized_value.to_integral_value():
            raise ValueError("term must be a whole number")
        return normalized_value

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, value: Union[Decimal, List[Decimal]]) -> Union[Decimal, List[Decimal]]:
        if isinstance(value, list):
            if len(value) == 0:
                raise ValueError("rate list must contain at least one value")
            normalized_values = [Decimal(str(rate_value)) for rate_value in value]
            if any(rate_value < 0 for rate_value in normalized_values):
                raise ValueError("rate values must be greater than or equal to 0")
            return normalized_values

        normalized_value = Decimal(str(value))
        if normalized_value < 0:
            raise ValueError("rate must be greater than or equal to 0")
        return normalized_value


@dataclass
class Loan(ABC):
    """Abstract base class for loans."""

    principal: Decimal
    term: Decimal
    rate: Union[Decimal, List[Decimal]]
    _schedule_cache: List[Dict[str, float]] | None = field(
        default=None, init=False, repr=False
    )

    def __post_init__(self) -> None:
        """Validate and normalize common loan fields."""
        try:
            validated = LoanInputModel(
                principal=self.principal,
                term=self.term,
                rate=self.rate,
            )
        except ValidationError as exc:
            raise ValueError(f"invalid loan inputs: {exc}") from exc

        self.principal = validated.principal
        self.term = validated.term
        self.rate = validated.rate

    @abstractmethod
    def monthly_payment(self) -> float:
        """Return the regular monthly payment amount."""

    def amortization_schedule(self) -> List[Dict[str, float]]:
        """Return month-by-month schedule dictionaries."""
        return self._amortization_schedule_up_to_n(int(self.term))

    def _amortization_schedule_up_to_n(self, upto_month: int) -> List[Dict[str, float]]:
        """Return cached schedule, extending it up to ``upto_month`` when needed."""
        term_as_int = int(self.term)
        if upto_month < 0 or upto_month > term_as_int:
            raise ValueError(f"upto_month must be between 0 and {term_as_int}")

        if self._schedule_cache is None:
            self._schedule_cache = []

        if len(self._schedule_cache) < upto_month:
            self._extend_schedule_cache(upto_month)

        return self._schedule_cache

    @abstractmethod
    def _extend_schedule_cache(self, upto_month: int) -> None:
        """Append missing schedule rows through ``upto_month``."""

    def balance_at(self, month: int) -> float:
        """Return balance after ``month`` months; ``ValueError`` if out of range."""

        term_as_int = int(self.term)
        if month < 0 or month > term_as_int:
            raise ValueError(f"month must be between 0 and {term_as_int}")
        if month == 0:
            return round(float(self.principal), 2)
        return self._amortization_schedule_up_to_n(month)[month - 1]["balance"]


@dataclass
class FixedRateLoan(Loan):
    """Fully amortizing fixed-rate loan."""

    def __post_init__(self) -> None:
        super().__post_init__()
        if isinstance(self.rate, Decimal):
            raise ValueError("FixedRateLoan rate must be a scalar Decimal")

    def _extend_schedule_cache(self, upto_month: int) -> None:
        """Append fixed-rate rows through ``upto_month``."""

        payment = Decimal(str(self.monthly_payment()))
        monthly_rate = self.rate / Decimal("12")
        balance = (
            self.principal
            if not self._schedule_cache
            else Decimal(str(self._schedule_cache[-1]["balance"]))
        )
        start_month = len(self._schedule_cache) + 1

        for month in range(start_month, upto_month + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest

            if month == int(self.term):
                principal_paid = balance
                payment = principal_paid + interest

            balance = balance - principal_paid

            self._schedule_cache.append(
                {
                    "month": month,
                    "payment": round(float(payment), 2),
                    "interest": round(float(interest), 2),
                    "principal": round(float(principal_paid), 2),
                    "balance": round(float(balance), 2),
                }
            )

    def monthly_payment(self) -> float:
        """Return level payment that fully amortizes principal over `term` months."""

        monthly_rate = self.rate / Decimal("12")
        if monthly_rate == 0:
            return float(self.principal / self.term)

        numerator = self.principal * monthly_rate
        denominator = Decimal("1") - (Decimal("1") + monthly_rate) ** (-int(self.term))
        return float(numerator / denominator)

@dataclass
class InterestOnlyLoan(Loan):
    """Interest-only loan: pay interest each month, then repay full principal on the last month."""

    def __post_init__(self) -> None:
        super().__post_init__()
        if isinstance(self.rate, Decimal):
            raise ValueError("InterestOnlyLoan rate must be a scalar Decimal")

    def _extend_schedule_cache(self, upto_month: int) -> None:
        """Append interest-only rows through ``upto_month``."""

        monthly_interest = self.principal * (self.rate / Decimal("12"))
        start_month = len(self._schedule_cache) + 1

        for month in range(start_month, upto_month + 1):
            if month < int(self.term):
                payment = monthly_interest
                principal_paid = Decimal("0")
                balance = self.principal
            else:
                payment = monthly_interest + self.principal
                principal_paid = self.principal
                balance = Decimal("0")

            self._schedule_cache.append(
                {
                    "month": month,
                    "payment": round(float(payment), 2),
                    "interest": round(float(monthly_interest), 2),
                    "principal": round(float(principal_paid), 2),
                    "balance": round(float(balance), 2),
                }
            )

    def monthly_payment(self) -> float:
        """Return monthly interest on principal (before the final principal payment)."""

        monthly_rate = self.rate / Decimal("12")
        return float(self.principal * monthly_rate)

