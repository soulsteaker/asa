"""
Simple Budget System - Your Actual Formula

Core Formula:
1. Paycheck - Bills = Leftover
2. Save half of Leftover → Safe
3. Other half → Pocket Pool, divide by days = daily allowance
4. Each day:
   - pocket + daily = new pocket
   - spendable = pocket / 4
   - remaining = pocket - spendable (or pocket * 3/4)
5. End of pay period: sweep remaining → Safe
"""

from datetime import datetime, timedelta
from typing import List
import math


class SimpleBudget:
    """Your actual budget system with 1/4 spendable rule"""

    def __init__(
        self,
        paycheck_amount: float,
        bills_per_paycheck: float,
        days_per_paycheck: int,
        save_fraction: float = 0.5,
        annual_return: float = 0.05
    ):
        self.paycheck_amount = paycheck_amount
        self.bills_per_paycheck = bills_per_paycheck
        self.days_per_paycheck = days_per_paycheck
        self.save_fraction = save_fraction
        self.annual_return = annual_return

        # Calculate daily allowance
        leftover = paycheck_amount - bills_per_paycheck
        spend_pool = leftover * (1 - save_fraction)
        self.daily = spend_pool / days_per_paycheck

        # Balances
        self.safe = leftover * save_fraction  # Initial save
        self.pocket = 0.0
        self.emergency = 0.0

        # History
        self.days: List[dict] = []

    def run_day(self, day_num: int, actual_spent: float = None) -> dict:
        """
        Run one day of the budget

        Args:
            day_num: Day number (1-indexed)
            actual_spent: How much you actually spent (if None, uses spendable amount)

        Returns:
            Dictionary with day's results
        """
        # Add daily allowance to pocket
        self.pocket += self.daily

        # Calculate spendable (1/4 of pocket)
        spendable = self.pocket / 4

        # Determine actual spending
        if actual_spent is None:
            actual_spent = spendable

        # Spend it
        self.pocket -= actual_spent
        remaining = self.pocket

        # Apply daily growth to safe
        daily_rate = math.pow(1 + self.annual_return, 1/365) - 1
        self.safe *= (1 + daily_rate)

        # Record
        day_record = {
            'day': day_num,
            'daily_added': self.daily,
            'pocket_before_spend': self.pocket + actual_spent,
            'spendable': spendable,
            'actual_spent': actual_spent,
            'remaining': remaining,
            'safe': self.safe,
            'total': self.safe + remaining
        }
        self.days.append(day_record)

        return day_record

    def end_of_period(self):
        """End of pay period: sweep pocket to safe, get new paycheck"""
        # Sweep remaining pocket to safe
        self.safe += self.pocket
        self.pocket = 0.0

        # New paycheck
        leftover = self.paycheck_amount - self.bills_per_paycheck
        self.safe += leftover * self.save_fraction

    def print_day(self, day_record: dict):
        """Print a day's activity"""
        print(f"Day {day_record['day']}: "
              f"Pocket ${day_record['pocket_before_spend']:.2f} "
              f"→ Spendable ${day_record['spendable']:.2f} "
              f"→ Spent ${day_record['actual_spent']:.2f} "
              f"→ Remaining ${day_record['remaining']:.2f} | "
              f"Safe ${day_record['safe']:.2f}")


def verify_your_example():
    """Verify against your manual calculation"""
    print("=" * 70)
    print("YOUR EXAMPLE VERIFICATION")
    print("=" * 70)
    print("\nParameters:")
    print("  Weekly paycheck: $200")
    print("  Daily: $200/7 = $28.571")
    print("  Subtract emergency: $28.571 - $3.571 = $25/day")
    print("  Formula: pocket + $25, then 1/4 is spendable\n")

    daily = 25.0
    pocket = 0.0

    print("Manual calculation:")

    # Day 1
    pocket += daily  # pocket = 25
    spendable = pocket / 4  # 6.25
    pocket -= spendable  # 18.75
    print(f"Day 1: pocket+daily={pocket+spendable:.2f}, spendable={spendable:.2f}, remaining={pocket:.2f}")

    # Day 2
    pocket += daily  # 18.75 + 25 = 43.75
    spendable = pocket / 4  # 10.9375
    pocket -= spendable  # 32.8125
    print(f"Day 2: pocket+daily={pocket+spendable:.2f}, spendable={spendable:.2f}, remaining={pocket:.2f}")

    # Day 3
    pocket += daily  # 32.8125 + 25 = 57.8125
    spendable = pocket / 4  # 14.453125
    pocket -= spendable  # 43.359375
    print(f"Day 3: pocket+daily={pocket+spendable:.2f}, spendable={spendable:.2f}, remaining={pocket:.2f}")

    print("\n" + "=" * 70)


def run_biweekly_example():
    """Run your 2k biweekly example"""
    print("\n" + "=" * 70)
    print("BIWEEKLY $2000 PAYCHECK EXAMPLE")
    print("=" * 70)

    budget = SimpleBudget(
        paycheck_amount=2000.0,
        bills_per_paycheck=500.0,
        days_per_paycheck=14,
        save_fraction=0.5,
        annual_return=0.05
    )

    print(f"\nLeftover after bills: ${budget.paycheck_amount - budget.bills_per_paycheck:.2f}")
    print(f"Saved to Safe: ${budget.safe:.2f}")
    print(f"Daily allowance: ${budget.daily:.2f}")
    print(f"\nRunning first 7 days (spending $30/day):\n")

    for day in range(1, 8):
        record = budget.run_day(day, actual_spent=30.0)
        budget.print_day(record)

    print(f"\nAfter 7 days:")
    print(f"  Pocket: ${budget.pocket:.2f}")
    print(f"  Safe: ${budget.safe:.2f}")
    print(f"  Total: ${budget.pocket + budget.safe:.2f}")


if __name__ == "__main__":
    verify_your_example()
    run_biweekly_example()
