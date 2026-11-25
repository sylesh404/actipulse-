"""Comprehensive test suite for Activity Comparison Engine (PROCESS 4)."""

import pandas as pd
import pytest
from modules.activity_comparison import (
    calculate_duration_difference,
    calculate_percentage_change,
    generate_change_status,
    compare_two_days,
    generate_weekly_comparison,
    calculate_weekly_statistics,
    compare_custom_periods,
    generate_comparison_insights,
)


@pytest.fixture
def sample_comparison_df():
    """Create sample activity DataFrame for comparison testing."""
    return pd.DataFrame([
        # Day 1: 2024-01-20
        {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "10:00",
         "activity_label": "Walking", "duration_minutes": 60.0},
        {"activity_date": "2024-01-20", "start_time": "10:00", "end_time": "12:00",
         "activity_label": "Sitting", "duration_minutes": 120.0},
        {"activity_date": "2024-01-20", "start_time": "12:00", "end_time": "12:30",
         "activity_label": "Standing", "duration_minutes": 30.0},
        
        # Day 2: 2024-01-21
        {"activity_date": "2024-01-21", "start_time": "09:00", "end_time": "10:30",
         "activity_label": "Walking", "duration_minutes": 90.0},
        {"activity_date": "2024-01-21", "start_time": "10:30", "end_time": "12:00",
         "activity_label": "Sitting", "duration_minutes": 90.0},
        {"activity_date": "2024-01-21", "start_time": "12:00", "end_time": "12:30",
         "activity_label": "Standing", "duration_minutes": 30.0},
        {"activity_date": "2024-01-21", "start_time": "14:00", "end_time": "15:00",
         "activity_label": "Running", "duration_minutes": 60.0},
        
        # Day 3-7 for weekly testing
        {"activity_date": "2024-01-22", "start_time": "09:00", "end_time": "10:00",
         "activity_label": "Walking", "duration_minutes": 60.0},
        {"activity_date": "2024-01-23", "start_time": "09:00", "end_time": "11:00",
         "activity_label": "Sitting", "duration_minutes": 120.0},
        {"activity_date": "2024-01-24", "start_time": "09:00", "end_time": "09:45",
         "activity_label": "Walking", "duration_minutes": 45.0},
        {"activity_date": "2024-01-25", "start_time": "09:00", "end_time": "10:30",
         "activity_label": "Walking", "duration_minutes": 90.0},
        {"activity_date": "2024-01-26", "start_time": "09:00", "end_time": "11:00",
         "activity_label": "Sitting", "duration_minutes": 120.0},
    ])


@pytest.fixture
def empty_df():
    """Create empty DataFrame."""
    return pd.DataFrame(columns=["activity_date", "start_time", "end_time", "activity_label", "duration_minutes"])


class TestDurationDifference:
    """Test duration difference calculation."""
    
    def test_positive_difference(self):
        """Test calculation with increase."""
        diff = calculate_duration_difference(60.0, 90.0)
        assert diff == 30.0
    
    def test_negative_difference(self):
        """Test calculation with decrease."""
        diff = calculate_duration_difference(120.0, 90.0)
        assert diff == -30.0
    
    def test_zero_difference(self):
        """Test calculation with no change."""
        diff = calculate_duration_difference(60.0, 60.0)
        assert diff == 0.0
    
    def test_from_zero(self):
        """Test calculation from zero baseline."""
        diff = calculate_duration_difference(0.0, 60.0)
        assert diff == 60.0


class TestPercentageChange:
    """Test percentage change calculation."""
    
    def test_percentage_increase(self):
        """Test percentage with increase."""
        pct = calculate_percentage_change(60.0, 90.0)
        assert pct == 50.0  # (90-60)/60 * 100 = 50%
    
    def test_percentage_decrease(self):
        """Test percentage with decrease."""
        pct = calculate_percentage_change(120.0, 90.0)
        assert pct == -25.0  # (90-120)/120 * 100 = -25%
    
    def test_percentage_no_change(self):
        """Test percentage with no change."""
        pct = calculate_percentage_change(60.0, 60.0)
        assert pct == 0.0
    
    def test_percentage_from_zero(self):
        """Test percentage from zero baseline (undefined)."""
        pct = calculate_percentage_change(0.0, 60.0)
        assert pct is None
    
    def test_percentage_double(self):
        """Test percentage when value doubles."""
        pct = calculate_percentage_change(50.0, 100.0)
        assert pct == 100.0


