"""Test UI components and dashboard rendering logic."""

import pandas as pd
from database.database import DatabaseManager
from components.charts import apply_actipulse_chart_theme, build_empty_state_figure
import plotly.graph_objects as go

def test_chart_generation():
    """Test chart generation without Streamlit context."""
    print("=" * 70)
    print("UI COMPONENTS TEST")
    print("=" * 70)
    
    # Test 1: Empty state figure
    print("\n1. Testing empty state chart...")
    fig = build_empty_state_figure("Test message")
    assert fig is not None
    print("   ✓ Empty state figure generated")
    
    # Test 2: Pie chart generation
    print("\n2. Testing pie chart generation...")
    activity_data = pd.Series({
        "Walking": 100,
        "Sitting": 200,
        "Standing": 50,
    })
    
    fig = go.Figure(data=[go.Pie(
        labels=activity_data.index,
        values=activity_data.values,
        hole=0.4,
    )])
    fig = apply_actipulse_chart_theme(fig, title="Test Distribution")
    assert fig is not None
    print("   ✓ Pie chart generated and themed")
    
    # Test 3: Bar chart generation
    print("\n3. Testing bar chart generation...")
    fig = go.Figure(data=[go.Bar(
        x=activity_data.index,
        y=activity_data.values,
    )])
    fig = apply_actipulse_chart_theme(fig, title="Test Bar Chart")
    assert fig is not None
    print("   ✓ Bar chart generated and themed")
    
    # Test 4: Dashboard metric calculations
    print("\n4. Testing dashboard metric calculations...")
    db = DatabaseManager()
    db.initialize_schema()
    
    # Clear existing data first
    db.clear_all_activity_records()
    print("   ✓ Database cleared")
    
    # Insert test data
    test_records = [
        {"activity_date": "2024-01-20", "start_time": "09:00", "end_time": "10:00", 
         "activity_label": "Walking", "duration_minutes": 60.0},
        {"activity_date": "2024-01-20", "start_time": "10:00", "end_time": "12:00", 
         "activity_label": "Sitting", "duration_minutes": 120.0},
        {"activity_date": "2024-01-21", "start_time": "09:00", "end_time": "10:00", 
         "activity_label": "Walking", "duration_minutes": 60.0},
    ]
    
    batch_id = db.insert_upload_batch("test.csv", "csv", len(test_records))
    inserted, _ = db.insert_activity_records(test_records, batch_id=batch_id)
    print(f"   ✓ Inserted {inserted} test records")
    
    # Retrieve and calculate metrics
    df = db.get_all_activity_records()
    total_duration = df["duration_minutes"].sum()
    walking_duration = df[df["activity_label"] == "Walking"]["duration_minutes"].sum()
    unique_days = df["activity_date"].nunique()
    
    print(f"   ✓ Metrics calculated:")
    print(f"     - Total duration: {total_duration} minutes")
    print(f"     - Walking duration: {walking_duration} minutes")
    print(f"     - Unique days: {unique_days}")
    
    assert total_duration == 240.0
    assert walking_duration == 120.0
    assert unique_days == 2
    
    # Test 5: Activity distribution calculation
    print("\n5. Testing activity distribution calculation...")
    activity_totals = df.groupby("activity_label")["duration_minutes"].sum().sort_values(ascending=False)
    print(f"   ✓ Activity distribution:")
    for activity, duration in activity_totals.items():
        percentage = (duration / total_duration) * 100
        print(f"     - {activity}: {duration} min ({percentage:.1f}%)")
    
    # Test 6: Date filtering
    print("\n6. Testing date filtering...")
    filtered = df[df["activity_date"] == "2024-01-20"]
    print(f"   ✓ Filtered to 2024-01-20: {len(filtered)} records")
    assert len(filtered) == 2
    
    # Test 7: Activity filtering
    print("\n7. Testing activity type filtering...")
    walking_only = df[df["activity_label"] == "Walking"]
    print(f"   ✓ Walking only: {len(walking_only)} records")
    assert len(walking_only) == 2
    
    # Test 8: Recent records
    print("\n8. Testing recent records retrieval...")
    recent = df.head(10)
    print(f"   ✓ Retrieved {len(recent)} recent records")
    
    # Clean up
    db.clear_all_activity_records()
    
    print("\n" + "=" * 70)
    print("✅ ALL UI COMPONENT TESTS PASSED")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        test_chart_generation()
    except Exception as e:
        print(f"\n❌ UI COMPONENT TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
