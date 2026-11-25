"""Activity data validation, time/duration calculation, and preprocessing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
import re
from typing import Any

import pandas as pd

from modules.data_loader import (
    EXPECTED_UPLOAD_COLUMNS,
    normalize_upload_columns,
)

PRESET_ACTIVITY_LABELS: tuple[str, ...] = (
    "Walking",
    "Sitting",
    "Standing",
    "Running",
    "Cycling",
    "Other",
)

STANDARD_ACTIVITY_LABELS: dict[str, str] = {
    "walk": "Walking",
    "walking": "Walking",
    "sit": "Sitting",
    "sitting": "Sitting",
    "stand": "Standing",
    "standing": "Standing",
    "run": "Running",
    "running": "Running",
    "jogging": "Running",
    "cycle": "Cycling",
    "cycling": "Cycling",
    "biking": "Cycling",
}

_TIME_PATTERNS = ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p")
_DATE_PATTERNS = ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y")


@dataclass(frozen=True)
class RejectedRecord:
    """Details explaining why a row was rejected or flagged as duplicate."""

    row_number: int
    raw_date: str
    raw_start_time: str
    raw_end_time: str
    raw_activity: str
    reason: str
    category: str  # "invalid" or "duplicate"


@dataclass
class PreprocessingReport:
    """Comprehensive validation and preprocessing summary for uploaded datasets."""

    total_records: int = 0
    valid_records_count: int = 0
    invalid_records_count: int = 0
    duplicate_records_count: int = 0
    overnight_records_count: int = 0
    missing_columns: list[str] = field(default_factory=list)
    valid_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    rejected_records: list[RejectedRecord] = field(default_factory=list)

    @property
    def has_schema_errors(self) -> bool:
        """Return True if required columns are missing from the dataset."""
        return len(self.missing_columns) > 0


def normalize_activity_label(label: Any) -> str:
    """Normalize raw activity labels while preserving custom user labels."""
    if label is None or (isinstance(label, float) and pd.isna(label)):
        return "Other"
    if not isinstance(label, str):
        label = str(label)
    trimmed = label.strip()
    if not trimmed:
        return "Other"

    cleaned = trimmed.lower()
    if cleaned in STANDARD_ACTIVITY_LABELS:
        return STANDARD_ACTIVITY_LABELS[cleaned]

    if trimmed.islower() or trimmed.isupper():
        return trimmed.title()
    return trimmed


def _is_missing_value(value: Any) -> bool:
    """Return True if value represents a missing or blank cell."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except TypeError:
        pass
    return isinstance(value, str) and not value.strip()


def parse_activity_date(value: Any) -> date:
    """Parse a date cell into a Python date object or raise ValueError."""
    if _is_missing_value(value):
        raise ValueError("Missing activity date.")

    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    # Strip ISO timestamp suffix if an Excel/CSV export includes midnight time
    if " " in text and re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}\s+00:00(:00)?$", text):
        text = text.split()[0]

    for fmt in _DATE_PATTERNS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Invalid date format '{text}'. Expected YYYY-MM-DD.")


def parse_activity_time(value: Any) -> time:
    """Parse a time cell into a Python time object or raise ValueError."""
    if _is_missing_value(value):
        raise ValueError("Missing time value.")

    if isinstance(value, pd.Timestamp):
        return value.time().replace(microsecond=0)
    if isinstance(value, datetime):
        return value.time().replace(microsecond=0)
    if isinstance(value, time):
        return value.replace(microsecond=0)

    text = str(value).strip()
    # Handle Excel fractional-day float strings if any sneak in? Reject non-time text cleanly.
    for fmt in _TIME_PATTERNS:
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue

    raise ValueError(f"Invalid time format '{text}'. Expected HH:MM (24-hour).")


def calculate_duration_minutes(
    activity_date: date,
    start_t: time,
    end_t: time,
    allow_overnight: bool = True,
) -> tuple[float, bool]:
    """Calculate activity duration in minutes in Python, supporting overnight intervals.

    Returns:
        Tuple of (duration_minutes, is_overnight).
    """
    start_dt = datetime.combine(activity_date, start_t)
    end_dt = datetime.combine(activity_date, end_t)
    is_overnight = False

    if end_dt < start_dt:
        if not allow_overnight:
            raise ValueError("End time is earlier than start time (negative duration).")
        end_dt += timedelta(days=1)
        is_overnight = True

    delta_minutes = round((end_dt - start_dt).total_seconds() / 60.0, 2)
    if delta_minutes <= 0:
        raise ValueError("Duration must be greater than 0 minutes (zero or negative duration).")

    return delta_minutes, is_overnight


