"""Add sample activity data to the database for testing."""

from database.database import DatabaseManager
from datetime import date, timedelta
import random

def add_sample_data():
    """Add comprehensive sample activity data."""
    db = DatabaseManager()
    db.initialize_schema()
    
    # Generate data for the last 14 days
    today = date.today()
    activities = ["Walking", "Sitting", "Standing", "Running", "Cycling"]
    
    sample_records = []
    
    for days_ago in range(14):
        current_date = today - timedelta(days=days_ago)
        date_str = current_date.isoformat()
        
        # Morning activities (6 AM - 12 PM)
        sample_records.append({
            "activity_date": date_str,
            "start_time": "06:00:00",
            "end_time": "06:45:00",
            "activity_label": "Walking",
            "duration_minutes": 45.0,
        })
        
        sample_records.append({
            "activity_date": date_str,
            "start_time": "08:00:00",
            "end_time": "12:00:00",
            "activity_label": "Sitting",
            "duration_minutes": 240.0,
        })
        
        # Afternoon activities (12 PM - 6 PM)
        sample_records.append({
            "activity_date": date_str,
            "start_time": "12:30:00",
            "end_time": "13:00:00",
            "activity_label": "Walking",
            "duration_minutes": 30.0,
        })
        
        sample_records.append({
            "activity_date": date_str,
            "start_time": "13:00:00",
            "end_time": "17:00:00",
            "activity_label": "Sitting",
            "duration_minutes": 240.0,
        })
        
        # Evening activities (6 PM - 10 PM)
        sample_records.append({
            "activity_date": date_str,
            "start_time": "18:00:00",
            "end_time": "19:00:00",
            "activity_label": random.choice(["Standing", "Walking"]),
            "duration_minutes": 60.0,
        })
        
        # Add some variety
        if days_ago % 3 == 0:
            sample_records.append({
                "activity_date": date_str,
                "start_time": "07:00:00",
                "end_time": "07:30:00",
                "activity_label": "Running",
                "duration_minutes": 30.0,
            })
        
        if days_ago % 4 == 0:
            sample_records.append({
                "activity_date": date_str,
                "start_time": "17:30:00",
                "end_time": "18:30:00",
                "activity_label": "Cycling",
                "duration_minutes": 60.0,
            })
    
    # Insert all records
    batch_id = db.insert_upload_batch(
        filename="sample_data.csv",
        file_format="csv",
        row_count=len(sample_records),
    )
    
    inserted, duplicates = db.insert_activity_records(sample_records, batch_id=batch_id)
    
    print(f"✅ Successfully added {inserted} sample activity records!")
    print(f"   Covering {14} days of activity data")
    if duplicates > 0:
        print(f"   Skipped {duplicates} duplicate records")
    
    # Verify
    df = db.get_all_activity_records()
    print(f"\n📊 Database now contains {len(df)} total records")
    print(f"   Date range: {df['activity_date'].min()} to {df['activity_date'].max()}")
    print(f"   Activities: {', '.join(df['activity_label'].unique())}")

if __name__ == "__main__":
    add_sample_data()
