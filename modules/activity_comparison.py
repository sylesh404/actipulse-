"""Cross-day activity duration comparison engine for ActiPulse AI.

PROCESS 4 implementation: Comprehensive comparison functionality for analyzing
activity duration changes across different dates, weekly trends, custom periods,
and generating data-driven insights about activity patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from modules.activity_analytics import (
    calculate_total_duration,
    calculate_activity_duration_by_label,
    calculate_daily_summary,
)


@dataclass(frozen=True)
class ActivityComparison:
    """Comparison details for a single activity between two dates."""

    activity_label: str
    previous_duration: float
    current_duration: float
    absolute_difference: float
    percentage_change: float | None
    change_status: str  # "increased", "decreased", "unchanged", "newly_recorded"


@dataclass
class DayComparisonResult:
    """Complete comparison summary between two activity dates."""

    previous_date: str
    current_date: str
    comparisons: list[ActivityComparison] = field(default_factory=list)
    previous_total: float = 0.0
    current_total: float = 0.0
    total_difference: float = 0.0
    activities_compared: int = 0


@dataclass
class WeeklyStatistics:
    """Weekly activity statistics and trends."""

    dates: list[str] = field(default_factory=list)
    daily_totals: list[float] = field(default_factory=list)
    daily_walking: list[float] = field(default_factory=list)
    daily_sitting: list[float] = field(default_factory=list)
    daily_standing: list[float] = field(default_factory=list)
    daily_running: list[float] = field(default_factory=list)
    daily_cycling: list[float] = field(default_factory=list)
    
    # Summary statistics
    highest_walking_duration: float = 0.0
    lowest_walking_duration: float = 0.0
    highest_sitting_duration: float = 0.0
    total_walking: float = 0.0
    total_sitting: float = 0.0
    total_standing: float = 0.0
    average_daily_duration: float = 0.0
    days_with_data: int = 0


@dataclass
class PeriodComparisonResult:
    """Comparison between two custom date ranges."""

    period_a_start: str
    period_a_end: str
    period_b_start: str
    period_b_end: str
    
    period_a_walking: float = 0.0
    period_a_sitting: float = 0.0
    period_a_standing: float = 0.0
    period_a_running: float = 0.0
    period_a_cycling: float = 0.0
    period_a_total: float = 0.0
    
    period_b_walking: float = 0.0
    period_b_sitting: float = 0.0
    period_b_standing: float = 0.0
    period_b_running: float = 0.0
    period_b_cycling: float = 0.0
    period_b_total: float = 0.0
    
    walking_difference: float = 0.0
    sitting_difference: float = 0.0
    standing_difference: float = 0.0
    running_difference: float = 0.0
    cycling_difference: float = 0.0
    total_difference: float = 0.0


def calculate_duration_difference(
    previous_duration: float,
    current_duration: float,
) -> float:
    """Calculate absolute duration difference between two values.
    
    Args:
        previous_duration: Duration from previous/baseline period
        current_duration: Duration from current/target period
        
    Returns:
        Difference (current - previous), positive means increase
    """
    return round(current_duration - previous_duration, 2)


def calculate_percentage_change(
    previous_duration: float,
    current_duration: float,
) -> float | None:
    """Calculate percentage change between two duration values.
    
    Args:
        previous_duration: Duration from previous/baseline period
        current_duration: Duration from current/target period
        
    Returns:
        Percentage change, or None if previous is zero
    """
    if previous_duration == 0:
        return None
    
    change = ((current_duration - previous_duration) / previous_duration) * 100.0
    return round(change, 1)


def generate_change_status(
    previous_duration: float,
    current_duration: float,
) -> str:
    """Generate human-readable change status.
    
    Args:
        previous_duration: Duration from previous/baseline period
        current_duration: Duration from current/target period
        
    Returns:
        Status string: "increased", "decreased", "unchanged", "newly_recorded"
    """
    if previous_duration == 0 and current_duration > 0:
        return "newly_recorded"
    elif current_duration > previous_duration:
        return "increased"
    elif current_duration < previous_duration:
        return "decreased"
    else:
        return "unchanged"


def compare_two_days(
    df: pd.DataFrame,
    previous_date: str,
    current_date: str,
) -> DayComparisonResult:
    """Compare activity durations between two specific dates.
    
    Args:
        df: DataFrame with activity records
        previous_date: Previous/baseline date (YYYY-MM-DD)
        current_date: Current/target date (YYYY-MM-DD)
        
    Returns:
        DayComparisonResult with detailed comparison
    """
    if df is None or df.empty:
        return DayComparisonResult(
            previous_date=previous_date,
            current_date=current_date,
        )
    
    # Get data for each date
    prev_df = df[df["activity_date"] == previous_date].copy()
    curr_df = df[df["activity_date"] == current_date].copy()
    
    # Get all unique activities from both dates
    all_activities = set()
    if not prev_df.empty:
        all_activities.update(prev_df["activity_label"].unique())
    if not curr_df.empty:
        all_activities.update(curr_df["activity_label"].unique())
    
    # Calculate comparisons for each activity
    comparisons = []
    for activity in sorted(all_activities):
        prev_duration = calculate_activity_duration_by_label(prev_df, activity)
        curr_duration = calculate_activity_duration_by_label(curr_df, activity)
        
        diff = calculate_duration_difference(prev_duration, curr_duration)
        pct_change = calculate_percentage_change(prev_duration, curr_duration)
        status = generate_change_status(prev_duration, curr_duration)
        
        comparisons.append(ActivityComparison(
            activity_label=activity,
            previous_duration=prev_duration,
            current_duration=curr_duration,
            absolute_difference=diff,
            percentage_change=pct_change,
            change_status=status,
        ))
    
    # Calculate totals
    prev_total = calculate_total_duration(prev_df)
    curr_total = calculate_total_duration(curr_df)
    total_diff = calculate_duration_difference(prev_total, curr_total)
    
    return DayComparisonResult(
        previous_date=previous_date,
        current_date=current_date,
        comparisons=comparisons,
        previous_total=prev_total,
        current_total=curr_total,
        total_difference=total_diff,
        activities_compared=len(comparisons),
    )


def generate_weekly_comparison(
    df: pd.DataFrame,
    start_date: str,
    num_days: int = 7,
) -> WeeklyStatistics:
    """Generate weekly activity statistics and daily breakdowns.
    
    Args:
        df: DataFrame with activity records
        start_date: Starting date (YYYY-MM-DD)
        num_days: Number of days to analyze (default 7)
        
    Returns:
        WeeklyStatistics with daily breakdowns and summary stats
    """
    if df is None or df.empty:
        return WeeklyStatistics()
    
    # Generate date range
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    dates = [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]
    
    # Calculate daily metrics
    daily_totals = []
    daily_walking = []
    daily_sitting = []
    daily_standing = []
    daily_running = []
    daily_cycling = []
    
    for date in dates:
        daily_df = df[df["activity_date"] == date]
        
        daily_totals.append(calculate_total_duration(daily_df))
        daily_walking.append(calculate_activity_duration_by_label(daily_df, "Walking"))
        daily_sitting.append(calculate_activity_duration_by_label(daily_df, "Sitting"))
        daily_standing.append(calculate_activity_duration_by_label(daily_df, "Standing"))
        daily_running.append(calculate_activity_duration_by_label(daily_df, "Running"))
        daily_cycling.append(calculate_activity_duration_by_label(daily_df, "Cycling"))
    
    # Calculate summary statistics (excluding days with no data)
    walking_values = [v for v in daily_walking if v > 0]
    sitting_values = [v for v in daily_sitting if v > 0]
    total_values = [v for v in daily_totals if v > 0]
    
    return WeeklyStatistics(
        dates=dates,
        daily_totals=daily_totals,
        daily_walking=daily_walking,
        daily_sitting=daily_sitting,
        daily_standing=daily_standing,
        daily_running=daily_running,
        daily_cycling=daily_cycling,
        highest_walking_duration=max(walking_values) if walking_values else 0.0,
        lowest_walking_duration=min(walking_values) if walking_values else 0.0,
        highest_sitting_duration=max(sitting_values) if sitting_values else 0.0,
        total_walking=sum(daily_walking),
        total_sitting=sum(daily_sitting),
        total_standing=sum(daily_standing),
        average_daily_duration=sum(total_values) / len(total_values) if total_values else 0.0,
        days_with_data=len(total_values),
    )


def calculate_weekly_statistics(weekly_stats: WeeklyStatistics) -> dict[str, Any]:
    """Extract key statistics from weekly data.
    
    Args:
        weekly_stats: WeeklyStatistics object
        
    Returns:
        Dictionary with key metrics
    """
    return {
        "highest_walking": weekly_stats.highest_walking_duration,
        "lowest_walking": weekly_stats.lowest_walking_duration,
        "highest_sitting": weekly_stats.highest_sitting_duration,
        "total_walking": weekly_stats.total_walking,
        "total_sitting": weekly_stats.total_sitting,
        "total_standing": weekly_stats.total_standing,
        "average_daily": weekly_stats.average_daily_duration,
        "days_with_data": weekly_stats.days_with_data,
    }


def compare_custom_periods(
    df: pd.DataFrame,
    period_a_start: str,
    period_a_end: str,
    period_b_start: str,
    period_b_end: str,
) -> PeriodComparisonResult:
    """Compare activity durations between two custom date ranges.
    
    Args:
        df: DataFrame with activity records
        period_a_start: Period A start date (YYYY-MM-DD)
        period_a_end: Period A end date (YYYY-MM-DD)
        period_b_start: Period B start date (YYYY-MM-DD)
        period_b_end: Period B end date (YYYY-MM-DD)
        
    Returns:
        PeriodComparisonResult with detailed comparison
    """
    if df is None or df.empty:
        return PeriodComparisonResult(
            period_a_start=period_a_start,
            period_a_end=period_a_end,
            period_b_start=period_b_start,
            period_b_end=period_b_end,
        )
    
    # Filter data for each period
    period_a_df = df[
        (df["activity_date"] >= period_a_start) &
        (df["activity_date"] <= period_a_end)
    ].copy()
    
    period_b_df = df[
        (df["activity_date"] >= period_b_start) &
        (df["activity_date"] <= period_b_end)
    ].copy()
    
    # Calculate durations for period A
    a_walking = calculate_activity_duration_by_label(period_a_df, "Walking")
    a_sitting = calculate_activity_duration_by_label(period_a_df, "Sitting")
    a_standing = calculate_activity_duration_by_label(period_a_df, "Standing")
    a_running = calculate_activity_duration_by_label(period_a_df, "Running")
    a_cycling = calculate_activity_duration_by_label(period_a_df, "Cycling")
    a_total = calculate_total_duration(period_a_df)
    
    # Calculate durations for period B
    b_walking = calculate_activity_duration_by_label(period_b_df, "Walking")
    b_sitting = calculate_activity_duration_by_label(period_b_df, "Sitting")
    b_standing = calculate_activity_duration_by_label(period_b_df, "Standing")
    b_running = calculate_activity_duration_by_label(period_b_df, "Running")
    b_cycling = calculate_activity_duration_by_label(period_b_df, "Cycling")
    b_total = calculate_total_duration(period_b_df)
    
    # Calculate differences
    walking_diff = calculate_duration_difference(a_walking, b_walking)
    sitting_diff = calculate_duration_difference(a_sitting, b_sitting)
    standing_diff = calculate_duration_difference(a_standing, b_standing)
    running_diff = calculate_duration_difference(a_running, b_running)
    cycling_diff = calculate_duration_difference(a_cycling, b_cycling)
    total_diff = calculate_duration_difference(a_total, b_total)
    
    return PeriodComparisonResult(
        period_a_start=period_a_start,
        period_a_end=period_a_end,
        period_b_start=period_b_start,
        period_b_end=period_b_end,
        period_a_walking=a_walking,
        period_a_sitting=a_sitting,
        period_a_standing=a_standing,
        period_a_running=a_running,
        period_a_cycling=a_cycling,
        period_a_total=a_total,
        period_b_walking=b_walking,
        period_b_sitting=b_sitting,
        period_b_standing=b_standing,
        period_b_running=b_running,
        period_b_cycling=b_cycling,
        period_b_total=b_total,
        walking_difference=walking_diff,
        sitting_difference=sitting_diff,
        standing_difference=standing_diff,
        running_difference=running_diff,
        cycling_difference=cycling_diff,
        total_difference=total_diff,
    )


def generate_comparison_insights(
    comparison: DayComparisonResult | None = None,
    weekly_stats: WeeklyStatistics | None = None,
    period_comparison: PeriodComparisonResult | None = None,
) -> list[str]:
    """Generate data-driven insights about activity changes.
    
    Args:
        comparison: Optional day-to-day comparison result
        weekly_stats: Optional weekly statistics
        period_comparison: Optional period comparison result
        
    Returns:
        List of insight strings
    """
    insights = []
    
    # Day-to-day insights
    if comparison and comparison.comparisons:
        for comp in comparison.comparisons:
            if comp.change_status == "newly_recorded":
                insights.append(
                    f"{comp.activity_label} was newly recorded on {comparison.current_date} "
                    f"with {comp.current_duration:.0f} minutes."
                )
            elif comp.change_status == "increased":
                insights.append(
                    f"{comp.activity_label} duration increased by {comp.absolute_difference:.0f} minutes "
                    f"({comp.percentage_change:+.1f}% change)."
                )
            elif comp.change_status == "decreased":
                insights.append(
                    f"{comp.activity_label} duration decreased by {abs(comp.absolute_difference):.0f} minutes "
                    f"({comp.percentage_change:.1f}% change)."
                )
            elif comp.change_status == "unchanged" and comp.previous_duration > 0:
                insights.append(
                    f"{comp.activity_label} duration remained unchanged at {comp.current_duration:.0f} minutes."
                )
    
    # Weekly insights
    if weekly_stats and weekly_stats.days_with_data > 0:
        if weekly_stats.highest_walking_duration > 0:
            # Find day with highest walking
            max_idx = weekly_stats.daily_walking.index(weekly_stats.highest_walking_duration)
            day_name = datetime.strptime(weekly_stats.dates[max_idx], "%Y-%m-%d").strftime("%A")
            insights.append(
                f"Walking had its highest recorded duration on {day_name} "
                f"({weekly_stats.highest_walking_duration:.0f} minutes)."
            )
        
        insights.append(
            f"Average recorded activity duration: {weekly_stats.average_daily_duration:.0f} minutes "
            f"per day (across {weekly_stats.days_with_data} days with data)."
        )
    
    # Period comparison insights
    if period_comparison and period_comparison.period_b_total > 0:
        if period_comparison.walking_difference != 0:
            direction = "more" if period_comparison.walking_difference > 0 else "less"
            insights.append(
                f"Period B contained {abs(period_comparison.walking_difference):.0f} minutes {direction} "
                f"walking than Period A."
            )
        
        if period_comparison.sitting_difference != 0:
            direction = "more" if period_comparison.sitting_difference > 0 else "less"
            insights.append(
                f"Period B contained {abs(period_comparison.sitting_difference):.0f} minutes {direction} "
                f"sitting than Period A."
            )
    
    if not insights:
        insights.append("No significant changes detected in the comparison.")
    
    return insights


def compare_activity_days(
    df: pd.DataFrame,
    baseline_date: str,
    target_date: str,
) -> DayComparisonResult:
    """Legacy function for backward compatibility. Use compare_two_days instead."""
    return compare_two_days(df, baseline_date, target_date)
