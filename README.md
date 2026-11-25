# ActiPulse AI - Physical Activity Diary Narrator

> **Premium Sports-Tech Physical Activity Intelligence Platform**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.39+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

ActiPulse AI is an advanced physical activity tracking and analysis platform powered by AI. Track, visualize, and understand your daily activities with intelligent pattern detection and professional reporting.

![ActiPulse AI](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## ✨ Features

### Core Capabilities
- 📊 **Activity Tracking** - Record walking, sitting, standing, running, and cycling activities
- 📈 **Advanced Analytics** - Comprehensive duration and distribution analysis
- 🤖 **AI Narratives** - Multi-LLM support (Groq + Google Gemini) for activity insights
- 💬 **AI Assistant** - Interactive chat-based activity analysis

### Advanced Intelligence (v2.0.0)

#### ⏱️ Smart Activity Timeline
Interactive daily timeline visualization showing chronological activity sessions
- Plotly-based horizontal timeline charts
- Activity-specific color coding
- Time range filters (Morning/Afternoon/Evening/Night)
- Overnight session handling
- Real-time statistics dashboard

#### 🔍 Intelligent Pattern Detection
AI-powered statistical analysis detecting unusual activity patterns
- Median + IQR statistical methods
- Three-tier severity classification (Significant/Moderate/Minor)
- Pattern types: unusual duration, session changes, distribution shifts
- Configurable lookback period (7-90 days)
- 30-day trend visualization

#### 📊 Advanced Evidence-Based Reporting
Professional report generation with timeline and pattern analysis
- **PDF Reports** - Multi-page professional documents (ReportLab)
- **Excel Reports** - 5-sheet workbooks with comprehensive data (OpenPyXL)
- Customizable content sections
- Report generation history tracking

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sylesh404/actipulse-.git
cd actipulse-
```

2. **Create virtual environment**
```bash
python -m venv .venv
```

3. **Activate virtual environment**

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**

Create a `.env` file in the root directory:
```env
# API Keys (optional - for AI features)
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database (optional - defaults to data/actipulse.db)
DATABASE_PATH=data/actipulse.db

# LLM Provider (optional - defaults to auto)
LLM_PROVIDER=auto
```

6. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage

### Uploading Activity Data

1. Navigate to **📤 Upload Activity**
2. Upload a CSV or Excel file with columns:
   - `date` (YYYY-MM-DD)
   - `start_time` (HH:MM)
   - `end_time` (HH:MM)
   - `activity` (Walking, Sitting, Standing, Running, Cycling)

**Or** manually enter activities using the form.

### Viewing Analytics

- **📊 Activity Analytics** - Duration breakdowns and distribution
- **⚖️ Activity Comparison** - Compare activities across time periods
- **⏱️ Smart Timeline** - Interactive daily visualization

### Generating Insights

- **🔍 Pattern Detection** - Find unusual activity patterns
- **📝 AI Activity Diary** - Generate AI narratives for your activities
- **💬 AI Assistant** - Chat with AI about your activity data
- **📊 Advanced Reports** - Create professional PDF/Excel reports

---

## 🏗️ Architecture

```
ActiPulse AI/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
│
├── backend/
│   └── services/          # Backend business logic
│       ├── activity_timeline.py
│       ├── pattern_detection.py
│       ├── pdf_report_generator.py
│       └── excel_report_generator.py
│
├── components/            # UI components
│   ├── dashboard.py
│   ├── sidebar.py
│   ├── timeline_page.py
│   ├── pattern_page.py
│   └── reports_page.py
│
├── database/              # Data persistence
│   └── database.py        # SQLite operations
│
├── modules/               # Core modules
│   ├── ai_narrator_v2.py
│   ├── llm_provider.py
│   └── preprocessing.py
│
└── assets/
    └── style.css          # Premium sports-tech styling
```

---

## 🎨 Design Philosophy

### Premium Sports-Tech Aesthetic
- **Primary Color:** Neon Green (#AFFA00)
- **Background:** Pure Black (#000000)
- **Surface:** Charcoal (#1C1C1C)
- **Typography:** Clean, athletic, high-contrast

### Evidence-Based Approach
- Never fabricates data - all information from database
- Never treats missing data as zero
- Python-side calculations
- Single source of truth (SQLite database)

---

## 🔧 Technology Stack

- **UI Framework:** Streamlit 1.39+
- **Visualization:** Plotly 5.24+
- **Data Processing:** Pandas 2.2+, NumPy 1.26+
- **PDF Generation:** ReportLab 4.2+
- **Excel Generation:** OpenPyXL 3.1+
- **AI Integration:** Groq + Google Gemini
- **Database:** SQLite 3

---

## 📊 Key Statistics

- **8 New Files** - Advanced features implementation
- **2,500+ Lines of Code** - Backend services and UI
- **10+ Data Classes** - Type-safe data structures
- **25+ Functions** - Comprehensive feature set
- **3 Major Features** - Timeline, Patterns, Reports

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Get up and running
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical overview
- **[Completion Report](ACTIPULSE_ADVANCED_FEATURES_COMPLETION_REPORT.md)** - Full documentation
- **[Project Structure](PROJECT_STRUCTURE.md)** - Architecture guide
- **[Changelog](CHANGELOG_ADVANCED_FEATURES.md)** - Version history

---

## 🔐 Privacy & Security

- ✅ **Local Storage** - All data stored locally in SQLite
- ✅ **No Cloud Sync** - No external data transmission
- ✅ **Full Control** - You own and control all data
- ✅ **Optional AI** - AI features require API keys (not mandatory)

### Medical Disclaimer
⚠️ ActiPulse AI is for informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers with questions about your physical health.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📋 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Streamlit** - Amazing UI framework
- **Plotly** - Interactive visualizations
- **ReportLab & OpenPyXL** - Report generation
- **Groq & Google** - AI/LLM capabilities

---

## 📞 Support

For questions or issues:
- 📧 Open an issue on GitHub
- 📖 Check the [documentation](ACTIPULSE_ADVANCED_FEATURES_COMPLETION_REPORT.md)
- 💬 Review the [Quick Start Guide](QUICK_START_GUIDE.md)

---

## 🎯 Roadmap

### Current (v2.0.0)
- ✅ Smart Activity Timeline
- ✅ Intelligent Pattern Detection
- ✅ Advanced Evidence-Based Reporting
- ✅ Multi-LLM Support (Groq + Gemini)
- ✅ Premium Sports-Tech UI

### Future Enhancements
- [ ] Multi-day timeline view
- [ ] Predictive pattern analysis
- [ ] Automated email reports
- [ ] Machine learning models
- [ ] Mobile app integration
- [ ] Real-time activity tracking

---

**Made with ⚡ by the ActiPulse AI Team**

**Version 2.0.0** | **Last Updated: 2024** | **Status: Production Ready**
