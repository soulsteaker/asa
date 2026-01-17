#!/usr/bin/env python3
"""
Compare different save fractions and spending levels
"""

from run_jan_to_june import BudgetSim, run_simulation
from datetime import datetime


def compare_save_fractions():
    """Compare different save percentages"""
    print("=" * 100)
    print("SCENARIO COMPARISON: DIFFERENT SAVE PERCENTAGES")
    print("Jan 1 - June 30, 2026 | $2000 biweekly | $500 bills | $30/day spending")
    print("=" * 100)

    save_fractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    results = []

    for save_frac in save_fractions:
        sim = run_simulation(
            start=datetime(2026, 1, 1),
            end=datetime(2026, 6, 30),
            paycheck_amount=2000.0,
            bills_per_check=500.0,
            days_between_checks=14,
            first_paycheck_date=datetime(2026, 1, 3),
            daily_spending=30.0,
            save_frac=save_frac
        )

        total_spent = sum(d['spent'] for d in sim.days_log)
        final_worth = sim.safe + sim.pocket

        results.append({
            'save_pct': save_frac * 100,
            'daily': sim.daily,
            'total_spent': total_spent,
            'safe': sim.safe,
            'pocket': sim.pocket,
            'total': final_worth
        })

    # Print table
    print(f"\n{'Save %':<10} {'Daily':<12} {'Total Spent':<15} {'Safe':<15} {'Pocket':<12} {'Total':<15}")
    print("-" * 100)

    for r in results:
        print(f"{r['save_pct']:>6.0f}%   "
              f"${r['daily']:>9.2f}  "
              f"${r['total_spent']:>12,.2f}  "
              f"${r['safe']:>12,.2f}  "
              f"${r['pocket']:>9,.2f}  "
              f"${r['total']:>12,.2f}")

    print("=" * 100)

    # Show growth percentages
    baseline = results[4]  # 50%
    print(f"\nCompared to baseline (50% save rate, Net Worth ${baseline['total']:,.2f}):")
    print("-" * 70)

    for r in results:
        if r['save_pct'] == 50:
            continue
        diff = r['total'] - baseline['total']
        pct_change = (diff / baseline['total']) * 100
        print(f"  {r['save_pct']:>3.0f}% save: ${diff:>+10,.2f} ({pct_change:>+6.2f}%)")

    print()


def compare_spending_levels():
    """Compare different daily spending amounts"""
    print("\n" + "=" * 100)
    print("SCENARIO COMPARISON: DIFFERENT SPENDING LEVELS")
    print("Jan 1 - June 30, 2026 | $2000 biweekly | $500 bills | 50% save")
    print("=" * 100)

    spending_levels = [20, 30, 40, 50, 53.57]  # 53.57 is the daily allowance
    results = []

    for spending in spending_levels:
        sim = run_simulation(
            start=datetime(2026, 1, 1),
            end=datetime(2026, 6, 30),
            paycheck_amount=2000.0,
            bills_per_check=500.0,
            days_between_checks=14,
            first_paycheck_date=datetime(2026, 1, 3),
            daily_spending=spending,
            save_frac=0.5
        )

        total_spent = sum(d['spent'] for d in sim.days_log)
        final_worth = sim.safe + sim.pocket

        results.append({
            'spending': spending,
            'total_spent': total_spent,
            'safe': sim.safe,
            'pocket': sim.pocket,
            'total': final_worth
        })

    # Print table
    print(f"\n{'Daily Spend':<15} {'Total Spent':<15} {'Safe':<15} {'Pocket':<12} {'Total':<15}")
    print("-" * 100)

    for r in results:
        print(f"${r['spending']:>10.2f}    "
              f"${r['total_spent']:>12,.2f}  "
              f"${r['safe']:>12,.2f}  "
              f"${r['pocket']:>9,.2f}  "
              f"${r['total']:>12,.2f}")

    print("=" * 100)

    # Show impact of reducing spending
    print("\nImpact of reducing daily spending from $30:")
    print("-" * 70)

    baseline = results[1]  # $30/day
    for r in results:
        if r['spending'] == 30:
            continue
        diff = r['total'] - baseline['total']
        saved_per_day = 30 - r['spending']
        print(f"  ${r['spending']:.2f}/day (save ${saved_per_day:+.2f}/day): "
              f"Net worth ${diff:>+10,.2f}")

    print()


def show_formula_breakdown():
    """Show how the formula works step by step"""
    print("\n" + "=" * 100)
    print("FORMULA BREAKDOWN")
    print("=" * 100)

    print("""
Your Budget System:

1. PAYCHECK PROCESSING:
   Leftover = Paycheck - Bills
   Save = Leftover × save_fraction → goes to Safe
   Spend Pool = Leftover × (1 - save_fraction)
   Daily Allowance = Spend Pool / days_in_period

2. DAILY OPERATION:
   pocket = pocket + daily_allowance
   spendable = pocket / 4
   You can spend up to 'spendable' amount
   remaining = pocket - actual_spent

3. END OF PAY PERIOD:
   Safe = Safe + pocket (sweep remaining)
   pocket = 0 (reset)
   Process new paycheck

4. COMPOUND GROWTH:
   Safe grows at 5% annual (daily compounding)
   daily_rate = (1 + 0.05)^(1/365) - 1
   Safe = Safe × (1 + daily_rate)

EXAMPLE with $2000 biweekly, $500 bills, 50% save:
   Leftover = $2000 - $500 = $1500
   Save = $1500 × 0.5 = $750 → Safe
   Spend Pool = $1500 × 0.5 = $750
   Daily = $750 / 14 = $53.57

   Day 1: pocket = 0 + 53.57 = $53.57
          spendable = 53.57 / 4 = $13.39
          If you spend $30, pocket = $23.57

   Day 2: pocket = 23.57 + 53.57 = $77.14
          spendable = 77.14 / 4 = $19.29
          If you spend $30, pocket = $47.14

   ...and so on. The less you spend, the more accumulates!
    """)

    print("=" * 100)


def main():
    show_formula_breakdown()
    compare_save_fractions()
    compare_spending_levels()


if __name__ == "__main__":
    main()
