"""
parse_totals.py
Extract TOTAL amounts and dates from a financial text report.
"""
import re
import sys
from datetime import datetime
from .plot import show


def parse_file(file_path):
    dates = []
    dollars = []

    # Regex patterns
    total_line_pattern = re.compile(r"TOTAL:\s*\$?([\d,]+)")
    date_pattern = re.compile(r"\(?([A-Za-z]{3,9} \d{1,2}, \d{4})\)?")

    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith("TOTAL:"):
                    # Extract dollar amount
                    dollar_match = total_line_pattern.search(line)
                    if dollar_match:
                        amount_str = dollar_match.group(1).replace(",", "")
                        amount = float(amount_str)
                    else:
                        continue

                    # Extract date
                    date_match = date_pattern.search(line)
                    if date_match:
                        date_str = date_match.group(1)
                        date_obj = datetime.strptime(date_str, "%b %d, %Y")
                    else:
                        continue

                    dollars.append(amount)
                    dates.append(date_obj)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)

    return dates, dollars

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_totals.py <filename>")
        sys.exit(1)

    #import pdb; pdb.set_trace()
    file_path = sys.argv[1]
    dates, dollars = parse_file(file_path)

    print("\nExtracted totals:")
    for d, y in zip(dates, dollars):
        print(f"{d.date()} → ${y:,.0f}")

    show(dates, dollars)


if __name__ == "__main__":
    main()
