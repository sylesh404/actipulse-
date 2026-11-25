"""ActiPulse AI – Physical Activity Diary Narrator.

Process 1 entry point: configures Streamlit, initializes SQLite foundation,
applies SaaS styling, and routes between all seven application pages.
"""

from __future__ import annotations

import logging

from dotenv import load_dotenv
import streamlit as st

from components.dashboard import (
    render_activity_analytics_page,
    render_activity_comparison_page,
    render_ai_activity_diary_page,
    render_ai_assistant_page,
    render_ai_settings_page,
    render_home_dashboard,
    render_advanced_reports_page,
    render_upload_activity_page,
)
from components.timeline_page import render_timeline_page
from components.pattern_page import render_pattern_detection_page
from components.sidebar import render_sidebar
from components.ui_components import load_custom_css
from database.database import DatabaseManager
from modules import APP_NAME, APP_SUBTITLE

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def configure_page() -> None:
    """Configure Streamlit page metadata and responsive wide layout."""
    st.set_page_config(
        page_title=f"{APP_NAME} – {APP_SUBTITLE}",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )


@st.cache_resource
def get_initialized_database() -> DatabaseManager:
    """Create and initialize the SQLite database schema once per session."""
    manager = DatabaseManager()
    manager.initialize_schema()
    return manager


def main() -> None:
    """Run the ActiPulse AI Streamlit application."""
    configure_page()
    load_custom_css()

    try:
        db_manager = get_initialized_database()
    except Exception as exc:
        logger.exception("Failed to initialize database: %s", exc)
        st.error("Unable to initialize the local SQLite database. Check logs for details.")
        st.stop()

    selected_page = render_sidebar()

    if selected_page == "Home Dashboard":
        render_home_dashboard(db_manager)
    elif selected_page == "Upload Activity":
        render_upload_activity_page(db_manager)
    elif selected_page == "Activity Analytics":
        render_activity_analytics_page(db_manager)
    elif selected_page == "Activity Comparison":
        render_activity_comparison_page(db_manager)
    elif selected_page == "Smart Timeline":
        render_timeline_page(db_manager)
    elif selected_page == "Pattern Detection":
        render_pattern_detection_page(db_manager)
    elif selected_page == "AI Activity Diary":
        render_ai_activity_diary_page(db_manager)
    elif selected_page == "AI Assistant":
        render_ai_assistant_page(db_manager)
    elif selected_page == "AI Settings":
        render_ai_settings_page()
    elif selected_page == "Advanced Reports":
        render_advanced_reports_page(db_manager)
    else:
        render_home_dashboard(db_manager)


if __name__ == "__main__":
    main()
