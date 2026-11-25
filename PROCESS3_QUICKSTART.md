# PROCESS 3 Quick Start Guide

## Activity Analytics Engine

### Launch the Application

```powershell
cd "c:\Users\Sakthi sylesh\Downloads\ActiPulse AI – Physical Activity Diary Narrator"
.venv\Scripts\Activate.ps1
streamlit run app.py
```

Application opens at: **http://localhost:8501**

---

## Explore Activity Analytics

### 1. Navigate to Activity Analytics

Click **"📊 Activity Analytics"** in the sidebar.

### 2. Upload Sample Data (if needed)

If you haven't uploaded data yet:
1. Go to "Upload Activity"
2. Upload `data/sample_activity.csv` (42 records)
3. Return to "Activity Analytics"

### 3. View Analytics Dashboard

The Activity Analytics page shows 6 sections:

#### A. Activity Overview Cards
- Total Duration (minutes & hours)
- Walking, Sitting, Standing durations
- Total sessions with average duration

#### B. Activity Distribution
- Interactive donut chart (hover for details)
- Bar chart showing duration by activity
- Click and drag to zoom, double-click to reset

#### C. Daily Activity Breakdown
- Select any recorded date from dropdown
- View complete breakdown for that day
- See session count and top activity
- Detailed activity table with percentages

#### D. Activity by Time of Day
- Bar chart showing when activities occur
- 5 time periods: Early Morning, Morning, Afternoon, Evening, Night
- See which periods have most activity

#### E. Activity Insights
- 6+ automatically generated observations
- Based on your actual data
- Example: "Sitting was the largest recorded activity with 120 minutes (40%)"

#### F. Detailed Analytics Table
- Complete metrics for each activity
- Min, max, and average durations
- Session counts and percentages

---

## Use Filters

### Date Range Filter (Sidebar)
1. Click the date range picker in the sidebar
2. Select start and end dates
3. All analytics update automatically

### Activity Type Filter (Sidebar)
1. Use the multi-select dropdown
2. Choose which activities to include
3. Remove activities to focus on specific types

---

## Analytics Functions Available

All these functions work with your data:

### Core Calculations
- `calculate_total_duration(df)` - Total minutes
- `calculate_activity_duration_by_label(df, "Walking")` - Specific activity
- `calculate_activity_distribution(df)` - Full breakdown with percentages
- `calculate_activity_statistics(df)` - Summary stats
- `calculate_daily_summary(df, "2024-01-20")` - Single day analysis
- `analyze_time_periods(df)` - Time of day breakdown
- `generate_activity_insights(df)` - Automatic observations

---

## Run Tests

### Unit Tests (31 tests)
```powershell
python -m pytest tests/test_activity_analytics.py -v
```

### Integration Tests
```powershell
$env:PYTHONPATH="$PWD"
python tests/test_analytics_integration.py
```

---

## Example Analytics Workflow

1. **Upload Data**
   - Go to "Upload Activity"
   - Upload your CSV or Excel file
   - Verify validation report

2. **View Overview**
   - Go to "Home Dashboard"
   - See high-level metrics
   - Check recent activities

3. **Deep Dive Analytics**
   - Go to "Activity Analytics"
   - Review activity distribution
   - Select specific dates for daily breakdown
   - Check time-of-day patterns
   - Read generated insights

4. **Filter Analysis**
   - Use date range to focus on specific period
   - Filter by activity type to compare
   - Export insights for reporting

---

## What Makes Good Analytics Data?

### Best Practices
✅ Record complete time intervals (start + end time)
✅ Use consistent activity labels
✅ Include all activity types
✅ Record activities as they happen
✅ Upload data regularly

### What Analytics Handles
✅ Overnight activities (23:30 to 00:30)
✅ Custom activity labels (Yoga, Swimming, etc.)
✅ Overlapping activities (summed durations)
✅ Empty datasets (graceful handling)
✅ Single-day or multi-day analysis

---

## Understanding the Metrics

### Total Duration
Sum of all activity durations in minutes/hours.

### Activity Distribution
Percentage breakdown showing which activities take most time.

### Session Count
Number of separate activity intervals recorded.

### Average Duration
Total duration divided by number of sessions.

### Time Periods
- **Early Morning:** 05:00-08:00
- **Morning:** 08:00-12:00
- **Afternoon:** 12:00-17:00
- **Evening:** 17:00-21:00
- **Night:** 21:00-05:00

### Insights
Automatically generated observations based on:
- Largest activity category
- Session patterns
- Time period distribution
- Duration extremes
- Activity variety

---

## Troubleshooting

### "No activity data available"
**Solution:** Upload data via "Upload Activity" page first.

### Filters show no results
**Solution:** Adjust date range or include more activity types.

### Charts not interactive
**Solution:** Hover over charts to see tooltips. Click and drag to zoom.

### Want to reset view?
**Solution:** Double-click any chart to reset zoom.

---

## Technical Details

### Calculation Method
- All calculations use Python and Pandas
- No AI/LLM used for numerical computations
- Pure mathematical operations
- Verifiable and reproducible

### Data Handling
- Records retrieved from SQLite database
- Filters applied using Pandas
- Calculations cached for performance
- No data modification during analysis

### Visualization
- Interactive Plotly charts
- Zoom, pan, hover tooltips
- Professional SaaS styling
- Responsive design

---

## Next Steps

After exploring Activity Analytics:
- Try different date ranges
- Compare weekdays vs weekends (filter by date)
- Identify your most common activities
- Track changes over time

**PROCESS 3 Complete!**

Ready for PROCESS 4: Activity Comparison (cross-day analysis).