class TestChangeStatus:
    """Test change status generation."""
    
    def test_status_increased(self):
        """Test increased status."""
        status = generate_change_status(60.0, 90.0)
        assert status == "increased"
    
    def test_status_decreased(self):
        """Test decreased status."""
        status = generate_change_status(90.0, 60.0)
        assert status == "decreased"
    
    def test_status_unchanged(self):
        """Test unchanged status."""
        status = generate_change_status(60.0, 60.0)
        assert status == "unchanged"
    
    def test_status_newly_recorded(self):
        """Test newly recorded status."""
        status = generate_change_status(0.0, 60.0)
        assert status == "newly_recorded"


class TestTwoDayComparison:
    """Test day-to-day comparison."""
    
    def test_compare_two_days(self, sample_comparison_df):
        """Test comparing two specific days."""
        comparison = compare_two_days(sample_comparison_df, "2024-01-20", "2024-01-21")
        
        assert comparison.previous_date == "2024-01-20"
        assert comparison.current_date == "2024-01-21"
        assert comparison.previous_total == 210.0  # 60+120+30
        assert comparison.current_total == 270.0  # 90+90+30+60
        assert comparison.total_difference == 60.0
        assert comparison.activities_compared == 4  # Walking, Sitting, Standing, Running
        
        # Check specific activity comparisons
        walking = next(c for c in comparison.comparisons if c.activity_label == "Walking")
        assert walking.previous_duration == 60.0
        assert walking.current_duration == 90.0
        assert walking.absolute_difference == 30.0
        assert walking.percentage_change == 50.0
        assert walking.change_status == "increased"
        
        sitting = next(c for c in comparison.comparisons if c.activity_label == "Sitting")
        assert sitting.previous_duration == 120.0
        assert sitting.current_duration == 90.0
        assert sitting.absolute_difference == -30.0
        assert sitting.percentage_change == -25.0
        assert sitting.change_status == "decreased"
        
        standing = next(c for c in comparison.comparisons if c.activity_label == "Standing")
        assert standing.previous_duration == 30.0
        assert standing.current_duration == 30.0
        assert standing.absolute_difference == 0.0
        assert standing.change_status == "unchanged"
        
        running = next(c for c in comparison.comparisons if c.activity_label == "Running")
        assert running.previous_duration == 0.0
        assert running.current_duration == 60.0
        assert running.change_status == "newly_recorded"
    
    def test_compare_empty_df(self, empty_df):
        """Test comparison with empty DataFrame."""
        comparison = compare_two_days(empty_df, "2024-01-20", "2024-01-21")
        
        assert comparison.previous_total == 0.0
        assert comparison.current_total == 0.0
        assert comparison.activities_compared == 0
    
    def test_compare_missing_date(self, sample_comparison_df):
        """Test comparison when one date has no data."""
        comparison = compare_two_days(sample_comparison_df, "2024-01-20", "2024-01-30")
        
        assert comparison.previous_total == 210.0
        assert comparison.current_total == 0.0
        assert comparison.total_difference == -210.0


class TestWeeklyComparison:
    """Test weekly comparison and statistics."""
    
    def test_weekly_comparison(self, sample_comparison_df):
        """Test weekly comparison generation."""
        weekly = generate_weekly_comparison(sample_comparison_df, "2024-01-20", num_days=7)
        
        assert len(weekly.dates) == 7
        assert len(weekly.daily_totals) == 7
        assert weekly.days_with_data == 7  # All 7 days have some data
        
        # Check first day
        assert weekly.dates[0] == "2024-01-20"
        assert weekly.daily_totals[0] == 210.0
        assert weekly.daily_walking[0] == 60.0
        assert weekly.daily_sitting[0] == 120.0
        
        # Check totals
        assert weekly.total_walking > 0
        assert weekly.total_sitting > 0
        assert weekly.average_daily_duration > 0
    
    def test_weekly_statistics(self, sample_comparison_df):
        """Test weekly statistics extraction."""
        weekly = generate_weekly_comparison(sample_comparison_df, "2024-01-20", num_days=7)
        stats = calculate_weekly_statistics(weekly)
        
        assert "highest_walking" in stats
        assert "lowest_walking" in stats
        assert "total_walking" in stats
        assert "average_daily" in stats
        assert stats["days_with_data"] == 7
    
    def test_weekly_with_missing_days(self, sample_comparison_df):
        """Test weekly comparison with days that have no data."""
        weekly = generate_weekly_comparison(sample_comparison_df, "2024-01-27", num_days=7)
        
        # Days after 2024-01-26 should have no data
        assert weekly.dates[-1] == "2024-02-02"
        # Should handle missing days gracefully
        assert all(isinstance(v, float) for v in weekly.daily_totals)


