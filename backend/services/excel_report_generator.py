"""Excel Report Generation Service - OpenPyXL Implementation."""

from __future__ import annotations

import io
from datetime import datetime
from typing import TYPE_CHECKING

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils.dataframe import dataframe_to_rows

from backend.services.activity_timeline import (
    get_daily_timeline,
    get_timeline_statistics,
)
from backend.services.pattern_detection import get_pattern_overview

if TYPE_CHECKING:
    from database.database import DatabaseManager

# ActiPulse AI Brand Colors (for Excel)
ACTIPULSE_GREEN = "AFFA00"
ACTIPULSE_LIGHT_GREEN = "CFED89"
ACTIPULSE_DARK = "1C1C1C"
ACTIPULSE_WHITE = "FFFFFF"


def generate_activity_report_excel(
    db_manager: DatabaseManager,
    start_date: str,
    end_date: str,
) -> bytes:
    """
    Generate a comprehensive activity report Excel workbook with multiple sheets.
    
    Args:
        db_manager: Database manager instance
        start_date: Start date (ISO format: YYYY-MM-DD)
        end_date: End date (ISO format: YYYY-MM-DD)
    
    Returns:
        Excel file bytes
    """
    # Create workbook
    wb = Workbook()
    
    # Remove default sheet
    if "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])
    
    # Sheet 1: Summary
    _create_summary_sheet(wb, db_manager, start_date, end_date)
    
    # Sheet 2: Activity Data
    _create_activity_data_sheet(wb, db_manager, start_date, end_date)
    
    # Sheet 3: Timeline Analysis
    _create_timeline_sheet(wb, db_manager, start_date, end_date)
    
    # Sheet 4: Pattern Detection
    _create_pattern_sheet(wb, db_manager, start_date, end_date)
    
    # Sheet 5: Daily Statistics
    _create_daily_stats_sheet(wb, db_manager, start_date, end_date)
    
    # Save to bytes
    buffer = io.BytesIO()
    wb.save(buffer)
    excel_bytes = buffer.getvalue()
    buffer.close()
    
    return excel_bytes


