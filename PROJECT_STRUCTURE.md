# ActiPulse AI - Project Structure

## 📁 Directory Layout

```
ActiPulse AI – Physical Activity Diary Narrator/
│
├── 📄 app.py                              # Main Streamlit application entry point
├── 📄 requirements.txt                     # Python dependencies
├── 📄 .env                                 # Environment configuration (API keys)
│
├── 📂 assets/                              # Static assets
│   └── 📄 style.css                        # Premium sports-tech CSS styling
│
├── 📂 backend/                             # Backend services layer
│   └── 📂 services/                        # Business logic services
│       ├── 📄 activity_timeline.py         # ⏱️ Timeline data processing
│       ├── 📄 pattern_detection.py         # 🔍 Statistical pattern analysis
│       ├── 📄 pdf_report_generator.py      # 📄 ReportLab PDF generation
│       └── 📄 excel_report_generator.py    # 📊 OpenPyXL Excel generation
│
├── 📂 components/                          # Frontend UI components
│   ├── 📄 charts.py                        # Plotly chart builders
│   ├── 📄 dashboard.py                     # Home dashboard and page renderers
│   ├── 📄 sidebar.py                       # Navigation sidebar
│   ├── 📄 ui_components.py                 # Reusable UI elements
│   ├── 📄 timeline_page.py                 # ⏱️ Smart Timeline page UI
│   ├── 📄 pattern_page.py                  # 🔍 Pattern Detection page UI
│   └── 📄 reports_page.py                  # 📊 Advanced Reports page UI
│
├── 📂 database/                            # Data persistence layer
│   └── 📄 database.py                      # SQLite connection and CRUD operations
│
├── 📂 modules/                             # Core business logic modules
│   ├── 📄 __init__.py                      # Module initialization
│   ├── 📄 activity_analytics.py            # Activity calculation functions
│   ├── 📄 ai_agent.py                      # Tool-based AI agent
│   ├── 📄 ai_narrator.py                   # Legacy AI narrator
│   ├── 📄 ai_narrator_v2.py                # Enhanced AI narrator
│   ├── 📄 data_loader.py                   # CSV/Excel file loading
│   ├── 📄 llm_provider.py                  # Multi-LLM manager (Groq + Gemini)
│   └── 📄 preprocessing.py                 # Data validation and cleaning
│
├── 📂 data/                                # SQLite database storage
│   └── 📄 actipulse.db                     # Local database file
│
└── 📂 docs/                                # Documentation (new)
    ├── 📄 ACTIPULSE_ADVANCED_FEATURES_COMPLETION_REPORT.md
    ├── 📄 QUICK_START_GUIDE.md
    ├── 📄 IMPLEMENTATION_SUMMARY.md
    ├── 📄 CHANGELOG_ADVANCED_FEATURES.md
    └── 📄 PROJECT_STRUCTURE.md             # This file
```

---

## 🗂️ File Organization by Feature

### Core Application
```
app.py                              Main entry point, routing
requirements.txt                     Dependencies
.env                                 Configuration
```

### Feature 1: Smart Activity Timeline ⏱️
```
backend/services/activity_timeline.py    Data processing & statistics
components/timeline_page.py              UI and visualization
```

### Feature 2: Intelligent Pattern Detection 🔍
```
backend/services/pattern_detection.py    Statistical analysis engine
components/pattern_page.py               UI and pattern visualization
```

### Feature 3: Advanced Reports 📊
```
backend/services/pdf_report_generator.py    PDF generation with ReportLab
backend/services/excel_report_generator.py  Excel generation with OpenPyXL
components/reports_page.py                  UI and report management
```

### UI Components
```
components/sidebar.py               Navigation menu
components/dashboard.py             Home and page renderers
components/ui_components.py         Reusable UI elements
components/charts.py                Chart builders
assets/style.css                    Sports-tech styling
```

### Data Layer
```
database/database.py                SQLite operations
data/actipulse.db                   Local database
```

### Business Logic
```
modules/activity_analytics.py       Activity calculations
modules/data_loader.py              File import logic
modules/preprocessing.py            Data validation
modules/llm_provider.py             Multi-LLM management
modules/ai_narrator_v2.py           AI narrative generation
modules/ai_agent.py                 Tool-based AI
```

### Documentation
```
ACTIPULSE_ADVANCED_FEATURES_COMPLETION_REPORT.md   Technical documentation
QUICK_START_GUIDE.md                                User guide
IMPLEMENTATION_SUMMARY.md                           Developer summary
CHANGELOG_ADVANCED_FEATURES.md                      Version history
PROJECT_STRUCTURE.md                                This file
```

