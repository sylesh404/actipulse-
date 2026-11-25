"""Advanced Reports Page - PDF and Excel Export with Timeline and Patterns."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

import streamlit as st

from backend.services.excel_report_generator import generate_activity_report_excel
from backend.services.pdf_report_generator import (
    generate_activity_report_pdf,
    generate_quick_summary_pdf,
)
from components.ui_components import render_non_medical_disclaimer, render_page_hero

if TYPE_CHECKING:
    from database.database import DatabaseManager


def render_advanced_reports_page(db_manager: DatabaseManager) -> None:
    """Render the Advanced Reports page with PDF and Excel generation."""
    render_page_hero(
        eyebrow="ActiPulse AI • Advanced Intelligence",
        title="📊 Advanced Activity Reports",
        subtitle=(
            "Generate comprehensive PDF and Excel reports with timeline analysis, "
            "pattern detection, and AI-generated narratives."
        ),
    )

    # Check if data exists
    df = db_manager.get_all_activity_records()
    
    if df.empty:
        st.warning(
            "⚠️ **No activity data available**\n\n"
            "Please upload activity data first to generate reports."
        )
        render_non_medical_disclaimer()
        return

    # Report type tabs
    tab1, tab2 = st.tabs(["📄 PDF Reports", "📊 Excel Reports"])
    
    with tab1:
        _render_pdf_reports_section(db_manager, df)
    
    with tab2:
        _render_excel_reports_section(db_manager, df)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Report history section
    _render_report_history_section(db_manager)
    
    render_non_medical_disclaimer()


def _render_pdf_reports_section(db_manager: DatabaseManager, df) -> None:
    """Render the PDF reports section."""
    st.markdown("### 📄 PDF Report Generator")
    st.markdown(
        "Generate professional PDF reports with timeline visualizations, "
        "pattern analysis, and AI narratives using ReportLab."
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Quick report
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### ⚡ Quick Daily Summary")
        st.markdown("Generate a single-day PDF summary with all features.")
        
        quick_date = st.date_input(
            "Select Date",
            value=date.today(),
            max_value=date.today(),
            key="pdf_quick_date",
        )
    
    with col2:
        st.markdown("<div style='height: 2.8rem;'></div>", unsafe_allow_html=True)
        if st.button("📄 Generate Daily PDF", type="primary", use_container_width=True, key="btn_quick_pdf"):
            with st.spinner("🔄 Generating PDF report..."):
                try:
                    pdf_bytes = generate_quick_summary_pdf(
                        db_manager=db_manager,
                        target_date=quick_date.isoformat(),
                    )
                    
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"actipulse_daily_report_{quick_date.isoformat()}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    
                    # Log to report history
                    _log_report_generation(
                        db_manager,
                        f"Daily Summary - {quick_date.isoformat()}",
                        "PDF",
                        quick_date.isoformat(),
                        quick_date.isoformat(),
                    )
                    
                    st.success("✅ PDF report generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Comprehensive report
    st.markdown("#### 📊 Comprehensive Period Report")
    st.markdown("Generate a multi-page PDF report for a date range with detailed analysis.")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        min_date = df["activity_date"].min()
        max_date = df["activity_date"].max()
        
        default_start = date.today() - timedelta(days=7)
        default_end = date.today()
        
        date_range = st.date_input(
            "Date Range",
            value=(default_start, default_end),
            max_value=date.today(),
            key="pdf_date_range",
        )
    
    with col2:
        st.markdown("**Report Contents**")
        
        include_timeline = st.checkbox("Timeline Analysis", value=True, key="pdf_timeline")
        include_patterns = st.checkbox("Pattern Detection", value=True, key="pdf_patterns")
        include_narratives = st.checkbox("AI Narratives", value=True, key="pdf_narratives")
    
    with col3:
        st.markdown("<div style='height: 2.8rem;'></div>", unsafe_allow_html=True)
        
        if st.button("📄 Generate Full PDF", type="primary", use_container_width=True, key="btn_full_pdf"):
            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
                
                with st.spinner("🔄 Generating comprehensive PDF report..."):
                    try:
                        pdf_bytes = generate_activity_report_pdf(
                            db_manager=db_manager,
                            start_date=start_date.isoformat(),
                            end_date=end_date.isoformat(),
                            include_timeline=include_timeline,
                            include_patterns=include_patterns,
                            include_ai_narratives=include_narratives,
                        )
                        
                        st.download_button(
                            label="⬇️ Download Full PDF",
                            data=pdf_bytes,
                            file_name=f"actipulse_report_{start_date.isoformat()}_to_{end_date.isoformat()}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        
                        # Log to report history
                        _log_report_generation(
                            db_manager,
                            f"Comprehensive Report - {start_date.isoformat()} to {end_date.isoformat()}",
                            "PDF",
                            start_date.isoformat(),
                            end_date.isoformat(),
                        )
                        
                        st.success("✅ Comprehensive PDF report generated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")
            else:
                st.warning("⚠️ Please select a valid date range.")


def _render_excel_reports_section(db_manager: DatabaseManager, df) -> None:
    """Render the Excel reports section."""
    st.markdown("### 📊 Excel Workbook Generator")
    st.markdown(
        "Generate multi-sheet Excel workbooks with raw data, statistics, "
        "timeline analysis, and patterns using OpenPyXL."
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        min_date = df["activity_date"].min()
        max_date = df["activity_date"].max()
        
        default_start = date.today() - timedelta(days=30)
        default_end = date.today()
        
        excel_date_range = st.date_input(
            "Date Range",
            value=(default_start, default_end),
            max_value=date.today(),
            key="excel_date_range",
        )
        
        st.markdown(
            "**Excel workbook includes:**\n"
            "- 📋 Summary sheet with key metrics\n"
            "- 📊 Raw activity data\n"
            "- ⏱️ Timeline analysis\n"
            "- 🔍 Pattern detection results\n"
            "- 📈 Daily statistics"
        )
    
    with col2:
        st.markdown("<div style='height: 2.8rem;'></div>", unsafe_allow_html=True)
        
        if st.button("📊 Generate Excel", type="primary", use_container_width=True, key="btn_excel"):
            if excel_date_range and len(excel_date_range) == 2:
                start_date, end_date = excel_date_range
                
                with st.spinner("🔄 Generating Excel workbook..."):
                    try:
                        excel_bytes = generate_activity_report_excel(
                            db_manager=db_manager,
                            start_date=start_date.isoformat(),
                            end_date=end_date.isoformat(),
                        )
                        
                        st.download_button(
                            label="⬇️ Download Excel Workbook",
                            data=excel_bytes,
                            file_name=f"actipulse_report_{start_date.isoformat()}_to_{end_date.isoformat()}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                        
                        # Log to report history
                        _log_report_generation(
                            db_manager,
                            f"Excel Report - {start_date.isoformat()} to {end_date.isoformat()}",
                            "Excel",
                            start_date.isoformat(),
                            end_date.isoformat(),
                        )
                        
                        st.success("✅ Excel workbook generated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error generating Excel: {str(e)}")
            else:
                st.warning("⚠️ Please select a valid date range.")


def _render_report_history_section(db_manager: DatabaseManager) -> None:
    """Render the report generation history."""
    st.markdown("### 📜 Report History")
    
    with db_manager.connect() as conn:
        history = conn.execute(
            """
            SELECT report_name, report_format, date_range_start, date_range_end, created_at
            FROM report_history
            ORDER BY created_at DESC
            LIMIT 20
            """
        ).fetchall()
    
    if history:
        # Display as a table
        import pandas as pd
        
        history_df = pd.DataFrame([
            {
                "Report": row["report_name"],
                "Format": row["report_format"],
                "Period": f"{row['date_range_start']} to {row['date_range_end']}" if row["date_range_start"] else "N/A",
                "Generated": row["created_at"],
            }
            for row in history
        ])
        
        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No reports generated yet. Create your first report above!")


def _log_report_generation(
    db_manager: DatabaseManager,
    report_name: str,
    report_format: str,
    start_date: str,
    end_date: str,
) -> None:
    """Log report generation to history."""
    try:
        with db_manager.connect() as conn:
            conn.execute(
                """
                INSERT INTO report_history (report_name, report_format, date_range_start, date_range_end)
                VALUES (?, ?, ?, ?)
                """,
                (report_name, report_format, start_date, end_date),
            )
    except Exception:
        pass  # Don't fail report generation if history logging fails
