#!/usr/bin/env python3
"""
Budget System with Emergency Fund from Rounding
Tracks the "change" from rounding daily allowance as a separate emergency fund
"""

from datetime import datetime, timedelta
from typing import List
import math


class BudgetWithEmergency:
    """Budget tracker with emergency fund from rounding"""

    def __init__(
        self,
        paycheck: float,
        bills: float,
        days_between_checks: int,
        save_fraction: float = 0.5,
        daily_rounding: float = None,  # e.g., 50.00 to round to nearest $50
        annual_return: float = 0.05
    ):
        self.paycheck = paycheck
        self.bills = bills
        self.days_between_checks = days_between_checks
        self.save_fraction = save_fraction
        self.annual_return = annual_return

        # Calculate daily allowance
        leftover = paycheck - bills
        spend_pool = leftover * (1 - save_fraction)
        self.daily_exact = spend_pool / days_between_checks

        # Apply rounding for emergency fund
        if daily_rounding is not None:
            self.daily_actual = daily_rounding
        else:
            # Default: round to nearest cent
            self.daily_actual = round(self.daily_exact, 2)

        # Emergency comes from the rounding difference
        self.daily_emergency = self.daily_exact - self.daily_actual

        # Balances
        self.safe = 0.0
        self.pocket = 0.0
        self.emergency = 0.0

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
            spending: How much to spend

        Returns:
            Day record
        """
        # Add daily to pocket (rounded amount)
        self.pocket += self.daily_actual

        # Add emergency fund from rounding
        self.emergency += self.daily_emergency

        # Spendable is 1/4 of pocket
        spendable = self.pocket / 4

        # Spend (can't spend more than you have)
        spent = min(spending, self.pocket)
        self.pocket -= spent

        # Apply growth to safe and emergency fund
        daily_rate = math.pow(1 + self.annual_return, 1/365) - 1
        if self.safe > 0:
            self.safe *= (1 + daily_rate)
        if self.emergency > 0:
            self.emergency *= (1 + daily_rate)

        record = {
            'date': date,
            'daily_actual': self.daily_actual,
            'daily_emergency': self.daily_emergency,
            'spendable': spendable,
            'spent': spent,
            'pocket': self.pocket,
            'safe': self.safe,
            'emergency': self.emergency,
            'total': self.pocket + self.safe + self.emergency
        }
        self.days_log.append(record)
        return record


def run_emergency_simulation(
    start: datetime,
    end: datetime,
    paycheck_amount: float,
    bills_per_check: float,
    days_between_checks: int,
    first_paycheck_date: datetime,
    daily_spending: float,
    save_frac: float = 0.5,
    daily_rounding: float = None
):
    """Run simulation with emergency fund tracking"""

    sim = BudgetWithEmergency(
        paycheck=paycheck_amount,
        bills=bills_per_check,
        days_between_checks=days_between_checks,
        save_fraction=save_frac,
        daily_rounding=daily_rounding,
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


def print_monthly_summary(sim: BudgetWithEmergency):
    """Print monthly summary with emergency fund"""
    monthly = {}

    for record in sim.days_log:
        month_key = (record['date'].year, record['date'].month)

        if month_key not in monthly:
            monthly[month_key] = {
                'month': record['date'].strftime('%B %Y'),
                'days': 0,
                'spent': 0,
                'emergency_added': 0,
                'end_pocket': 0,
                'end_safe': 0,
                'end_emergency': 0
            }

        m = monthly[month_key]
        m['days'] += 1
        m['spent'] += record['spent']
        m['emergency_added'] += record['daily_emergency']
        m['end_pocket'] = record['pocket']
        m['end_safe'] = record['safe']
        m['end_emergency'] = record['emergency']

    print("\n" + "=" * 115)
    print("MONTHLY SUMMARY WITH EMERGENCY FUND")
    print("=" * 115)
    print(f"{'Month':<15} {'Days':<6} {'Spent':<12} {'Emerg+':<12} {'Pocket':<12} {'Safe':<14} {'Emergency':<14} {'Total':<14}")
    print("-" * 115)

    for key in sorted(monthly.keys()):
        m = monthly[key]
        total = m['end_pocket'] + m['end_safe'] + m['end_emergency']

        print(f"{m['month']:<15} {m['days']:<6} "
              f"${m['spent']:>9,.2f}  "
              f"${m['emergency_added']:>9,.2f}  "
              f"${m['end_pocket']:>9,.2f}  "
              f"${m['end_safe']:>11,.2f}  "
              f"${m['end_emergency']:>11,.2f}  "
              f"${total:>11,.2f}")

    print("=" * 115)


def compare_rounding_strategies():
    """Compare different rounding amounts for emergency fund"""
    print("=" * 115)
    print("EMERGENCY FUND COMPARISON: DIFFERENT ROUNDING STRATEGIES")
    print("Jan 1 - June 30, 2026 | $2000 biweekly | $500 bills | 50% save | $30/day spending")
    print("=" * 115)

    # Exact daily is $53.571428...
    # Let's test different rounding strategies
    strategies = [
        {"name": "No rounding (exact)", "round_to": 53.571428},
        {"name": "Round to cent", "round_to": 53.57},
        {"name": "Round to dollar", "round_to": 53.00},
        {"name": "Round to $50", "round_to": 50.00},
        {"name": "Round to $45", "round_to": 45.00},
        {"name": "Round to $40", "round_to": 40.00},
    ]

    results = []

    for strategy in strategies:
        sim = run_emergency_simulation(
            start=datetime(2026, 1, 1),
            end=datetime(2026, 6, 30),
            paycheck_amount=2000.0,
            bills_per_check=500.0,
            days_between_checks=14,
            first_paycheck_date=datetime(2026, 1, 3),
            daily_spending=30.0,
            save_frac=0.5,
            daily_rounding=strategy["round_to"]
        )

        total_spent = sum(d['spent'] for d in sim.days_log)

        results.append({
            'name': strategy['name'],
            'daily': strategy['round_to'],
            'emergency_per_day': sim.daily_emergency,
            'total_spent': total_spent,
            'safe': sim.safe,
            'emergency': sim.emergency,
            'pocket': sim.pocket,
            'total': sim.safe + sim.emergency + sim.pocket
        })

    # Print table
    print(f"\n{'Strategy':<25} {'Daily':<10} {'Emerg/Day':<12} {'Emergency':<14} {'Safe':<14} {'Total':<14}")
    print("-" * 115)

    for r in results:
        print(f"{r['name']:<25} "
              f"${r['daily']:>7.2f}  "
              f"${r['emergency_per_day']:>9.2f}  "
              f"${r['emergency']:>11,.2f}  "
              f"${r['safe']:>11,.2f}  "
              f"${r['total']:>11,.2f}")

    print("=" * 115)

    # Show annual projection
    print("\n" + "=" * 80)
    print("ANNUAL EMERGENCY FUND PROJECTION (26 paychecks/year)")
    print("=" * 80)
    print(f"{'Strategy':<25} {'Per Paycheck':<16} {'Annual (no growth)':<20} {'6mo Actual':<14}")
    print("-" * 80)

    for r in results:
        per_paycheck = r['emergency_per_day'] * 14
        annual_no_growth = per_paycheck * 26
        six_month_actual = r['emergency']

        print(f"{r['name']:<25} "
              f"${per_paycheck:>13.2f}  "
              f"${annual_no_growth:>17.2f}  "
              f"${six_month_actual:>11,.2f}")

    print("=" * 80)


def main():
    print("=" * 115)
    print("BUDGET WITH EMERGENCY FUND FROM ROUNDING")
    print("=" * 115)

    # Example: Round to $50/day instead of $53.57
    print("\nExample: Round daily to $50 (from $53.571428)")
    print("Emergency fund = $53.571428 - $50.00 = $3.571428 per day\n")

    sim = run_emergency_simulation(
        start=datetime(2026, 1, 1),
        end=datetime(2026, 6, 30),
        paycheck_amount=2000.0,
        bills_per_check=500.0,
        days_between_checks=14,
        first_paycheck_date=datetime(2026, 1, 3),
        daily_spending=30.0,
        save_frac=0.5,
        daily_rounding=50.00
    )

    print_monthly_summary(sim)

    print(f"\n{'='*115}")
    print(f"FINAL TOTALS (as of June 30, 2026)")
    print(f"{'='*115}")
    print(f"Total Paychecks: {sim.total_paychecks}")
    print(f"Total Days: {len(sim.days_log)}")
    print(f"Daily Allowance (exact): ${sim.daily_exact:.6f}")
    print(f"Daily Allowance (actual): ${sim.daily_actual:.2f}")
    print(f"Emergency per day: ${sim.daily_emergency:.6f}")
    print()
    print(f"Safe Balance: ${sim.safe:,.2f}")
    print(f"Emergency Fund: ${sim.emergency:,.2f}")
    print(f"Pocket Balance: ${sim.pocket:,.2f}")
    print(f"Total Net Worth: ${sim.safe + sim.emergency + sim.pocket:,.2f}")
    print(f"{'='*115}\n")

    # Compare strategies
    compare_rounding_strategies()

    # Show the math
    print("\n" + "=" * 80)
    print("HOW THE EMERGENCY FUND WORKS")
    print("=" * 80)
    print("""
The emergency fund comes from the rounding "change":

Example: $2000 paycheck, $500 bills, 50% save, 14 days
  Exact daily = ($2000 - $500) × 0.5 ÷ 14 = $53.571428

If you round to $50/day:
  Emergency per day = $53.571428 - $50.00 = $3.571428
  Per paycheck (14 days) = $3.571428 × 14 = $50.00
  Per year (26 paychecks) = $50.00 × 26 = $1,300.00

Over 6 months with 5% compound growth:
  Emergency fund grows to $646.71 (from $650 contributions + growth)

This money sits SEPARATELY for true emergencies:
  - Car repair
  - Medical bills
  - Unexpected expenses

It grows at 5% annually just like your Safe balance!
    """)
    print("=" * 80)


if __name__ == "__main__":
    main()
