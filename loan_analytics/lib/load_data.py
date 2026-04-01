from __future__ import annotations

from typing import Dict
import pandas as pd

from .loans_factory import create_loan
from .loans import Loan


def load_loans_from_csv(path: str) -> Dict[int, Loan]:
    """Parse CSV."""

    df = pd.read_csv(path)
    records = df.to_dict(orient="records")

    loans_by_id: Dict[int, Loan] = {}
    for item in records:
        loan_id = int(item["loan_id"])
        loans_by_id[loan_id] = create_loan(item)

    return loans_by_id
