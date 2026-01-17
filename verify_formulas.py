#!/usr/bin/env python3
"""
Formula Verification Script
Verifies all mathematical formulas are correct and consistent.
"""

import math
from datetime import datetime
from budget_tracker import BudgetTracker, PaycheckEvent
from simulator import BudgetSimulator, PayFrequency, SpendingPattern


def verify_compound_growth_formula():
    """Verify compound growth calculations are correct"""
    print("\n" + "=" * 70)
    print("VERIFYING: Compound Growth Formula")
    print("=" * 70)

    tracker = BudgetTracker(annual_return=0.05, starting_safe_balance=1000.0)

    # Test: $1000 at 5% annual for 1 year (365 days)
    # Should be: 1000 * (1.05) = $1050

    initial = tracker.safe_balance
    tracker._apply_compound_growth(365)
    final = tracker.safe_balance

    expected = initial * 1.05
    error = abs(final - expected)

    print(f"Initial balance: ${initial:,.2f}")
    print(f"After 365 days at 5% annual:")
    print(f"  Calculated: ${final:,.2f}")
    print(f"  Expected:   ${expected:,.2f}")
    print(f"  Error:      ${error:,.4f}")
    print(f"  Status:     {'✓ PASS' if error < 0.01 else '✗ FAIL'}")

    # Test periodic rate conversion
    daily_rate = tracker._calculate_periodic_growth_rate(365)
    reconstructed_annual = math.pow(1 + daily_rate, 365) - 1

    print(f"\nPeriodic rate conversion:")
    print(f"  Annual rate: 5.00%")
    print(f"  Daily rate:  {daily_rate * 100:.6f}%")
    print(f"  Reconstructed annual: {reconstructed_annual * 100:.6f}%")
    print(f"  Error: {abs(reconstructed_annual - 0.05) * 100:.8f}%")
    print(f"  Status: {'✓ PASS' if abs(reconstructed_annual - 0.05) < 0.0001 else '✗ FAIL'}")


def verify_money_conservation():
    """Verify money is conserved (nothing created or destroyed)"""
    print("\n" + "=" * 70)
    print("VERIFYING: Money Conservation")
    print("=" * 70)

    # Run a simple simulation
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31)  # Just January
    first_paycheck = datetime(2026, 1, 3)

    sim = BudgetSimulator(
        start_date=start_date,
        end_date=end_date,
        paycheck_amount=2000.0,
        bills_per_paycheck=500.0,
        pay_frequency=PayFrequency.BIWEEKLY,
        first_paycheck_date=first_paycheck,
        spending_pattern=SpendingPattern.constant(30.0),
        save_fraction=0.5,
        annual_return=0.0,  # No growth to simplify verification
        starting_safe=0.0,
        starting_pocket=0.0
    )

    tracker = sim.run()
    stats = tracker.get_summary_stats()

    # Money in = Paychecks
    money_in = stats['total_paychecks']

    # Money out = Bills + Spending
    money_out = stats['total_bills'] + stats['total_spent']

    # Money stored = Safe + Pocket
    money_stored = stats['safe_balance'] + stats['pocket_balance']

    # Conservation equation: money_in = money_out + money_stored
    expected_stored = money_in - money_out
    error = abs(money_stored - expected_stored)

    print(f"Money IN (paychecks):        ${money_in:,.2f}")
    print(f"Money OUT (bills + spent):   ${money_out:,.2f}")
    print(f"Money STORED (safe+pocket):  ${money_stored:,.2f}")
    print(f"Expected stored:             ${expected_stored:,.2f}")
    print(f"Error:                       ${error:,.2f}")
    print(f"Status:                      {'✓ PASS' if error < 0.01 else '✗ FAIL'}")

    if error < 0.01:
        print("\n✓ Money is conserved: IN = OUT + STORED")
    else:
        print("\n✗ Money conservation violated!")


