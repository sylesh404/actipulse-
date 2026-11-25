"""Comprehensive test suite for Activity Analytics Engine (PROCESS 3)."""

import pandas as pd
import pytest
from modules.activity_analytics import (
    calculate_total_duration,
    calculate_activity_duration_by_label,
    calculate_activity_distribution,
    calculate_activity_statistics,
    calculate_daily_summary,
    analyze_time_periods,
    generate_activity_insights,
    compute_activity_summary,
)


@pytest.fixture
def sample_activity_df():
    """Create sample activity DataFrame for testing."""
    return pd.DataFrame([
        {
            "activity_date": "2024-01-20",
            "start_time": "09:00",
            "end_time": "10:00",
            "activity_label": "Walking",
            "duration_minutes": 60.0,
        },
        {
            "activity_date": "2024-01-20",
            "start_time": "10:00",
            "end_time": "12:00",
            "activity_label": "Sitting",
            "duration_minutes": 120.0,
        },
        {
            "activity_date": "2024-01-20",
            "start_time": "12:00",
            "end_time": "12:30",
            "activity_label": "Walking",
            "duration_minutes": 30.0,
        },
        {
            "activity_date": "2024-01-20",
            "start_time": "12:30",
            "end_time": "13:00",
            "activity_label": "Standing",
            "duration_minutes": 30.0,
        },
        {
            "activity_date": "2024-01-21",
            "start_time": "09:00",
            "end_time": "10:00",
            "activity_label": "Running",
            "duration_minutes": 60.0,
        },
    ])


@pytest.fixture
def empty_df():
    """Create empty DataFrame."""
    return pd.DataFrame(columns=["activity_date", "start_time", "end_time", "activity_label", "duration_minutes"])


class TestTotalDuration:
    """Test total duration calculation."""
    
    def test_calculate_total_duration_valid(self, sample_activity_df):
        """Test total duration calculation with valid data."""
        total = calculate_total_duration(sample_activity_df)
        assert total == 300.0  # 60 + 120 + 30 + 30 + 60
    
    def test_calculate_total_duration_empty(self, empty_df):
        """Test total duration with empty DataFrame."""
        total = calculate_total_duration(empty_df)
        assert total == 0.0
    
    def test_calculate_total_duration_none(self):
        """Test total duration with None input."""
        total = calculate_total_duration(None)
        assert total == 0.0


class TestActivityDurationByLabel:
    """Test activity duration by label calculation."""
    
    def test_walking_duration(self, sample_activity_df):
        """Test walking duration calculation."""
        walking = calculate_activity_duration_by_label(sample_activity_df, "Walking")
        assert walking == 90.0  # 60 + 30
    
    def test_sitting_duration(self, sample_activity_df):
        """Test sitting duration calculation."""
        sitting = calculate_activity_duration_by_label(sample_activity_df, "Sitting")
        assert sitting == 120.0
    
    def test_standing_duration(self, sample_activity_df):
        """Test standing duration calculation."""
        standing = calculate_activity_duration_by_label(sample_activity_df, "Standing")
        assert standing == 30.0
    
    def test_running_duration(self, sample_activity_df):
        """Test running duration calculation."""
        running = calculate_activity_duration_by_label(sample_activity_df, "Running")
        assert running == 60.0
    
    def test_nonexistent_activity(self, sample_activity_df):
        """Test duration for non-existent activity label."""
        cycling = calculate_activity_duration_by_label(sample_activity_df, "Cycling")
        assert cycling == 0.0
    
    def test_empty_df(self, empty_df):
        """Test duration with empty DataFrame."""
        walking = calculate_activity_duration_by_label(empty_df, "Walking")
        assert walking == 0.0


class TestActivityDistribution:
    """Test activity distribution calculation."""
    
    def test_distribution_calculation(self, sample_activity_df):
        """Test activity distribution metrics."""
        distribution = calculate_activity_distribution(sample_activity_df)
        
        assert len(distribution) == 4  # Walking, Sitting, Standing, Running
        
        # Should be sorted by duration descending
        assert distribution[0].activity_label == "Sitting"
        assert distribution[0].total_minutes == 120.0
        assert distribution[0].percentage == 40.0  # 120/300 * 100
        assert distribution[0].session_count == 1
        
        # Find Walking in distribution
        walking_item = next(item for item in distribution if item.activity_label == "Walking")
        assert walking_item.total_minutes == 90.0
        assert walking_item.percentage == 30.0  # 90/300 * 100
        assert walking_item.session_count == 2
        assert walking_item.average_duration == 45.0
        assert walking_item.min_duration == 30.0
        assert walking_item.max_duration == 60.0
    
    def test_distribution_empty(self, empty_df):
        """Test distribution with empty DataFrame."""
        distribution = calculate_activity_distribution(empty_df)
        assert distribution == []
    
    def test_distribution_percentages_sum(self, sample_activity_df):
        """Test that percentages sum to approximately 100."""
        distribution = calculate_activity_distribution(sample_activity_df)
        total_percentage = sum(item.percentage for item in distribution)
        assert abs(total_percentage - 100.0) < 0.1  # Allow small floating point error


