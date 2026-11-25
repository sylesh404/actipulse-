"""Foundation unit tests for analytics contracts, database schema, and navigation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from components.sidebar import NAVIGATION_PAGES
from database.database import DatabaseManager
from modules import NON_MEDICAL_DISCLAIMER
from modules.activity_analytics import ActivityDistributionItem, ActivitySummary, compute_activity_summary
from modules.activity_comparison import DayComparisonResult, compare_activity_days
from modules.ai_narrator import create_genai_client
from modules.data_loader import ConfigurationError


def test_database_manager_initializes_schema(tmp_path: Path) -> None:
    db_file = tmp_path / "test_actipulse.db"
    manager = DatabaseManager(db_path=db_file)
    manager.initialize_schema()

    assert db_file.exists()
    counts = manager.get_table_counts()
    assert counts == {
        "upload_batches": 0,
        "activity_records": 0,
        "daily_narratives": 0,
        "report_history": 0,
    }


def test_navigation_has_all_seven_pages() -> None:
    keys = [key for key, _ in NAVIGATION_PAGES]
    assert keys == [
        "Home Dashboard",
        "Upload Activity",
        "Activity Analytics",
        "Activity Comparison",
        "AI Activity Diary",
        "AI Assistant",
        "Reports",
    ]


def test_analytics_and_comparison_dataclasses() -> None:
    item = ActivityDistributionItem(
        activity_label="Walking",
        total_minutes=45.0,
        percentage=60.0,
        session_count=2,
    )
    summary = ActivitySummary(
        total_minutes=75.0,
        total_sessions=3,
        unique_days=1,
        top_activity="Walking",
        distribution=[item],
    )
    assert summary.top_activity == "Walking"
    assert summary.distribution[0].percentage == 60.0

    comparison = DayComparisonResult(
        baseline_date="2026-11-24",
        target_date="2026-11-25",
        delta_minutes_by_activity={"Walking": 15.0},
        total_delta_minutes=15.0,
    )
    assert comparison.total_delta_minutes == 15.0


def test_placeholder_analytics_and_comparison_raise_not_implemented() -> None:
    df = pd.DataFrame()
    with pytest.raises(NotImplementedError):
        compute_activity_summary(df)
    with pytest.raises(NotImplementedError):
        compare_activity_days(df, "2026-11-24", "2026-11-25")


def test_create_genai_client_requires_valid_env_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    with pytest.raises(ConfigurationError):
        create_genai_client()


def test_non_medical_disclaimer_present() -> None:
    assert "does not provide medical advice" in NON_MEDICAL_DISCLAIMER.lower()