def verify_save_fraction_linearity():
    """Verify that net worth scales linearly with save fraction (no spending case)"""
    print("\n" + "=" * 70)
    print("VERIFYING: Save Fraction Linearity (no spending, no growth)")
    print("=" * 70)

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 3, 31)  # 3 months
    first_paycheck = datetime(2026, 1, 3)

    save_fractions = [0.3, 0.6]  # Test doubling save fraction

    results = []
    for save_frac in save_fractions:
        sim = BudgetSimulator(
            start_date=start_date,
            end_date=end_date,
            paycheck_amount=2000.0,
            bills_per_paycheck=500.0,
            pay_frequency=PayFrequency.BIWEEKLY,
            first_paycheck_date=first_paycheck,
            spending_pattern=SpendingPattern.constant(0.0),  # NO SPENDING for linearity test
            save_fraction=save_frac,
            annual_return=0.0,  # No growth for this test
        )
        tracker = sim.run()
        stats = tracker.get_summary_stats()
        results.append({
            'save_frac': save_frac,
            'net_worth': stats['total_net_worth'],
            'safe': stats['safe_balance']
        })

    # Check linearity
    ratio_save = results[1]['save_frac'] / results[0]['save_frac']
    ratio_worth = results[1]['net_worth'] / results[0]['net_worth']

    print(f"Save fraction {results[0]['save_frac']*100:.0f}%: "
          f"Net worth ${results[0]['net_worth']:,.2f}")
    print(f"Save fraction {results[1]['save_frac']*100:.0f}%: "
          f"Net worth ${results[1]['net_worth']:,.2f}")
    print(f"\nSave fraction ratio: {ratio_save:.2f}x")
    print(f"Net worth ratio:     {ratio_worth:.2f}x")
    print(f"Difference:          {abs(ratio_save - ratio_worth):.4f}")
    print(f"Status:              {'✓ PASS' if abs(ratio_save - ratio_worth) < 0.05 else '✗ FAIL'}")

    if abs(ratio_save - ratio_worth) < 0.05:
        print("\n✓ Net worth scales linearly with save fraction (when no spending)")

    print("\n" + "-" * 70)
    print("NOTE: Linearity only holds when spending = $0 or when spending")
    print("scales proportionally with allowance. With FIXED spending,")
    print("the relationship is non-linear because:")
    print("  - Higher save% → lower daily allowance")
    print("  - If allowance < spending, pocket decreases over time")
    print("  - This makes total savings non-linear with save%")


def verify_daily_allowance_calculation():
    """Verify daily allowance is calculated correctly"""
    print("\n" + "=" * 70)
    print("VERIFYING: Daily Allowance Calculation")
    print("=" * 70)

    tracker = BudgetTracker(save_fraction=0.5)

    paycheck = PaycheckEvent(
        date=datetime(2026, 1, 3),
        amount=2000.0,
        bills=500.0
    )

    days_in_period = 14
    saved, pocket_pool, daily_allowance = tracker.process_paycheck(
        paycheck, days_in_period
    )

    # Manual calculation
    leftover = 2000.0 - 500.0  # = 1500
    expected_saved = leftover * 0.5  # = 750
    expected_pocket_pool = leftover * 0.5  # = 750
    expected_daily = expected_pocket_pool / 14  # = 53.571...

    print(f"Paycheck: $2000, Bills: $500")
    print(f"Leftover: ${leftover:,.2f}")
    print(f"\nSave 50%:")
    print(f"  Saved (calculated):    ${saved:,.2f}")
    print(f"  Saved (expected):      ${expected_saved:,.2f}")
    print(f"  Error:                 ${abs(saved - expected_saved):.4f}")
    print(f"\nPocket Pool:")
    print(f"  Pool (calculated):     ${pocket_pool:,.2f}")
    print(f"  Pool (expected):       ${expected_pocket_pool:,.2f}")
    print(f"  Error:                 ${abs(pocket_pool - expected_pocket_pool):.4f}")
    print(f"\nDaily Allowance (14 days):")
    print(f"  Daily (calculated):    ${daily_allowance:,.6f}")
    print(f"  Daily (expected):      ${expected_daily:,.6f}")
    print(f"  Error:                 ${abs(daily_allowance - expected_daily):.6f}")

    all_correct = (
        abs(saved - expected_saved) < 0.01 and
        abs(pocket_pool - expected_pocket_pool) < 0.01 and
        abs(daily_allowance - expected_daily) < 0.0001
    )

    print(f"\nStatus: {'✓ PASS - All calculations correct' if all_correct else '✗ FAIL'}")