def _create_summary_sheet(
    wb: Workbook,
    db_manager: DatabaseManager,
    start_date: str,
    end_date: str,
) -> None:
    """Create the summary sheet with key metrics."""
    ws = wb.create_sheet("Summary", 0)
    
    # Title
    ws["A1"] = "ACTIPULSE AI - ACTIVITY REPORT"
    ws["A1"].font = Font(name="Arial", size=18, bold=True, color=ACTIPULSE_DARK)
    ws.merge_cells("A1:D1")
    
    ws["A2"] = "Physical Activity Intelligence Report"
    ws["A2"].font = Font(name="Arial", size=12, color=ACTIPULSE_DARK)
    ws.merge_cells("A2:D2")
    
    # Report metadata
    ws["A4"] = "Report Period:"
    ws["B4"] = f"{start_date} to {end_date}"
    ws["A5"] = "Generated:"
    ws["B5"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    _apply_header_style(ws, "A4")
    _apply_header_style(ws, "A5")
    
    # Get activity data
    df = db_manager.get_all_activity_records()
    if not df.empty:
        df_filtered = df[
            (df["activity_date"] >= start_date) & (df["activity_date"] <= end_date)
        ]
        
        if not df_filtered.empty:
            # Key metrics
            ws["A7"] = "KEY METRICS"
            ws["A7"].font = Font(name="Arial", size=14, bold=True, color=ACTIPULSE_DARK)
            ws.merge_cells("A7:D7")
            _apply_fill(ws, "A7:D7", ACTIPULSE_GREEN)
            
            ws["A9"] = "Total Activity Records:"
            ws["B9"] = len(df_filtered)
            ws["A10"] = "Days with Activity:"
            ws["B10"] = df_filtered["activity_date"].nunique()
            ws["A11"] = "Total Duration (minutes):"
            ws["B11"] = df_filtered["duration_minutes"].sum()
            ws["A12"] = "Average Daily Duration (minutes):"
            ws["B12"] = df_filtered.groupby("activity_date")["duration_minutes"].sum().mean()
            
            for row in range(9, 13):
                _apply_header_style(ws, f"A{row}")
            
            # Activity breakdown
            ws["A14"] = "ACTIVITY BREAKDOWN"
            ws["A14"].font = Font(name="Arial", size=14, bold=True, color=ACTIPULSE_DARK)
            ws.merge_cells("A14:D14")
            _apply_fill(ws, "A14:D14", ACTIPULSE_GREEN)
            
            activity_summary = (
                df_filtered.groupby("activity_label")["duration_minutes"]
                .agg(["count", "sum", "mean"])
                .reset_index()
            )
            
            # Headers
            ws["A16"] = "Activity"
            ws["B16"] = "Sessions"
            ws["C16"] = "Total (min)"
            ws["D16"] = "Average (min)"
            
            for col in ["A16", "B16", "C16", "D16"]:
                _apply_header_style(ws, col)
                _apply_fill(ws, col, ACTIPULSE_LIGHT_GREEN)
            
            # Data
            row_idx = 17
            for _, row in activity_summary.iterrows():
                ws[f"A{row_idx}"] = row["activity_label"]
                ws[f"B{row_idx}"] = int(row["count"])
                ws[f"C{row_idx}"] = round(row["sum"], 1)
                ws[f"D{row_idx}"] = round(row["mean"], 1)
                row_idx += 1
    
    # Adjust column widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20


def _create_activity_data_sheet(
    wb: Workbook,
    db_manager: DatabaseManager,
    start_date: str,
    end_date: str,
) -> None:
    """Create the raw activity data sheet."""
    ws = wb.create_sheet("Activity Data")
    
    # Get activity data
    df = db_manager.get_all_activity_records()
    if not df.empty:
        df_filtered = df[
            (df["activity_date"] >= start_date) & (df["activity_date"] <= end_date)
        ].copy()
        
        if not df_filtered.empty:
            # Select relevant columns
            df_export = df_filtered[[
                "activity_date",
                "activity_label",
                "start_time",
                "end_time",
                "duration_minutes",
            ]].copy()
            
            # Round duration
            df_export["duration_minutes"] = df_export["duration_minutes"].round(1)
            
            # Write to sheet
            for r_idx, row in enumerate(dataframe_to_rows(df_export, index=False, header=True), 1):
                for c_idx, value in enumerate(row, 1):
                    cell = ws.cell(row=r_idx, column=c_idx, value=value)
                    
                    # Style header row
                    if r_idx == 1:
                        _apply_header_style(ws, cell.coordinate)
                        _apply_fill(ws, cell.coordinate, ACTIPULSE_GREEN)
            
            # Adjust column widths
            ws.column_dimensions["A"].width = 15
            ws.column_dimensions["B"].width = 15
            ws.column_dimensions["C"].width = 12
            ws.column_dimensions["D"].width = 12
            ws.column_dimensions["E"].width = 18
        else:
            ws["A1"] = "No activity data found for the specified period."
    else:
        ws["A1"] = "No activity data available."


def _create_timeline_sheet(
    wb: Workbook,
    db_manager: DatabaseManager,
    start_date: str,
    end_date: str,
) -> None:
    """Create the timeline analysis sheet."""
    ws = wb.create_sheet("Timeline")
    
    # Title
    ws["A1"] = "TIMELINE ANALYSIS"
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color=ACTIPULSE_DARK)
    ws.merge_cells("A1:F1")
    _apply_fill(ws, "A1:F1", ACTIPULSE_GREEN)
    
    # Headers
    headers = ["Date", "Total Sessions", "Duration (min)", "Unique Activities", "First Activity", "Last Activity"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=header)
        _apply_header_style(ws, cell.coordinate)
        _apply_fill(ws, cell.coordinate, ACTIPULSE_LIGHT_GREEN)
    
    # Analyze each day
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    row_idx = 4
    for target_date in date_range:
        date_str = target_date.strftime("%Y-%m-%d")
        timeline = get_daily_timeline(db_manager, date_str)
        
        if timeline.sessions:
            stats = get_timeline_statistics(db_manager, date_str)
            
            ws[f"A{row_idx}"] = date_str
            ws[f"B{row_idx}"] = stats.total_sessions
            ws[f"C{row_idx}"] = round(stats.total_duration_minutes, 1)
            ws[f"D{row_idx}"] = stats.unique_activities
            ws[f"E{row_idx}"] = stats.first_activity_time or "N/A"
            ws[f"F{row_idx}"] = stats.last_activity_time or "N/A"
            
            row_idx += 1
    
    if row_idx == 4:
        ws["A4"] = "No timeline data available for the specified period."
    
    # Adjust column widths
    for col in ["A", "B", "C", "D", "E", "F"]:
        ws.column_dimensions[col].width = 18


