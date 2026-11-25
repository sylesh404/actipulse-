"""Test complete PROCESS 2 workflow: Upload → Database → Dashboard."""

from pathlib import Path
import pandas as pd
from database.database import DatabaseManager
from modules.data_loader import load_activity_file
from modules.preprocessing import preprocess_activity_dataframe

def test_complete_workflow():
    """Test the complete data flow from upload to dashboard metrics."""
    print("=" * 70)
    print("COMPLETE WORKFLOW TEST: Upload → Validation → Database → Dashboard")
    print("=" * 70)
    
    # Initialize database
    print("\n1. Initializing database...")
    db = DatabaseManager()
    db.initialize_schema()
    db.clear_all_activity_records()
    print("   ✓ Database initialized and cleared")
    
    # Load CSV file
    print("\n2. Loading CSV file...")
    csv_path = Path("data/sample_activity.csv")
    df = load_activity_file(csv_path)
    print(f"   ✓ Loaded {len(df)} rows from CSV")
    
    # Preprocess and validate
    print("\n3. Validating and preprocessing data...")
    existing_keys = db.get_existing_record_keys()
    report = preprocess_activity_dataframe(df, existing_keys=existing_keys, allow_overnight=True)
    
    print(f"   ✓ Validation complete:")
    print(f"     - Total: {report.total_records}")
    print(f"     - Valid: {report.valid_records_count}")
    print(f"     - Invalid: {report.invalid_records_count}")
    print(f"     - Duplicates: {report.duplicate_records_count}")
    
    # Insert into database
    print("\n4. Inserting records into database...")
    batch_id = db.insert_upload_batch(
        filename="sample_activity.csv",
        file_format="csv",
        row_count=report.valid_records_count,
    )
    records_to_insert = report.valid_df.to_dict("records")
    inserted, duplicates = db.insert_activity_records(records_to_insert, batch_id=batch_id)
    print(f"   ✓ Inserted {inserted} records (batch_id: {batch_id})")
    
    # Calculate dashboard metrics
    print("\n5. Calculating dashboard metrics...")
    all_records = db.get_all_activity_records()
    
    total_duration = all_records["duration_minutes"].sum()
    walking_duration = all_records[all_records["activity_label"] == "Walking"]["duration_minutes"].sum()
    sitting_duration = all_records[all_records["activity_label"] == "Sitting"]["duration_minutes"].sum()
    standing_duration = all_records[all_records["activity_label"] == "Standing"]["duration_minutes"].sum()
    running_duration = all_records[all_records["activity_label"] == "Running"]["duration_minutes"].sum()
    cycling_duration = all_records[all_records["activity_label"] == "Cycling"]["duration_minutes"].sum()
    unique_days = all_records["activity_date"].nunique()
    
    print(f"   ✓ Dashboard metrics calculated:")
    print(f"     - Total Duration: {total_duration:.0f} minutes ({total_duration/60:.1f} hours)")
    print(f"     - Walking: {walking_duration:.0f} min ({walking_duration/total_duration*100:.1f}%)")
    print(f"     - Sitting: {sitting_duration:.0f} min ({sitting_duration/total_duration*100:.1f}%)")
    print(f"     - Standing: {standing_duration:.0f} min ({standing_duration/total_duration*100:.1f}%)")
    print(f"     - Running: {running_duration:.0f} min ({running_duration/total_duration*100:.1f}%)")
    print(f"     - Cycling: {cycling_duration:.0f} min ({cycling_duration/total_duration*100:.1f}%)")
    print(f"     - Total Records: {len(all_records)}")
    print(f"     - Unique Days: {unique_days}")
    
    # Test activity distribution
    print("\n6. Testing activity distribution...")
    activity_totals = all_records.groupby("activity_label")["duration_minutes"].sum().sort_values(ascending=False)
    print("   ✓ Activity distribution (by duration):")
    for activity, duration in activity_totals.items():
        print(f"     - {activity}: {duration:.0f} min")
    
    # Test date filtering
    print("\n7. Testing date range filtering...")
    date_filtered = all_records[all_records["activity_date"] == "2024-01-15"]
    print(f"   ✓ Filtered to 2024-01-15: {len(date_filtered)} records, {date_filtered['duration_minutes'].sum():.0f} min")
    
    # Test activity filtering
    print("\n8. Testing activity type filtering...")
    walking_only = all_records[all_records["activity_label"] == "Walking"]
    print(f"   ✓ Walking activities: {len(walking_only)} records, {walking_only['duration_minutes'].sum():.0f} min")
    
    # Test recent records
    print("\n9. Testing recent records retrieval...")
    recent_10 = all_records.head(10)
    print(f"   ✓ Retrieved {len(recent_10)} most recent records")
    
    # Test record deletion
    print("\n10. Testing record deletion...")
    first_id = all_records.iloc[0]["id"]
    deleted = db.delete_activity_record(first_id)
    print(f"   ✓ Deleted record ID {first_id}: {'Success' if deleted else 'Failed'}")
    
    remaining = db.get_all_activity_records()
    print(f"   ✓ Remaining records: {len(remaining)}")
    
    # Test Excel upload
    print("\n11. Testing Excel file upload...")
    excel_path = Path("data/sample_activity.xlsx")
    if excel_path.exists():
        excel_df = load_activity_file(excel_path)
        excel_report = preprocess_activity_dataframe(excel_df, existing_keys=db.get_existing_record_keys(), allow_overnight=True)
        print(f"   ✓ Loaded Excel: {len(excel_df)} rows")
        print(f"   ✓ Valid Excel records: {excel_report.valid_records_count}")
        
        excel_records = excel_report.valid_df.to_dict("records")
        excel_batch_id = db.insert_upload_batch("sample_activity.xlsx", "xlsx", excel_report.valid_records_count)
        excel_inserted, excel_dups = db.insert_activity_records(excel_records, batch_id=excel_batch_id)
        print(f"   ✓ Inserted {excel_inserted} Excel records ({excel_dups} duplicates)")
    else:
        print("   ⚠ Excel sample file not found (optional)")
    
    # Final summary
    print("\n12. Final database state...")
    final_records = db.get_all_activity_records()
    final_batches = db.get_table_counts()
    print(f"   ✓ Total activity records: {len(final_records)}")
    print(f"   ✓ Upload batches: {final_batches['upload_batches']}")
    print(f"   ✓ Total duration: {final_records['duration_minutes'].sum():.0f} minutes")
    
    # Test last updated timestamp
    last_update = db.get_last_updated_timestamp()
    print(f"   ✓ Last data update: {last_update}")
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE WORKFLOW TEST PASSED")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        test_complete_workflow()
    except Exception as e:
        print(f"\n❌ WORKFLOW TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