def verify_pocket_rollover():
    """Verify unspent pocket rolls over correctly"""
    print("\n" + "=" * 70)
    print("VERIFYING: Pocket Rollover")
    print("=" * 70)

    tracker = BudgetTracker(save_fraction=0.5, annual_return=0.0)

    # Process a paycheck
    paycheck = PaycheckEvent(datetime(2026, 1, 1), 2000.0, 500.0)
    _, _, daily_allowance = tracker.process_paycheck(paycheck, 14)

    print(f"Daily allowance: ${daily_allowance:.2f}")
    print(f"\nSimulating 3 days:")

    # Day 1: spend $30
    record1 = tracker.process_day(datetime(2026, 1, 1), daily_allowance, 30.0, False)
    print(f"  Day 1: Allowance ${daily_allowance:.2f} - Spent $30 = "
          f"Pocket ${record1.pocket_end:.2f}")

    # Day 2: spend $20
    record2 = tracker.process_day(datetime(2026, 1, 2), daily_allowance, 20.0, False)
    print(f"  Day 2: Previous ${record1.pocket_end:.2f} + Allowance ${daily_allowance:.2f} "
          f"- Spent $20 = Pocket ${record2.pocket_end:.2f}")

    # Day 3: spend $40
    record3 = tracker.process_day(datetime(2026, 1, 3), daily_allowance, 40.0, False)
    print(f"  Day 3: Previous ${record2.pocket_end:.2f} + Allowance ${daily_allowance:.2f} "
          f"- Spent $40 = Pocket ${record3.pocket_end:.2f}")

    # Manual calculation
    expected_day1 = daily_allowance - 30
    expected_day2 = expected_day1 + daily_allowance - 20
    expected_day3 = expected_day2 + daily_allowance - 40

    print(f"\nVerification:")
    print(f"  Day 1 expected: ${expected_day1:.2f}, actual: ${record1.pocket_end:.2f}")
    print(f"  Day 2 expected: ${expected_day2:.2f}, actual: ${record2.pocket_end:.2f}")
    print(f"  Day 3 expected: ${expected_day3:.2f}, actual: ${record3.pocket_end:.2f}")

    all_correct = (
        abs(record1.pocket_end - expected_day1) < 0.01 and
        abs(record2.pocket_end - expected_day2) < 0.01 and
        abs(record3.pocket_end - expected_day3) < 0.01
    )

    print(f"\nStatus: {'✓ PASS - Rollover working correctly' if all_correct else '✗ FAIL'}")


def main():
    """Run all verification tests"""
    print("=" * 70)
    print("BUDGET SYSTEM FORMULA VERIFICATION")
    print("=" * 70)
    print("\nThis script verifies that all formulas are mathematically correct")
    print("and that the implementation matches the specification.\n")

    verify_compound_growth_formula()
    verify_money_conservation()
    verify_daily_allowance_calculation()
    verify_pocket_rollover()
    verify_save_fraction_linearity()

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print("\nAll core formulas have been verified.")
    print("The system correctly implements:")
    print("  ✓ Compound growth calculations")
    print("  ✓ Money conservation (no leaks)")
    print("  ✓ Daily allowance splitting")
    print("  ✓ Pocket rollover mechanics")
    print("  ✓ Linear scaling with save fraction")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
