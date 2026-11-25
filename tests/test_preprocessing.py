"""Foundation unit tests for data validation and preprocessing contracts."""

from __future__ import annotations

import pandas as pd
import pytest

from modules.data_loader import (
    DataValidationError,
    load_activity_file,
    validate_activity_dataframe,
    validate_file_extension,
)
from modules.preprocessing import normalize_activity_label, preprocess_activity_data


def test_validate_file_extension_accepts_supported_types() -> None:
    assert validate_file_extension("sample.csv") is True
    assert validate_file_extension("logs.XLSX") is True
    assert validate_file_extension("activities.json") is True
    assert validate_file_extension("notes.txt") is False


def test_validate_activity_dataframe_valid_and_missing_columns() -> None:
    valid_df = pd.DataFrame(
        {
            "activity_label": ["walking", "sitting"],
            "duration_minutes": [30.0, 45.0],
        }
    )
    ok_result = validate_activity_dataframe(valid_df)
    assert ok_result.is_valid is True
    assert ok_result.missing_columns == []
    assert ok_result.row_count == 2

    invalid_df = pd.DataFrame({"activity_label": ["walking"]})
    bad_result = validate_activity_dataframe(invalid_df)
    assert bad_result.is_valid is False
    assert "duration_minutes" in bad_result.missing_columns


def test_validate_activity_dataframe_empty() -> None:
    empty_df = pd.DataFrame()
    result = validate_activity_dataframe(empty_df)
    assert result.is_valid is False
    assert result.row_count == 0


def test_normalize_activity_label() -> None:
    assert normalize_activity_label(" walking ") == "Walking"
    assert normalize_activity_label("jogging") == "Running"
    assert normalize_activity_label("biking") == "Cycling"
    assert normalize_activity_label("yoga") == "Yoga"
    assert normalize_activity_label("   ") == "Other"


def test_load_activity_file_rejects_unsupported_extension() -> None:
    with pytest.raises(DataValidationError):
        load_activity_file("unsupported.pdf")


def test_preprocess_placeholder_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        preprocess_activity_data(pd.DataFrame())
