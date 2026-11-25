# ActiPulse AI - PROCESS 2 Quick Start Guide

## 🚀 Launch the Application

### Step 1: Activate Virtual Environment
```powershell
cd "c:\Users\Sakthi sylesh\Downloads\ActiPulse AI – Physical Activity Diary Narrator"
.venv\Scripts\Activate.ps1
```

### Step 2: Run Streamlit
```powershell
streamlit run app.py
```

### Step 3: Open Browser
The application will automatically open at: **http://localhost:8501**

---

## 📊 Try It Out

### Option A: Upload Sample Data

1. Click **"Upload Activity"** in the sidebar
2. Go to **"📤 Upload File"** tab
3. Click **"Browse files"** or drag and drop
4. Upload `data/sample_activity.csv` (42 records)
5. Click **"✨ Validate & Process"**
6. Review the validation report
7. Click **"💾 Import X Valid Records"**
8. Navigate to **"Home Dashboard"** to see your data

### Option B: Manual Entry

1. Click **"Upload Activity"** in the sidebar
2. Go to **"✍️ Manual Entry"** tab
3. Select today's date
4. Choose start time: 09:00
5. Choose end time: 10:00
6. Select activity: Walking
7. Click **"➕ Add Activity Record"**
8. Navigate to **"Home Dashboard"** to see your record

### Option C: Try Invalid Data

1. Click **"Upload Activity"** in the sidebar
2. Upload `data/sample_invalid.csv`
3. See validation errors with detailed reasons
4. Only valid records can be imported

---

## 🧪 Run Tests

### All Tests
```powershell
python test_process2.py
python test_validation.py
python test_full_workflow.py
python test_ui_components.py
```

### Quick Test
```powershell
python test_process2.py
```

---

## 📁 Sample Files Available

- **data/sample_activity.csv** - 42 valid records (3 days)
- **data/sample_activity.xlsx** - 16 valid records (2 days)
- **data/sample_invalid.csv** - Mixed valid/invalid for testing

---

## 🎯 What to Explore

### Home Dashboard
- View real-time activity metrics
- Interactive Plotly charts
- Filter by date range and activity type
- Recent activity records table

### Upload Activity - File Upload
- CSV and Excel support
- Comprehensive validation
- Duplicate detection
- Overnight activity handling

### Upload Activity - Manual Entry
- Quick single record entry
- Activity type dropdown
- Custom activity labels
- Real-time validation

### Upload Activity - Manage Records
- View all records
- Filter by date and activity
- Delete individual records
- Clear all data option

---

## 🔄 Reset Database

To start fresh:
```powershell
Remove-Item data/actipulse.db
# Restart application
```

---

## 📚 Full Documentation

See **PROCESS2_README.md** for complete feature documentation.
See **PROCESS2_COMPLETION_REPORT.md** for implementation details.

---

## ✅ PROCESS 2 Complete

**Features Implemented:**
- ✅ Home Dashboard with real-time metrics
- ✅ CSV/Excel upload with validation
- ✅ Manual activity entry
- ✅ Activity management (view, filter, delete)
- ✅ Duplicate detection
- ✅ Overnight activity support
- ✅ Interactive Plotly charts
- ✅ Professional SaaS UI/UX

**All tests passing. Zero known issues.**

Ready for PROCESS 3!