class TestActivityStatistics:
    """Test comprehensive activity statistics."""
    
    def test_statistics_calculation(self, sample_activity_df):
        """Test all statistics are calculated correctly."""
        stats = calculate_activity_statistics(sample_activity_df)
        
        assert stats["total_minutes"] == 300.0
        assert stats["total_hours"] == 5.0
        assert stats["total_sessions"] == 5
        assert stats["unique_days"] == 2
        assert stats["average_session_duration"] == 60.0  # 300/5
        assert stats["walking_minutes"] == 90.0
        assert stats["sitting_minutes"] == 120.0
        assert stats["standing_minutes"] == 30.0
        assert stats["running_minutes"] == 60.0
        assert stats["cycling_minutes"] == 0.0
    
    def test_statistics_empty(self, empty_df):
        """Test statistics with empty DataFrame."""
        stats = calculate_activity_statistics(empty_df)
        
        assert stats["total_minutes"] == 0.0
        assert stats["total_hours"] == 0.0
        assert stats["total_sessions"] == 0
        assert stats["unique_days"] == 0
        assert stats["average_session_duration"] == 0.0


class TestDailySummary:
    """Test daily activity summary calculation."""
    
    def test_daily_summary_valid_date(self, sample_activity_df):
        """Test daily summary for existing date."""
        summary = calculate_daily_summary(sample_activity_df, "2024-01-20")
        
        assert summary.activity_date == "2024-01-20"
        assert summary.total_minutes == 240.0  # 60 + 120 + 30 + 30
        assert summary.total_hours == 4.0
        assert summary.total_sessions == 4
        assert summary.walking_minutes == 90.0
        assert summary.sitting_minutes == 120.0
        assert summary.standing_minutes == 30.0
        assert summary.running_minutes == 0.0
        assert summary.most_frequent_activity == "Sitting"
        
        # Check percentages
        assert summary.activity_percentages["Walking"] == 37.5  # 90/240 * 100
        assert summary.activity_percentages["Sitting"] == 50.0  # 120/240 * 100
        assert summary.activity_percentages["Standing"] == 12.5  # 30/240 * 100
    
    def test_daily_summary_nonexistent_date(self, sample_activity_df):
        """Test daily summary for non-existent date."""
        summary = calculate_daily_summary(sample_activity_df, "2024-01-25")
        
        assert summary.activity_date == "2024-01-25"
        assert summary.total_minutes == 0.0
        assert summary.total_sessions == 0
    
    def test_daily_summary_empty_df(self, empty_df):
        """Test daily summary with empty DataFrame."""
        summary = calculate_daily_summary(empty_df, "2024-01-20")
        
        assert summary.total_minutes == 0.0
        assert summary.total_sessions == 0


class TestTimePeriodAnalysis:
    """Test time period analysis."""
    
    def test_time_period_distribution(self):
        """Test activity distribution across time periods."""
        df = pd.DataFrame([
            {"start_time": "06:00", "end_time": "07:00", "activity_label": "Walking", "duration_minutes": 60.0},
            {"start_time": "09:00", "end_time": "11:00", "activity_label": "Sitting", "duration_minutes": 120.0},
            {"start_time": "14:00", "end_time": "15:00", "activity_label": "Standing", "duration_minutes": 60.0},
            {"start_time": "19:00", "end_time": "20:00", "activity_label": "Walking", "duration_minutes": 60.0},
            {"start_time": "22:00", "end_time": "23:00", "activity_label": "Sitting", "duration_minutes": 60.0},
        ])
        
        analysis = analyze_time_periods(df)
        
        assert analysis.early_morning_minutes == 60.0  # 06:00
        assert analysis.morning_minutes == 120.0  # 09:00
        assert analysis.afternoon_minutes == 60.0  # 14:00
        assert analysis.evening_minutes == 60.0  # 19:00
        assert analysis.night_minutes == 60.0  # 22:00
    
    def test_time_period_overnight_activity(self):
        """Test overnight activity handling."""
        df = pd.DataFrame([
            {"start_time": "23:30", "end_time": "00:30", "activity_label": "Sleeping", "duration_minutes": 60.0},
        ])
        
        analysis = analyze_time_periods(df)
        # Should be assigned to Night period (starts at 23:30)
        assert analysis.night_minutes == 60.0
    
    def test_time_period_empty(self, empty_df):
        """Test time period analysis with empty DataFrame."""
        analysis = analyze_time_periods(empty_df)
        
        assert analysis.early_morning_minutes == 0.0
        assert analysis.morning_minutes == 0.0
        assert analysis.afternoon_minutes == 0.0
        assert analysis.evening_minutes == 0.0
        assert analysis.night_minutes == 0.0


