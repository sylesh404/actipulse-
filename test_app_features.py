"""Test script to verify all app features are working."""

import sys
import traceback
from database.database import DatabaseManager
from modules.activity_analytics import (
    calculate_activity_statistics,
    calculate_activity_distribution,
    calculate_daily_summary,
    analyze_time_periods,
    generate_activity_insights,
)
from modules.activity_comparison import (
    compare_two_days,
    generate_weekly_comparison,
    compare_custom_periods,
    generate_comparison_insights,
)
from modules.ai_narrator import (
    is_gemini_configured,
    get_gemini_model_name,
    generate_daily_narrative,
    generate_weekly_narrative,
)
from components.charts import (
    build_activity_distribution_donut,
    build_activity_duration_bar,
    build_time_period_bar,
    build_day_comparison_chart,
    build_weekly_trend_line,
    build_weekly_stacked_bar,
)

def test_database():
    """Test database operations."""
    print("\n=== Testing Database ===")
    try:
        db = DatabaseManager()
        db.initialize_schema()
        df = db.get_all_activity_records()
        print(f"✅ Database initialized: {len(df)} records found")
        return db, df
    except Exception as e:
        print(f"❌ Database error: {e}")
        traceback.print_exc()
        return None, None

def test_analytics(df):
    """Test analytics module."""
    print("\n=== Testing Activity Analytics ===")
    if df.empty:
        print("⚠️ No data - skipping analytics tests")
        return
    
    try:
        stats = calculate_activity_statistics(df)
        print(f"✅ Activity statistics: {stats['total_minutes']:.0f} minutes total")
        
        distribution = calculate_activity_distribution(df)
        print(f"✅ Activity distribution: {len(distribution)} activities")
        
        date = df["activity_date"].iloc[0]
        daily_summary = calculate_daily_summary(df, date)
        print(f"✅ Daily summary for {date}: {daily_summary.total_minutes:.0f} minutes")
        
        time_analysis = analyze_time_periods(df)
        print(f"✅ Time period analysis: {time_analysis.morning_minutes:.0f} morning minutes")
        
        insights = generate_activity_insights(df)
        print(f"✅ Generated {len(insights)} insights")
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        traceback.print_exc()

def test_comparison(df):
    """Test comparison module."""
    print("\n=== Testing Activity Comparison ===")
    if df.empty or len(df["activity_date"].unique()) < 2:
        print("⚠️ Need at least 2 dates - skipping comparison tests")
        return
    
    try:
        dates = sorted(df["activity_date"].unique())
        
        comparison = compare_two_days(df, dates[0], dates[-1])
        print(f"✅ Day comparison: {comparison.activities_compared} activities compared")
        
        weekly_stats = generate_weekly_comparison(df, dates[0], num_days=7)
        print(f"✅ Weekly comparison: {weekly_stats.days_with_data} days with data")
        
        period_comp = compare_custom_periods(df, dates[0], dates[0], dates[-1], dates[-1])
        print(f"✅ Period comparison: {period_comp.total_difference:+.0f} min difference")
        
        insights = generate_comparison_insights(comparison=comparison)
        print(f"✅ Comparison insights: {len(insights)} generated")
        
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        traceback.print_exc()

def test_ai_narrator():
    """Test AI narrator module."""
    print("\n=== Testing AI Narrator ===")
    try:
        is_configured = is_gemini_configured()
        if is_configured:
            model = get_gemini_model_name()
            print(f"✅ Gemini configured: {model}")
        else:
            print("⚠️ Gemini not configured - will use fallback templates")
        
    except Exception as e:
        print(f"❌ AI Narrator error: {e}")
        traceback.print_exc()

def test_charts():
    """Test chart generation."""
    print("\n=== Testing Charts ===")
    try:
        # Test empty charts
        fig1 = build_activity_distribution_donut([])
        print("✅ Empty donut chart created")
        
        # Test with sample data
        sample_data = [
            {"activity_label": "Walking", "total_minutes": 120, "percentage": 50},
            {"activity_label": "Sitting", "total_minutes": 120, "percentage": 50},
        ]
        fig2 = build_activity_distribution_donut(sample_data)
        print("✅ Donut chart with data created")
        
        fig3 = build_activity_duration_bar(sample_data)
        print("✅ Duration bar chart created")
        
        time_data = {"Morning": 60, "Afternoon": 90, "Evening": 45}
        fig4 = build_time_period_bar(time_data)
        print("✅ Time period bar chart created")
        
        fig5 = build_day_comparison_chart(["Walking", "Sitting"], [60, 30], [45, 50], "Day 1", "Day 2")
        print("✅ Day comparison chart created")
        
        fig6 = build_weekly_trend_line(["2024-01-01", "2024-01-02"], [120, 150], "Walking")
        print("✅ Weekly trend line created")
        
        fig7 = build_weekly_stacked_bar(
            ["2024-01-01", "2024-01-02"],
            [60, 70],
            [30, 40],
            [20, 30],
            [10, 10],
        )
        print("✅ Weekly stacked bar chart created")
        
    except Exception as e:
        print(f"❌ Charts error: {e}")
        traceback.print_exc()

def main():
    """Run all tests."""
    print("=" * 60)
    print("ActiPulse AI - Feature Testing")
    print("=" * 60)
    
    db, df = test_database()
    
    if db is not None and df is not None:
        test_analytics(df)
        test_comparison(df)
        test_ai_narrator()
        test_charts()
    
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
