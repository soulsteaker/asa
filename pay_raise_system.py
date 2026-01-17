#!/usr/bin/env python3
"""
Self-Funding Pay Raise System
Gives yourself automatic raises from your Safe balance growth
"""

from datetime import datetime, timedelta
from typing import List
import math


class BudgetWithRaises:
    """Budget tracker with self-funding raises from Safe balance"""

    def __init__(
        self,
        paycheck: float,
        bills: float,
        days_between_checks: int,
        save_fraction: float = 0.5,
        raise_strategy: str = "growth_only",  # "growth_only", "percentage", or "combined"
        raise_percentage: float = 0.05,  # 5% of Safe per year
        annual_return: float = 0.05
    ):
        self.paycheck = paycheck
        self.bills = bills
        self.days_between_checks = days_between_checks
        self.save_fraction = save_fraction
        self.raise_strategy = raise_strategy
        self.raise_percentage = raise_percentage
        self.annual_return = annual_return
        self.paychecks_per_year = 26  # biweekly

        # Calculate initial daily allowance
        leftover = paycheck - bills
        spend_pool = leftover * (1 - save_fraction)
        self.base_daily = spend_pool / days_between_checks

        # Current daily (starts at base, increases with raises)
        self.daily = self.base_daily

        # Balances
        self.safe = 0.0
        self.pocket = 0.0

        # Tracking
        self.total_paychecks = 0
        self.total_raises_given = 0.0
        self.days_log = []
        self.paycheck_log = []

    def calculate_raise(self) -> float:
        """
        Calculate raise based on Safe balance and strategy

        Returns:
            Raise amount to add to this paycheck's spend pool
        """
        if self.safe <= 0:
            return 0.0

        if self.raise_strategy == "growth_only":
            # Use only the annual growth
            annual_growth = self.safe * self.annual_return
            raise_per_check = annual_growth / self.paychecks_per_year

        elif self.raise_strategy == "percentage":
            # Use percentage of Safe balance
            annual_raise = self.safe * self.raise_percentage
            raise_per_check = annual_raise / self.paychecks_per_year

        elif self.raise_strategy == "combined":
            # Use growth + percentage
            annual_growth = self.safe * self.annual_return
            annual_percentage = self.safe * self.raise_percentage
            total_annual = annual_growth + annual_percentage
            raise_per_check = total_annual / self.paychecks_per_year

        else:
            raise_per_check = 0.0

        return raise_per_check

    def process_paycheck(self):
        """Process a paycheck with automatic raise"""
        # Calculate raise from Safe balance
        raise_amount = self.calculate_raise()

        # Sweep pocket to safe
        self.safe += self.pocket
        self.pocket = 0.0

        # Process regular paycheck
        leftover = self.paycheck - self.bills
        saved = leftover * self.save_fraction

        # Add saved amount to Safe
        self.safe += saved

        # Spend pool includes raise
        spend_pool = (leftover * (1 - self.save_fraction)) + raise_amount

        # Update daily allowance
        self.daily = spend_pool / self.days_between_checks

        # Track
        self.total_paychecks += 1
        self.total_raises_given += raise_amount

        self.paycheck_log.append({
            'paycheck_num': self.total_paychecks,
            'safe_before': self.safe - saved,
            'raise_amount': raise_amount,
            'new_daily': self.daily,
            'safe_after': self.safe
        })

    def run_day(self, date: datetime, spending: float) -> dict:
        """Run one day"""
        # Add daily to pocket
        self.pocket += self.daily

        # Spendable is 1/4 of pocket
        spendable = self.pocket / 4

        # Spend
        spent = min(spending, self.pocket)
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


def run_raise_simulation(
    months: int,
    paycheck_amount: float,
    bills_per_check: float,
    daily_spending: float,
    raise_strategy: str = "growth_only",
    raise_percentage: float = 0.05,
    save_frac: float = 0.5
):
    """Run simulation with automatic raises"""

    start = datetime(2026, 1, 1)
    end = start + timedelta(days=months * 30)
    first_paycheck = datetime(2026, 1, 3)

    sim = BudgetWithRaises(
        paycheck=paycheck_amount,
        bills=bills_per_check,
        days_between_checks=14,
        save_fraction=save_frac,
        raise_strategy=raise_strategy,
        raise_percentage=raise_percentage,
        annual_return=0.05
    )

    # Process first paycheck
    sim.process_paycheck()

    # Simulate
    current_date = start
    next_paycheck = first_paycheck + timedelta(days=14)
    days_until_paycheck = (next_paycheck - current_date).days

    while current_date <= end:
        # Check for paycheck
        if days_until_paycheck == 0:
            sim.process_paycheck()
            next_paycheck += timedelta(days=14)
            days_until_paycheck = 14

        # Run day
        sim.run_day(current_date, daily_spending)

        # Next day
        current_date += timedelta(days=1)
        days_until_paycheck -= 1

    # Final sweep
    sim.safe += sim.pocket
    sim.pocket = 0

    return sim


