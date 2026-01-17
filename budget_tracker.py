"""
Budget Tracking System
Implements a daily pay budget system with compound growth and automatic savings.

Core Formula:
1. Paycheck P - Bills B = Leftover L
2. Split: Save (s*L) to Safe, Spend ((1-s)*L) to Pocket Pool
3. Daily Budget d = Pocket Pool / Days in period
4. Daily: Pocket += d, spend what's needed, rollover rest
5. End of period: sweep leftover to Safe
6. Year-end: keep min buffer, roll excess to next year
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple
import math


@dataclass
class PaycheckEvent:
    """Represents a paycheck event"""
    date: datetime
    amount: float
    bills: float

    @property
    def leftover(self) -> float:
        return self.amount - self.bills


@dataclass
class DailyRecord:
    """Record of a single day's budget activity"""
    date: datetime
    pocket_start: float
    daily_allowance: float
    pocket_available: float
    spent: float
    pocket_end: float
    safe_balance: float

    def __str__(self):
        return (f"{self.date.strftime('%Y-%m-%d')}: "
                f"Pocket ${self.pocket_end:,.2f} | "
                f"Safe ${self.safe_balance:,.2f} | "
                f"Spent ${self.spent:,.2f}")


class BudgetTracker:
    """
    Main budget tracking system implementing the split-save-daily-pay method.
    """

    def __init__(
        self,
        save_fraction: float = 0.5,
        annual_return: float = 0.05,
        year_end_safe_minimum: float = 10000.0,
        starting_safe_balance: float = 0.0,
        starting_pocket_balance: float = 0.0
    ):
        """
        Initialize the budget tracker.

        Args:
            save_fraction: Fraction of leftover to save (0.0 to 1.0)
            annual_return: Annual compound return rate (e.g., 0.05 for 5%)
            year_end_safe_minimum: Minimum to keep in Safe at year-end
            starting_safe_balance: Initial Safe balance
            starting_pocket_balance: Initial Pocket balance
        """
        self.save_fraction = save_fraction
        self.annual_return = annual_return
        self.year_end_safe_minimum = year_end_safe_minimum

        self.safe_balance = starting_safe_balance
        self.pocket_balance = starting_pocket_balance

        self.daily_records: List[DailyRecord] = []
        self.paychecks: List[PaycheckEvent] = []

    def _calculate_periodic_growth_rate(self, periods_per_year: int) -> float:
        """
        Convert annual return to periodic growth rate.

        Args:
            periods_per_year: Number of compounding periods per year

        Returns:
            Periodic growth rate
        """
        return math.pow(1 + self.annual_return, 1 / periods_per_year) - 1

    def _apply_compound_growth(self, days_elapsed: int):
        """
        Apply compound growth to Safe balance.

        Args:
            days_elapsed: Number of days since last growth application
        """
        if days_elapsed > 0 and self.safe_balance > 0:
            daily_rate = self._calculate_periodic_growth_rate(365)
            self.safe_balance *= math.pow(1 + daily_rate, days_elapsed)

    def process_paycheck(
        self,
        paycheck: PaycheckEvent,
        days_in_period: int,
        apply_growth_days: int = 0
    ) -> Tuple[float, float, float]:
        """
        Process a paycheck event.

        Args:
            paycheck: PaycheckEvent object
            days_in_period: Number of days this paycheck should last
            apply_growth_days: Days of growth to apply to Safe before processing

        Returns:
            Tuple of (saved_amount, pocket_pool_amount, daily_allowance)
        """
        # Apply compound growth to Safe if time has passed
        if apply_growth_days > 0:
            self._apply_compound_growth(apply_growth_days)

        # Record paycheck
        self.paychecks.append(paycheck)

        # Calculate amounts
        leftover = paycheck.leftover
        saved_amount = leftover * self.save_fraction
        pocket_pool_amount = leftover * (1 - self.save_fraction)

        # Update balances
        self.safe_balance += saved_amount
        daily_allowance = pocket_pool_amount / days_in_period

        return saved_amount, pocket_pool_amount, daily_allowance

    def process_day(
        self,
        date: datetime,
        daily_allowance: float,
        spent: float,
        apply_growth: bool = True
    ) -> DailyRecord:
        """
        Process a single day's budget activity.

        Args:
            date: Date of the day
            daily_allowance: Daily budget allocation
            spent: Amount spent this day
            apply_growth: Whether to apply daily growth to Safe

        Returns:
            DailyRecord for this day
        """
        # Apply daily growth to Safe
        if apply_growth:
            self._apply_compound_growth(1)

        # Update pocket
        pocket_start = self.pocket_balance
        self.pocket_balance += daily_allowance
        pocket_available = self.pocket_balance
        self.pocket_balance -= spent

        # Create record
        record = DailyRecord(
            date=date,
            pocket_start=pocket_start,
            daily_allowance=daily_allowance,
            pocket_available=pocket_available,
            spent=spent,
            pocket_end=self.pocket_balance,
            safe_balance=self.safe_balance
        )

        self.daily_records.append(record)
        return record

    def sweep_pocket_to_safe(self) -> float:
        """
        Sweep remaining pocket balance into Safe (end of period).

        Returns:
            Amount swept
        """
        swept = self.pocket_balance
        self.safe_balance += swept
        self.pocket_balance = 0.0
        return swept

    def year_end_reset(self) -> Tuple[float, float]:
        """
        Apply year-end rule: keep minimum in Safe, roll excess to Pocket.

        Returns:
            Tuple of (amount_kept_in_safe, amount_rolled_to_pocket)
        """
        if self.safe_balance > self.year_end_safe_minimum:
            excess = self.safe_balance - self.year_end_safe_minimum
            self.safe_balance = self.year_end_safe_minimum
            self.pocket_balance += excess
            return self.year_end_safe_minimum, excess
        else:
            return self.safe_balance, 0.0

    def get_summary_stats(self) -> dict:
        """
        Get summary statistics for the tracking period.

        Returns:
            Dictionary of summary statistics
        """
        if not self.daily_records:
            return {}

        total_spent = sum(r.spent for r in self.daily_records)
        total_paychecks = sum(p.amount for p in self.paychecks)
        total_bills = sum(p.bills for p in self.paychecks)
        total_leftover = total_paychecks - total_bills

        avg_daily_spend = total_spent / len(self.daily_records) if self.daily_records else 0

        max_pocket = max(r.pocket_end for r in self.daily_records)
        min_pocket = min(r.pocket_end for r in self.daily_records)

        return {
            'total_paychecks': total_paychecks,
            'total_bills': total_bills,
            'total_leftover': total_leftover,
            'total_spent': total_spent,
            'avg_daily_spend': avg_daily_spend,
            'safe_balance': self.safe_balance,
            'pocket_balance': self.pocket_balance,
            'total_net_worth': self.safe_balance + self.pocket_balance,
            'max_pocket': max_pocket,
            'min_pocket': min_pocket,
            'days_tracked': len(self.daily_records),
            'paychecks_received': len(self.paychecks)
        }
