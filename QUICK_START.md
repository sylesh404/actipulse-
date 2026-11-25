# ActiPulse AI - Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Check Status
```bash
python check_status.py
```
This verifies everything is ready to go!

### Step 2: Launch the App
The Streamlit server is already running. Just open your browser:

**🌐 http://localhost:8501**

If you need to restart it:
```bash
# Activate virtual environment (if not already)
.venv\Scripts\Activate.ps1

# Run the app
streamlit run app.py
```

### Step 3: Explore!
Sample data is already loaded with 79 records covering 14 days.

---

## 📊 What's Already Loaded

✅ **79 Activity Records**
- 📅 Date range: November 12-25, 2026
- ⏱️ Total duration: 150 hours (9000 minutes)
- 🏃 Activities: Walking, Sitting, Standing, Running, Cycling

---

## 🎯 Recommended First Steps

### 1️⃣ Home Dashboard
See your activity overview with charts and metrics

### 2️⃣ Activity Analytics
Explore detailed breakdowns and patterns

### 3️⃣ Activity Comparison
Compare different days and weeks

### 4️⃣ AI Activity Diary
Generate natural language narratives

---

## 💡 Key Features to Try

### Upload Your Own Data
1. Go to **Upload Activity**
2. Download sample CSV template
3. Format your data
4. Upload and import

### Manual Entry
1. Go to **Upload Activity** → Manual Entry tab
2. Fill in the form
3. Add single records instantly

### Compare Activities
1. Go to **Activity Comparison**
2. Try Day-to-Day comparison
3. View Weekly Trends
4. Compare custom periods

### Generate Narratives
1. Go to **AI Activity Diary**
2. Select a date
3. Choose your preferred tone
4. Generate your diary entry

### Ask Questions
1. Go to **AI Assistant**
2. Type natural language questions
3. Get data-backed answers

---

## 📚 Documentation

- **USER_GUIDE.md** - Complete user manual
- **FEATURES_SUMMARY.md** - Detailed feature list
- **README.md** - Technical documentation
- **This file** - Quick reference

---

## 🔧 Useful Commands

```bash
# Check status
python check_status.py

# Add more sample data
python add_sample_data.py

# Test all features
python test_app_features.py

# Run the app
streamlit run app.py
```

---

## ⚙️ Configuration (Optional)

### Add Gemini API Key
For advanced AI features (not required - fallback provided):

1. Open `.env` file
2. Add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Restart the app

Get a free key at: https://makersuite.google.com/app/apikey

---

## 📱 Browser Access

**Local Access**: http://localhost:8501

**Other Devices on Network**: 
- Find your IP address: `ipconfig` (Windows)
- Access from other device: `http://YOUR_IP:8501`

---

## ❓ Troubleshooting

### App not loading?
```bash
# 1. Check if Streamlit is running
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"}

# 2. If not running, start it
streamlit run app.py

# 3. Open browser to http://localhost:8501
```

### No data showing?
```bash
# Add sample data
python add_sample_data.py
```

### Need to reset?
```bash
# Clear database (if needed)
# Delete: data/actipulse.db
# Then restart app - it will recreate automatically
```

---

## 🎨 What You'll See

### Modern UI
- Clean, professional design
- Gradient buttons and smooth animations
- Interactive charts and visualizations
- Responsive layout

### Rich Analytics
- Pie charts, bar graphs, line charts
- Distribution analysis
- Time-of-day patterns
- Comparison tools

### AI Features
- Natural language diary entries
- Conversational Q&A
- Activity insights
- Pattern recognition

---

## ✨ Sample Questions to Ask AI Assistant

Try these once you're in the app:

- "How much time did I spend walking on November 25th?"
- "What was my most frequent activity this week?"
- "Compare my sitting time between yesterday and today"
- "Show me all activities on November 20th"
- "What's my total walking time for the past week?"

---

## 🎉 You're Ready!

Everything is set up and working. The webapp is accessible at:

**🌐 http://localhost:8501**

**Sample data is loaded. All features are working. Enjoy exploring!**

---

## 📧 Need Help?

1. Check **USER_GUIDE.md** for detailed instructions
2. Review **FEATURES_SUMMARY.md** for feature details
3. Run `python check_status.py` to verify setup
4. Make sure you're on the correct URL: http://localhost:8501

---

<div align="center">

**Happy tracking! 🎊**

Made with ❤️ by ActiPulse AI

</div>
