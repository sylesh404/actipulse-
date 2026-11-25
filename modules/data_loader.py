"""Data loading, column normalization, schema models, and preview helpers."""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Iterable

import pandas as pd


SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".xls")
REQUIRED_ACTIVITY_COLUMNS = ("activity_label", "duration_minutes")
EXPECTED_UPLOAD_COLUMNS = ("activity_date", "start_time", "end_time", "activity_label")
OPTIONAL_ACTIVITY_COLUMNS = ("activity_date", "start_time", "end_time", "notes")

COLUMN_ALIASES: dict[str, str] = {
    "date": "activity_date",
    "activity_date": "activity_date",
    "day": "activity_date",
    "record_date": "activity_date",
    "start": "start_time",
    "start_time": "start_time",
    "starttime": "start_time",
    "from": "start_time",
    "begin_time": "start_time",
    "end": "end_time",
    "end_time": "end_time",
    "endtime": "end_time",
    "to": "end_time",
    "finish_time": "end_time",
    "activity": "activity_label",
    "activity_label": "activity_label",
    "activity_type": "activity_label",
    "label": "activity_label",
    "type": "activity_label",
    "notes": "notes",
    "note": "notes",
}


class ActiPulseError(Exception):
    """Base exception for application-level errors."""


class ConfigurationError(ActiPulseError):
    """Raised when required configuration or API credentials are missing."""


class DataValidationError(ActiPulseError):
    """Raised when uploaded or provided activity data fails schema validation."""


@dataclass(frozen=True)
class ActivityRecord:
    """Canonical representation of a single recorded physical activity interval."""

    activity_label: str
    duration_minutes: float
    activity_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    notes: str | None = None


@dataclass
class ValidationResult:
    """Outcome of validating an activity dataset before processing."""

    is_valid: bool
    missing_columns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    row_count: int = 0


@dataclass
class DatasetPreview:
    """Preview metadata and sample rows for an uploaded dataset prior to import."""

    filename: str
    file_format: str
    row_count: int
    detected_columns: list[str]
    normalized_columns: list[str]
    missing_columns: list[str]
    preview_df: pd.DataFrame


def validate_file_extension(filename: str | Path) -> bool:
    """Return True if the file extension is supported for activity ingestion."""
    suffix = Path(filename).suffix.lower()
    return suffix in SUPPORTED_EXTENSIONS or suffix == ".json"


def normalize_column_name(column: Any) -> str:
    """Normalize raw column headers using standard activity aliases."""
    cleaned = str(column).strip().lower().replace(" ", "_").replace("-", "_")
    return COLUMN_ALIASES.get(cleaned, cleaned)


def normalize_upload_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with standardized activity column names.

    If multiple raw columns alias to the same canonical name, the first occurrence
    is kept and duplicates are prevented from silently colliding.
    """
    renamed_df = df.copy()
    new_columns: list[str] = []
    seen: set[str] = set()

    for col in renamed_df.columns:
        canonical = normalize_column_name(col)
        if canonical in seen:
            suffix = 2
            candidate = f"{canonical}_{suffix}"
            while candidate in seen:
                suffix += 1
                candidate = f"{canonical}_{suffix}"
            canonical = candidate
        seen.add(canonical)
        new_columns.append(canonical)

    renamed_df.columns = new_columns
    return renamed_df


def validate_activity_dataframe(
    df: pd.DataFrame,
    required_columns: Iterable[str] = REQUIRED_ACTIVITY_COLUMNS,
) -> ValidationResult:
    """Validate basic structural requirements of an activity DataFrame."""
    if df is None or df.empty:
        return ValidationResult(
            is_valid=False,
            errors=["The provided dataset is empty."],
            row_count=0,
        )

    normalized_cols = {normalize_column_name(col) for col in df.columns}
    missing = [col for col in required_columns if col.lower() not in normalized_cols]

    errors: list[str] = []
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")

    return ValidationResult(
        is_valid=len(errors) == 0,
        missing_columns=missing,
        errors=errors,
        row_count=len(df),
    )


def load_activity_file(
    file_source: str | Path | BinaryIO,
    filename: str | None = None,
) -> pd.DataFrame:
    """Load a CSV or Excel activity file from a filesystem path or uploaded file buffer."""
    resolved_name = filename
    if resolved_name is None:
        if isinstance(file_source, (str, Path)):
            resolved_name = Path(file_source).name
        else:
            resolved_name = getattr(file_source, "name", "")

    suffix = Path(resolved_name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise DataValidationError(
            f"Unsupported file format '{suffix or 'unknown'}'. Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    try:
        if isinstance(file_source, (str, Path)):
            path = Path(file_source)
            if not path.exists():
                raise DataValidationError(f"File not found: {path}")
            raw_bytes = path.read_bytes()
        else:
            if hasattr(file_source, "seek"):
                file_source.seek(0)
            raw_bytes = file_source.read()

        if not raw_bytes:
            raise DataValidationError("The uploaded file is empty.")

        buffer = io.BytesIO(raw_bytes)

        if suffix == ".csv":
            try:
                df = pd.read_csv(buffer, dtype=str, keep_default_na=True)
            except UnicodeDecodeError:
                buffer.seek(0)
                df = pd.read_csv(buffer, dtype=str, encoding="latin-1", keep_default_na=True)
        elif suffix == ".xlsx":
            df = pd.read_excel(buffer, engine="openpyxl")
        else:
            try:
                df = pd.read_excel(buffer)
            except ImportError as exc:
                raise DataValidationError(
                    "Reading legacy .xls files requires an optional .xls engine (xlrd). "
                    "Please save the workbook as .xlsx or .csv."
                ) from exc

    except DataValidationError:
        raise
    except Exception as exc:
        raise DataValidationError(f"Failed to read '{resolved_name}': {exc}") from exc

    if df.empty and len(df.columns) == 0:
        raise DataValidationError(f"No columns or rows could be parsed from '{resolved_name}'.")

    return df


def build_dataset_preview(
    raw_df: pd.DataFrame,
    filename: str,
    preview_rows: int = 10,
) -> DatasetPreview:
    """Create a structured preview summary for an uploaded activity DataFrame."""
    detected_columns = [str(col) for col in raw_df.columns]
    normalized_df = normalize_upload_columns(raw_df)
    normalized_columns = [str(col) for col in normalized_df.columns]
    missing_columns = [
        col for col in EXPECTED_UPLOAD_COLUMNS if col not in normalized_columns
    ]

    return DatasetPreview(
        filename=filename,
        file_format=Path(filename).suffix.lower().lstrip(".") or "unknown",
        row_count=len(raw_df),
        detected_columns=detected_columns,
        normalized_columns=normalized_columns,
        missing_columns=missing_columns,
        preview_df=raw_df.head(preview_rows).copy(),
    )


def generate_sample_csv_bytes() -> bytes:
    """Return a clean sample CSV template illustrating expected columns."""
    sample_csv = (
        "date,start_time,end_time,activity\n"
        "2026-11-25,07:00,07:30,Walking\n"
        "2026-11-25,07:30,09:00,Sitting\n"
        "2026-11-25,09:00,09:30,Standing\n"
        "2026-11-25,09:30,10:00,Walking\n"
    )
    return sample_csv.encode("utf-8")
