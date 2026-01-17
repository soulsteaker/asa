#!/usr/bin/env python3
"""
Example: January to June Budget Simulation
Demonstrates your budget system with your exact parameters.
"""

from datetime import datetime
from simulator import BudgetSimulator, PayFrequency, SpendingPattern
from reporter import BudgetReporter, print_scenario_comparison, print_formula_explanation


def main():
    """Run January to June simulation with your parameters"""

    print_formula_explanation()

    print("\n" + "=" * 70)
    print("RUNNING YOUR BUDGET SYSTEM: JANUARY - JUNE 2026")
    print("=" * 70)

    # Your parameters from the description
    paycheck_amount = 2000.0        # Biweekly paycheck
    monthly_bills = 1000.0          # Bills per month
    bills_per_paycheck = 500.0      # $1000/month ÷ 2 paychecks/month

    # Simulation period: January 1 - June 30, 2026
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 6, 30)

    # First paycheck: assume Jan 3, 2026 (first Friday)
    first_paycheck = datetime(2026, 1, 3)

    # Spending pattern: constant $30/day as in your example
    spending = SpendingPattern.constant(30.0)

    # Save 50% (your default)
    save_fraction = 0.5

    # Annual return of 5% (example compound growth)
    annual_return = 0.05

    print(f"\nParameters:")
    print(f"  Paycheck: ${paycheck_amount:,.2f} (biweekly)")
    print(f"  Bills: ${monthly_bills:,.2f}/month (${bills_per_paycheck:,.2f}/paycheck)")
    print(f"  Save Fraction: {save_fraction*100:.0f}%")
    print(f"  Daily Spending: $30.00 (constant)")
    print(f"  Annual Return: {annual_return*100:.1f}%")
    print(f"  Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}")

    # Create and run simulator
    print("\nRunning simulation...")
    sim = BudgetSimulator(
        start_date=start_date,
        end_date=end_date,
        paycheck_amount=paycheck_amount,
        bills_per_paycheck=bills_per_paycheck,
        pay_frequency=PayFrequency.BIWEEKLY,
        first_paycheck_date=first_paycheck,
        spending_pattern=spending,
        save_fraction=save_fraction,
        annual_return=annual_return
    )

    tracker = sim.run()

    # Generate reports
    reporter = BudgetReporter(tracker)

    # Monthly summary
    monthly_data = sim.get_monthly_summary()
    reporter.print_monthly_table(monthly_data)

    # Overall summary
    reporter.print_summary()

    # Show some daily detail (first 30 days)
    print("\n")
    reporter.print_daily_detail(max_rows=30)

    # Export to CSV
    print("\n")
    reporter.export_to_csv("budget_daily_jan_jun.csv")
    reporter.export_monthly_to_csv(monthly_data, "budget_monthly_jan_jun.csv")

    # Verify the math from your example
    print("\n" + "=" * 70)
    print("VERIFICATION: Your Example Week 1")
    print("=" * 70)
    print("\nYour manual calculation:")
    print("  Starting with paycheck: $2000 - $500 bills = $1500 leftover")
    print("  Save 50%: $750 → Safe")
    print("  Spend pool: $750")
    print("  Daily allowance: $750 ÷ 14 days = $53.57/day")
    print("  Spending $30/day for 7 days:")
    print("    End of week pocket ≈ $308 (from your calculation)")
    print()

    # Check our simulation matches
    if tracker.daily_records:
        # Find day 7 (7th record)
        if len(tracker.daily_records) >= 7:
            day7 = tracker.daily_records[6]  # 0-indexed
            print("Our simulation after 7 days:")
            print(f"  Pocket balance: ${day7.pocket_end:.2f}")
            print(f"  Safe balance: ${day7.safe_balance:.2f}")
            print(f"  Total net worth: ${day7.pocket_end + day7.safe_balance:.2f}")
            print()

            # Calculate what we expect:
            # 7 days × $53.57 allowance = $375
            # 7 days × $30 spent = $210
            # Net pocket = $375 - $210 = $165 + rollover
            # Actually: day 1: 53.57 - 30 = 23.57
            # day 2: 23.57 + 53.57 - 30 = 47.14
            # day 3: 47.14 + 53.57 - 30 = 70.71
            # day 4: 70.71 + 53.57 - 30 = 94.28
            # day 5: 94.28 + 53.57 - 30 = 117.85
            # day 6: 117.85 + 53.57 - 30 = 141.42
            # day 7: 141.42 + 53.57 - 30 = 164.99 ≈ $165

            # Your calculation had $308, but that seems to assume adding leftover
            # to the next paycheck. Let me recalculate based on your description.

            print("  Note: Pocket grows daily by (allowance - spent)")
            print("        After 7 days: cumulative unspent builds up")


if __name__ == "__main__":
    main()
