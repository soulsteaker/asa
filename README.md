# Budget Tracking System

A budget management system based on daily allowance with automatic savings and compound growth.

## Core Formula

```
1. Paycheck - Bills = Leftover
2. Save 50% of Leftover → Safe
3. Other 50% ÷ days = daily allowance
4. Each day: pocket + daily = new pocket
5. Spendable = pocket / 4
6. End of period: sweep pocket → Safe
```

## Quick Start

### Run January-June Simulation

```bash
python3 run_jan_to_june.py
```

Shows 6-month simulation with:
- $2000 biweekly paycheck
- $500 bills per paycheck
- $30/day spending
- 50% save rate
- 5% annual compound growth

### Compare Different Scenarios

```bash
python3 compare_scenarios.py
```

Compares:
- Different save percentages (10% to 90%)
- Different spending levels ($20 to $53/day)
- Shows impact on final net worth

### Verify Formula

```bash
python3 budget_simple.py
```

Verifies formula with your manual calculations.

## How It Works

### 1. Paycheck Processing

```
Leftover = Paycheck - Bills
Save to Safe = Leftover × save_fraction
Spend Pool = Leftover × (1 - save_fraction)
Daily Allowance = Spend Pool / days_in_period
```

**Example:** $2000 paycheck, $500 bills, 50% save, 14 days
- Leftover = $1500
- Save = $750 → Safe
- Spend Pool = $750
- Daily = $750 ÷ 14 = $53.57

### 2. Daily Operation

```
pocket = pocket + daily_allowance
spendable = pocket / 4
actual_spent = your spending (up to pocket balance)
pocket = pocket - actual_spent
```

**Example:** Day 1
- Pocket starts at $0
- Add daily: $0 + $53.57 = $53.57
- Spendable: $53.57 ÷ 4 = $13.39
- You spend $30: $53.57 - $30 = $23.57 remaining

**Example:** Day 2
- Previous remaining: $23.57
- Add daily: $23.57 + $53.57 = $77.14
- Spendable: $77.14 ÷ 4 = $19.29
- You spend $30: $77.14 - $30 = $47.14 remaining

The less you spend, the more accumulates!

### 3. End of Pay Period

```
Safe = Safe + pocket  (sweep remaining)
pocket = 0  (reset)
Process new paycheck
```

### 4. Compound Growth

Safe balance grows daily:
```
daily_rate = (1 + annual_rate)^(1/365) - 1
Safe = Safe × (1 + daily_rate)
```

At 5% annual: daily rate ≈ 0.0134%

## Key Insights

### 1. Spending Less = More Wealth

From comparison scenarios (Jan-June, $2000 biweekly, 50% save):

| Daily Spend | Total Net Worth | vs $30/day |
|-------------|-----------------|------------|
| $20/day     | $16,019.83      | +$1,830.36 |
| $30/day     | $14,189.47      | baseline   |
| $40/day     | $12,359.11      | -$1,830.36 |

Saving $10/day = **+$1,830** over 6 months!

### 2. Save Fraction Impact

When daily spending > daily allowance (like $30 > allowances at high save%):

| Save % | Daily Allowance | Net Worth  | vs 50%   |
|--------|-----------------|------------|----------|
| 50%    | $53.57/day      | $14,189.47 | baseline |
| 70%    | $32.14/day      | $14,217.29 | +$27.82  |
| 80%    | $21.43/day      | $15,800.08 | +$1,610  |
| 90%    | $10.71/day      | $17,775.09 | +$3,586  |

At 80-90% save, you're forced to spend less (pocket runs low), so you save more!

### 3. The Power of Rollover

The 1/4 spendable rule creates automatic savings:
- You can only spend 1/4 of pocket per day
- Unspent amounts accumulate
- Larger pocket → larger spendable next day
- At end of period, all remaining goes to Safe

## Files

- **run_jan_to_june.py** - Main simulation (Jan-June 2026)
- **compare_scenarios.py** - Compare different save% and spending
- **budget_simple.py** - Simple example with verification
- **budget_tracker.py** - Original complex implementation (deprecated)
- **simulator.py** - Original simulator (deprecated)
- **verify_formulas.py** - Formula verification tests

## Parameters You Can Change

In `run_jan_to_june.py`:

```python
paycheck = 2000.0           # Your paycheck amount
bills = 500.0               # Bills per paycheck
days_between_checks = 14    # Days between paychecks
daily_spending = 30.0       # How much you spend per day
save_frac = 0.5             # Save fraction (0.5 = 50%)
annual_return = 0.05        # Annual return (0.05 = 5%)
```

## Mathematical Formulas

### Compound Growth

After `n` days at annual rate `r`:
```
P_n = P_0 × (1 + r)^(n/365)
```

### Total Contributions

After `n` pay periods, with contribution `C` per period:
```
Total = P_0 × (1 + g)^n + C × [(1 + g)^n - 1] / g
```

Where:
- `P_0` = starting principal
- `C` = contribution per period
- `g` = periodic growth rate
- `n` = number of periods

### Save Fraction Impact

With no starting principal (`P_0 = 0`):
```
Final Net Worth ∝ save_fraction
```

Increasing save% by X% increases contributions by X%, which increases final net worth by approximately X% (when spending is flexible).

## License

MIT
