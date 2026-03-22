# finances

Small Python utilities for analyzing personal finance data in this repo.

The project currently does three main things:

- Parses a First Tech PDF export into CSV summaries.
- Parses `TOTAL:` lines from a text report and plots them over time.
- Runs a simple retirement projection using a 4% withdrawal model.

## Project Layout

- [`fin/pdf.py`](fin/pdf.py): extracts withdrawal transactions from a First Tech PDF and writes CSV outputs.
- [`fin/parser.py`](fin/parser.py): extracts dated `TOTAL:` values from a text file and plots them.
- [`fin/plot.py`](fin/plot.py): shared plotting helper used by `parser.py`.
- [`fin/four_percent_rule.py`](fin/four_percent_rule.py): prints a year-by-year retirement projection table.
- [`fin/generate_images.py`](fin/generate_images.py): generates PNG sequence diagrams into `docs/images/`.

## Setup

This repo uses Poetry.

```bash
poetry install
```

If you do not want to install the package entry points, you can still run the modules with `poetry run python -m ...`.

## Commands

### Parse First Tech PDF

Reads a PDF statement/export and writes three CSV files in the repo root.

```bash
poetry run python -m fin.pdf "First Tech Federal Credit Union.pdf"
```

You can omit the filename to use the default:

```bash
poetry run python -m fin.pdf
```

Outputs:

- `withdrawals_csv_style.csv`
- `withdrawals_grouped_by_payee.csv`
- `withdrawals_grouped_by_normalized_payee.csv`

What it does:

- Extracts negative transactions from the PDF.
- Extracts ACH debit descriptions.
- Normalizes similar payee names into grouped categories.
- Writes raw and grouped CSV summaries.

### Parse Totals From Text

Reads a text file containing lines that start with `TOTAL:` and include a date such as `Jan 2, 2024`.

```bash
poetry run python -m fin.parser path/to/report.txt
```

What it does:

- Extracts the dollar amount from each `TOTAL:` line.
- Extracts the associated date.
- Prints the values.
- Opens a matplotlib line chart.

### Retirement Projection

Runs a simple retirement projection using a fixed growth rate, withdrawal rate, and inflation rate.

```bash
poetry run python -m fin.four_percent_rule
```

Example with overrides:

```bash
poetry run python -m fin.four_percent_rule \
  --balance 1500000 \
  --age 59 \
  --growth 3.2 \
  --withdrawal 4.0 \
  --inflation 3.0 \
  --years 10
```

### Generate Diagram Images

Generates PNG sequence diagrams for the current scripts.

```bash
poetry run generate_images
```

Outputs:

- [`docs/images/parser_sequence.png`](docs/images/parser_sequence.png)
- [`docs/images/four_percent_rule_sequence.png`](docs/images/four_percent_rule_sequence.png)
- [`docs/images/pdf_sequence.png`](docs/images/pdf_sequence.png)

## Documentation

- Mermaid source: [`docs/sequence_diagrams.md`](docs/sequence_diagrams.md)
- PNG diagrams:
  - [`docs/images/parser_sequence.png`](docs/images/parser_sequence.png)
  - [`docs/images/four_percent_rule_sequence.png`](docs/images/four_percent_rule_sequence.png)
  - [`docs/images/pdf_sequence.png`](docs/images/pdf_sequence.png)

## Notes

- `fin/pdf.py` is currently tailored to the structure of the First Tech PDF export in this repo.
- `fin/parser.py` expects dates in the form `%b %d, %Y`, for example `Jan 2, 2024`.
- Generated CSV files are written to the repository root, not the `docs/` directory.
