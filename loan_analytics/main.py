"""Runtime entry point for generating loan schedules."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from numpy import append
import pandas as pd

from .lib.load_data import load_loans_from_csv

logger = logging.getLogger(__name__)


def main() -> None:

    logging.basicConfig(level=logging.INFO)

    output_dir = Path.cwd() / "outputs"
    input_csv_path = Path.cwd() / "input" / "loans.csv"

    loans = load_loans_from_csv(str(input_csv_path))
    logger.info("input validation completed")

    schedules_by_id = {
        loan.loan_id: loan.amortization_schedule()
        for loan in loans
    }
    logger.info("schedule calculation completed")


    # remove any previous output
    for output_type in ['csv', 'json']:
        output_path = Path(str(output_dir) + f'/schedule.{output_type}')
        if os.path.exists(output_path):
            os.remove(output_path)

        
    json_output_path = Path(str(output_dir) + '/schedule.json')
    with json_output_path.open("w") as file_handle:
        json.dump(schedules_by_id, file_handle, indent=2)
    logger.info('file "%s" saved', json_output_path.name)

    
    csv_output_path = Path(str(output_dir) + '/schedule.csv')
    for loan_id in schedules_by_id.keys():
        df = pd.DataFrame.from_records(schedules_by_id[loan_id])
        df.insert(0, "loan_id", loan_id)
        df.to_csv(csv_output_path, 
                                  index=False, mode='a', 
                                  header=not os.path.exists(csv_output_path))

    logger.info(f'file {csv_output_path.name} saved')



if __name__ == "__main__":
    main()
