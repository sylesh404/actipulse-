"""Downloadable activity report generation contracts (PDF, Excel, CSV)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ReportFormat(str, Enum):
    """Supported export formats for ActiPulse AI reports."""

    PDF = "pdf"
    EXCEL = "xlsx"
    CSV = "csv"


@dataclass(frozen=True)
class ReportMetadata:
    """Metadata describing a generated activity report artifact."""

    title: str
    report_format: ReportFormat
    date_range_start: str | None = None
    date_range_end: str | None = None


def export_activity_report(
    output_path: str | Path,
    metadata: ReportMetadata,
) -> Path:
    """Placeholder report exporter to be implemented in Process 6."""
    raise NotImplementedError("Report generation (PDF/Excel) will be implemented in Process 6.")
