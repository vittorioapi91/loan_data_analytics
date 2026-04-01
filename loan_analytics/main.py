"""Simple self-contained usage example."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd

from .lib.load_data import load_loans_from_csv

logger = logging.getLogger(__name__)


def main() -> None:

    logging.basicConfig(level=logging.INFO)

    output_dir = Path.cwd() / "outputs"
    input_csv_path = Path.cwd() / "input" / "loans.csv"

    loans_by_id = load_loans_from_csv(str(input_csv_path))
    
    schedules_by_id = {
        loan_id: loan.amortization_schedule()
        for loan_id, loan in loans_by_id.items()
    }
    logger.info("schedule calculation completed")

    # remove any previous output
    csv_output_path = Path(str(output_dir) + '/schedule.csv')
    if os.path.exists(csv_output_path):
        os.remove(csv_output_path)

    
    for loan_id in schedules_by_id.keys():
        df = pd.DataFrame.from_records(schedules_by_id[loan_id])
        df.insert(0, "loan_id", loan_id)
        df.to_csv(csv_output_path, 
                                  index=False, mode='a', 
                                  header=not os.path.exists(csv_output_path))

    logger.info(f'file {csv_output_path.name} saved')



if __name__ == "__main__":
    main()
