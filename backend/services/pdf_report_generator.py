"""PDF Report Generation Service - ReportLab Implementation."""

from __future__ import annotations

import io
from datetime import date, datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.services.activity_timeline import (
    get_daily_timeline,
    get_timeline_statistics,
)
from backend.services.pattern_detection import (
    detect_all_patterns_for_date,
    get_pattern_overview,
)

if TYPE_CHECKING:
    from database.database import DatabaseManager

# ActiPulse AI Brand Colors
ACTIPULSE_GREEN = colors.HexColor("#AFFA00")
ACTIPULSE_LIGHT_GREEN = colors.HexColor("#CFED89")
ACTIPULSE_DARK = colors.HexColor("#1C1C1C")
ACTIPULSE_BLACK = colors.black


def generate_activity_report_pdf(
    db_manager: DatabaseManager,
    start_date: str,
    end_date: str,
    include_timeline: bool = True,
    include_patterns: bool = True,
    include_ai_narratives: bool = True,
) -> bytes:
    """
    Generate a comprehensive activity report PDF.
    
    Args:
        db_manager: Database manager instance
        start_date: Start date (ISO format: YYYY-MM-DD)
        end_date: End date (ISO format: YYYY-MM-DD)
        include_timeline: Include timeline analysis
        include_patterns: Include pattern detection
        include_ai_narratives: Include AI-generated narratives
    
    Returns:
        PDF bytes
    """
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=0.75 * inch,
        title="ActiPulse AI Activity Report",
        author="ActiPulse AI",
    )
    
    # Build the story (content)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=ACTIPULSE_GREEN,
        spaceAfter=12,
        fontName="Helvetica-Bold",
    )
    
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=ACTIPULSE_GREEN,
        spaceAfter=10,
        spaceBefore=20,
        fontName="Helvetica-Bold",
    )
    
    subheading_style = ParagraphStyle(
        "CustomSubheading",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=ACTIPULSE_LIGHT_GREEN,
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )
    
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6,
        fontName="Helvetica",
    )
    
    # Title Page
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("ACTIPULSE AI", title_style))
    story.append(Paragraph("Physical Activity Intelligence Report", heading_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Report metadata
    story.append(Paragraph(f"<b>Report Period:</b> {start_date} to {end_date}", body_style))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Paragraph("<b>Report Type:</b> Comprehensive Activity Analysis", body_style))
    
    story.append(Spacer(1, 0.5 * inch))
    
    # Disclaimer
    disclaimer_text = (
        "<b>DISCLAIMER:</b> This report is for informational purposes only. "
        "It is not a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare provider with questions about your physical health."
    )
    story.append(Paragraph(disclaimer_text, body_style))
    
    story.append(PageBreak())
    
    # Section 1: Activity Summary
    story.append(Paragraph("1. Activity Summary", heading_style))
    
    # Get all activity records for the period
    df = db_manager.get_all_activity_records()
    if not df.empty:
        df_filtered = df[
            (df["activity_date"] >= start_date) & (df["activity_date"] <= end_date)
        ]
        
        if not df_filtered.empty:
            # Calculate summary statistics
            total_records = len(df_filtered)
            unique_days = df_filtered["activity_date"].nunique()
            total_duration = df_filtered["duration_minutes"].sum()
            
            story.append(Paragraph(f"<b>Total Activity Records:</b> {total_records}", body_style))
            story.append(Paragraph(f"<b>Days with Activity:</b> {unique_days}", body_style))
            story.append(Paragraph(f"<b>Total Duration:</b> {total_duration:.1f} minutes", body_style))
            
            story.append(Spacer(1, 0.2 * inch))
            
            # Activity breakdown table
            activity_summary = (
                df_filtered.groupby("activity_label")["duration_minutes"]
                .agg(["count", "sum", "mean"])
                .reset_index()
            )
            activity_summary.columns = ["Activity", "Sessions", "Total (min)", "Avg (min)"]
            
            # Format the data
            table_data = [["Activity", "Sessions", "Total (min)", "Avg (min)"]]
            for _, row in activity_summary.iterrows():
                table_data.append([
                    row["Activity"],
                    str(int(row["Sessions"])),
                    f"{row['Total (min)']:.1f}",
                    f"{row['Avg (min)']:.1f}",
                ])
            
            # Create table
            activity_table = Table(table_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
            activity_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), ACTIPULSE_GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ]))
            
            story.append(activity_table)
        else:
            story.append(Paragraph("No activity records found for the specified period.", body_style))
    else:
        story.append(Paragraph("No activity records found in the database.", body_style))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Section 2: Timeline Analysis
    if include_timeline:
        story.append(Paragraph("2. Timeline Analysis", heading_style))
        
        # Analyze each day in the period
        date_range = []
        current = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        while current <= end:
            date_range.append(current)
            current = current.replace(day=current.day + 1) if current.day < 28 else current.replace(month=current.month + 1, day=1) if current.month < 12 else current.replace(year=current.year + 1, month=1, day=1)
        
        for target_date in date_range[:7]:  # Limit to first 7 days for brevity
            date_str = target_date.isoformat()
            timeline = get_daily_timeline(db_manager, date_str)
            
            if timeline.sessions:
                story.append(Paragraph(f"<b>{target_date.strftime('%B %d, %Y')}</b>", subheading_style))
                
                stats = get_timeline_statistics(db_manager, date_str)
                
                story.append(Paragraph(
                    f"Sessions: {stats.total_sessions} | "
                    f"Duration: {stats.total_duration_minutes:.1f} min | "
                    f"Activities: {stats.unique_activities}",
                    body_style,
                ))
                
                # Session details
                for session in timeline.sessions[:5]:  # Limit to 5 sessions per day
                    story.append(Paragraph(
                        f"• {session.activity_label}: {session.start_time} - {session.end_time} "
                        f"({session.duration_minutes:.1f} min)",
                        body_style,
                    ))
                
                story.append(Spacer(1, 0.1 * inch))
        
        story.append(Spacer(1, 0.2 * inch))
    
    # Section 3: Pattern Detection
    if include_patterns:
        story.append(Paragraph("3. Pattern Detection", heading_style))
        
        # Get pattern overview for the period
        overview = get_pattern_overview(db_manager, days=30)
        
        if overview:
            total_patterns = sum(len(patterns) for patterns in overview.values())
            story.append(Paragraph(f"<b>Total Patterns Detected:</b> {total_patterns}", body_style))
            story.append(Spacer(1, 0.1 * inch))
            
            # Show patterns for each date (limit to recent dates)
            pattern_dates = sorted(overview.keys(), reverse=True)[:5]
            
            for date_str in pattern_dates:
                patterns = overview[date_str]
                if patterns:
                    story.append(Paragraph(f"<b>{date_str}</b>", subheading_style))
                    
                    for pattern in patterns:
                        story.append(Paragraph(
                            f"• [{pattern.severity.upper()}] {pattern.activity_label}: "
                            f"{pattern.description}",
                            body_style,
                        ))
                    
                    story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph("No unusual patterns detected in the analyzed period.", body_style))
        
        story.append(Spacer(1, 0.2 * inch))
    
    # Section 4: AI Narratives
    if include_ai_narratives:
        story.append(Paragraph("4. AI-Generated Narratives", heading_style))
        
        # Get AI narratives from database
        narratives = db_manager.get_ai_narratives_for_period(start_date, end_date)
        
        if narratives:
            for narrative in narratives[:5]:  # Limit to 5 narratives
                story.append(Paragraph(f"<b>{narrative['date']}</b>", subheading_style))
                story.append(Paragraph(narrative['narrative'], body_style))
                story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph("No AI narratives available for the specified period.", body_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def generate_quick_summary_pdf(db_manager: DatabaseManager, target_date: str) -> bytes:
    """
    Generate a quick daily summary PDF report.
    
    Args:
        db_manager: Database manager instance
        target_date: Target date (ISO format: YYYY-MM-DD)
    
    Returns:
        PDF bytes
    """
    return generate_activity_report_pdf(
        db_manager=db_manager,
        start_date=target_date,
        end_date=target_date,
        include_timeline=True,
        include_patterns=True,
        include_ai_narratives=True,
    )
