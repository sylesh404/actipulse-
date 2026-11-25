# ActiPulse AI - User Guide

## 🎯 Quick Start Guide

Welcome to ActiPulse AI! This guide will help you get started quickly.

### Starting the Application

1. **Activate virtual environment**:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

2. **Run the app**:
   ```bash
   streamlit run app.py
   ```

3. **Open in browser**:
   - Automatically opens at `http://localhost:8501`
   - Or navigate there manually

### First Time Setup

#### Option 1: Use Sample Data (Recommended for Testing)
```bash
python add_sample_data.py
```
This adds 14 days of sample activity data so you can explore all features immediately.

#### Option 2: Upload Your Own Data
1. Navigate to **Upload Activity** in the sidebar
2. Click **Download Sample CSV** to see the format
3. Prepare your data file
4. Upload and import

---

## 📊 Main Features

### 1. Home Dashboard
**What it does**: Provides a comprehensive overview of all your activity data

**Key Features**:
- Total duration metrics for all activities
- Activity breakdown by type
- Recent activity log
- Interactive pie charts and bar graphs
- Date range filtering

**How to use**:
1. Select date range in sidebar (optional)
2. Filter by activity types (optional)
3. View KPI cards showing totals
4. Explore charts and recent activities

---

### 2. Upload Activity

**What it does**: Import or manually add activity records

#### Tab 1: File Upload

**Supported formats**: CSV, Excel (.xlsx, .xls)

**Required columns**:
- `date` (YYYY-MM-DD, MM/DD/YYYY, or DD-MM-YYYY)
- `start_time` (HH:MM or HH:MM:SS)
- `end_time` (HH:MM or HH:MM:SS)
- `activity` (Walking, Sitting, Standing, Running, Cycling, or custom)

**Steps**:
1. Click **Choose a file** and select your CSV/Excel
2. Review the preview (shows first 10 rows)
3. Click **Validate & Process**
4. Review validation report
5. Click **Import X Valid Records**

**Example CSV**:
```csv
date,start_time,end_time,activity
2024-01-15,09:00,10:30,Walking
2024-01-15,10:30,12:00,Sitting
2024-01-15,14:00,15:00,Running
```

#### Tab 2: Manual Entry

**When to use**: Adding single records or activities not in a file

**Steps**:
1. Select activity date
2. Choose activity type
3. Set start and end times
4. Click **Add Activity Record**

**Tips**:
- Use "Other" for custom activities
- Times in 24-hour format
- Overnight activities automatically handled

#### Tab 3: Manage Records

**Features**:
- View all records in table format
- Filter by date or activity
- Delete individual records
- Clear all records (with confirmation)

---

### 3. Activity Analytics

**What it does**: Deep dive into your activity patterns and durations

#### Overview Cards
- Total duration across all activities
- Breakdown by activity type (Walking, Sitting, Standing, etc.)
- Total sessions and average duration

#### Activity Distribution
- **Donut chart**: Visual percentage breakdown
- **Bar chart**: Total duration comparison

#### Daily Breakdown
- Select any date to see detailed analysis
- Activity breakdown table
- Percentage distribution
- Session counts

#### Time-of-Day Analysis
Shows activity distribution across:
- Early Morning (00:00-06:00)
- Morning (06:00-12:00)
- Afternoon (12:00-18:00)
- Evening (18:00-22:00)
- Night (22:00-00:00)

#### Activity Insights
AI-generated observations about your patterns:
- Most frequent activities
- Duration trends
- Pattern observations

---

### 4. Activity Comparison

**What it does**: Compare activities across different time periods

#### Tab 1: Day-to-Day Comparison

**Use case**: Compare two specific dates

**Steps**:
1. Select "Previous Date" (baseline)
2. Select "Current Date" (target)
3. View comparison metrics
4. Analyze grouped bar chart
5. Review detailed table with change percentages

**Indicators**:
- 🟢 ↑ Increased duration
- 🔴 ↓ Decreased duration
- 🆕 Newly recorded activity
- ⚪ → No change

#### Tab 2: Weekly Trends

**Use case**: Analyze 7-day patterns

**Steps**:
1. Select week start date
2. View weekly summary cards
3. Analyze trend lines for different activities
4. Review stacked bar chart showing composition
5. Check daily summary table

**Features**:
- Average daily duration
- Total walking/sitting/standing
- Highest/lowest durations
- Day-by-day breakdown

#### Tab 3: Period Comparison

**Use case**: Compare any two custom date ranges

**Steps**:
1. Define Period A (start and end dates)
2. Define Period B (start and end dates)
3. View total comparison
4. Analyze activity-by-activity breakdown
5. Review insights

---

### 5. AI Activity Diary

**What it does**: Generate natural-language narratives from your activity data

**Prerequisites**: 
- Gemini API key configured in `.env` (optional - uses templates as fallback)

#### Tab 1: Daily Narrative

**Use case**: Get a diary entry for a specific day

**Steps**:
1. Select date from dropdown
2. Choose narrative tone:
   - Reflective & Clear
   - Casual & Friendly
   - Professional & Concise
