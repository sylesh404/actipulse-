"""Integration tests for Activity Analytics with database."""

import pandas as pd
from database.database import DatabaseManager
from modules.activity_analytics import (
    calculate_total_duration,
    calculate_activity_distribution,
    calculate_daily_summary,
    analyze_time_periods,
    generate_activity_insights,
)


def test_analytics_with_real_database():
    """Test analytics engine with actual database operations."""
    print("\n" + "="*70)
    print("INTEGRATION TEST: Analytics Engine with Database")
    print("="*70)
    
    # Initialize database
    db = DatabaseManager()
    db.initialize_schema()
    db.clear_all_activity_records()
    
    # Insert test data
    test_records = [
        {"activity_date": "2024-01-20", "start_time": "07:00", "end_time": "07:30",
         "activity_label": "Walking", "duration_minutes": 30.0},
        {"activity_date": "2024-01-20", "start_time": "07:30", "end_time": "09:00",
         "activity_label": "Sitting", "duration_minutes": 90.0},
        {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "09:30",
         "activity_label": "Standing", "duration_minutes": 30.0},
        {"activity_date": "2024-01-20", "start_time": "09:30", "end_time": "10:00",
         "activity_label": "Walking", "duration_minutes": 30.0},
        {"activity_date": "2024-01-20", "start_time": "10:00", "end_time": "12:00",
         "activity_label": "Sitting", "duration_minutes": 120.0},
        {"activity_date": "2024-01-20", "start_time": "14:00", "end_time": "15:00",
         "activity_label": "Standing", "duration_minutes": 60.0},
        {"activity_date": "2024-01-20", "start_time": "19:00", "end_time": "20:00",
         "activity_label": "Walking", "duration_minutes": 60.0},
        {"activity_date": "2024-01-21", "start_time": "06:00", "end_time": "07:00",
         "activity_label": "Running", "duration_minutes": 60.0},
        {"activity_date": "2024-01-21", "start_time": "09:00", "end_time": "11:00",
         "activity_label": "Sitting", "duration_minutes": 120.0},
    ]
    
    batch_id = db.insert_upload_batch("test_analytics.csv", "csv", len(test_records))
    inserted, _ = db.insert_activity_records(test_records, batch_id=batch_id)
    print(f"\n1. Inserted {inserted} test records into database")
    
    # Retrieve data
    df = db.get_all_activity_records()
    print(f"   Retrieved {len(df)} records from database")
    assert len(df) == 9
    
    # Test 1: Total Duration
    print("\n2. Testing total duration calculation...")
    total = calculate_total_duration(df)
    print(f"   Total duration: {total} minutes ({total/60:.1f} hours)")
    assert total == 600.0  # 30+90+30+30+120+60+60+60+120
    
    # Test 2: Activity Distribution
    print("\n3. Testing activity distribution...")
    distribution = calculate_activity_distribution(df)
    print(f"   Found {len(distribution)} activity types:")
    for item in distribution:
        print(f"   - {item.activity_label}: {item.total_minutes:.0f} min ({item.percentage:.1f}%)")
        print(f"     Sessions: {item.session_count}, Avg: {item.average_duration:.1f} min")
    
    assert len(distribution) == 4  # Walking, Sitting, Standing, Running
    sitting = next(item for item in distribution if item.activity_label == "Sitting")
    assert sitting.total_minutes == 330.0
    assert sitting.session_count == 3
    
    # Test 3: Daily Summary
    print("\n4. Testing daily summary for 2024-01-20...")
    summary = calculate_daily_summary(df, "2024-01-20")
    print(f"   Total: {summary.total_minutes} min ({summary.total_hours:.1f} hrs)")
    print(f"   Sessions: {summary.total_sessions}")
    print(f"   Top activity: {summary.most_frequent_activity}")
    print(f"   Walking: {summary.walking_minutes} min")
    print(f"   Sitting: {summary.sitting_minutes} min")
    print(f"   Standing: {summary.standing_minutes} min")
    
    assert summary.total_minutes == 420.0
    assert summary.total_sessions == 7
    assert summary.most_frequent_activity == "Sitting"
    
    # Test 4: Time Period Analysis
    print("\n5. Testing time period analysis...")
    time_analysis = analyze_time_periods(df)
    print(f"   Early Morning: {time_analysis.early_morning_minutes} min")
    print(f"   Morning: {time_analysis.morning_minutes} min")
    print(f"   Afternoon: {time_analysis.afternoon_minutes} min")
    print(f"   Evening: {time_analysis.evening_minutes} min")
    print(f"   Night: {time_analysis.night_minutes} min")
    
    assert time_analysis.early_morning_minutes > 0  # 06:00 and 07:00 activities
    assert time_analysis.morning_minutes > 0  # 09:00-10:00 activities
    assert time_analysis.afternoon_minutes > 0  # 14:00 activity
    assert time_analysis.evening_minutes > 0  # 19:00 activity
    
    # Test 5: Activity Insights
    print("\n6. Testing activity insights generation...")
    insights = generate_activity_insights(df)
    print(f"   Generated {len(insights)} insights:")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight}")
    
    assert len(insights) > 0
    insights_text = " ".join(insights)
    assert "Sitting" in insights_text
    
    # Test 6: Filter by date
    print("\n7. Testing date filtering...")
    df_filtered = df[df["activity_date"] == "2024-01-21"]
    total_filtered = calculate_total_duration(df_filtered)
    print(f"   2024-01-21 total: {total_filtered} minutes")
    assert total_filtered == 180.0  # 60 + 120
    
    # Test 7: Filter by activity
    print("\n8. Testing activity filtering...")
    df_walking = df[df["activity_label"] == "Walking"]
    walking_total = calculate_total_duration(df_walking)
    print(f"   Walking total: {walking_total} minutes")
    assert walking_total == 120.0  # 30 + 30 + 60
    
    # Clean up
    db.clear_all_activity_records()
    
    print("\n" + "="*70)
    print("ALL INTEGRATION TESTS PASSED")
    print("="*70)


