"""Factory for creating loan instances from configuration."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from .loans import FixedRateLoan, InterestOnlyLoan, Loan


def create_loan(config: Dict[str, Any]) -> Loan:
    """Build a loan from `type`, `principal`, `term`, and `rate` with the appropriate class.
    """

    loan_type = str(config["type"])

    principal = Decimal(str(config["principal"]))
    term = Decimal(str(config["term"]))
    rate = Decimal(str(config["rate"]))

    if loan_type == 'fixed_rate':
        return FixedRateLoan(principal=principal, term=term, rate=rate)
    if loan_type == "interest_only":
        return InterestOnlyLoan(principal=principal, term=term, rate=rate)

    raise ValueError(f"unsupported loan type: {config['type']}")
