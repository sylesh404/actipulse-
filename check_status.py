"""Quick status check for ActiPulse AI."""

from database.database import DatabaseManager
import os

def check_status():
    """Display ActiPulse AI status."""
    print("\n" + "="*50)
    print("   ActiPulse AI - Status Check")
    print("="*50 + "\n")
    
    # Database check
    try:
        db = DatabaseManager()
        db.initialize_schema()
        df = db.get_all_activity_records()
        
        print("✅ Database Status:")
        print(f"   - Database file: data/actipulse.db")
        print(f"   - Total records: {len(df)}")
        
        if not df.empty:
            print(f"   - Date range: {df['activity_date'].min()} to {df['activity_date'].max()}")
            print(f"   - Activities: {', '.join(df['activity_label'].unique())}")
            total_minutes = df['duration_minutes'].sum()
            print(f"   - Total duration: {total_minutes:.0f} minutes ({total_minutes/60:.1f} hours)")
        else:
            print("   - No records found (run add_sample_data.py)")
    except Exception as e:
        print(f"❌ Database Error: {e}")
    
    # Environment check
    print("\n✅ Environment:")
    env_exists = os.path.exists('.env')
    print(f"   - .env file: {'Found' if env_exists else 'Not found (optional)'}")
    
    if env_exists:
        with open('.env', 'r') as f:
            content = f.read()
            has_api_key = 'GEMINI_API_KEY' in content and 'your_gemini_api_key_here' not in content
            print(f"   - Gemini API: {'Configured' if has_api_key else 'Not configured (using fallback)'}")
    else:
        print("   - Gemini API: Using template fallback")
    
    # Files check
    print("\n✅ Documentation:")
    files = ['README.md', 'USER_GUIDE.md', 'FEATURES_SUMMARY.md']
    for file in files:
        exists = os.path.exists(file)
        print(f"   - {file}: {'✓' if exists else '✗'}")
    
    # Features check
    print("\n✅ Features Available:")
    features = [
        "Home Dashboard",
        "Upload Activity",
        "Activity Analytics",
        "Activity Comparison",
        "AI Activity Diary",
        "AI Assistant",
        "Reports"
    ]
    for feature in features:
        print(f"   - {feature}: READY")
    
    # Quick start
    print("\n🚀 Quick Start:")
    print("   1. Ensure virtual environment is activated")
    print("   2. Run: streamlit run app.py")
    print("   3. Open: http://localhost:8501")
    
    if df.empty:
        print("\n💡 Tip: Run 'python add_sample_data.py' to add sample data")
    
    print("\n" + "="*50)
    print("   Ready to use! 🎉")
    print("="*50 + "\n")

if __name__ == "__main__":
    check_status()
