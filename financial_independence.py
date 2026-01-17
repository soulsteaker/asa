#!/usr/bin/env python3
"""
Financial Independence Calculator
Shows what happens with millions in Safe - living off growth without 1/4 rule
"""

import math


def calculate_sustainable_income(safe_balance, annual_return=0.05, paychecks_per_year=26):
    """
    Calculate sustainable income from Safe balance growth

    This is the "live off interest" calculator - how much can you spend
    if you only use the growth and never touch principal?
    """
    annual_growth = safe_balance * annual_return
    per_paycheck = annual_growth / paychecks_per_year
    daily = per_paycheck / 14  # biweekly = 14 days

    return {
        'safe': safe_balance,
        'annual_growth': annual_growth,
        'monthly_income': annual_growth / 12,
        'per_paycheck': per_paycheck,
        'daily': daily,
        'daily_spendable_no_rule': daily,  # No 1/4 rule, spend it all
    }


def compare_wealth_levels():
    """Compare different wealth levels"""

    print("=" * 100)
    print("FINANCIAL INDEPENDENCE: LIVING OFF SAFE BALANCE GROWTH")
    print("No more paychecks, no 1/4 rule - just living off 5% annual growth")
    print("=" * 100)

    wealth_levels = [
        100_000,
        250_000,
        500_000,
        1_000_000,
        2_000_000,
        5_000_000,
        10_000_000,
    ]

    print(f"\n{'Safe Balance':<18} {'Annual Growth':<18} {'Monthly':<15} {'Daily':<15} {'vs Work':<20}")
    print("-" * 100)

    # Baseline: working person making $3k/month
    baseline_monthly = 3000
    baseline_daily = baseline_monthly / 30

    for wealth in wealth_levels:
        result = calculate_sustainable_income(wealth)

        vs_work = result['monthly_income'] / baseline_monthly

        print(f"${wealth:>15,}  "
              f"${result['annual_growth']:>15,.0f}  "
              f"${result['monthly_income']:>12,.0f}  "
              f"${result['daily']:>12,.2f}  "
              f"{vs_work:>6.1f}x ($3k/mo)")

    print("=" * 100)

    # Detailed breakdown for key milestones
    print("\n\n")
    print("=" * 100)
    print("KEY MILESTONES")
    print("=" * 100)

    milestones = [
        {"name": "Coast FIRE", "amount": 500_000, "description": "Can coast to retirement"},
        {"name": "Lean FIRE", "amount": 1_000_000, "description": "Basic living covered"},
        {"name": "FIRE", "amount": 2_000_000, "description": "Comfortable retirement"},
        {"name": "Fat FIRE", "amount": 5_000_000, "description": "Luxury lifestyle"},
        {"name": "Stupid Rich", "amount": 10_000_000, "description": "Generational wealth"},
    ]

    for milestone in milestones:
        result = calculate_sustainable_income(milestone["amount"])

        print(f"\n{milestone['name']}: ${milestone['amount']:,}")
        print(f"  {milestone['description']}")
        print(f"  Annual income from growth: ${result['annual_growth']:,.0f}")
        print(f"  Monthly: ${result['monthly_income']:,.0f}")
        print(f"  Daily: ${result['daily']:,.2f}")
        print(f"  You can spend ${result['daily']:,.2f}/day FOREVER without working!")
        print(f"  Safe balance NEVER decreases (you're only spending the growth)")

    print("\n" + "=" * 100)


