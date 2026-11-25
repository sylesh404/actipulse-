"""Test validation scenarios for PROCESS 2."""

import pandas as pd
from modules.preprocessing import preprocess_activity_dataframe

def test_invalid_scenarios():
    """Test various invalid data scenarios."""
    print("=" * 70)
    print("VALIDATION TEST: Invalid Data Scenarios")
    print("=" * 70)
    
    # Test 1: Missing required columns
    print("\n1. Testing missing required columns...")
    invalid_df = pd.DataFrame({
        "date": ["2024-01-20"],
        "start_time": ["09:00"],
        # Missing end_time and activity
    })
    report = preprocess_activity_dataframe(invalid_df, existing_keys=set())
    print(f"   ✓ Missing columns detected: {report.missing_columns}")
    assert report.has_schema_errors
    
    # Test 2: Invalid date format
    print("\n2. Testing invalid date format...")
    invalid_dates = pd.DataFrame({
        "date": ["2024-13-45", "not-a-date", "2024-01-15"],
        "start_time": ["09:00", "10:00", "11:00"],
        "end_time": ["10:00", "11:00", "12:00"],
        "activity": ["Walking", "Sitting", "Standing"],
    })
    report = preprocess_activity_dataframe(invalid_dates, existing_keys=set())
    print(f"   ✓ Total: {report.total_records}, Valid: {report.valid_records_count}, Invalid: {report.invalid_records_count}")
    assert report.invalid_records_count == 2
    assert report.valid_records_count == 1
    
    # Test 3: Invalid time format
    print("\n3. Testing invalid time format...")
    invalid_times = pd.DataFrame({
        "date": ["2024-01-20", "2024-01-20", "2024-01-20"],
        "start_time": ["09:00", "25:00", "10:00"],
        "end_time": ["10:00", "26:00", "not-time"],
        "activity": ["Walking", "Sitting", "Standing"],
    })
    report = preprocess_activity_dataframe(invalid_times, existing_keys=set())
    print(f"   ✓ Total: {report.total_records}, Valid: {report.valid_records_count}, Invalid: {report.invalid_records_count}")
    assert report.invalid_records_count == 2
    assert report.valid_records_count == 1
    
    # Test 4: End time before start time (without overnight)
    print("\n4. Testing end time before start time (negative duration)...")
    negative_duration = pd.DataFrame({
        "date": ["2024-01-20"],
        "start_time": ["15:00"],
        "end_time": ["14:00"],
        "activity": ["Walking"],
    })
    # This should work if allow_overnight=True (treat as overnight)
    report = preprocess_activity_dataframe(negative_duration, existing_keys=set(), allow_overnight=True)
    print(f"   ✓ With overnight allowed - Valid: {report.valid_records_count}, Overnight: {report.overnight_records_count}")
    assert report.valid_records_count == 1
    assert report.overnight_records_count == 1
    
    # Test 5: Empty activity labels
    print("\n5. Testing empty/missing activity labels...")
    empty_labels = pd.DataFrame({
        "date": ["2024-01-20", "2024-01-20", "2024-01-20"],
        "start_time": ["09:00", "10:00", "11:00"],
        "end_time": ["10:00", "11:00", "12:00"],
        "activity": ["Walking", "", None],
    })
    report = preprocess_activity_dataframe(empty_labels, existing_keys=set())
    print(f"   ✓ Total: {report.total_records}, Valid: {report.valid_records_count}, Invalid: {report.invalid_records_count}")
    assert report.invalid_records_count == 2
    assert report.valid_records_count == 1
    
    # Test 6: Zero duration
    print("\n6. Testing zero duration (same start and end time)...")
    zero_duration = pd.DataFrame({
        "date": ["2024-01-20"],
        "start_time": ["10:00"],
        "end_time": ["10:00"],
        "activity": ["Walking"],
    })
    report = preprocess_activity_dataframe(zero_duration, existing_keys=set())
    print(f"   ✓ Total: {report.total_records}, Valid: {report.valid_records_count}, Invalid: {report.invalid_records_count}")
    assert report.invalid_records_count == 1
    
    # Test 7: Duplicate detection within file
    print("\n7. Testing duplicate detection within uploaded file...")
    duplicates = pd.DataFrame({
        "date": ["2024-01-20", "2024-01-20", "2024-01-20"],
        "start_time": ["09:00", "09:00", "10:00"],
        "end_time": ["10:00", "10:00", "11:00"],
        "activity": ["Walking", "Walking", "Sitting"],
    })
    report = preprocess_activity_dataframe(duplicates, existing_keys=set())
    print(f"   ✓ Total: {report.total_records}, Valid: {report.valid_records_count}, Duplicates: {report.duplicate_records_count}")
    assert report.duplicate_records_count == 1
    assert report.valid_records_count == 2
    
    # Test 8: Duplicate against existing database records
    print("\n8. Testing duplicate detection against existing records...")
    existing = {
        ("2024-01-20", "09:00", "10:00", "walking"),
    }
    new_data = pd.DataFrame({
        "date": ["2024-01-20", "2024-01-20"],
        "start_time": ["09:00", "11:00"],
        "end_time": ["10:00", "12:00"],
        "activity": ["Walking", "Sitting"],
    })
    report = preprocess_activity_dataframe(new_data, existing_keys=existing)
    print(f"   ✓ Total: {report.total_records}, Valid: {report.valid_records_count}, Duplicates: {report.duplicate_records_count}")
    assert report.duplicate_records_count == 1
    assert report.valid_records_count == 1
    
    # Test 9: Overnight activity validation
    print("\n9. Testing overnight activity (23:30 to 00:30)...")
    overnight = pd.DataFrame({
        "date": ["2024-01-20"],
        "start_time": ["23:30"],
        "end_time": ["00:30"],
        "activity": ["Sleeping"],
    })
    report = preprocess_activity_dataframe(overnight, existing_keys=set(), allow_overnight=True)
    print(f"   ✓ Valid: {report.valid_records_count}, Overnight: {report.overnight_records_count}")
    assert report.valid_records_count == 1
    assert report.overnight_records_count == 1
    
    # Verify duration is 60 minutes
    duration = report.valid_df.iloc[0]["duration_minutes"]
    print(f"   ✓ Duration calculated correctly: {duration} minutes")
    assert duration == 60.0
    
    # Test 10: Mixed valid and invalid records
    print("\n10. Testing mixed valid and invalid records...")
    mixed = pd.DataFrame({
        "date": ["2024-01-20", "invalid", "2024-01-21", "2024-01-22"],
        "start_time": ["09:00", "10:00", "25:00", "11:00"],
        "end_time": ["10:00", "11:00", "12:00", "12:00"],
        "activity": ["Walking", "Sitting", "Standing", ""],
    })
    report = preprocess_activity_dataframe(mixed, existing_keys=set())
    print(f"   ✓ Total: {report.total_records}")
    print(f"   ✓ Valid: {report.valid_records_count}")
    print(f"   ✓ Invalid: {report.invalid_records_count}")
    print(f"   ✓ Rejected reasons:")
    for rec in report.rejected_records:
        print(f"     - Row {rec.row_number}: {rec.reason}")
    
    assert report.valid_records_count == 1
    assert report.invalid_records_count == 3
    
    print("\n" + "=" * 70)
    print("✅ ALL VALIDATION TESTS PASSED")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        test_invalid_scenarios()
    except Exception as e:
        print(f"\n❌ VALIDATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
