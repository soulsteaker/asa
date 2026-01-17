#!/usr/bin/env python3
"""
Wealth Leverage Calculator
Shows the difference between conservative (growth only) and aggressive (principal access)
"""


def conservative_fire(safe_balance, annual_return=0.05):
    """Conservative: Live off growth only, never touch principal"""
    annual_income = safe_balance * annual_return
    monthly = annual_income / 12
    daily = annual_income / 365

    return {
        'strategy': 'Conservative (Growth Only)',
        'safe': safe_balance,
        'annual_income': annual_income,
        'monthly': monthly,
        'daily': daily,
        'safe_after_year': safe_balance,  # Principal never touched
        'sustainable': 'Forever'
    }


def aggressive_leverage(safe_balance, paychecks_per_year=26):
    """
    Aggressive: Divide total Safe by pay periods for maximum daily spending

    This calculates "what if I spread my entire $1M across the year?"
    Daily access = (Safe / paychecks) / 14 days
    """
    per_paycheck = safe_balance / paychecks_per_year
    daily_access = per_paycheck / 14

    # If you actually spent this much, Safe would be depleted in 1 year
    annual_spending = daily_access * 365

    return {
        'strategy': 'Aggressive (Total Access)',
        'safe': safe_balance,
        'per_paycheck_access': per_paycheck,
        'daily_access': daily_access,
        'annual_if_spent_all': annual_spending,
        'safe_after_year': 0,  # Would be depleted
        'sustainable': '1 year (then broke)'
    }


def smart_hybrid(safe_balance, annual_return=0.05, withdraw_rate=0.04):
    """
    Smart Hybrid: 4% withdrawal rule (standard FIRE strategy)

    Take 4% per year from Safe (principal + growth)
    Historically sustainable for 30+ years
    """
    annual_withdrawal = safe_balance * withdraw_rate
    monthly = annual_withdrawal / 12
    daily = annual_withdrawal / 365

    # After 1 year with 5% growth and 4% withdrawal
    growth = safe_balance * annual_return
    withdrawn = annual_withdrawal
    safe_after = safe_balance + growth - withdrawn
    net_change = growth - withdrawn

    return {
        'strategy': '4% Rule (Smart Hybrid)',
        'safe': safe_balance,
        'annual_income': annual_withdrawal,
        'monthly': monthly,
        'daily': daily,
        'safe_after_year': safe_after,
        'net_change': net_change,
        'sustainable': '30+ years (historical)'
    }


def ultra_aggressive_your_idea(safe_balance, kept_in_safe=0.5, paychecks_per_year=26):
    """
    YOUR IDEA: Split Safe in half
    - Keep half earning 5%
    - Leverage other half for high daily spending

    Example: $2M total
    - $1M stays in Safe earning 5% = $50k/year
    - $1M divided by 26 paychecks = $38,461/paycheck
    - Daily from that $1M = $2,747/day

    Question: Is this sustainable?
    """
    kept_amount = safe_balance * kept_in_safe
    leverage_amount = safe_balance * (1 - kept_in_safe)

    # Growth from kept portion
    annual_growth = kept_amount * 0.05

    # Spending power from leveraged portion
    per_paycheck = leverage_amount / paychecks_per_year
    daily_from_leverage = per_paycheck / 14
    annual_from_leverage = leverage_amount  # If you spent it all

    # Net result after 1 year
    safe_after = kept_amount + annual_growth
    total_spent = annual_from_leverage
    net_change = safe_after - safe_balance

    # How many years sustainable?
    if total_spent > annual_growth:
        years_sustainable = leverage_amount / (total_spent - annual_growth)
    else:
        years_sustainable = float('inf')

    return {
        'strategy': f'Ultra Aggressive (Split {kept_in_safe*100:.0f}/{(1-kept_in_safe)*100:.0f})',
        'safe_start': safe_balance,
        'kept_in_safe': kept_amount,
        'leverage_portion': leverage_amount,
        'daily_spending_power': daily_from_leverage,
        'annual_if_spent_all': annual_from_leverage,
        'growth_from_kept': annual_growth,
        'safe_after_year': safe_after,
        'net_change': net_change,
        'years_sustainable': years_sustainable
    }