def test_analytics_with_sample_data():
    """Test analytics with the actual sample CSV data."""
    print("\n" + "="*70)
    print("INTEGRATION TEST: Analytics with Sample CSV Data")
    print("="*70)
    
    from pathlib import Path
    from modules.data_loader import load_activity_file
    from modules.preprocessing import preprocess_activity_dataframe
    
    db = DatabaseManager()
    db.initialize_schema()
    db.clear_all_activity_records()
    
    # Load sample CSV
    csv_path = Path("data/sample_activity.csv")
    if not csv_path.exists():
        print("   ⚠ Sample CSV not found, skipping this test")
        return
    
    print("\n1. Loading sample CSV...")
    raw_df = load_activity_file(csv_path)
    print(f"   Loaded {len(raw_df)} rows")
    
    print("\n2. Preprocessing data...")
    report = preprocess_activity_dataframe(raw_df, existing_keys=set())
    print(f"   Valid records: {report.valid_records_count}")
    
    print("\n3. Inserting into database...")
    batch_id = db.insert_upload_batch("sample_activity.csv", "csv", report.valid_records_count)
    records = report.valid_df.to_dict("records")
    inserted, _ = db.insert_activity_records(records, batch_id=batch_id)
    print(f"   Inserted {inserted} records")
    
    print("\n4. Running analytics...")
    df = db.get_all_activity_records()
    
    # Calculate metrics
    total = calculate_total_duration(df)
    distribution = calculate_activity_distribution(df)
    insights = generate_activity_insights(df)
    
    print(f"\n   Total Duration: {total:.0f} minutes ({total/60:.1f} hours)")
    print(f"   Activity Types: {len(distribution)}")
    print(f"   Top Activity: {distribution[0].activity_label if distribution else 'None'}")
    print(f"   Generated Insights: {len(insights)}")
    
    # Verify results are reasonable
    assert total > 0
    assert len(distribution) > 0
    assert len(insights) > 0
    
    # Clean up
    db.clear_all_activity_records()
    
    print("\n" + "="*70)
    print("SAMPLE DATA ANALYTICS TEST PASSED")
    print("="*70)


def test_empty_analytics():
    """Test analytics with empty database."""
    print("\n" + "="*70)
    print("INTEGRATION TEST: Analytics with Empty Database")
    print("="*70)
    
    db = DatabaseManager()
    db.initialize_schema()
    db.clear_all_activity_records()
    
    df = db.get_all_activity_records()
    assert df.empty
    
    print("\n1. Testing analytics with empty data...")
    total = calculate_total_duration(df)
    distribution = calculate_activity_distribution(df)
    insights = generate_activity_insights(df)
    
    print(f"   Total: {total}")
    print(f"   Distribution: {len(distribution)} items")
    print(f"   Insights: {insights}")
    
    assert total == 0.0
    assert distribution == []
    assert "No activity records" in insights[0]
    
    print("\n" + "="*70)
    print("EMPTY DATA TEST PASSED")
    print("="*70)


if __name__ == "__main__":
    test_analytics_with_real_database()
    test_analytics_with_sample_data()
    test_empty_analytics()
    print("\nALL INTEGRATION TESTS COMPLETED SUCCESSFULLY")
