# Loan data analytics

Library to calculate loan schedules.

## 1. Classes (base and concrete types)

- **`Loan`** (`loan_analytics.lib.loans`) — Abstract base class. Holds **`principal`**, **`term`** (months), and **`rate`** (annual). 

- **`FixedRateLoan`** — Fully amortizing fixed-rate loan: payment is level over the term until the balance reaches zero.

- **`InterestOnlyLoan`** — Interest due each month on the full principal; the **last** month pays that month’s interest plus the full principal in one payment.

## 3. How to run

**Tests** (from the repo root, so imports resolve):

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

**Sample schedule export** (loads and validates loans from `input/loans.csv`, then writes JSON and CSV under `outputs/`; that directory must already exist):

```bash
PYTHONPATH=. python3 -m loan_analytics.main
```
