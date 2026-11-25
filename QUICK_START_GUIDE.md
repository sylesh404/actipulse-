# ActiPulse AI - Advanced Features Quick Start Guide

## 🚀 What's New

Three powerful advanced features have been added to ActiPulse AI:

### 1. ⏱️ Smart Activity Timeline
Interactive daily timeline showing your activities chronologically with intelligent edge case handling.

### 2. 🔍 Intelligent Pattern Detection  
AI-powered statistical analysis detecting unusual activity patterns and behavioral changes.

### 3. 📊 Advanced Evidence-Based Reporting
Professional PDF and Excel report generation with timeline analysis and pattern insights.

---

## 🎯 Quick Start

### Starting the Application

```bash
cd "ActiPulse AI – Physical Activity Diary Narrator"
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📍 Navigation

Look for three new menu items in the sidebar:

- **⏱️ Smart Timeline** - View your daily activity timeline
- **🔍 Pattern Detection** - Discover unusual activity patterns  
- **📊 Advanced Reports** - Generate professional reports

---

## 💡 Feature Walkthrough

### Smart Activity Timeline

1. Click **⏱️ Smart Timeline** in sidebar
2. Select a date to analyze
3. Optional: Filter by time range (Morning/Afternoon/Evening/Night)
4. View your interactive timeline chart
5. Check daily statistics at the top

**What you'll see:**
- Color-coded horizontal bars for each activity
- Hover over bars for detailed session info
- Total sessions, duration, and unique activities
- Handles overnight activities automatically

---

### Intelligent Pattern Detection

1. Click **🔍 Pattern Detection** in sidebar
2. Select the date to analyze
3. Choose historical baseline (7, 14, 30, 60, or 90 days)
4. Click **🔍 Analyze Patterns**
5. Review detected patterns organized by severity

**Pattern Severity Levels:**
- 🔴 **Significant** - Major deviations (>1.5 std)
- 🟠 **Moderate** - Notable changes (>1.0 std)
- 🟢 **Minor** - Small variations (>30% change)

**What it detects:**
- Unusual activity duration (too long or too short)
- Session duration trend changes
- Activity distribution anomalies

---

### Advanced Reports

1. Click **📊 Advanced Reports** in sidebar
2. Choose between **PDF** or **Excel** tab

#### For PDF Reports:
- **Quick Daily Summary**: Single-day comprehensive report
  - Select date
  - Click **Generate Daily PDF**
  - Download your report
  
- **Comprehensive Period Report**: Multi-day analysis
  - Select date range
  - Toggle sections (Timeline/Patterns/Narratives)
  - Click **Generate Full PDF**
  - Download your report

#### For Excel Reports:
- Select date range
- Click **Generate Excel**
- Download multi-sheet workbook
  - Summary sheet
  - Raw activity data
  - Timeline analysis
  - Pattern detection results
  - Daily statistics

---

## 🎨 Visual Guide

### Timeline Colors
- **Walking**: Bright neon green (#AFFA00)
- **Sitting**: Light green (#CFED89)
- **Standing**: White (#FFFFFF)
- **Running**: Lime green (#7FBF00)
- **Cycling**: Yellow-green (#9FD500)

### Pattern Severity Colors
- **Significant**: Red (#FF4444)
- **Moderate**: Orange (#FFAA00)
- **Minor**: Neon green (#AFFA00)

---

## 📊 Sample Workflow

### Complete Activity Analysis Workflow

1. **Upload Data** (📤 Upload Activity)
   - Upload your CSV/Excel activity file
   - Or manually enter activities

2. **View Timeline** (⏱️ Smart Timeline)
   - See chronological activity visualization
   - Identify gaps or overlaps

3. **Detect Patterns** (🔍 Pattern Detection)
   - Find unusual activity patterns
   - Understand behavioral changes

4. **Generate Report** (📊 Advanced Reports)
   - Create professional PDF/Excel report
   - Share with healthcare provider if needed

5. **Review AI Insights** (📝 AI Activity Diary)
   - Get AI-generated activity narratives
   - Understand context and patterns

---

## ⚙️ Configuration Tips

### Best Practices

**For Timeline:**
- Use time range filters to focus on specific periods
- Check overnight activities (they span across midnight correctly)

**For Pattern Detection:**
- Use 30-day baseline for reliable results
- Need at least 5 historical samples for detection
- Significant patterns warrant closer attention

**For Reports:**
- Include Timeline for session overview
- Include Patterns for unusual activity insights
- Include AI Narratives for contextual understanding
- Excel format best for detailed data analysis
- PDF format best for sharing/printing

---

## 🔧 Troubleshooting

### "No patterns detected"
✅ Normal! Means all activities are within expected ranges.
- Try a longer lookback period (60 or 90 days)
- Need sufficient historical data (5+ samples)

### "No timeline data available"
✅ Upload activity data first
- Go to **📤 Upload Activity**
- Upload CSV/Excel or enter manually

### "Report generation failed"
✅ Check date range has data
- Verify activities exist for selected dates
- Try a different date range

---

## 📚 Additional Resources

### Full Documentation
See `ACTIPULSE_ADVANCED_FEATURES_COMPLETION_REPORT.md` for:
- Complete technical details
- Architecture overview
- Data structures
- API reference

### Support
For issues or questions:
1. Check the completion report
2. Review this quick start guide
3. Examine error messages carefully

---

## 🎓 Tips for Best Results

### Data Quality
- Upload complete, accurate activity data
- Include start/end times for timeline accuracy
- Use consistent activity labels

### Analysis
- Check timeline before running pattern detection
- Use longer lookback periods for stability
- Review significant patterns carefully

### Reporting
- Generate reports regularly (weekly/monthly)
- Include all sections for comprehensive view
- Keep reports for trend analysis

---

## 🏆 Key Benefits

### Smart Timeline
- Visualize your entire day at a glance
- Identify activity gaps
- Understand daily patterns

### Pattern Detection  
- Discover unusual behavior automatically
- Statistical confidence in findings
- Early detection of changes

### Advanced Reports
- Professional documentation
- Shareable with healthcare providers
- Excel format for custom analysis
- PDF format for archiving

---

## ⚠️ Important Notes

### Medical Disclaimer
ActiPulse AI is for informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers with questions about your physical health.

### Data Privacy
- All data stored locally on your computer
- No external data transmission
- Reports generated client-side
- Complete privacy and control

---

## 🎉 Get Started Now!

1. Launch the app: `streamlit run app.py`
2. Upload your activity data
3. Explore the new features
4. Generate your first report

**Happy tracking with ActiPulse AI! ⚡**
