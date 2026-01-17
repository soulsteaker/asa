"""
Budget Simulation Engine
Runs budget simulations over specified time periods with various spending patterns.
"""

from datetime import datetime, timedelta
from typing import Callable, List, Optional
from enum import Enum
from budget_tracker import BudgetTracker, PaycheckEvent, DailyRecord


class PayFrequency(Enum):
    """Pay frequency options"""
    WEEKLY = 7
    BIWEEKLY = 14
    SEMIMONTHLY = 15  # Approximate
    MONTHLY = 30  # Approximate


class SpendingPattern:
    """Defines spending behavior patterns"""

    @staticmethod
    def constant(amount: float) -> Callable[[datetime], float]:
        """Constant daily spending"""
        return lambda date: amount

    @staticmethod
    def variable(min_amount: float, max_amount: float, seed: int = 42) -> Callable[[datetime], float]:
        """Variable daily spending between min and max"""
        import random
        random.seed(seed)
        return lambda date: random.uniform(min_amount, max_amount)

    @staticmethod
    def weekday_weekend(weekday: float, weekend: float) -> Callable[[datetime], float]:
        """Different spending for weekdays vs weekends"""
        def spend(date: datetime) -> float:
            return weekend if date.weekday() >= 5 else weekday
        return spend

    @staticmethod
    def custom(spend_func: Callable[[datetime], float]) -> Callable[[datetime], float]:
        """Custom spending function"""
        return spend_func


