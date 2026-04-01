"""Factory for creating loan instances from configuration."""

from __future__ import annotations

from typing import Any, Dict

from .loans import FixedRateLoan, InterestOnlyLoan, Loan


def create_loan(config: Dict[str, Any]) -> Loan:
    """Build a loan from `type`, `principal`, `term`, and `rate` with the appropriate class.
    """

    if "type" not in config:
        raise ValueError("loan config requires a 'type' field")

    loan_type = str(config["type"]).strip().lower()
    required_fields = ("principal", "term", "rate")
    missing = [field for field in required_fields if field not in config]
    if missing:
        raise ValueError(f"loan config missing required fields: {', '.join(missing)}")

    principal = float(config["principal"])
    term = int(config["term"])
    rate = float(config["rate"])

    if loan_type == 'fixed_rate':
        return FixedRateLoan(principal=principal, term=term, rate=rate)
    if loan_type == "interest_only":
        return InterestOnlyLoan(principal=principal, term=term, rate=rate)

    raise ValueError(f"unsupported loan type: {config['type']}")