3. Click **Generate Narrative**
4. Read your personalized diary entry

**What's included**:
- Overview of day's activities
- Duration summaries
- Pattern observations
- Comparison with previous day (if available)

#### Tab 2: Weekly Summary

**Use case**: Get a comprehensive week overview

**Steps**:
1. Select week start date
2. Click **Generate Weekly Summary**
3. Read your weekly narrative

**What's included**:
- Week-at-a-glance overview
- Trend analysis
- Activity highlights
- Pattern insights

---

### 6. AI Assistant

**What it does**: Answer questions about your activity data in natural language

**Prerequisites**: Gemini API key (optional - provides data-only responses as fallback)

**How to use**:
1. Type your question in the chat input
2. Press Enter
3. View AI response with data-backed answers
4. Continue conversation

**Example Questions**:
- "How much time did I spend walking today?"
- "What was my most frequent activity yesterday?"
- "Compare my sitting time between Monday and Tuesday"
- "What activities did I do on November 25th?"
- "Show me my total activity time this week"

**Features**:
- Conversation history maintained
- Context-aware responses
- Data-driven answers
- Suggested questions provided

---

### 7. Reports

**What it does**: Generate professional PDF reports

**Coming soon** - Full implementation in progress

**Planned features**:
- Customizable date ranges
- Activity selection
- Charts and visualizations
- Statistical summaries
- Download as PDF

---

## 🎨 Customization

### Activity Types

Default activities:
- Walking
- Sitting
- Standing
- Running
- Cycling
- Other (custom)

Add your own activities by selecting "Other" and entering a custom name.

### Date Filtering

Most pages support filtering:
- **Date Range**: Select start and end dates
- **Activity Types**: Multi-select specific activities
- Filters persist within each session

---

## 🔧 Configuration

### Gemini API Setup (Optional)

1. **Get API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with Google account
   - Create new API key

2. **Configure App**:
   - Open `.env` file in project root
   - Add your key:
     ```
     GEMINI_API_KEY=your_actual_key_here
     GEMINI_MODEL=gemini-2.5-flash
     ```

3. **Verify**:
   - Restart the app
   - Visit AI Activity Diary or AI Assistant pages
   - Look for "✅ Gemini API Configured" message

**Without API**: App uses template-based narratives as fallback - still fully functional!

---

## 💡 Tips & Best Practices

### Data Entry Tips
1. **Consistent Format**: Use the same date/time format throughout
2. **No Gaps**: End time of one activity should match start of next (not required)
3. **Overnight Activities**: Fully supported - end time can be after midnight
4. **Custom Activities**: Use clear, consistent names

### Analytics Tips
1. **Regular Data**: Upload data regularly for best trend analysis
2. **Compare Periods**: Use similar date ranges for fair comparisons
3. **Filter Smartly**: Use filters to focus on specific activities
4. **Review Insights**: Check AI-generated insights for pattern observations

### Performance Tips
1. **Data Size**: App handles thousands of records efficiently
2. **Date Ranges**: Smaller ranges load faster
3. **Charts**: Allow time for complex visualizations to render
4. **Database**: Stored locally in `data/actipulse.db`

---

## ❓ FAQ

### Q: Where is my data stored?
**A**: Locally in an SQLite database at `data/actipulse.db`. Your data never leaves your computer.

### Q: Do I need the Gemini API?
**A**: No! The app works fully without it, using template-based narratives instead.

### Q: Can I edit existing records?
**A**: Currently you can delete and re-add. Edit functionality coming soon.

### Q: What time zones are supported?
**A**: App uses your local system time zone.

### Q: Can I export my data?
**A**: PDF reports are coming soon. The database file can be backed up directly.

### Q: How do I clear all data?
**A**: Upload Activity → Manage Records → Clear All Activity Records

### Q: Is there a mobile app?
**A**: Currently web-only, but the UI is responsive and works on tablets.

### Q: Can multiple people use this?
**A**: Each installation has its own database. Run separate instances for multiple users.

---

## 🐛 Troubleshooting

### App won't start
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.12+ required)

### No data showing
- Verify data was imported successfully
- Check filters aren't excluding data
- Try refreshing the page

### Charts not loading
- Wait a few seconds for rendering
- Check browser console for errors
- Try a different browser

### API not working
- Verify `.env` file exists in project root
- Check API key is correct
- Ensure no extra spaces in `.env`
- Restart the app after changes

### Upload fails
- Verify file format (CSV or Excel)
- Check required columns exist
- Review validation report for specific errors
- Try sample CSV format

---

## 📧 Getting Help

### Resources
- **README.md**: Technical documentation
- **This Guide**: User documentation
- **Sample Data**: `python add_sample_data.py`
- **Test Features**: `python test_app_features.py`

### Support
- Check this guide first
- Review error messages carefully
- Try with sample data to isolate issues
- Restart app after configuration changes

---

**Last Updated**: November 2024  
**App Version**: 1.0.0  
**Guide Version**: 1.0.0

---

<div align="center">

**Happy Tracking! 🎉**

[⬆ Back to Top](#actipulse-ai---user-guide)

</div>
