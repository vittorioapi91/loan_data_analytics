from __future__ import annotations

import random
from typing import List
from pathlib import Path
import pandas as pd

from .loans_factory import create_loan
from .loans import Loan


REQUIRED_COLS = {"type", "principal", "term", "rate"}


def validate_loans_csv(path: str) -> pd.DataFrame:
    """Check required columns and numeric `principal`, `term`, `rate`."""

    df = pd.read_csv(path)

    required_columns = REQUIRED_COLS
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV missing required columns: {missing}")

    if df.empty:
        raise ValueError("CSV file has no loan rows")

    type_series = df["type"]
    if type_series.isna().any():
        raise ValueError("'type' column contains null values")
    if not type_series.map(lambda value: isinstance(value, str)).all():
        raise ValueError("'type' column must contain string values")

    for column in ("principal", "term", "rate"):
        numeric_series = pd.to_numeric(df[column], errors="coerce")
        if numeric_series.isna().any():
            raise ValueError(f"'{column}' column must contain numeric values")
        df[column] = numeric_series

    return df


def load_loans_from_csv(path: str) -> List[Loan]:
    """Validated and parse CSV."""

    df = validate_loans_csv(path)
    df.insert(0, "loan_id", random.sample(range(100000, 1000000), k=len(df)))

    df.to_csv(str(Path(path).parent) + "/loans_with_id.csv", index=False)
    records = df.to_dict(orient="records")

    loans: List[Loan] = []
    for item in records:
        loans.append(create_loan(item))

    return loans