---

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Timeline  │  │  Patterns  │  │  Reports   │  ...more   │
│  │   Page     │  │    Page    │  │    Page    │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
│        │               │               │                    │
│        │               │               │                    │
└────────┼───────────────┼───────────────┼────────────────────┘
         │               │               │
         ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND SERVICES LAYER                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Timeline  │  │  Pattern   │  │   Report   │           │
│  │  Service   │  │  Detection │  │ Generators │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
│        │               │               │                    │
│        └───────────────┼───────────────┘                    │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              DatabaseManager                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │  activity_ │  │   daily_   │  │  report_   │    │  │
│  │  │  records   │  │ narratives │  │  history   │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│                     SQLite (actipulse.db)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Dependencies

### Timeline Page Dependencies
```
timeline_page.py
├── streamlit
├── plotly.graph_objects
├── backend.services.activity_timeline
│   ├── get_daily_timeline()
│   ├── get_timeline_statistics()
│   └── filter_timeline_by_time_range()
├── components.ui_components
│   ├── render_page_hero()
│   └── render_non_medical_disclaimer()
└── database.database (DatabaseManager)
```

### Pattern Page Dependencies
```
pattern_page.py
├── streamlit
├── plotly.graph_objects
├── pandas
├── backend.services.pattern_detection
│   ├── detect_all_patterns_for_date()
│   ├── get_pattern_overview()
│   └── calculate_historical_baseline()
├── components.ui_components
│   ├── render_page_hero()
│   └── render_non_medical_disclaimer()
└── database.database (DatabaseManager)
```

### Reports Page Dependencies
```
reports_page.py
├── streamlit
├── backend.services.pdf_report_generator
│   ├── generate_activity_report_pdf()
│   └── generate_quick_summary_pdf()
├── backend.services.excel_report_generator
│   └── generate_activity_report_excel()
├── components.ui_components
│   ├── render_page_hero()
│   └── render_non_medical_disclaimer()
└── database.database (DatabaseManager)
```

---

## 🗄️ Database Schema

### Tables Used by Advanced Features

#### activity_records (primary data source)
```sql
CREATE TABLE activity_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER,
    activity_date TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    activity_label TEXT NOT NULL,
    duration_minutes REAL NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (batch_id) REFERENCES upload_batches(id)
);

-- Indexes
CREATE INDEX idx_activity_records_date ON activity_records(activity_date);
CREATE INDEX idx_activity_records_label ON activity_records(activity_label);
```

#### daily_narratives (used in reports)
```sql
CREATE TABLE daily_narratives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_date TEXT NOT NULL UNIQUE,
    narrative_text TEXT NOT NULL,
    model_name TEXT,
    generated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

#### report_history (tracks report generation)
```sql
CREATE TABLE report_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_name TEXT NOT NULL,
    report_format TEXT NOT NULL,
    date_range_start TEXT,
    date_range_end TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

## 🎨 UI Component Hierarchy

```
App Root (app.py)
│
├── Sidebar (sidebar.py)
│   ├── Brand Header
│   ├── Navigation Menu
│   │   ├── 🏠 Home Dashboard
│   │   ├── 📤 Upload Activity
│   │   ├── 📊 Activity Analytics
│   │   ├── ⚖️ Activity Comparison
│   │   ├── ⏱️ Smart Timeline         [NEW]
│   │   ├── 🔍 Pattern Detection      [NEW]
│   │   ├── 📝 AI Activity Diary
│   │   ├── 💬 AI Assistant
│   │   ├── ⚙️ AI Settings
│   │   └── 📊 Advanced Reports       [NEW]
│   └── Status Footer
│
└── Main Content Area
    ├── Page Hero (render_page_hero)
    │   ├── Eyebrow
    │   ├── Title
    │   └── Subtitle
    │
    ├── Page Content
    │   ├── KPI Cards (render_kpi_card)
    │   ├── Charts (Plotly)
    │   ├── Tables (Dataframes)
    │   ├── Forms (Streamlit)
    │   └── Custom Components
    │
    └── Page Footer
        └── Medical Disclaimer (render_non_medical_disclaimer)
```

---

## 🔧 Configuration Files

### requirements.txt
```
streamlit>=1.39.0        # UI framework
pandas>=2.2.0            # Data processing
numpy>=1.26.0            # Numerical ops
plotly>=5.24.0           # Visualizations
google-genai>=0.8.0      # Gemini AI
groq>=0.11.0             # Groq AI
openpyxl>=3.1.5          # Excel generation
reportlab>=4.2.0         # PDF generation
python-dotenv>=1.0.1     # Environment config
pytest>=8.3.0            # Testing
```

