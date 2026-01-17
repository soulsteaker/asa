"""
Budget Reporting and Visualization Tools
Generates formatted reports, tables, and exports for budget simulations.
"""

from typing import List, Optional
from datetime import datetime
import csv
from budget_tracker import BudgetTracker, DailyRecord


class BudgetReporter:
    """Generates various reports from budget tracking data"""

    def __init__(self, tracker: BudgetTracker):
        self.tracker = tracker

    def format_currency(self, amount: float) -> str:
        """Format amount as currency"""
        return f"${amount:,.2f}"

    def print_summary(self):
        """Print overall summary statistics"""
        stats = self.tracker.get_summary_stats()

        print("\n" + "=" * 70)
        print("BUDGET SUMMARY")
        print("=" * 70)
        print(f"Period: {stats['days_tracked']} days")
        print(f"Paychecks Received: {stats['paychecks_received']}")
        print()
        print(f"Total Paycheck Income:  {self.format_currency(stats['total_paychecks'])}")
        print(f"Total Bills Paid:       {self.format_currency(stats['total_bills'])}")
        print(f"Total Leftover:         {self.format_currency(stats['total_leftover'])}")
        print()
        print(f"Total Spent:            {self.format_currency(stats['total_spent'])}")
        print(f"Average Daily Spend:    {self.format_currency(stats['avg_daily_spend'])}")
        print()
        print(f"Safe Balance:           {self.format_currency(stats['safe_balance'])}")
        print(f"Pocket Balance:         {self.format_currency(stats['pocket_balance'])}")
        print(f"Total Net Worth:        {self.format_currency(stats['total_net_worth'])}")
        print()
        print(f"Pocket Range: {self.format_currency(stats['min_pocket'])} "
              f"to {self.format_currency(stats['max_pocket'])}")
        print("=" * 70)

    def print_monthly_table(self, monthly_data: List[dict]):
        """Print monthly summary table"""
        if not monthly_data:
            print("No monthly data available")
            return

        print("\n" + "=" * 110)
        print("MONTHLY BREAKDOWN")
        print("=" * 110)

        # Header
        print(f"{'Month':<12} {'Days':<6} {'Spent':<12} {'Avg/Day':<12} "
              f"{'Safe':<14} {'Pocket':<14} {'Net Worth':<14}")
        print("-" * 110)

        # Data rows
        for month in monthly_data:
            month_name = datetime(month['year'], month['month'], 1).strftime('%b %Y')
            print(f"{month_name:<12} "
                  f"{month['days']:<6} "
                  f"{self.format_currency(month['total_spent']):<12} "
                  f"{self.format_currency(month['avg_daily_spend']):<12} "
                  f"{self.format_currency(month['ending_safe']):<14} "
                  f"{self.format_currency(month['ending_pocket']):<14} "
                  f"{self.format_currency(month['total_net_worth']):<14}")

        print("=" * 110)

    def print_daily_detail(self, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          max_rows: int = 50):
        """
        Print detailed daily records

        Args:
            start_date: Optional filter for start date
            end_date: Optional filter for end date
            max_rows: Maximum rows to display
        """
        records = self.tracker.daily_records

        # Filter by date range if specified
        if start_date:
            records = [r for r in records if r.date >= start_date]
        if end_date:
            records = [r for r in records if r.date <= end_date]

        if not records:
            print("No daily records available")
            return

        # Limit rows
        if len(records) > max_rows:
            print(f"\nShowing first {max_rows} of {len(records)} days...")
            records = records[:max_rows]

        print("\n" + "=" * 110)
        print("DAILY DETAIL")
        print("=" * 110)

        # Header
        print(f"{'Date':<12} {'Allowance':<12} {'Spent':<12} "
              f"{'Pocket Start':<14} {'Pocket End':<14} {'Safe':<14}")
        print("-" * 110)

        # Data rows
        for record in records:
            print(f"{record.date.strftime('%Y-%m-%d'):<12} "
                  f"{self.format_currency(record.daily_allowance):<12} "
                  f"{self.format_currency(record.spent):<12} "
                  f"{self.format_currency(record.pocket_start):<14} "
                  f"{self.format_currency(record.pocket_end):<14} "
                  f"{self.format_currency(record.safe_balance):<14}")

        print("=" * 110)

    def export_to_csv(self, filename: str):
        """
        Export daily records to CSV file

        Args:
            filename: Output CSV filename
        """
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'date', 'pocket_start', 'daily_allowance', 'pocket_available',
                'spent', 'pocket_end', 'safe_balance', 'net_worth'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for record in self.tracker.daily_records:
                writer.writerow({
                    'date': record.date.strftime('%Y-%m-%d'),
                    'pocket_start': f"{record.pocket_start:.2f}",
                    'daily_allowance': f"{record.daily_allowance:.2f}",
                    'pocket_available': f"{record.pocket_available:.2f}",
                    'spent': f"{record.spent:.2f}",
                    'pocket_end': f"{record.pocket_end:.2f}",
                    'safe_balance': f"{record.safe_balance:.2f}",
                    'net_worth': f"{record.pocket_end + record.safe_balance:.2f}"
                })

        print(f"Exported {len(self.tracker.daily_records)} daily records to {filename}")

    def export_monthly_to_csv(self, monthly_data: List[dict], filename: str):
        """
        Export monthly summary to CSV file

        Args:
            monthly_data: Monthly summary data
            filename: Output CSV filename
        """
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'year', 'month', 'month_name', 'days', 'total_spent',
                'avg_daily_spend', 'ending_safe', 'ending_pocket',
                'max_pocket', 'min_pocket', 'total_net_worth'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for month in monthly_data:
                month_name = datetime(month['year'], month['month'], 1).strftime('%B %Y')
                writer.writerow({
                    'year': month['year'],
                    'month': month['month'],
                    'month_name': month_name,
                    'days': month['days'],
                    'total_spent': f"{month['total_spent']:.2f}",
                    'avg_daily_spend': f"{month['avg_daily_spend']:.2f}",
                    'ending_safe': f"{month['ending_safe']:.2f}",
                    'ending_pocket': f"{month['ending_pocket']:.2f}",
                    'max_pocket': f"{month['max_pocket']:.2f}",
                    'min_pocket': f"{month['min_pocket']:.2f}",
                    'total_net_worth': f"{month['total_net_worth']:.2f}"
                })

        print(f"Exported monthly summary to {filename}")


