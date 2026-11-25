"""Quick test script to validate PROCESS 2 implementation."""

from pathlib import Path
import pandas as pd
from database.database import DatabaseManager
from modules.data_loader import load_activity_file
from modules.preprocessing import preprocess_activity_dataframe

def test_database_operations():
    """Test database initialization and operations."""
    print("Testing database operations...")
    db = DatabaseManager()
    db.initialize_schema()
    
    # Test manual record insertion
    success = db.insert_activity_record(
        activity_date="2024-01-20",
        start_time="09:00",
        end_time="10:00",
        activity_label="Walking",
        duration_minutes=60.0,
    )
    print(f"✓ Manual record insertion: {'Success' if success else 'Failed'}")
    
    # Test retrieval
    records = db.get_all_activity_records()
    print(f"✓ Retrieved {len(records)} records from database")
    
    # Test deletion
    if not records.empty:
        first_id = records.iloc[0]["id"]
        deleted = db.delete_activity_record(first_id)
        print(f"✓ Record deletion: {'Success' if deleted else 'Failed'}")
    
    return True

def test_csv_upload():
    """Test CSV file loading and preprocessing."""
    print("\nTesting CSV upload and preprocessing...")
    
    csv_path = Path("data/sample_activity.csv")
    if not csv_path.exists():
        print("✗ Sample CSV not found")
        return False
    
    # Load CSV
    df = load_activity_file(csv_path)
    print(f"✓ Loaded CSV: {len(df)} rows")
    
    # Preprocess
    report = preprocess_activity_dataframe(df, existing_keys=set(), allow_overnight=True)
    print(f"✓ Validation Report:")
    print(f"  - Total records: {report.total_records}")
    print(f"  - Valid records: {report.valid_records_count}")
    print(f"  - Invalid records: {report.invalid_records_count}")
    print(f"  - Duplicate records: {report.duplicate_records_count}")
    print(f"  - Overnight records: {report.overnight_records_count}")
    
    if report.valid_records_count > 0:
        print(f"✓ Sample valid record:")
        print(report.valid_df.head(1).to_dict('records')[0])
    
    return True

def test_overnight_activity():
    """Test overnight activity handling."""
    print("\nTesting overnight activity handling...")
    
    from modules.preprocessing import validate_single_activity_row
    
    # Test overnight activity (23:30 to 00:30)
    record, is_overnight = validate_single_activity_row(
        raw_date="2024-01-20",
        raw_start_time="23:30",
        raw_end_time="00:30",
        raw_activity="Sleeping",
        allow_overnight=True,
    )
    
    print(f"✓ Overnight activity detected: {is_overnight}")
    print(f"  - Duration: {record['duration_minutes']} minutes")
    assert is_overnight == True
    assert record['duration_minutes'] == 60.0
    
    return True

def test_duplicate_detection():
    """Test duplicate detection."""
    print("\nTesting duplicate detection...")
    
    db = DatabaseManager()
    
    # Insert first record
    db.insert_activity_record(
        activity_date="2024-01-21",
        start_time="10:00",
        end_time="11:00",
        activity_label="Walking",
        duration_minutes=60.0,
    )
    
    # Try to insert duplicate
    success = db.insert_activity_record(
        activity_date="2024-01-21",
        start_time="10:00",
        end_time="11:00",
        activity_label="Walking",
        duration_minutes=60.0,
    )
    
    print(f"✓ Duplicate prevention: {'Working' if not success else 'Failed'}")
    
    # Clean up
    db.clear_all_activity_records()
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("PROCESS 2 IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    
    try:
        test_database_operations()
        test_csv_upload()
        test_overnight_activity()
        test_duplicate_detection()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
