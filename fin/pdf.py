#!/usr/bin/env python3

import argparse
import re
import csv
from decimal import Decimal
from datetime import datetime
from pypdf import PdfReader


MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract withdrawal transactions from a Bank PDF export."
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file.",
    )
    return parser.parse_args()


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_money(value: str) -> Decimal:
    cleaned = value.replace("$", "").replace(",", "").strip()
    return Decimal(cleaned)


def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        parts.append(txt)
    return "\n".join(parts)


def split_sections(full_text: str) -> tuple[str, str]:
    if "DESCRIPTION" not in full_text:
        raise ValueError("Could not find DESCRIPTION section in PDF text.")

    left, right = full_text.split("DESCRIPTION", 1)

    if "Load more transactions" in left:
        left = left.split("Load more transactions", 1)[0]

    return left, right


def extract_transactions(transactions_text: str) -> list[dict]:
    pattern = re.compile(
        r"\b("
        r"JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"
        r")\s+(\d{1,2})\s+(\d{4})\s+(-?\$[\d,]+\.\d{2})\s+(\$[\d,]+\.\d{2})"
    )

    rows = []
    for match in pattern.finditer(transactions_text):
        mon, day, year, amount_str, balance_str = match.groups()
        date_obj = datetime(int(year), MONTHS[mon], int(day))
        amount = parse_money(amount_str)
        balance = parse_money(balance_str)

        if amount < 0:
            rows.append(
                {
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "amount": amount,
                    "balance": balance,
                }
            )

    return rows


def extract_descriptions(descriptions_text: str) -> list[str]:
    lines = [line.strip() for line in descriptions_text.splitlines()]
    lines = [line for line in lines if line]

    descriptions = []
    i = 0

    stop_markers = {
        "HOME EQUITY LINE OR LOAN",
        "Ask FT Chat!",
    }

    while i < len(lines):
        line = lines[i]

        if line in stop_markers:
            break

        if line.startswith("ACH Debit "):
            desc = line[len("ACH Debit ") :].strip()
            i += 1

            while i < len(lines):
                nxt = lines[i].strip()

                if (
                    nxt.startswith("ACH Debit ")
                    or nxt == "Add a category"
                    or nxt in {"Bills & Utilities", "Shopping", "Transfer"}
                    or nxt in stop_markers
                ):
                    break

                desc += " " + nxt
                i += 1

            descriptions.append(normalize_whitespace(desc))
            continue

        i += 1

    return descriptions


def normalize_payee(payee: str) -> str:
    """
    Convert similar payee strings to one canonical grouped name.
    Keeps original payee text intact elsewhere.
    """
    p = normalize_whitespace(payee).upper()

    # Remove common ACH noise / punctuation variation
    p = p.replace(".", "")
    p = p.replace(",", "")
    p = re.sub(r"\s+", " ", p).strip()

    # Custom payee rules
    rules = [
        (r"^ATT\s*-\s*PAYMENT$", "ATT"),
        (r"^ATT\s*-\s*PAYMENT\s*$", "ATT"),
        (r"^PORTLAND GENERAL .*", "PORTLAND GENERAL"),
        (r"^NORTHWEST NATURA .*", "NORTHWEST NATURAL"),
        (r"^CHASE CREDIT CRD\s*-\s*EPAY$", "CHASE CREDIT CARD"),
        (r"^AMEX EPAYMENT .*", "AMEX"),
        (r"^CAPITAL ONE\s*-\s*TRANSFER$", "CAPITAL ONE"),
        (r"^CAPITAL ONE\s*-\s*ONLINE PMT$", "CAPITAL ONE"),
        (r"^JPMORGAN CHASE\s*-\s*EXT TRNSFR$", "JPMORGAN CHASE"),
        (r"^CTY PORTLAND .*", "CITY OF PORTLAND"),
        (r"^LUMENCENTURYLINK .*", "CENTURYLINK"),
        (r"^QUANTUM FIBER .*", "QUANTUM FIBER"),
        (r"^ALLSTATE INS CO .*", "ALLSTATE"),
        (r"^LOWES\s*-\s*SYF PAYMNT$", "LOWE'S"),
        (r"^VENMO\s*-\s*PAYMENT$", "VENMO"),
        (r"^HEIBERG GARBAGE .*", "HEIBERG GARBAGE"),
        (r"^VANGUARD BUY INDIVIDUAL BUY .*", "VANGUARD"),
        (r"^MULTNOMAH COUNTY FIRST TECH FCU B BILL PAYMT$", "MULTNOMAH COUNTY"),
    ]

    for pattern, canonical in rules:
        if re.match(pattern, p):
            return canonical

    # Generic cleanup: trim trailing merchant-type suffixes
    p = re.sub(
        r"\s*-\s*(BILLPAY|PAYMENT|UTILITY|INS PREM|REFUSE SVC|SPEEDPAY|ACH PMT|ONLINE PMT|TRANSFER)$",
        "",
        p,
    )

    return p


def write_transactions_csv(rows: list[dict], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "payee", "normalized_payee", "amount", "balance"])
        for row in rows:
            writer.writerow(
                [
                    row["date"],
                    row["payee"],
                    row["normalized_payee"],
                    f"{row['amount']:.2f}",
                    f"{row['balance']:.2f}",
                ]
            )


def write_grouped_csv(rows: list[dict], key_name: str, output_path: str) -> None:
    summary = {}

    for row in rows:
        key = row[key_name]
        summary.setdefault(key, {"count": 0, "total": Decimal("0.00")})
        summary[key]["count"] += 1
        summary[key]["total"] += row["amount"]

    sorted_items = sorted(
        summary.items(),
        key=lambda kv: abs(kv[1]["total"]),
        reverse=True,
    )

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([key_name, "count", "total_withdrawn"])
        for key, stats in sorted_items:
            writer.writerow(
                [
                    key,
                    stats["count"],
                    f"{stats['total']:.2f}",
                ]
            )


def main():
    args = parse_args()
    pdf_path = args.pdf_path

    transactions_csv = "withdrawals_csv_style.csv"
    raw_grouped_csv = "withdrawals_grouped_by_payee.csv"
    normalized_grouped_csv = "withdrawals_grouped_by_normalized_payee.csv"

    full_text = extract_pdf_text(pdf_path)
    transactions_text, descriptions_text = split_sections(full_text)

    transactions = extract_transactions(transactions_text)
    descriptions = extract_descriptions(descriptions_text)

    if len(transactions) != len(descriptions):
        raise ValueError(
            f"Count mismatch: found {len(transactions)} withdrawal rows but "
            f"{len(descriptions)} descriptions."
        )

    for row, desc in zip(transactions, descriptions):
        row["payee"] = desc
        row["normalized_payee"] = normalize_payee(desc)

    write_transactions_csv(transactions, transactions_csv)
    write_grouped_csv(transactions, "payee", raw_grouped_csv)
    write_grouped_csv(transactions, "normalized_payee", normalized_grouped_csv)

    total = sum(row["amount"] for row in transactions)

    print(f"Parsed {len(transactions)} withdrawals")
    print(f"Total withdrawals: {total:.2f}")
    print(f"Wrote: {transactions_csv}")
    print(f"Wrote: {raw_grouped_csv}")
    print(f"Wrote: {normalized_grouped_csv}")


if __name__ == "__main__":
    main()