def validate_single_activity_row(
    raw_date: Any,
    raw_start_time: Any,
    raw_end_time: Any,
    raw_activity: Any,
    allow_overnight: bool = True,
) -> tuple[dict[str, Any], bool]:
    """Validate and normalize a single activity record.

    Returns:
        Tuple of (normalized_record_dict, is_overnight).
    """
    if _is_missing_value(raw_activity):
        raise ValueError("Empty or missing activity label.")

    parsed_date = parse_activity_date(raw_date)
    parsed_start = parse_activity_time(raw_start_time)
    parsed_end = parse_activity_time(raw_end_time)
    duration_minutes, is_overnight = calculate_duration_minutes(
        parsed_date,
        parsed_start,
        parsed_end,
        allow_overnight=allow_overnight,
    )

    label_text = normalize_activity_label(str(raw_activity))
    if not label_text:
        raise ValueError("Empty or missing activity label.")

    start_fmt = parsed_start.strftime("%H:%M") if parsed_start.second == 0 else parsed_start.strftime("%H:%M:%S")
    end_fmt = parsed_end.strftime("%H:%M") if parsed_end.second == 0 else parsed_end.strftime("%H:%M:%S")

    record = {
        "activity_date": parsed_date.isoformat(),
        "start_time": start_fmt,
        "end_time": end_fmt,
        "activity_label": label_text,
        "duration_minutes": duration_minutes,
        "is_overnight": is_overnight,
    }
    return record, is_overnight


def preprocess_activity_dataframe(
    raw_df: pd.DataFrame,
    existing_keys: set[tuple[str, str, str, str]] | None = None,
    allow_overnight: bool = True,
) -> PreprocessingReport:
    """Validate, clean, compute durations, and detect duplicates for an uploaded DataFrame."""
    if raw_df is None or raw_df.empty:
        return PreprocessingReport(
            total_records=0,
            missing_columns=list(EXPECTED_UPLOAD_COLUMNS),
        )

    df = normalize_upload_columns(raw_df)
    missing_cols = [col for col in EXPECTED_UPLOAD_COLUMNS if col not in df.columns]
    if missing_cols:
        return PreprocessingReport(
            total_records=len(df),
            missing_columns=missing_cols,
        )

    known_db_keys = set(existing_keys) if existing_keys else set()
    batch_keys: set[tuple[str, str, str, str]] = set()

    valid_rows: list[dict[str, Any]] = []
    rejected: list[RejectedRecord] = []
    invalid_count = 0
    duplicate_count = 0
    overnight_count = 0

    for idx, row in df.iterrows():
        row_num = int(idx) + 1 if isinstance(idx, (int, float)) else len(valid_rows) + len(rejected) + 1
        raw_date = row.get("activity_date")
        raw_start = row.get("start_time")
        raw_end = row.get("end_time")
        raw_act = row.get("activity_label")

        try:
            normalized, is_overnight = validate_single_activity_row(
                raw_date=raw_date,
                raw_start_time=raw_start,
                raw_end_time=raw_end,
                raw_activity=raw_act,
                allow_overnight=allow_overnight,
            )
        except ValueError as exc:
            invalid_count += 1
            rejected.append(
                RejectedRecord(
                    row_number=row_num,
                    raw_date="" if _is_missing_value(raw_date) else str(raw_date),
                    raw_start_time="" if _is_missing_value(raw_start) else str(raw_start),
                    raw_end_time="" if _is_missing_value(raw_end) else str(raw_end),
                    raw_activity="" if _is_missing_value(raw_act) else str(raw_act),
                    reason=str(exc),
                    category="invalid",
                )
            )
            continue

        dedup_key = (
            normalized["activity_date"],
            normalized["start_time"],
            normalized["end_time"],
            normalized["activity_label"].strip().lower(),
        )

        if dedup_key in batch_keys:
            duplicate_count += 1
            rejected.append(
                RejectedRecord(
                    row_number=row_num,
                    raw_date=normalized["activity_date"],
                    raw_start_time=normalized["start_time"],
                    raw_end_time=normalized["end_time"],
                    raw_activity=normalized["activity_label"],
                    reason="Duplicate record within uploaded file.",
                    category="duplicate",
                )
            )
            continue

        if dedup_key in known_db_keys:
            duplicate_count += 1
            rejected.append(
                RejectedRecord(
                    row_number=row_num,
                    raw_date=normalized["activity_date"],
                    raw_start_time=normalized["start_time"],
                    raw_end_time=normalized["end_time"],
                    raw_activity=normalized["activity_label"],
                    reason="Duplicate of an existing record in the database.",
                    category="duplicate",
                )
            )
            continue

        batch_keys.add(dedup_key)
        if is_overnight:
            overnight_count += 1
        valid_rows.append(normalized)

    valid_columns = [
        "activity_date",
        "start_time",
        "end_time",
        "activity_label",
        "duration_minutes",
        "is_overnight",
    ]
    valid_df = pd.DataFrame(valid_rows, columns=valid_columns)

    return PreprocessingReport(
        total_records=len(df),
        valid_records_count=len(valid_rows),
        invalid_records_count=invalid_count,
        duplicate_records_count=duplicate_count,
        overnight_records_count=overnight_count,
        missing_columns=[],
        valid_df=valid_df,
        rejected_records=rejected,
    )


def preprocess_activity_data(
    df: pd.DataFrame,
    existing_keys: set[tuple[str, str, str, str]] | None = None,
    allow_overnight: bool = True,
) -> pd.DataFrame:
    """Process an uploaded activity DataFrame and return the cleaned valid DataFrame.

    Raises:
        ValueError: If required columns are missing.
    """
    report = preprocess_activity_dataframe(
        df,
        existing_keys=existing_keys,
        allow_overnight=allow_overnight,
    )
    if report.has_schema_errors:
        raise ValueError(
            f"Missing required columns: {', '.join(report.missing_columns)}"
        )
    return report.valid_df