class TestActivityInsights:
    """Test activity insights generation."""
    
    def test_insights_generation(self, sample_activity_df):
        """Test that insights are generated from data."""
        insights = generate_activity_insights(sample_activity_df)
        
        assert len(insights) > 0
        assert isinstance(insights, list)
        assert all(isinstance(insight, str) for insight in insights)
        
        # Check for expected insight patterns
        insights_text = " ".join(insights)
        assert "Sitting" in insights_text  # Top activity
        assert "session" in insights_text.lower()
    
    def test_insights_empty(self, empty_df):
        """Test insights with empty data."""
        insights = generate_activity_insights(empty_df)
        
        assert len(insights) == 1
        assert "No activity records" in insights[0]
    
    def test_insights_with_date_filter(self, sample_activity_df):
        """Test insights for specific date."""
        insights = generate_activity_insights(sample_activity_df, "2024-01-20")
        
        assert len(insights) > 0
        insights_text = " ".join(insights)
        assert "Sitting" in insights_text


class TestActivitySummary:
    """Test complete activity summary computation."""
    
    def test_compute_summary(self, sample_activity_df):
        """Test complete summary computation."""
        summary = compute_activity_summary(sample_activity_df)
        
        assert summary.total_minutes == 300.0
        assert summary.total_hours == 5.0
        assert summary.total_sessions == 5
        assert summary.unique_days == 2
        assert summary.top_activity == "Sitting"
        assert len(summary.distribution) == 4
    
    def test_compute_summary_empty(self, empty_df):
        """Test summary with empty DataFrame."""
        summary = compute_activity_summary(empty_df)
        
        assert summary.total_minutes == 0.0
        assert summary.total_sessions == 0
        assert summary.top_activity is None
        assert summary.distribution == []


class TestCustomActivityLabels:
    """Test handling of custom activity labels."""
    
    def test_custom_labels_in_distribution(self):
        """Test that custom labels are included in distribution."""
        df = pd.DataFrame([
            {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "10:00", 
             "activity_label": "Yoga", "duration_minutes": 60.0},
            {"activity_date": "2024-01-20", "start_time": "10:00", "end_time": "11:00", 
             "activity_label": "Swimming", "duration_minutes": 60.0},
        ])
        
        distribution = calculate_activity_distribution(df)
        labels = [item.activity_label for item in distribution]
        
        assert "Yoga" in labels
        assert "Swimming" in labels
    
    def test_custom_labels_in_daily_summary(self):
        """Test custom labels in daily summary."""
        df = pd.DataFrame([
            {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "10:00", 
             "activity_label": "Yoga", "duration_minutes": 60.0},
        ])
        
        summary = calculate_daily_summary(df, "2024-01-20")
        assert summary.other_minutes == 60.0  # Custom labels counted as "other"


class TestOverlappingRecords:
    """Test handling of overlapping activity records."""
    
    def test_overlapping_durations_summed(self):
        """Test that overlapping records have their durations summed (not deduplicated)."""
        df = pd.DataFrame([
            {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "10:00", 
             "activity_label": "Walking", "duration_minutes": 60.0},
            {"activity_date": "2024-01-20", "start_time": "09:30", "end_time": "10:30", 
             "activity_label": "Listening to Music", "duration_minutes": 60.0},
        ])
        
        total = calculate_total_duration(df)
        assert total == 120.0  # Both durations are summed (overlaps are allowed)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_single_record(self):
        """Test with single activity record."""
        df = pd.DataFrame([
            {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "10:00", 
             "activity_label": "Walking", "duration_minutes": 60.0},
        ])
        
        distribution = calculate_activity_distribution(df)
        assert len(distribution) == 1
        assert distribution[0].percentage == 100.0
    
    def test_very_short_duration(self):
        """Test with very short duration activities."""
        df = pd.DataFrame([
            {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "09:01", 
             "activity_label": "Walking", "duration_minutes": 1.0},
        ])
        
        total = calculate_total_duration(df)
        assert total == 1.0
    
    def test_very_long_duration(self):
        """Test with very long duration activities."""
        df = pd.DataFrame([
            {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "21:00", 
             "activity_label": "Working", "duration_minutes": 720.0},
        ])
        
        total = calculate_total_duration(df)
        assert total == 720.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