### .env (example)
```
# API Keys
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

# Database
DATABASE_PATH=data/actipulse.db

# App Settings
LLM_PROVIDER=auto  # auto, groq, or gemini
```

---

## 📊 Code Metrics

### File Sizes (approximate)
```
activity_timeline.py          ~400 lines
pattern_detection.py          ~500 lines
pdf_report_generator.py       ~350 lines
excel_report_generator.py     ~400 lines
timeline_page.py              ~350 lines
pattern_page.py               ~450 lines
reports_page.py               ~300 lines
```

### Total New Code
```
Backend Services:   ~1,650 lines
Frontend UI:        ~1,100 lines
Documentation:      ~2,000 lines
Total:              ~4,750 lines
```

---

## 🚀 Execution Flow

### Application Startup
```
1. app.py main()
   ├── configure_page()
   ├── load_custom_css()
   ├── get_initialized_database()
   ├── render_sidebar()
   └── route_to_selected_page()
```

### Timeline Page Flow
```
1. User navigates to Smart Timeline
2. render_timeline_page(db_manager)
   ├── render_page_hero()
   ├── date_selection_ui()
   ├── get_daily_timeline(db_manager, date)
   ├── get_timeline_statistics(db_manager, date)
   ├── create_timeline_chart(timeline_data)
   └── render_non_medical_disclaimer()
```

### Pattern Detection Flow
```
1. User navigates to Pattern Detection
2. render_pattern_detection_page(db_manager)
   ├── render_page_hero()
   ├── date_and_lookback_selection_ui()
   ├── detect_all_patterns_for_date(db_manager, date, lookback)
   ├── render_pattern_summary_cards()
   ├── render_pattern_details()
   ├── render_pattern_visualization()
   └── render_non_medical_disclaimer()
```

### Report Generation Flow
```
1. User navigates to Advanced Reports
2. render_advanced_reports_page(db_manager)
   ├── render_page_hero()
   ├── date_range_selection_ui()
   ├── generate_activity_report_pdf() or
   │   generate_activity_report_excel()
   ├── log_report_generation(db_manager)
   ├── download_button(report_bytes)
   └── render_non_medical_disclaimer()
```

---

## 🔍 Key Design Patterns

### Separation of Concerns
- **Backend:** Pure Python logic, no UI dependencies
- **Frontend:** Streamlit UI, calls backend services
- **Database:** Single source of truth, accessed via DatabaseManager

### Dataclass Pattern
```python
@dataclass
class TimelineSession:
    activity_label: str
    start_time: str
    duration_minutes: float
    # ... more fields
```

### Service Layer Pattern
```python
def get_daily_timeline(db_manager, date):
    # 1. Fetch data from database
    # 2. Process and validate
    # 3. Return structured dataclass
```

### Component Pattern
```python
def render_timeline_page(db_manager):
    # 1. Render UI elements
    # 2. Handle user interactions
    # 3. Call backend services
    # 4. Display results
```

---

## 📚 Import Map

### Circular Dependency Avoidance
```
✅ GOOD: UI → Services → Database
❌ BAD:  Services → UI
❌ BAD:  Database → Services
```

### Import Guidelines
- UI components import from backend services ✅
- Backend services import from database ✅
- Backend services DO NOT import from UI ✅
- All modules import from modules/ as needed ✅

---

## 🎯 Entry Points

### Main Application
```bash
streamlit run app.py
```

### Testing (when implemented)
```bash
pytest tests/
```

### Database Inspection
```bash
sqlite3 data/actipulse.db
```

---

## 📖 Documentation Map

### For Users
- `QUICK_START_GUIDE.md` - How to use the features
- In-app help text and tooltips

### For Developers
- `PROJECT_STRUCTURE.md` - This file (architecture overview)
- `IMPLEMENTATION_SUMMARY.md` - Technical summary
- `ACTIPULSE_ADVANCED_FEATURES_COMPLETION_REPORT.md` - Full documentation
- Inline code comments and docstrings

### For Maintainers
- `CHANGELOG_ADVANCED_FEATURES.md` - Version history
- Code docstrings and type hints
- Database schema comments

---

## 🛠️ Development Workflow

### Adding New Features
1. Create backend service in `backend/services/`
2. Create UI component in `components/`
3. Add navigation item in `sidebar.py`
4. Add routing in `app.py`
5. Update documentation

### Modifying Existing Features
1. Update backend service logic
2. Update UI component if needed
3. Test thoroughly
4. Update changelog

---

This project structure document provides a comprehensive map of ActiPulse AI's organization, making it easy for developers to navigate and understand the codebase.

**Last Updated:** 2024  
**Version:** 2.0.0