def print_paycheck_progression(sim: BudgetWithRaises):
    """Print how raises progressed over paychecks"""
    print("\n" + "=" * 100)
    print("PAYCHECK PROGRESSION (showing raises)")
    print("=" * 100)
    print(f"{'Check #':<10} {'Safe Before':<15} {'Raise':<12} {'New Daily':<12} {'Safe After':<15} {'Daily +%':<12}")
    print("-" * 100)

    base_daily = sim.base_daily

    for i, log in enumerate(sim.paycheck_log):
        if i < 15 or i >= len(sim.paycheck_log) - 5:  # Show first 15 and last 5
            daily_increase_pct = ((log['new_daily'] - base_daily) / base_daily) * 100
            print(f"{log['paycheck_num']:<10} "
                  f"${log['safe_before']:>12,.2f}  "
                  f"${log['raise_amount']:>9,.2f}  "
                  f"${log['new_daily']:>9.2f}  "
                  f"${log['safe_after']:>12,.2f}  "
                  f"{daily_increase_pct:>+9.1f}%")
        elif i == 15:
            print("   ...")

    print("=" * 100)


def compare_raise_strategies():
    """Compare different raise strategies over 12 months"""
    print("=" * 100)
    print("SELF-FUNDING RAISE SYSTEM COMPARISON")
    print("12 months | $1500 biweekly | $500 bills | $30/day spending")
    print("=" * 100)

    strategies = [
        {"name": "No Raises (baseline)", "strategy": None, "pct": 0.0},
        {"name": "Growth Only (5%)", "strategy": "growth_only", "pct": 0.05},
        {"name": "5% of Safe", "strategy": "percentage", "pct": 0.05},
        {"name": "10% of Safe", "strategy": "percentage", "pct": 0.10},
        {"name": "Growth + 5%", "strategy": "combined", "pct": 0.05},
    ]

    results = []

    for strat in strategies:
        if strat["strategy"] is None:
            # Baseline without raises
            from run_jan_to_june import run_simulation
            sim_base = run_simulation(
                start=datetime(2026, 1, 1),
                end=datetime(2026, 12, 31),
                paycheck_amount=1500.0,
                bills_per_check=500.0,
                days_between_checks=14,
                first_paycheck_date=datetime(2026, 1, 3),
                daily_spending=30.0,
                save_frac=0.5
            )

            results.append({
                'name': strat['name'],
                'final_safe': sim_base.safe,
                'final_total': sim_base.safe + sim_base.pocket,
                'total_raises': 0.0,
                'final_daily': 1500.0 * 0.5 / 14  # constant
            })
        else:
            sim = run_raise_simulation(
                months=12,
                paycheck_amount=1500.0,
                bills_per_check=500.0,
                daily_spending=30.0,
                raise_strategy=strat["strategy"],
                raise_percentage=strat["pct"],
                save_frac=0.5
            )

            results.append({
                'name': strat['name'],
                'final_safe': sim.safe,
                'final_total': sim.safe + sim.pocket,
                'total_raises': sim.total_raises_given,
                'final_daily': sim.daily,
                'sim': sim
            })

    # Print comparison
    print(f"\n{'Strategy':<25} {'Final Safe':<15} {'Total Raises':<15} {'Final Daily':<12} {'Total Worth':<15}")
    print("-" * 100)

    baseline_worth = results[0]['final_total']

    for r in results:
        worth_diff = r['final_total'] - baseline_worth
        print(f"{r['name']:<25} "
              f"${r['final_safe']:>12,.2f}  "
              f"${r['total_raises']:>12,.2f}  "
              f"${r['final_daily']:>9.2f}  "
              f"${r['final_total']:>12,.2f} ({worth_diff:+,.0f})")

    print("=" * 100)

    # Show detailed progression for "Growth Only"
    print("\n\n")
    print("*" * 100)
    print("DETAILED EXAMPLE: GROWTH ONLY STRATEGY")
    print("*" * 100)

    growth_only_sim = results[1]['sim']
    print_paycheck_progression(growth_only_sim)

    print("\n" + "=" * 100)
    print("HOW IT WORKS: GROWTH ONLY")
    print("=" * 100)
    print(f"""
Your Safe grows at 5% annually. Each paycheck, you take that year's growth
and spread it across 26 paychecks to give yourself a raise.

Example:
  Paycheck 1:  Safe = $500,   Growth = $25/year  → Raise = $25/26 = $0.96
  Paycheck 6:  Safe = $3,000, Growth = $150/year → Raise = $150/26 = $5.77
  Paycheck 13: Safe = $6,500, Growth = $325/year → Raise = $325/26 = $12.50
  Paycheck 26: Safe = $13,000, Growth = $650/year → Raise = $650/26 = $25.00

By end of year, your daily allowance went from ${growth_only_sim.base_daily:.2f}
to ${growth_only_sim.daily:.2f} (+{((growth_only_sim.daily/growth_only_sim.base_daily - 1)*100):.1f}%)

And your Safe balance is ${growth_only_sim.safe:,.2f}!

This is SUSTAINABLE because you're only spending what Safe earned in growth.
Safe keeps growing, raises keep coming!
    """)
    print("=" * 100)


def main():
    compare_raise_strategies()


if __name__ == "__main__":
    main()