def print_scenario_comparison(results: List[dict]):
    """
    Print comparison table for multiple scenarios

    Args:
        results: List of scenario results from run_scenario_comparison
    """
    print("\n" + "=" * 90)
    print("SCENARIO COMPARISON: IMPACT OF SAVE FRACTION")
    print("=" * 90)

    # Header
    print(f"{'Save %':<10} {'Total Spent':<14} {'Safe Balance':<16} "
          f"{'Pocket Balance':<16} {'Net Worth':<14}")
    print("-" * 90)

    # Data rows
    for result in results:
        stats = result['stats']
        save_pct = result['save_percentage']

        print(f"{save_pct:>6.1f}%   "
              f"${stats['total_spent']:>11,.2f}  "
              f"${stats['safe_balance']:>13,.2f}  "
              f"${stats['pocket_balance']:>13,.2f}  "
              f"${stats['total_net_worth']:>11,.2f}")

    print("=" * 90)

    # Show growth percentages
    if len(results) > 1:
        baseline = results[0]
        print(f"\nCompared to {baseline['save_percentage']:.0f}% save rate:")
        print("-" * 60)

        for result in results[1:]:
            baseline_nw = baseline['stats']['total_net_worth']
            current_nw = result['stats']['total_net_worth']
            pct_change = ((current_nw - baseline_nw) / baseline_nw) * 100

            print(f"  {result['save_percentage']:.0f}% save: "
                  f"Net worth {'+' if pct_change >= 0 else ''}{pct_change:.1f}% "
                  f"(${current_nw - baseline_nw:+,.2f})")

        print()


def print_formula_explanation():
    """Print the budget formula explanation"""
    print("\n" + "=" * 70)
    print("BUDGET SYSTEM FORMULA")
    print("=" * 70)
    print("""
1. PAYCHECK PROCESSING:
   - Leftover L = Paycheck P - Bills B
   - Save to Safe: S = L × save_fraction
   - Add to Pocket Pool: Q = L × (1 - save_fraction)
   - Daily Allowance: d = Q / days_in_period

2. DAILY OPERATION:
   - Pocket Balance = Previous Balance + Daily Allowance
   - Spend what you need
   - Unspent rolls over to next day

3. END OF PAY PERIOD:
   - Sweep remaining Pocket → Safe
   - Reset for next paycheck

4. COMPOUND GROWTH:
   - Safe balance grows daily at rate: (1 + annual_rate)^(1/365) - 1
   - Growth compounds continuously

5. YEAR-END RESET (optional):
   - Keep minimum buffer in Safe (e.g., $10,000)
   - Roll excess → Pocket Pool for next year
   - Increases daily allowance automatically

KEY INSIGHT:
The less you spend daily, the more rolls over → higher pocket balance
→ more swept to Safe → more compound growth → wealth builds faster
    """)
    print("=" * 70)
