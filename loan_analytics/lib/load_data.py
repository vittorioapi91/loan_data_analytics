from __future__ import annotations

import random
from typing import List
from pathlib import Path
import pandas as pd

from .loans_factory import create_loan
from .loans import Loan



def load_loans_from_csv(path: str) -> List[Loan]:
    """Validated and parse CSV."""

    df = pd.read_csv(path)
    records = df.to_dict(orient="records")

    loans: List[Loan] = []
    for item in records:
        loans.append(create_loan(item))

    return loans
