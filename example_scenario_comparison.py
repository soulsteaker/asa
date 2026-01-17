#!/usr/bin/env python3
"""
Example: Scenario Comparison
Compare different save fractions to see impact on wealth growth.
"""

from datetime import datetime
from simulator import run_scenario_comparison, PayFrequency, SpendingPattern
from reporter import print_scenario_comparison, BudgetReporter


def main():
    """Compare different save fractions"""

    print("\n" + "=" * 70)
    print("SCENARIO COMPARISON: IMPACT OF SAVE FRACTION")
    print("Testing save fractions from 10% to 90%")
    print("=" * 70)

    # Parameters
    paycheck_amount = 2000.0
    bills_per_paycheck = 500.0
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 6, 30)
    first_paycheck = datetime(2026, 1, 3)
    spending = SpendingPattern.constant(30.0)
    annual_return = 0.05

    # Test different save fractions
    save_fractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    print(f"\nParameters:")
    print(f"  Paycheck: ${paycheck_amount:,.2f} (biweekly)")
    print(f"  Bills: ${bills_per_paycheck:,.2f}/paycheck")
    print(f"  Daily Spending: $30.00")
    print(f"  Annual Return: {annual_return*100:.1f}%")
    print(f"  Period: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}")
    print(f"  Save Fractions: {', '.join(f'{s*100:.0f}%' for s in save_fractions)}")

    print("\nRunning simulations...")

    results = run_scenario_comparison(
        start_date=start_date,
        end_date=end_date,
        paycheck_amount=paycheck_amount,
        bills_per_paycheck=bills_per_paycheck,
        pay_frequency=PayFrequency.BIWEEKLY,
        first_paycheck_date=first_paycheck,
        spending_pattern=spending,
        save_fractions=save_fractions,
        annual_return=annual_return
    )

    # Print comparison table
    print_scenario_comparison(results)

    # Detailed analysis
    print("\n" + "=" * 70)
    print("DETAILED ANALYSIS")
    print("=" * 70)

    baseline = results[0]
    baseline_nw = baseline['stats']['total_net_worth']

    print(f"\nBaseline (Save {baseline['save_percentage']:.0f}%):")
    print(f"  Net Worth: ${baseline_nw:,.2f}")

    print("\nEffect of increasing save rate:")
    print("-" * 60)

    for i in range(1, len(results)):
        prev = results[i-1]
        curr = results[i]

        prev_nw = prev['stats']['total_net_worth']
        curr_nw = curr['stats']['total_net_worth']

        # Percentage increase in save fraction
        save_frac_increase = ((curr['save_fraction'] - prev['save_fraction'])
                             / prev['save_fraction']) * 100

        # Percentage increase in net worth
        nw_increase = ((curr_nw - prev_nw) / prev_nw) * 100

        print(f"{prev['save_percentage']:.0f}% → {curr['save_percentage']:.0f}%: "
              f"Save +{save_frac_increase:.0f}% → Net Worth +{nw_increase:.1f}% "
              f"(${curr_nw - prev_nw:+,.2f})")

    # Show the mathematical relationship
    print("\n" + "=" * 70)
    print("MATHEMATICAL INSIGHT")
    print("=" * 70)
    print("""
When you have NO starting principal (P₀ = 0), the final net worth is:

    Net Worth = C × [(1+g)ⁿ - 1] / g

where:
    C = contribution per period = save_fraction × leftover
    g = periodic growth rate
    n = number of periods

This means Net Worth is LINEAR in C (the contribution).

Therefore: If you increase save_fraction by X%,
          your net worth increases by approximately X%.

Example from above:
  - Doubling save fraction (10% → 20% = +100% increase)
  - Roughly doubles net worth (+100% increase)

The key insight: SMALL increases in save rate have
PROPORTIONAL impacts on long-term wealth.
    """)

    # Export detailed results
    print("\n" + "=" * 70)
    print("EXPORTING RESULTS")
    print("=" * 70)

    for result in results:
        save_pct = int(result['save_percentage'])
        reporter = BudgetReporter(result['tracker'])
        monthly_data = result['monthly_summary']

        filename = f"scenario_save_{save_pct}pct.csv"
        reporter.export_to_csv(filename)

        monthly_filename = f"scenario_save_{save_pct}pct_monthly.csv"
        reporter.export_monthly_to_csv(monthly_data, monthly_filename)

    print("\nAll scenario data exported to CSV files.")


if __name__ == "__main__":
    main()