def compare_all_strategies():
    """Compare all wealth access strategies"""

    print("=" * 120)
    print("WEALTH LEVERAGE STRATEGIES: HOW TO ACCESS YOUR $1M-$2M")
    print("=" * 120)

    wealth_levels = [1_000_000, 2_000_000, 5_000_000]

    for wealth in wealth_levels:
        print(f"\n\n{'='*120}")
        print(f"SCENARIO: ${wealth:,} in Safe")
        print(f"{'='*120}\n")

        # Strategy 1: Conservative
        cons = conservative_fire(wealth)
        print(f"1. {cons['strategy']}")
        print(f"   Daily spending: ${cons['daily']:,.2f}")
        print(f"   Annual income: ${cons['annual_income']:,.0f}")
        print(f"   Safe after 1 year: ${cons['safe_after_year']:,.0f}")
        print(f"   Sustainable: {cons['sustainable']}")

        # Strategy 2: Smart 4% rule
        smart = smart_hybrid(wealth)
        print(f"\n2. {smart['strategy']}")
        print(f"   Daily spending: ${smart['daily']:,.2f}")
        print(f"   Annual income: ${smart['annual_income']:,.0f}")
        print(f"   Safe after 1 year: ${smart['safe_after_year']:,.0f} ({smart['net_change']:+,.0f})")
        print(f"   Sustainable: {smart['sustainable']}")

        # Strategy 3: Aggressive total access
        agg = aggressive_leverage(wealth)
        print(f"\n3. {agg['strategy']}")
        print(f"   Daily access: ${agg['daily_access']:,.2f}")
        print(f"   Per paycheck: ${agg['per_paycheck_access']:,.0f}")
        print(f"   Annual if spent all: ${agg['annual_if_spent_all']:,.0f}")
        print(f"   Safe after 1 year: ${agg['safe_after_year']:,} (BROKE!)")
        print(f"   Sustainable: {agg['sustainable']}")

        # Strategy 4: YOUR IDEA - Split approach
        if wealth >= 2_000_000:
            your = ultra_aggressive_your_idea(wealth, kept_in_safe=0.5)
            print(f"\n4. {your['strategy']} (YOUR IDEA)")
            print(f"   Keep in Safe: ${your['kept_in_safe']:,.0f} (earning 5%)")
            print(f"   Leverage: ${your['leverage_portion']:,.0f}")
            print(f"   Daily spending power: ${your['daily_spending_power']:,.2f}")
            print(f"   Growth from kept half: ${your['growth_from_kept']:,.0f}/year")
            print(f"   If you spent the full leverage: Safe drops to ${your['safe_after_year']:,.0f}")
            print(f"   Years sustainable: {your['years_sustainable']:.1f} years")

        print(f"\n{'-'*120}")
        print("COMPARISON:")
        print(f"  Conservative: ${cons['daily']:,.2f}/day forever")
        print(f"  4% Rule: ${smart['daily']:,.2f}/day for 30+ years")
        print(f"  Aggressive: ${agg['daily_access']:,.2f}/day for 1 year (then broke)")
        if wealth >= 2_000_000:
            print(f"  Your Split: ${your['daily_spending_power']:,.2f}/day for {your['years_sustainable']:.1f} years")


