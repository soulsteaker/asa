#!/usr/bin/env python3
"""
Budget simulation for $3000/month income
Shows 3-month and 6-month results
"""

from datetime import datetime, timedelta
from run_jan_to_june import BudgetSim, run_simulation, print_monthly_summary


def run_3k_scenario(months: int, daily_spending: float, bills_per_month: float = 1000.0):
    """
    Run scenario with $3000/month income

    Args:
        months: Number of months to simulate (3 or 6)
        daily_spending: Daily spending amount
        bills_per_month: Monthly bills
    """
    # $3000/month = $1500 biweekly (26 paychecks/year = $39k/year ÷ 26)
    # Or $3000/month × 12 months = $36k/year ÷ 26 = $1384.62 biweekly
    # Let's use $1500 biweekly which gives $3000/month average

    paycheck_biweekly = 1500.0
    bills_per_check = bills_per_month / 2  # Split monthly bills across 2 paychecks

    # Determine end date based on months
    start = datetime(2026, 1, 1)
    if months == 3:
        end = datetime(2026, 3, 31)
    elif months == 6:
        end = datetime(2026, 6, 30)
    else:
        end = datetime(2026, 1, 1) + timedelta(days=months * 30)

    print("=" * 100)
    print(f"BUDGET SIMULATION: {months} MONTHS ($3000/month income)")
    print("=" * 100)
    print(f"\nIncome:")
    print(f"  Monthly: $3,000.00")
    print(f"  Biweekly paycheck: ${paycheck_biweekly:,.2f}")
    print(f"  Annual: ${paycheck_biweekly * 26:,.2f}")
    print(f"\nExpenses:")
    print(f"  Bills/month: ${bills_per_month:,.2f}")
    print(f"  Bills/paycheck: ${bills_per_check:,.2f}")
    print(f"  Daily spending: ${daily_spending:.2f}")
    print(f"\nSavings:")
    print(f"  Save rate: 50%")

    leftover = paycheck_biweekly - bills_per_check
    save_amount = leftover * 0.5
    spend_pool = leftover * 0.5
    daily_allowance = spend_pool / 14

    print(f"  Leftover per check: ${leftover:,.2f}")
    print(f"  Saved per check: ${save_amount:,.2f}")
    print(f"  Daily allowance: ${daily_allowance:.2f}")

    # Run simulation
    sim = run_simulation(
        start=start,
        end=end,
        paycheck_amount=paycheck_biweekly,
        bills_per_check=bills_per_check,
        days_between_checks=14,
        first_paycheck_date=datetime(2026, 1, 3),
        daily_spending=daily_spending,
        save_frac=0.5
    )

    # Print monthly summary
    print_monthly_summary(sim)

    # Final totals
    print(f"\n{'='*100}")
    print(f"FINAL TOTALS ({months} months)")
    print(f"{'='*100}")
    print(f"Paychecks received: {sim.total_paychecks}")
    print(f"Total days: {len(sim.days_log)}")
    print(f"\nIncome:")
    print(f"  Total paychecks: ${sim.total_paychecks * paycheck_biweekly:,.2f}")
    print(f"  Total bills: ${sim.total_paychecks * bills_per_check:,.2f}")
    print(f"  Total leftover: ${sim.total_paychecks * leftover:,.2f}")
    print(f"\nSpending:")
    total_spent = sum(d['spent'] for d in sim.days_log)
    print(f"  Total spent: ${total_spent:,.2f}")
    print(f"  Average/day: ${total_spent/len(sim.days_log):.2f}")
    print(f"\nBalances:")
    print(f"  Safe: ${sim.safe:,.2f}")
    print(f"  Pocket: ${sim.pocket:,.2f}")
    print(f"  Total Net Worth: ${sim.safe + sim.pocket:,.2f}")
    print(f"\nSavings Rate:")
    saved = sim.safe + sim.pocket
    total_income = sim.total_paychecks * paycheck_biweekly
    savings_rate = (saved / total_income) * 100
    print(f"  Saved: ${saved:,.2f} out of ${total_income:,.2f}")
    print(f"  Effective savings rate: {savings_rate:.1f}%")
    print(f"{'='*100}\n")

    return sim


def main():
    # Ask user for parameters or use defaults
    print("=" * 100)
    print("$3000/MONTH BUDGET SIMULATOR")
    print("=" * 100)

    # Scenario 1: 3 months, $30/day spending, $1000/month bills
    print("\n\n")
    print("*" * 100)
    print("SCENARIO 1: 3 MONTHS")
    print("*" * 100)
    sim_3mo = run_3k_scenario(months=3, daily_spending=30.0, bills_per_month=1000.0)

    # Scenario 2: 6 months, same parameters
    print("\n\n")
    print("*" * 100)
    print("SCENARIO 2: 6 MONTHS")
    print("*" * 100)
    sim_6mo = run_3k_scenario(months=6, daily_spending=30.0, bills_per_month=1000.0)

    # Comparison
    print("\n\n")
    print("=" * 100)
    print("COMPARISON: 3 MONTHS vs 6 MONTHS")
    print("=" * 100)

    total_3mo = sim_3mo.safe + sim_3mo.pocket
    total_6mo = sim_6mo.safe + sim_6mo.pocket

    print(f"\n{'Period':<12} {'Paychecks':<12} {'Total Spent':<15} {'Net Worth':<15} {'$/Month':<15}")
    print("-" * 100)

    spent_3mo = sum(d['spent'] for d in sim_3mo.days_log)
    spent_6mo = sum(d['spent'] for d in sim_6mo.days_log)

    print(f"{'3 months':<12} {sim_3mo.total_paychecks:<12} "
          f"${spent_3mo:>12,.2f}  ${total_3mo:>12,.2f}  ${total_3mo/3:>12,.2f}")
    print(f"{'6 months':<12} {sim_6mo.total_paychecks:<12} "
          f"${spent_6mo:>12,.2f}  ${total_6mo:>12,.2f}  ${total_6mo/6:>12,.2f}")

    print("\n" + "=" * 100)
    print("\nKey Insight: Net Worth per month stays consistent because you're")
    print("saving at a steady rate. Compound growth effect is small over 6 months")
    print("but would be significant over years!")
    print("=" * 100)


if __name__ == "__main__":
    main()