def _create_pattern_sheet(
    wb: Workbook,
    db_manager: DatabaseManager,
    start_date: str,
    end_date: str,
) -> None:
    """Create the pattern detection sheet."""
    ws = wb.create_sheet("Patterns")
    
    # Title
    ws["A1"] = "PATTERN DETECTION"
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color=ACTIPULSE_DARK)
    ws.merge_cells("A1:F1")
    _apply_fill(ws, "A1:F1", ACTIPULSE_GREEN)
    
    # Get pattern overview
    overview = get_pattern_overview(db_manager, days=30)
    
    if overview:
        # Headers
        headers = ["Date", "Activity", "Pattern Type", "Severity", "Confidence", "Description"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_idx, value=header)
            _apply_header_style(ws, cell.coordinate)
            _apply_fill(ws, cell.coordinate, ACTIPULSE_LIGHT_GREEN)
        
        # Data
        row_idx = 4
        for date_str, patterns in sorted(overview.items()):
            for pattern in patterns:
                ws[f"A{row_idx}"] = date_str
                ws[f"B{row_idx}"] = pattern.activity_label
                ws[f"C{row_idx}"] = pattern.pattern_type.replace("_", " ").title()
                ws[f"D{row_idx}"] = pattern.severity.upper()
                ws[f"E{row_idx}"] = f"{pattern.confidence:.0%}"
                ws[f"F{row_idx}"] = pattern.description
                
                # Color code severity
                severity_colors = {
                    "significant": "FF4444",
                    "moderate": "FFAA00",
                    "minor": "AFFA00",
                }
                _apply_fill(ws, f"D{row_idx}", severity_colors.get(pattern.severity, "FFFFFF"))
                
                row_idx += 1
        
        if row_idx == 4:
            ws["A4"] = "No patterns detected in the analyzed period."
    else:
        ws["A3"] = "No pattern data available."
    
    # Adjust column widths
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 25
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 50


def _create_daily_stats_sheet(
    wb: Workbook,
    db_manager: DatabaseManager,
    start_date: str,
    end_date: str,
) -> None:
    """Create the daily statistics sheet."""
    ws = wb.create_sheet("Daily Stats")
    
    # Title
    ws["A1"] = "DAILY STATISTICS"
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color=ACTIPULSE_DARK)
    ws.merge_cells("A1:H1")
    _apply_fill(ws, "A1:H1", ACTIPULSE_GREEN)
    
    # Get activity data
    df = db_manager.get_all_activity_records()
    if not df.empty:
        df_filtered = df[
            (df["activity_date"] >= start_date) & (df["activity_date"] <= end_date)
        ].copy()
        
        if not df_filtered.empty:
            # Calculate daily statistics
            daily_stats = df_filtered.groupby("activity_date").agg({
                "duration_minutes": ["sum", "mean", "max", "min", "count"],
            }).reset_index()
            
            daily_stats.columns = ["Date", "Total (min)", "Avg (min)", "Max (min)", "Min (min)", "Sessions"]
            
            # Round values
            for col in ["Total (min)", "Avg (min)", "Max (min)", "Min (min)"]:
                daily_stats[col] = daily_stats[col].round(1)
            
            # Write to sheet
            for r_idx, row in enumerate(dataframe_to_rows(daily_stats, index=False, header=True), 3):
                for c_idx, value in enumerate(row, 1):
                    cell = ws.cell(row=r_idx, column=c_idx, value=value)
                    
                    # Style header row
                    if r_idx == 3:
                        _apply_header_style(ws, cell.coordinate)
                        _apply_fill(ws, cell.coordinate, ACTIPULSE_LIGHT_GREEN)
            
            # Adjust column widths
            for col in ["A", "B", "C", "D", "E", "F"]:
                ws.column_dimensions[col].width = 15
        else:
            ws["A3"] = "No activity data found for the specified period."
    else:
        ws["A3"] = "No activity data available."


def _apply_header_style(ws, cell_coordinate: str) -> None:
    """Apply header style to a cell."""
    cell = ws[cell_coordinate]
    cell.font = Font(name="Arial", size=11, bold=True, color=ACTIPULSE_DARK)
    cell.alignment = Alignment(horizontal="left", vertical="center")


def _apply_fill(ws, cell_range: str, color: str) -> None:
    """Apply fill color to a cell or range."""
    if ":" in cell_range:
        # Range
        start, end = cell_range.split(":")
        for row in ws[cell_range]:
            for cell in row:
                cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    else:
        # Single cell
        ws[cell_range].fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
