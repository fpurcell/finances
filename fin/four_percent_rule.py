#!/usr/bin/env python3

import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Retirement projection with optional overrides for starting balance, "
            "starting age, growth rate, withdrawal rate, and inflation."
        )
    )
    parser.add_argument(
        "--balance",
        type=float,
        default=1_500_000,
        help="Starting balance in dollars (default: 1500000)",
    )
    parser.add_argument(
        "--age",
        type=int,
        default=59,
        help="Starting age (default: 59)",
    )
    parser.add_argument(
        "--growth",
        type=float,
        default=3.2,
        help="Annual growth rate in percent (default: 3.2)",
    )
    parser.add_argument(
        "--withdrawal",
        type=float,
        default=4.0,
        help="Annual withdrawal rate in percent of starting balance (default: 4.0)",
    )
    parser.add_argument(
        "--inflation",
        type=float,
        default=3.0,
        help="Annual inflation rate in percent for increasing withdrawals (default: 3.0)",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=10,
        help="Number of years to project (default: 10)",
    )
    return parser.parse_args()


def money(value: float) -> str:
    return f"${value:,.2f}"


def main():
    args = parse_args()

    starting_balance = args.balance
    starting_age = args.age
    growth_rate = args.growth / 100.0
    withdrawal_rate = args.withdrawal / 100.0
    inflation_rate = args.inflation / 100.0
    years = args.years

    first_year_withdrawal = starting_balance * withdrawal_rate
    balance = starting_balance
    current_withdrawal = first_year_withdrawal

    print()
    print("Retirement Projection")
    print("---------------------")
    print(f"Starting balance: {money(starting_balance)}")
    print(f"Starting age: {starting_age}")
    print(f"Growth rate: {args.growth:.2f}%")
    print(f"Withdrawal rate: {args.withdrawal:.2f}%")
    print(f"Inflation rate: {args.inflation:.2f}%")
    print(f"First-year withdrawal: {money(first_year_withdrawal)}")
    print(f"Years: {years}")
    print()

    header = (
        f"{'Year':>4}  {'Age':>3}  {'Start Balance':>15}  "
        f"{'Growth':>12}  {'Withdrawal':>12}  {'End Balance':>15}"
    )
    print(header)
    print("-" * len(header))

    for year in range(1, years + 1):
        age = starting_age + year - 1
        start_balance = balance
        growth = start_balance * growth_rate
        end_balance = start_balance + growth - current_withdrawal

        print(
            f"{year:>4}  {age:>3}  {money(start_balance):>15}  "
            f"{money(growth):>12}  {money(current_withdrawal):>12}  "
            f"{money(end_balance):>15}"
        )

        balance = end_balance
        current_withdrawal *= (1 + inflation_rate)

    print()
    print(f"Ending balance after {years} years: {money(balance)}")


if __name__ == "__main__":
    main()