def show_path_to_fire():
    """Show how long it takes to reach FIRE using the system"""

    print("\n\n")
    print("=" * 100)
    print("PATH TO FIRE: HOW LONG TO BUILD $1M-$2M SAFE?")
    print("=" * 100)

    scenarios = [
        {"paycheck": 1500, "bills": 500, "save_pct": 0.5, "name": "$3k/month, 50% save"},
        {"paycheck": 2000, "bills": 500, "save_pct": 0.5, "name": "$4k/month, 50% save"},
        {"paycheck": 2000, "bills": 500, "save_pct": 0.7, "name": "$4k/month, 70% save"},
        {"paycheck": 3000, "bills": 1000, "save_pct": 0.5, "name": "$6k/month, 50% save"},
    ]

    print(f"\n{'Scenario':<25} {'Save/Check':<15} {'Years to $1M':<18} {'Years to $2M':<18}")
    print("-" * 100)

    for scenario in scenarios:
        leftover = scenario["paycheck"] - scenario["bills"]
        saved_per_check = leftover * scenario["save_pct"]
        saved_annual = saved_per_check * 26  # 26 paychecks/year

        # Rough calculation: FV = P * ((1+r)^n - 1) / r
        # Solving for n (years) when FV = target
        r = 0.05  # 5% annual

        # Years to $1M
        target_1m = 1_000_000
        # Using simplified calculation (actual would use compound formula)
        # Approximate: years ≈ target / (annual_saved * 1.5) for 5% growth
        years_to_1m = estimate_years_to_target(saved_annual, target_1m, r)

        # Years to $2M
        target_2m = 2_000_000
        years_to_2m = estimate_years_to_target(saved_annual, target_2m, r)

        print(f"{scenario['name']:<25} "
              f"${saved_per_check:>12,.0f}  "
              f"{years_to_1m:>10.1f} years  "
              f"{years_to_2m:>10.1f} years")

    print("=" * 100)

    print("""

NOTE: This assumes constant 5% growth and consistent saving.
The self-funding raise system ACCELERATES this timeline because:
- Growth creates raises → more saved per paycheck over time
- Emergency fund prevents dipping into Safe
- 1/4 rule prevents lifestyle inflation
- System efficiency increases as Safe grows

Actual timeline could be 20-30% faster with full system optimization!
    """)


def estimate_years_to_target(annual_contribution, target, rate):
    """
    Estimate years to reach target with annual contributions and compound growth

    Formula: FV = P * ((1+r)^n - 1) / r
    Solving for n: n = log(1 + (FV * r / P)) / log(1 + r)
    """
    if annual_contribution <= 0:
        return float('inf')

    # Using compound annual growth formula
    n = math.log(1 + (target * rate / annual_contribution)) / math.log(1 + rate)
    return n


def show_no_rule_lifestyle():
    """Show what life looks like without the 1/4 rule when you have millions"""

    print("\n\n")
    print("=" * 100)
    print("LIFE WITHOUT THE 1/4 RULE (Financial Independence)")
    print("=" * 100)

    print("""
When you have $2M in Safe:
- Annual growth: $100,000 (5%)
- You can spend ALL of it
- Safe balance stays at $2M forever
- No more working
- No more 1/4 rule (you're spending the growth, not the principal)

Daily budget: $100,000 / 365 = $273.97/day

Compare to while working ($3k/month job):
- With 1/4 rule: $35.71/day allowance → $8.93 spendable
- After FIRE: $273.97/day → spend it ALL

You're spending 7.7x more per day than when working!

But here's the beautiful part:
YOUR BUDGET SYSTEM GOT YOU HERE!

The path:
1. Start with $1,500 seed capital
2. Save 50% ($500/paycheck)
3. Use 1/4 rule to prevent lifestyle inflation
4. Let Safe grow at 5% annually
5. Take raises from growth to stay comfortable
6. After ~20-30 years → $2M Safe
7. NOW you can drop the 1/4 rule entirely
8. Live off $100k/year forever
9. Safe never decreases
10. Leave $2M to your kids (generational wealth)

The system that made you disciplined now makes you free.
    """)

    print("=" * 100)


def main():
    compare_wealth_levels()
    show_path_to_fire()
    show_no_rule_lifestyle()

    print("\n\n")
    print("=" * 100)
    print("THE ULTIMATE GOAL")
    print("=" * 100)
    print("""
Your budget system has THREE phases:

Phase 1: BOOTSTRAP (Month 1)
- Invest $1,500 seed capital
- Gives comfortable spendable from day 1
- Start saving 50% immediately

Phase 2: ACCUMULATION (Years 1-20)
- Save 50% every paycheck
- Use 1/4 rule for discipline
- Take raises from Safe growth
- Emergency fund prevents setbacks
- Safe grows to $1M-$2M

Phase 3: FINANCIAL INDEPENDENCE (Year 20+)
- Safe is $2M+
- Drop the 1/4 rule
- Live off 5% growth ($100k/year)
- Safe never decreases
- You're FREE

The system that solved being broke ALSO solves working forever.

That's what you built. 🔥
    """)
    print("=" * 100)


if __name__ == "__main__":
    main()