def your_idea_deep_dive():
    """Deep dive into YOUR split strategy"""

    print("\n\n")
    print("=" * 120)
    print("YOUR IDEA: SPLIT STRATEGY DEEP DIVE")
    print("=" * 120)

    print("""
Your Concept: "Keep $1M in Safe earning 5%, leverage the other $1M for high daily spending"

Let's see what actually happens:

Starting: $2M total
- $1M in Safe earning 5% = $50k/year growth
- $1M to leverage = $38,461/paycheck ÷ 14 days = $2,747/day potential

If you spend $2,747/day for a year:
- Total spent = $1,002,655
- Growth from Safe = $50,000
- Net loss = -$952,655
- Safe after 1 year = $2M - $952,655 = $1,047,345

Year 2:
- Keep half: $523,673 earning 5%
- Leverage half: $523,673 → $1,914/day
- Spend that for a year = -$698,610
- Growth = $26,184
- Net loss = -$672,426
- Safe after year 2 = $374,919

Year 3: Broke.

CONCLUSION: Spending the full leverage amount depletes Safe in ~2-3 years.
    """)

    print("\n" + "=" * 120)
    print("SMARTER VERSION: Spend LESS than the leverage, let Safe regenerate")
    print("=" * 120)

    print("""
What if you only spend 50% of the daily leverage?

$2M split:
- $1M kept, $1M leverage
- Daily potential: $2,747
- Actually spend: $1,373/day (50% of potential)
- Annual spending: $501,328

Year 1:
- Spent: $501,328
- Growth from kept $1M: $50,000
- Net: -$451,328
- Safe: $1,548,672

Year 2:
- Split: $774k kept, $774k leverage
- Daily potential: $2,126
- Spend 50%: $1,063/day = $388k/year
- Growth: $38,733
- Net: -$349,267
- Safe: $1,199,405

After 5-7 years: Safe approaches zero

BETTER: Spend WAY less, like $500/day instead
    """)

    # Calculate sustainable spending with split strategy
    safe = 2_000_000
    kept = 1_000_000
    leverage = 1_000_000
    growth_rate = 0.05

    print("\n" + "=" * 120)
    print("SUSTAINABLE SPLIT STRATEGY")
    print("=" * 120)

    print(f"""
To make the split strategy SUSTAINABLE:

Starting Safe: ${safe:,}
Split: ${kept:,} kept, ${leverage:,} leverage

For it to be sustainable over 30+ years:
Annual spending must ≤ Annual growth

Annual growth from $1M at 5% = $50,000
Plus you can draw down the leverage $1M slowly over 30 years = $33,333/year
Total sustainable = $50,000 + $33,333 = $83,333/year
Daily sustainable = $228/day

But wait... that's WORSE than the 4% rule on $2M = $80k/year = $219/day!

OPTIMAL: Don't split. Use 4% rule on full $2M.
Daily: ${(2_000_000 * 0.04)/365:,.2f}
Sustainable: 30+ years
Safe stays around $2M (with market growth)
    """)


def main():
    compare_all_strategies()
    your_idea_deep_dive()

    print("\n\n")
    print("=" * 120)
    print("BOTTOM LINE")
    print("=" * 120)
    print("""
Your split idea is BRILLIANT for understanding leverage, but here's the math:

Best strategies by Safe balance:

$1M Safe:
  - 4% rule: $40k/year = $109/day (sustainable 30+ years) ✓
  - Conservative: $50k/year = $137/day (forever) ✓
  - Your split: $1,373/day (2-3 years) ✗

$2M Safe:
  - 4% rule: $80k/year = $219/day (sustainable 30+ years) ✓
  - Conservative: $100k/year = $274/day (forever) ✓
  - Your split: $2,747/day (2-3 years) ✗

The ultra-high daily ($2,747) is POSSIBLE but burns through Safe fast.

SMARTER APPROACH:
When Safe hits $2M, you can:
1. Live off $274/day FOREVER (5% growth only)
2. Live off $219/day for 30+ years (4% rule)
3. Take occasional "bonuses" from principal for big purchases
4. Still leave wealth to your kids

Your system got you to $2M.
Now you can spend $200-300/day for life without working.
That's the win. 🔥
    """)
    print("=" * 120)


if __name__ == "__main__":
    main()
