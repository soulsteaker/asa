#!/usr/bin/env python3
"""
January to June Budget Simulation
Using your actual 1/4 spendable formula
"""

from datetime import datetime, timedelta
import math


class BudgetSim:
    """Budget simulator with your actual formula"""

    def __init__(
        self,
        paycheck: float,
        bills: float,
        days_between_checks: int,
        save_fraction: float = 0.5,
        annual_return: float = 0.05
    ):
        self.paycheck = paycheck
        self.bills = bills
        self.days_between_checks = days_between_checks
        self.save_fraction = save_fraction
        self.annual_return = annual_return

        # Calculate daily allowance
        leftover = paycheck - bills
        self.daily = (leftover * (1 - save_fraction)) / days_between_checks

        # Balances
        self.safe = 0.0
        self.pocket = 0.0

        # Tracking
        self.total_paychecks = 0
        self.days_log = []

    def process_paycheck(self):
        """Process a paycheck"""
        leftover = self.paycheck - self.bills
        saved = leftover * self.save_fraction

        # Sweep pocket to safe
        self.safe += self.pocket
        self.pocket = 0.0

        # Add saved amount
        self.safe += saved
        self.total_paychecks += 1

    def run_day(self, date: datetime, spending: float) -> dict:
        """
        Run one day

        Args:
            date: Date
            spending: How much to spend (use 1/4 rule or actual amount)

        Returns:
            Day record
        """
        # Add daily to pocket
        self.pocket += self.daily

        # Spendable is 1/4 of pocket
        spendable = self.pocket / 4

        # Spend (can override with actual spending)
        spent = min(spending, self.pocket)  # Can't spend more than you have
        self.pocket -= spent

        # Apply growth to safe
        daily_rate = math.pow(1 + self.annual_return, 1/365) - 1
        if self.safe > 0:
            self.safe *= (1 + daily_rate)

        record = {
            'date': date,
            'daily': self.daily,
            'spendable': spendable,
            'spent': spent,
            'pocket': self.pocket,
            'safe': self.safe,
            'total': self.pocket + self.safe
        }
        self.days_log.append(record)
        return record


def run_simulation(
    start: datetime,
    end: datetime,
    paycheck_amount: float,
    bills_per_check: float,
    days_between_checks: int,
    first_paycheck_date: datetime,
    daily_spending: float,
    save_frac: float = 0.5
):
    """Run full simulation"""

    sim = BudgetSim(
        paycheck=paycheck_amount,
        bills=bills_per_check,
        days_between_checks=days_between_checks,
        save_fraction=save_frac,
        annual_return=0.05
    )

    # Process first paycheck
    sim.process_paycheck()

    # Track paycheck dates
    current_date = start
    next_paycheck = first_paycheck_date + timedelta(days=days_between_checks)
    days_until_paycheck = (next_paycheck - current_date).days

    while current_date <= end:
        # Check for paycheck
        if days_until_paycheck == 0:
            sim.process_paycheck()
            next_paycheck += timedelta(days=days_between_checks)
            days_until_paycheck = days_between_checks

        # Run day
        sim.run_day(current_date, daily_spending)

        # Next day
        current_date += timedelta(days=1)
        days_until_paycheck -= 1

    # Final sweep
    sim.safe += sim.pocket
    sim.pocket = 0

    return sim


def print_monthly_summary(sim: BudgetSim):
    """Print monthly summary"""
    monthly = {}

    for record in sim.days_log:
        month_key = (record['date'].year, record['date'].month)

        if month_key not in monthly:
            monthly[month_key] = {
                'month': record['date'].strftime('%B %Y'),
                'days': 0,
                'spent': 0,
                'end_pocket': 0,
                'end_safe': 0
            }

        m = monthly[month_key]
        m['days'] += 1
        m['spent'] += record['spent']
        m['end_pocket'] = record['pocket']
        m['end_safe'] = record['safe']

    print("\n" + "=" * 100)
    print("MONTHLY SUMMARY")
    print("=" * 100)
    print(f"{'Month':<15} {'Days':<8} {'Total Spent':<15} {'Avg/Day':<12} {'Pocket':<15} {'Safe':<15} {'Total':<15}")
    print("-" * 100)

    for key in sorted(monthly.keys()):
        m = monthly[key]
        avg = m['spent'] / m['days']
        total = m['end_pocket'] + m['end_safe']

        print(f"{m['month']:<15} {m['days']:<8} "
              f"${m['spent']:>12,.2f}  "
              f"${avg:>9,.2f}  "
              f"${m['end_pocket']:>12,.2f}  "
              f"${m['end_safe']:>12,.2f}  "
              f"${total:>12,.2f}")

    print("=" * 100)


def main():
    print("=" * 100)
    print("BUDGET SIMULATION: JANUARY - JUNE 2026")
    print("Using your actual formula: pocket + daily, spendable = pocket/4")
    print("=" * 100)

    # Parameters
    paycheck = 2000.0
    bills = 500.0
    save_frac = 0.5

    print(f"\nPaycheck: ${paycheck:,.2f} (biweekly)")
    print(f"Bills: ${bills:,.2f} per paycheck")
    print(f"Leftover: ${paycheck - bills:,.2f}")
    print(f"Save {save_frac*100:.0f}%: ${(paycheck-bills)*save_frac:,.2f} → Safe")
    print(f"Spend pool: ${(paycheck-bills)*(1-save_frac):,.2f}")
    print(f"Daily allowance: ${(paycheck-bills)*(1-save_frac)/14:.2f}")
    print(f"Daily spending: $30.00 (constant)")

    # Run simulation
    sim = run_simulation(
        start=datetime(2026, 1, 1),
        end=datetime(2026, 6, 30),
        paycheck_amount=paycheck,
        bills_per_check=bills,
        days_between_checks=14,
        first_paycheck_date=datetime(2026, 1, 3),
        daily_spending=30.0,
        save_frac=save_frac
    )

    # Print results
    print_monthly_summary(sim)

    print(f"\n{'='*100}")
    print(f"FINAL TOTALS (as of June 30, 2026)")
    print(f"{'='*100}")
    print(f"Total Paychecks: {sim.total_paychecks}")
    print(f"Total Days: {len(sim.days_log)}")
    print(f"Safe Balance: ${sim.safe:,.2f}")
    print(f"Pocket Balance: ${sim.pocket:,.2f}")
    print(f"Total Net Worth: ${sim.safe + sim.pocket:,.2f}")
    print(f"{'='*100}\n")

    # Show first week detail
    print("=" * 100)
    print("FIRST WEEK DETAIL")
    print("=" * 100)
    print(f"{'Date':<12} {'Daily':<10} {'Spendable':<12} {'Spent':<10} {'Pocket':<12} {'Safe':<15}")
    print("-" * 100)

    for record in sim.days_log[:7]:
        print(f"{record['date'].strftime('%Y-%m-%d'):<12} "
              f"${record['daily']:>7.2f}  "
              f"${record['spendable']:>9.2f}  "
              f"${record['spent']:>7.2f}  "
              f"${record['pocket']:>9.2f}  "
              f"${record['safe']:>12,.2f}")

    print("=" * 100)


if __name__ == "__main__":
    main()