class BudgetSimulator:
    """
    Simulates budget tracking over a time period with specified parameters.
    """

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        paycheck_amount: float,
        bills_per_paycheck: float,
        pay_frequency: PayFrequency,
        first_paycheck_date: datetime,
        spending_pattern: Callable[[datetime], float],
        save_fraction: float = 0.5,
        annual_return: float = 0.05,
        starting_safe: float = 0.0,
        starting_pocket: float = 0.0
    ):
        """
        Initialize the simulator.

        Args:
            start_date: Simulation start date
            end_date: Simulation end date
            paycheck_amount: Gross paycheck amount
            bills_per_paycheck: Bills to pay per paycheck
            pay_frequency: How often paychecks arrive
            first_paycheck_date: Date of first paycheck
            spending_pattern: Function that returns spending amount for a given date
            save_fraction: Fraction of leftover to save
            annual_return: Annual compound return rate
            starting_safe: Starting Safe balance
            starting_pocket: Starting Pocket balance
        """
        self.start_date = start_date
        self.end_date = end_date
        self.paycheck_amount = paycheck_amount
        self.bills_per_paycheck = bills_per_paycheck
        self.pay_frequency = pay_frequency
        self.first_paycheck_date = first_paycheck_date
        self.spending_pattern = spending_pattern
        self.save_fraction = save_fraction
        self.annual_return = annual_return

        self.tracker = BudgetTracker(
            save_fraction=save_fraction,
            annual_return=annual_return,
            starting_safe_balance=starting_safe,
            starting_pocket_balance=starting_pocket
        )

        self.paycheck_dates: List[datetime] = []
        self.current_daily_allowance: float = 0.0

    def _generate_paycheck_dates(self) -> List[datetime]:
        """Generate all paycheck dates within the simulation period"""
        dates = []
        current = self.first_paycheck_date

        # Add paychecks before start if needed
        while current < self.start_date:
            current += timedelta(days=self.pay_frequency.value)

        # Add paychecks within simulation period
        while current <= self.end_date:
            dates.append(current)
            current += timedelta(days=self.pay_frequency.value)

        return dates

    def run(self) -> BudgetTracker:
        """
        Run the simulation.

        Returns:
            BudgetTracker with complete simulation results
        """
        # Generate paycheck dates
        self.paycheck_dates = self._generate_paycheck_dates()

        # Track current paycheck period
        current_paycheck_idx = 0
        next_paycheck_date = self.paycheck_dates[current_paycheck_idx] if self.paycheck_dates else None

        # Initialize first paycheck at start of simulation
        # This ensures we have money to spend from day 1
        if next_paycheck_date and next_paycheck_date >= self.start_date:
            days_in_period = self.pay_frequency.value
            paycheck = PaycheckEvent(
                date=next_paycheck_date,
                amount=self.paycheck_amount,
                bills=self.bills_per_paycheck
            )
            _, _, self.current_daily_allowance = self.tracker.process_paycheck(
                paycheck, days_in_period
            )
            current_paycheck_idx += 1
            next_paycheck_date = (self.paycheck_dates[current_paycheck_idx]
                                 if current_paycheck_idx < len(self.paycheck_dates)
                                 else None)

        # Simulate each day
        current_date = self.start_date
        last_paycheck_date = self.first_paycheck_date

        while current_date <= self.end_date:
            # Check if paycheck arrives today
            if next_paycheck_date and current_date >= next_paycheck_date:
                # Sweep pocket to safe at end of pay period
                self.tracker.sweep_pocket_to_safe()

                # Calculate days since last paycheck for growth
                days_since_last = (next_paycheck_date - last_paycheck_date).days

                # Process new paycheck
                paycheck = PaycheckEvent(
                    date=next_paycheck_date,
                    amount=self.paycheck_amount,
                    bills=self.bills_per_paycheck
                )

                days_in_period = self.pay_frequency.value
                _, _, self.current_daily_allowance = self.tracker.process_paycheck(
                    paycheck,
                    days_in_period,
                    apply_growth_days=0  # Growth applied daily instead
                )

                last_paycheck_date = next_paycheck_date
                current_paycheck_idx += 1
                next_paycheck_date = (self.paycheck_dates[current_paycheck_idx]
                                     if current_paycheck_idx < len(self.paycheck_dates)
                                     else None)

            # Get spending for this day
            spent = self.spending_pattern(current_date)

            # Process the day
            self.tracker.process_day(
                date=current_date,
                daily_allowance=self.current_daily_allowance,
                spent=spent,
                apply_growth=True
            )

            current_date += timedelta(days=1)

        # Sweep any remaining pocket balance to safe at end of simulation
        if self.tracker.pocket_balance > 0:
            self.tracker.sweep_pocket_to_safe()

        return self.tracker

    def get_monthly_summary(self) -> List[dict]:
        """
        Get summary statistics by month.

        Returns:
            List of monthly summary dictionaries
        """
        if not self.tracker.daily_records:
            return []

        monthly_data = {}

        for record in self.tracker.daily_records:
            month_key = (record.date.year, record.date.month)

            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'year': record.date.year,
                    'month': record.date.month,
                    'days': 0,
                    'total_spent': 0.0,
                    'ending_safe': 0.0,
                    'ending_pocket': 0.0,
                    'max_pocket': 0.0,
                    'min_pocket': float('inf')
                }

            month = monthly_data[month_key]
            month['days'] += 1
            month['total_spent'] += record.spent
            month['ending_safe'] = record.safe_balance
            month['ending_pocket'] = record.pocket_end
            month['max_pocket'] = max(month['max_pocket'], record.pocket_end)
            month['min_pocket'] = min(month['min_pocket'], record.pocket_end)

        # Convert to list and add calculated fields
        result = []
        for key in sorted(monthly_data.keys()):
            month = monthly_data[key]
            month['avg_daily_spend'] = month['total_spent'] / month['days']
            month['total_net_worth'] = month['ending_safe'] + month['ending_pocket']
            result.append(month)

        return result


def run_scenario_comparison(
    start_date: datetime,
    end_date: datetime,
    paycheck_amount: float,
    bills_per_paycheck: float,
    pay_frequency: PayFrequency,
    first_paycheck_date: datetime,
    spending_pattern: Callable[[datetime], float],
    save_fractions: List[float],
    annual_return: float = 0.05
) -> List[dict]:
    """
    Run multiple simulations with different save fractions.

    Args:
        (same as BudgetSimulator plus)
        save_fractions: List of save fractions to test (e.g., [0.3, 0.5, 0.7])

    Returns:
        List of result dictionaries, one per save fraction
    """
    results = []

    for save_frac in save_fractions:
        sim = BudgetSimulator(
            start_date=start_date,
            end_date=end_date,
            paycheck_amount=paycheck_amount,
            bills_per_paycheck=bills_per_paycheck,
            pay_frequency=pay_frequency,
            first_paycheck_date=first_paycheck_date,
            spending_pattern=spending_pattern,
            save_fraction=save_frac,
            annual_return=annual_return
        )

        tracker = sim.run()
        stats = tracker.get_summary_stats()
        monthly = sim.get_monthly_summary()

        results.append({
            'save_fraction': save_frac,
            'save_percentage': save_frac * 100,
            'stats': stats,
            'monthly_summary': monthly,
            'tracker': tracker
        })

    return results