class TestCustomPeriodComparison:
    """Test custom date range comparison."""
    
    def test_period_comparison(self, sample_comparison_df):
        """Test comparing two custom periods."""
        comparison = compare_custom_periods(
            sample_comparison_df,
            "2024-01-20", "2024-01-21",
            "2024-01-22", "2024-01-23"
        )
        
        assert comparison.period_a_start == "2024-01-20"
        assert comparison.period_a_end == "2024-01-21"
        assert comparison.period_b_start == "2024-01-22"
        assert comparison.period_b_end == "2024-01-23"
        
        # Period A: Days 1-2
        assert comparison.period_a_total == 480.0  # 210 + 270
        assert comparison.period_a_walking == 150.0  # 60 + 90
        
        # Period B: Days 3-4
        assert comparison.period_b_total == 180.0  # 60 + 120
        assert comparison.period_b_walking == 60.0
        
        # Differences
        assert comparison.total_difference == -300.0  # B - A
        assert comparison.walking_difference == -90.0
    
    def test_period_comparison_single_day(self, sample_comparison_df):
        """Test period comparison with single-day periods."""
        comparison = compare_custom_periods(
            sample_comparison_df,
            "2024-01-20", "2024-01-20",
            "2024-01-21", "2024-01-21"
        )
        
        assert comparison.period_a_total == 210.0
        assert comparison.period_b_total == 270.0
        assert comparison.total_difference == 60.0
    
    def test_period_comparison_empty(self, empty_df):
        """Test period comparison with empty data."""
        comparison = compare_custom_periods(
            empty_df,
            "2024-01-20", "2024-01-21",
            "2024-01-22", "2024-01-23"
        )
        
        assert comparison.period_a_total == 0.0
        assert comparison.period_b_total == 0.0
        assert comparison.total_difference == 0.0


class TestComparisonInsights:
    """Test comparison insights generation."""
    
    def test_day_comparison_insights(self, sample_comparison_df):
        """Test insights from day-to-day comparison."""
        comparison = compare_two_days(sample_comparison_df, "2024-01-20", "2024-01-21")
        insights = generate_comparison_insights(comparison=comparison)
        
        assert len(insights) > 0
        insights_text = " ".join(insights)
        
        # Should mention walking increase
        assert "Walking" in insights_text
        assert "increased" in insights_text.lower()
        
        # Should mention sitting decrease
        assert "Sitting" in insights_text
        assert "decreased" in insights_text.lower()
        
        # Should mention running as newly recorded
        assert "Running" in insights_text
        assert "newly recorded" in insights_text.lower()
    
    def test_weekly_insights(self, sample_comparison_df):
        """Test insights from weekly comparison."""
        weekly = generate_weekly_comparison(sample_comparison_df, "2024-01-20", num_days=7)
        insights = generate_comparison_insights(weekly_stats=weekly)
        
        assert len(insights) > 0
        insights_text = " ".join(insights)
        
        # Should mention highest walking day
        assert "highest" in insights_text.lower()
        assert "Walking" in insights_text
    
    def test_period_insights(self, sample_comparison_df):
        """Test insights from period comparison."""
        period_comp = compare_custom_periods(
            sample_comparison_df,
            "2024-01-20", "2024-01-21",
            "2024-01-22", "2024-01-23"
        )
        insights = generate_comparison_insights(period_comparison=period_comp)
        
        assert len(insights) > 0
        insights_text = " ".join(insights)
        
        # Should mention period differences
        assert "Period" in insights_text
    
    def test_insights_no_data(self):
        """Test insights with no comparison data."""
        insights = generate_comparison_insights()
        
        assert len(insights) == 1
        assert "No significant changes" in insights[0]


class TestCustomActivityLabels:
    """Test comparison with custom activity labels."""
    
    def test_custom_labels_comparison(self):
        """Test comparison with custom activity types."""
        df = pd.DataFrame([
            {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "10:00",
             "activity_label": "Yoga", "duration_minutes": 60.0},
            {"activity_date": "2024-01-21", "start_time": "09:00", "end_time": "10:30",
             "activity_label": "Yoga", "duration_minutes": 90.0},
        ])
        
        comparison = compare_two_days(df, "2024-01-20", "2024-01-21")
        
        yoga = next(c for c in comparison.comparisons if c.activity_label == "Yoga")
        assert yoga.previous_duration == 60.0
        assert yoga.current_duration == 90.0
        assert yoga.absolute_difference == 30.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_to_zero_comparison(self):
        """Test comparison when both days have zero duration for an activity."""
        status = generate_change_status(0.0, 0.0)
        assert status == "unchanged"
    
    def test_very_small_change(self):
        """Test with very small duration change."""
        diff = calculate_duration_difference(60.1, 60.2)
        assert abs(diff - 0.1) < 0.01
        
        pct = calculate_percentage_change(60.0, 60.1)
        assert abs(pct - 0.17) < 0.1  # ~0.17%
    
    def test_very_large_percentage(self):
        """Test with very large percentage change."""
        pct = calculate_percentage_change(10.0, 1000.0)
        assert pct == 9900.0  # 9900% increase


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
