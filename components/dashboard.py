"""Home Dashboard and page placeholder renderers for ActiPulse AI."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import build_empty_state_figure
from components.ui_components import (
    render_kpi_card,
    render_non_medical_disclaimer,
    render_page_hero,
    render_placeholder_section,
)
from database.database import DatabaseManager
from modules.ai_narrator import get_gemini_model_name, is_gemini_configured


def render_home_dashboard(db_manager: DatabaseManager) -> None:
    """Render the Home Dashboard with activity overview and analytics."""
    from datetime import date as dt_date, timedelta

    render_page_hero(
        eyebrow="ActiPulse AI • Home Dashboard",
        title="Your Daily Activity Overview",
        subtitle=(
            "Track your walking, sitting, standing, running, and cycling activities. "
            "View comprehensive analytics and insights about your physical activity patterns."
        ),
    )

    df = db_manager.get_all_activity_records()

    # Dashboard filters in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔍 Dashboard Filters")
        
        if not df.empty:
            min_date = df["activity_date"].min()
            max_date = df["activity_date"].max()
            
            date_range = st.date_input(
                "Date Range",
                value=(dt_date.fromisoformat(min_date), dt_date.fromisoformat(max_date)),
                help="Filter activities by date range",
            )
            
            all_activities = sorted(df["activity_label"].unique())
            activity_filter = st.multiselect(
                "Activity Types",
                options=all_activities,
                default=all_activities,
                help="Select activity types to include",
            )
        else:
            date_range = None
            activity_filter = []

    # Apply filters
    filtered_df = df.copy()
    if not filtered_df.empty and date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["activity_date"] >= start_date.isoformat()) &
            (filtered_df["activity_date"] <= end_date.isoformat())
        ]
    if not filtered_df.empty and activity_filter:
        filtered_df = filtered_df[filtered_df["activity_label"].isin(activity_filter)]

    # Display metrics
    _render_activity_summary_cards(filtered_df)

    if filtered_df.empty:
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        _render_empty_dashboard_state()
    else:
        st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
        
        # Charts section
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            _render_activity_distribution_pie(filtered_df)
        with col2:
            _render_activity_duration_bar(filtered_df)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Recent activities
        _render_recent_activities(filtered_df)

    # Last update info
    last_update = db_manager.get_last_updated_timestamp()
    if last_update:
        st.caption(f"📅 Last data update: {last_update}")

    render_non_medical_disclaimer()


def _render_activity_summary_cards(df) -> None:
    """Render metric cards for activity summary."""
    import pandas as pd

    if df.empty:
        total_duration = 0
        walking_duration = 0
        sitting_duration = 0
        standing_duration = 0
        record_count = 0
        unique_days = 0
    else:
        total_duration = df["duration_minutes"].sum()
        walking_duration = df[df["activity_label"] == "Walking"]["duration_minutes"].sum()
        sitting_duration = df[df["activity_label"] == "Sitting"]["duration_minutes"].sum()
        standing_duration = df[df["activity_label"] == "Standing"]["duration_minutes"].sum()
        record_count = len(df)
        unique_days = df["activity_date"].nunique()

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        render_kpi_card(
            label="Total Duration",
            value=f"{total_duration:.0f} min",
            hint=f"{total_duration / 60:.1f} hours recorded",
        )
    with col2:
        render_kpi_card(
            label="Activity Records",
            value=str(record_count),
            hint=f"{unique_days} days tracked",
        )
    with col3:
        render_kpi_card(
            label="Walking Duration",
            value=f"{walking_duration:.0f} min",
            hint=f"{(walking_duration / total_duration * 100) if total_duration > 0 else 0:.1f}% of total",
        )

    col4, col5, col6 = st.columns(3, gap="medium")
    with col4:
        render_kpi_card(
            label="Sitting Duration",
            value=f"{sitting_duration:.0f} min",
            hint=f"{(sitting_duration / total_duration * 100) if total_duration > 0 else 0:.1f}% of total",
        )
    with col5:
        render_kpi_card(
            label="Standing Duration",
            value=f"{standing_duration:.0f} min",
            hint=f"{(standing_duration / total_duration * 100) if total_duration > 0 else 0:.1f}% of total",
        )
    with col6:
        render_kpi_card(
            label="Recorded Days",
            value=str(unique_days),
            hint=f"Avg {(total_duration / unique_days) if unique_days > 0 else 0:.0f} min/day",
        )


def _render_empty_dashboard_state() -> None:
    """Render empty state when no data is available."""
    st.markdown(
        """
        <div class="ap-card" style="text-align: center; padding: 3rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.8;">📊</div>
            <div class="ap-section-title" style="font-size: 1.5rem; margin-bottom: 0.75rem;">Welcome to ActiPulse AI</div>
            <p class="ap-section-desc" style="max-width: 600px; margin: 0 auto 2rem auto; font-size: 1rem; line-height: 1.7;">
                Start tracking your physical activities to unlock powerful analytics, AI-powered insights, 
                and personalized activity narratives. Upload your data or manually add records to get started.
            </p>
            <div style="display: flex; gap: 1rem; justify-content: center; align-items: center; flex-wrap: wrap; margin-top: 1.5rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📤</div>
                    <div style="font-weight: 600; color: #4338CA;">Upload Data</div>
                    <div style="font-size: 0.85rem; color: #64748B;">CSV or Excel files</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✍️</div>
                    <div style="font-weight: 600; color: #4338CA;">Manual Entry</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Add records one by one</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
                    <div style="font-weight: 600; color: #4338CA;">View Analytics</div>
                    <div style="font-size: 0.85rem; color: #64748B;">Comprehensive insights</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📤 Get Started - Upload Activity Data", type="primary", use_container_width=True):
            st.session_state["selected_page"] = "Upload Activity"
            st.rerun()


def _render_activity_distribution_pie(df) -> None:
    """Render pie chart showing activity distribution."""
    from components.charts import apply_actipulse_chart_theme
    import plotly.graph_objects as go

    activity_totals = df.groupby("activity_label")["duration_minutes"].sum().sort_values(ascending=False)
    
    fig = go.Figure(data=[go.Pie(
        labels=activity_totals.index,
        values=activity_totals.values,
        hole=0.4,
        textinfo="label+percent",
        textposition="auto",
    )])
    
    fig = apply_actipulse_chart_theme(fig, title="Activity Distribution")
    st.plotly_chart(fig, use_container_width=True)


def _render_activity_duration_bar(df) -> None:
    """Render bar chart showing total duration by activity."""
    from components.charts import apply_actipulse_chart_theme
    import plotly.graph_objects as go

    activity_totals = df.groupby("activity_label")["duration_minutes"].sum().sort_values(ascending=False)
    
    fig = go.Figure(data=[go.Bar(
        x=activity_totals.index,
        y=activity_totals.values,
        text=[f"{v:.0f} min" for v in activity_totals.values],
        textposition="auto",
    )])
    
    fig.update_layout(
        xaxis_title="Activity Type",
        yaxis_title="Total Duration (minutes)",
    )
    
    fig = apply_actipulse_chart_theme(fig, title="Total Duration by Activity")
    st.plotly_chart(fig, use_container_width=True)


def _render_recent_activities(df) -> None:
    """Render table of recent activity records."""
    st.markdown("### 📋 Recent Activity Records")
    
    recent_df = df.head(10).copy()
    display_df = recent_df[["activity_date", "start_time", "end_time", "activity_label", "duration_minutes"]].copy()
    display_df.columns = ["Date", "Start Time", "End Time", "Activity", "Duration (min)"]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_upload_activity_page(db_manager: DatabaseManager) -> None:
    """Complete activity data management page with CSV/Excel upload and manual entry."""
    render_page_hero(
        eyebrow="Page 2 of 7 • Data Ingestion",
        title="Upload Activity",
        subtitle="Import recorded physical activity datasets (CSV, Excel) or manually enter activity records.",
    )

    tab1, tab2, tab3 = st.tabs(["📤 Upload File", "✍️ Manual Entry", "📋 Manage Records"])

    with tab1:
        _render_file_upload_section(db_manager)

    with tab2:
        _render_manual_entry_section(db_manager)

    with tab3:
        _render_activity_management_section(db_manager)

    render_non_medical_disclaimer()


def _render_file_upload_section(db_manager: DatabaseManager) -> None:
    """Render CSV/Excel upload section with validation and preview."""
    from modules.data_loader import (
        EXPECTED_UPLOAD_COLUMNS,
        DataValidationError,
        build_dataset_preview,
        generate_sample_csv_bytes,
        load_activity_file,
    )
    from modules.preprocessing import preprocess_activity_dataframe

    st.markdown("### Upload Activity Data")
    st.markdown(
        "Upload a CSV or Excel file containing your physical activity records. "
        "The file should include: **date**, **start_time**, **end_time**, and **activity**."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "xlsx", "xls"],
            help="Upload CSV or Excel files with activity records",
        )
    with col2:
        st.download_button(
            label="📥 Download Sample CSV",
            data=generate_sample_csv_bytes(),
            file_name="actipulse_sample.csv",
            mime="text/csv",
        )

    if uploaded_file is not None:
        try:
            raw_df = load_activity_file(uploaded_file, filename=uploaded_file.name)
            preview = build_dataset_preview(raw_df, filename=uploaded_file.name, preview_rows=10)

            st.success(f"✅ File loaded: **{preview.filename}** ({preview.file_format.upper()}) — {preview.row_count} records")

            if preview.missing_columns:
                st.error(
                    f"❌ **Missing required columns:** {', '.join(preview.missing_columns)}\n\n"
                    f"Expected columns: {', '.join(EXPECTED_UPLOAD_COLUMNS)}"
                )
                st.markdown("#### File Preview")
                st.dataframe(preview.preview_df, use_container_width=True)
                return

            st.markdown("#### Dataset Preview")
            st.dataframe(preview.preview_df, use_container_width=True)

            if st.button("✨ Validate & Process", type="primary", use_container_width=True):
                with st.spinner("Validating activity records..."):
                    existing_keys = db_manager.get_existing_record_keys()
                    report = preprocess_activity_dataframe(
                        raw_df,
                        existing_keys=existing_keys,
                        allow_overnight=True,
                    )

                    _display_validation_report(report)

                    if report.valid_records_count > 0 and not report.has_schema_errors:
                        if st.button(
                            f"💾 Import {report.valid_records_count} Valid Records",
                            type="primary",
                            key="import_btn",
                        ):
                            batch_id = db_manager.insert_upload_batch(
                                filename=preview.filename,
                                file_format=preview.file_format,
                                row_count=report.valid_records_count,
                            )
                            records_to_insert = report.valid_df.to_dict("records")
                            inserted, duplicates = db_manager.insert_activity_records(
                                records_to_insert,
                                batch_id=batch_id,
                            )
                            st.success(
                                f"✅ **Successfully imported {inserted} activity records!**"
                            )
                            if duplicates > 0:
                                st.info(f"ℹ️ Skipped {duplicates} duplicate records.")
                            st.rerun()

        except DataValidationError as exc:
            st.error(f"❌ **Upload Error:** {exc}")
        except Exception as exc:
            st.error(f"❌ **Unexpected Error:** {exc}")


def _display_validation_report(report) -> None:
    """Display comprehensive validation report."""
    st.markdown("#### Validation Report")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", report.total_records)
    with col2:
        st.metric("Valid", report.valid_records_count, delta_color="normal")
    with col3:
        st.metric("Invalid", report.invalid_records_count, delta_color="inverse")
    with col4:
        st.metric("Duplicates", report.duplicate_records_count, delta_color="off")

    if report.overnight_records_count > 0:
        st.info(f"ℹ️ **{report.overnight_records_count}** overnight activities detected and handled correctly.")

    if report.valid_records_count > 0:
        st.success(f"✅ **{report.valid_records_count}** records ready for import")
        with st.expander("🔍 Preview Valid Records"):
            st.dataframe(report.valid_df, use_container_width=True)

    if report.rejected_records:
        st.warning(f"⚠️ **{len(report.rejected_records)}** records rejected")
        with st.expander("📋 View Rejected Records"):
            rejected_data = [
                {
                    "Row": r.row_number,
                    "Date": r.raw_date,
                    "Start": r.raw_start_time,
                    "End": r.raw_end_time,
                    "Activity": r.raw_activity,
                    "Reason": r.reason,
                    "Category": r.category,
                }
                for r in report.rejected_records
            ]
            st.dataframe(rejected_data, use_container_width=True)


def _render_manual_entry_section(db_manager: DatabaseManager) -> None:
    """Render manual activity entry form."""
    from datetime import date as dt_date, datetime
    from modules.preprocessing import (
        PRESET_ACTIVITY_LABELS,
        validate_single_activity_row,
    )

    st.markdown("### Manually Add Activity Record")
    st.markdown("Enter a single activity record manually.")

    with st.form("manual_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            activity_date = st.date_input(
                "Activity Date",
                value=dt_date.today(),
                help="Select the date of the activity",
            )
        with col2:
            activity_label_choice = st.selectbox(
                "Activity Type",
                options=list(PRESET_ACTIVITY_LABELS),
                help="Select the type of activity",
            )

        col3, col4 = st.columns(2)
        with col3:
            start_time = st.time_input(
                "Start Time",
                value=datetime.strptime("09:00", "%H:%M").time(),
                help="When did the activity start?",
            )
        with col4:
            end_time = st.time_input(
                "End Time",
                value=datetime.strptime("10:00", "%H:%M").time(),
                help="When did the activity end?",
            )

        custom_label = None
        if activity_label_choice == "Other":
            custom_label = st.text_input(
                "Custom Activity Label",
                help="Enter a custom activity name",
            )

        submitted = st.form_submit_button("➕ Add Activity Record", type="primary", use_container_width=True)

        if submitted:
            final_label = custom_label.strip() if activity_label_choice == "Other" and custom_label else activity_label_choice

            if not final_label:
                st.error("❌ Please provide an activity label.")
            else:
                try:
                    normalized_record, is_overnight = validate_single_activity_row(
                        raw_date=activity_date,
                        raw_start_time=start_time,
                        raw_end_time=end_time,
                        raw_activity=final_label,
                        allow_overnight=True,
                    )

                    success = db_manager.insert_activity_record(
                        activity_date=normalized_record["activity_date"],
                        start_time=normalized_record["start_time"],
                        end_time=normalized_record["end_time"],
                        activity_label=normalized_record["activity_label"],
                        duration_minutes=normalized_record["duration_minutes"],
                    )

                    if success:
                        st.success(
                            f"✅ **Activity recorded:** {normalized_record['activity_label']} "
                            f"on {normalized_record['activity_date']} "
                            f"({normalized_record['duration_minutes']:.0f} minutes)"
                        )
                        if is_overnight:
                            st.info("ℹ️ Overnight activity detected and recorded correctly.")
                        st.rerun()
                    else:
                        st.warning("⚠️ This activity record already exists in the database.")

                except ValueError as exc:
                    st.error(f"❌ **Validation Error:** {exc}")
                except Exception as exc:
                    st.error(f"❌ **Error:** {exc}")


def _render_activity_management_section(db_manager: DatabaseManager) -> None:
    """Render activity records table with filtering and deletion."""
    st.markdown("### Manage Activity Records")

    df = db_manager.get_all_activity_records()

    if df.empty:
        st.info("📭 No activity records found. Upload data or add records manually.")
        return

    st.markdown(f"**Total Records:** {len(df)}")

    col1, col2, col3 = st.columns(3)
    with col1:
        unique_dates = sorted(df["activity_date"].unique(), reverse=True)
        date_filter = st.selectbox(
            "Filter by Date",
            options=["All Dates"] + list(unique_dates),
            key="date_filter",
        )
    with col2:
        unique_labels = sorted(df["activity_label"].unique())
        label_filter = st.selectbox(
            "Filter by Activity",
            options=["All Activities"] + list(unique_labels),
            key="label_filter",
        )
    with col3:
        st.markdown("<div style='height: 1.9rem;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    filtered_df = df.copy()
    if date_filter != "All Dates":
        filtered_df = filtered_df[filtered_df["activity_date"] == date_filter]
    if label_filter != "All Activities":
        filtered_df = filtered_df[filtered_df["activity_label"] == label_filter]

    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} records**")

    display_df = filtered_df[["id", "activity_date", "start_time", "end_time", "activity_label", "duration_minutes"]].copy()
    display_df.columns = ["ID", "Date", "Start", "End", "Activity", "Duration (min)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_del1, col_del2 = st.columns([2, 1])
    with col_del1:
        record_id_to_delete = st.number_input(
            "Enter Record ID to Delete",
            min_value=1,
            step=1,
            help="Enter the ID from the table above",
        )
    with col_del2:
        st.markdown("<div style='height: 1.9rem;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Delete Record", type="secondary"):
            if db_manager.delete_activity_record(int(record_id_to_delete)):
                st.success(f"✅ Record {record_id_to_delete} deleted successfully.")
                st.rerun()
            else:
                st.error(f"❌ Record {record_id_to_delete} not found.")

    st.markdown("---")
    st.markdown("#### ⚠️ Danger Zone")
    if st.button("🗑️ Clear All Activity Records", type="secondary"):
        st.session_state["confirm_clear"] = True

    if st.session_state.get("confirm_clear", False):
        st.warning("⚠️ **Are you sure?** This will permanently delete ALL activity records.")
        col_confirm1, col_confirm2 = st.columns(2)
        with col_confirm1:
            if st.button("✅ Yes, Delete All", type="primary"):
                deleted_count = db_manager.clear_all_activity_records()
                st.success(f"✅ Deleted {deleted_count} activity records.")
                st.session_state["confirm_clear"] = False
                st.rerun()
        with col_confirm2:
            if st.button("❌ Cancel"):
                st.session_state["confirm_clear"] = False
                st.rerun()


def render_activity_analytics_page(db_manager: DatabaseManager) -> None:
    """Complete Activity Analytics page with comprehensive duration and distribution analysis."""
    render_page_hero(
        eyebrow="Page 3 of 7 • Duration & Distribution",
        title="Activity Analytics",
        subtitle="Explore total recorded durations, activity breakdowns, daily summaries, and time-based patterns.",
    )

    df = db_manager.get_all_activity_records()

    if df.empty:
        st.info("📭 No activity data available. Upload activity records to view analytics.")
        if st.button("📤 Go to Upload Activity", type="primary"):
            st.session_state["selected_page"] = "Upload Activity"
            st.rerun()
        render_non_medical_disclaimer()
        return

    # Sidebar filters
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Analytics Filters")
        
        min_date = df["activity_date"].min()
        max_date = df["activity_date"].max()
        
        date_range = st.date_input(
            "Date Range",
            value=(pd.to_datetime(min_date).date(), pd.to_datetime(max_date).date()),
            help="Filter analytics by date range",
        )
        
        all_activities = sorted(df["activity_label"].unique())
        activity_filter = st.multiselect(
            "Activity Types",
            options=all_activities,
            default=all_activities,
            help="Select activity types to include",
        )

    # Apply filters
    filtered_df = df.copy()
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["activity_date"] >= start_date.isoformat()) &
            (filtered_df["activity_date"] <= end_date.isoformat())
        ]
    if activity_filter:
        filtered_df = filtered_df[filtered_df["activity_label"].isin(activity_filter)]

    if filtered_df.empty:
        st.warning("⚠️ No data matches the selected filters.")
        render_non_medical_disclaimer()
        return

    # Import analytics functions
    from modules.activity_analytics import (
        calculate_activity_statistics,
        calculate_activity_distribution,
        calculate_daily_summary,
        analyze_time_periods,
        generate_activity_insights,
    )
    from components.charts import (
        build_activity_distribution_donut,
        build_activity_duration_bar,
        build_time_period_bar,
    )

    # Section A: Activity Overview Cards
    st.markdown("### 📈 Activity Overview")
    stats = calculate_activity_statistics(filtered_df)
    
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    with col1:
        render_kpi_card(
            label="Total Duration",
            value=f"{stats['total_minutes']:.0f} min",
            hint=f"{stats['total_hours']:.1f} hours",
        )
    with col2:
        render_kpi_card(
            label="Walking",
            value=f"{stats['walking_minutes']:.0f} min",
            hint=f"{(stats['walking_minutes']/stats['total_minutes']*100) if stats['total_minutes'] > 0 else 0:.1f}%",
        )
    with col3:
        render_kpi_card(
            label="Sitting",
            value=f"{stats['sitting_minutes']:.0f} min",
            hint=f"{(stats['sitting_minutes']/stats['total_minutes']*100) if stats['total_minutes'] > 0 else 0:.1f}%",
        )
    with col4:
        render_kpi_card(
            label="Standing",
            value=f"{stats['standing_minutes']:.0f} min",
            hint=f"{(stats['standing_minutes']/stats['total_minutes']*100) if stats['total_minutes'] > 0 else 0:.1f}%",
        )
    with col5:
        render_kpi_card(
            label="Total Sessions",
            value=str(stats['total_sessions']),
            hint=f"Avg: {stats['average_session_duration']:.1f} min",
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Section B: Activity Distribution Charts
    st.markdown("### 📊 Activity Distribution")
    distribution = calculate_activity_distribution(filtered_df)
    distribution_dict = [
        {
            "activity_label": item.activity_label,
            "total_minutes": item.total_minutes,
            "percentage": item.percentage,
        }
        for item in distribution
    ]

    col_chart1, col_chart2 = st.columns(2, gap="large")
    with col_chart1:
        st.plotly_chart(
            build_activity_distribution_donut(distribution_dict),
            use_container_width=True,
        )
    with col_chart2:
        st.plotly_chart(
            build_activity_duration_bar(distribution_dict),
            use_container_width=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Section C: Daily Activity Breakdown
    st.markdown("### 📅 Daily Activity Breakdown")
    
    unique_dates = sorted(filtered_df["activity_date"].unique(), reverse=True)
    selected_date = st.selectbox(
        "Select Date",
        options=unique_dates,
        help="Choose a date to view detailed breakdown",
    )

    if selected_date:
        daily_summary = calculate_daily_summary(filtered_df, selected_date)
        
        col_d1, col_d2, col_d3, col_d4 = st.columns(4, gap="medium")
        with col_d1:
            render_kpi_card(
                label="Daily Total",
                value=f"{daily_summary.total_minutes:.0f} min",
                hint=f"{daily_summary.total_hours:.1f} hours",
            )
        with col_d2:
            render_kpi_card(
                label="Sessions",
                value=str(daily_summary.total_sessions),
                hint="recorded intervals",
            )
        with col_d3:
            render_kpi_card(
                label="Top Activity",
                value=daily_summary.most_frequent_activity or "N/A",
                hint="by duration",
            )
        with col_d4:
            walking_pct = daily_summary.activity_percentages.get("Walking", 0)
            render_kpi_card(
                label="Walking",
                value=f"{daily_summary.walking_minutes:.0f} min",
                hint=f"{walking_pct:.1f}%",
            )

        # Daily breakdown table
        if daily_summary.activity_percentages:
            st.markdown("#### Activity Breakdown")
            breakdown_data = []
            for activity, percentage in sorted(
                daily_summary.activity_percentages.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                daily_df = filtered_df[
                    (filtered_df["activity_date"] == selected_date) &
                    (filtered_df["activity_label"] == activity)
                ]
                duration = daily_df["duration_minutes"].sum()
                breakdown_data.append({
                    "Activity": activity,
                    "Duration (min)": f"{duration:.1f}",
                    "Duration (hrs)": f"{duration/60:.2f}",
                    "Percentage": f"{percentage:.1f}%",
                    "Sessions": len(daily_df),
                })
            st.dataframe(breakdown_data, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Section D: Time-Based Activity Analysis
    st.markdown("### 🕐 Activity by Time of Day")
    time_analysis = analyze_time_periods(filtered_df)
    
    time_period_data = {
        "Early Morning": time_analysis.early_morning_minutes,
        "Morning": time_analysis.morning_minutes,
        "Afternoon": time_analysis.afternoon_minutes,
        "Evening": time_analysis.evening_minutes,
        "Night": time_analysis.night_minutes,
    }
    
    st.plotly_chart(
        build_time_period_bar(time_period_data),
        use_container_width=True,
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Section E: Activity Pattern Insights
    st.markdown("### 💡 Activity Insights")
    insights = generate_activity_insights(filtered_df)
    
    for insight in insights:
        st.markdown(f"- {insight}")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Section F: Detailed Analytics Table
    st.markdown("### 📋 Detailed Analytics Table")
    
    if distribution:
        table_data = []
        for item in distribution:
            table_data.append({
                "Activity": item.activity_label,
                "Total Duration (min)": f"{item.total_minutes:.1f}",
                "Total Duration (hrs)": f"{item.total_hours:.2f}",
                "Percentage": f"{item.percentage:.1f}%",
                "Sessions": item.session_count,
                "Avg Duration (min)": f"{item.average_duration:.1f}",
                "Min Duration (min)": f"{item.min_duration:.1f}",
                "Max Duration (min)": f"{item.max_duration:.1f}",
            })
        st.dataframe(table_data, use_container_width=True, hide_index=True)

    render_non_medical_disclaimer()


def render_activity_comparison_page(db_manager: DatabaseManager) -> None:
    """Complete Activity Comparison page with day-to-day, weekly, and period comparisons."""
    render_page_hero(
        eyebrow="Page 4 of 7 • Cross-Day Comparison",
        title="Activity Comparison",
        subtitle="Compare activity durations across different dates, analyze weekly trends, and identify routine shifts.",
    )

    df = db_manager.get_all_activity_records()

    if df.empty:
        st.info("📭 No activity data available. Upload activity records to compare durations across dates.")
        if st.button("📤 Go to Upload Activity", type="primary"):
            st.session_state["selected_page"] = "Upload Activity"
            st.rerun()
        render_non_medical_disclaimer()
        return

    # Import comparison functions
    from datetime import datetime, timedelta
    from modules.activity_comparison import (
        compare_two_days,
        generate_weekly_comparison,
        compare_custom_periods,
        generate_comparison_insights,
    )
    from components.charts import (
        build_day_comparison_chart,
        build_weekly_trend_line,
        build_weekly_stacked_bar,
    )

    # Get available dates
    available_dates = sorted(df["activity_date"].unique(), reverse=True)
    
    if len(available_dates) < 2:
        st.warning("⚠️ At least 2 dates with activity data are required for comparison.")
        render_non_medical_disclaimer()
        return

    # Tabs for different comparison types
    tab1, tab2, tab3 = st.tabs(["📅 Day-to-Day", "📊 Weekly Trends", "📆 Period Comparison"])

    # TAB 1: Day-to-Day Comparison
    with tab1:
        st.markdown("### Day-to-Day Activity Comparison")
        
        col_prev, col_curr = st.columns(2)
        with col_prev:
            previous_date = st.selectbox(
                "Previous Date",
                options=available_dates,
                index=min(1, len(available_dates)-1),
                help="Select the baseline/previous date",
            )
        with col_curr:
            current_date = st.selectbox(
                "Current Date",
                options=available_dates,
                index=0,
                help="Select the target/current date",
            )

        if previous_date and current_date:
            comparison = compare_two_days(df, previous_date, current_date)
            
            # Section B: Daily Comparison Cards
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4, gap="medium")
            with col1:
                render_kpi_card(
                    label=f"{previous_date}",
                    value=f"{comparison.previous_total:.0f} min",
                    hint=f"{comparison.previous_total/60:.1f} hours",
                )
            with col2:
                render_kpi_card(
                    label=f"{current_date}",
                    value=f"{comparison.current_total:.0f} min",
                    hint=f"{comparison.current_total/60:.1f} hours",
                )
            with col3:
                diff_color = "🟢" if comparison.total_difference > 0 else "🔴" if comparison.total_difference < 0 else "⚪"
                render_kpi_card(
                    label="Total Change",
                    value=f"{diff_color} {comparison.total_difference:+.0f} min",
                    hint="Duration difference",
                )
            with col4:
                render_kpi_card(
                    label="Activities",
                    value=str(comparison.activities_compared),
                    hint="compared",
                )

            # Section C: Activity Comparison Chart
            if comparison.comparisons:
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                activities = [c.activity_label for c in comparison.comparisons]
                prev_values = [c.previous_duration for c in comparison.comparisons]
                curr_values = [c.current_duration for c in comparison.comparisons]
                
                st.plotly_chart(
                    build_day_comparison_chart(
                        activities, prev_values, curr_values,
                        previous_date, current_date
                    ),
                    use_container_width=True,
                )

            # Section D: Duration Difference Table
            st.markdown("### 📋 Detailed Comparison Table")
            if comparison.comparisons:
                table_data = []
                for comp in comparison.comparisons:
                    # Determine color indicator
                    if comp.change_status == "increased":
                        indicator = "🟢 ↑"
                    elif comp.change_status == "decreased":
                        indicator = "🔴 ↓"
                    elif comp.change_status == "newly_recorded":
                        indicator = "🆕"
                    else:
                        indicator = "⚪ →"
                    
                    # Format percentage change
                    if comp.percentage_change is None:
                        pct_str = "N/A"
                    else:
                        pct_str = f"{comp.percentage_change:+.1f}%"
                    
                    table_data.append({
                        "Activity": comp.activity_label,
                        "Previous (min)": f"{comp.previous_duration:.0f}",
                        "Current (min)": f"{comp.current_duration:.0f}",
                        "Difference": f"{comp.absolute_difference:+.0f}",
                        "Change %": pct_str,
                        "Status": indicator,
                    })
                
                st.dataframe(table_data, use_container_width=True, hide_index=True)

            # Section G: Comparison Insights
            st.markdown("### 💡 Activity Change Insights")
            insights = generate_comparison_insights(comparison=comparison)
            for insight in insights:
                st.markdown(f"- {insight}")

    # TAB 2: Weekly Trends
    with tab2:
        st.markdown("### Weekly Activity Trends")
        
        # Week selection
        min_date = df["activity_date"].min()
        week_start = st.date_input(
            "Week Start Date",
            value=pd.to_datetime(min_date).date(),
            help="Select the starting date for 7-day analysis",
        )
        
        if week_start:
            weekly_stats = generate_weekly_comparison(df, week_start.isoformat(), num_days=7)
            
            # Weekly summary cards
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            col_w1, col_w2, col_w3, col_w4 = st.columns(4, gap="medium")
            with col_w1:
                render_kpi_card(
                    label="Avg Daily Duration",
                    value=f"{weekly_stats.average_daily_duration:.0f} min",
                    hint=f"{weekly_stats.days_with_data} days with data",
                )
            with col_w2:
                render_kpi_card(
                    label="Total Walking",
                    value=f"{weekly_stats.total_walking:.0f} min",
                    hint=f"{weekly_stats.total_walking/60:.1f} hours",
                )
            with col_w3:
                render_kpi_card(
                    label="Total Sitting",
                    value=f"{weekly_stats.total_sitting:.0f} min",
                    hint=f"{weekly_stats.total_sitting/60:.1f} hours",
                )
            with col_w4:
                render_kpi_card(
                    label="Total Standing",
                    value=f"{weekly_stats.total_standing:.0f} min",
                    hint=f"{weekly_stats.total_standing/60:.1f} hours",
                )

            # Section E: Weekly Trends Charts
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("### 📈 Weekly Activity Trends")
            
            col_chart1, col_chart2 = st.columns(2, gap="large")
            with col_chart1:
                st.plotly_chart(
                    build_weekly_trend_line(
                        weekly_stats.dates,
                        weekly_stats.daily_totals,
                        "Total Activity"
                    ),
                    use_container_width=True,
                )
            with col_chart2:
                st.plotly_chart(
                    build_weekly_trend_line(
                        weekly_stats.dates,
                        weekly_stats.daily_walking,
                        "Walking"
                    ),
                    use_container_width=True,
                )

            # Stacked bar chart
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            # Calculate "other" activities
            other_values = [
                total - walk - sit - stand
                for total, walk, sit, stand in zip(
                    weekly_stats.daily_totals,
                    weekly_stats.daily_walking,
                    weekly_stats.daily_sitting,
                    weekly_stats.daily_standing,
                )
            ]
            
            st.plotly_chart(
                build_weekly_stacked_bar(
                    weekly_stats.dates,
                    weekly_stats.daily_walking,
                    weekly_stats.daily_sitting,
                    weekly_stats.daily_standing,
                    other_values,
                ),
                use_container_width=True,
            )

            # Daily summary table
            st.markdown("### 📅 Daily Activity Summary")
            daily_summary_data = []
            for i, date in enumerate(weekly_stats.dates):
                if weekly_stats.daily_totals[i] > 0:
                    daily_summary_data.append({
                        "Date": date,
                        "Total (min)": f"{weekly_stats.daily_totals[i]:.0f}",
                        "Walking": f"{weekly_stats.daily_walking[i]:.0f}",
                        "Sitting": f"{weekly_stats.daily_sitting[i]:.0f}",
                        "Standing": f"{weekly_stats.daily_standing[i]:.0f}",
                        "Running": f"{weekly_stats.daily_running[i]:.0f}",
                        "Cycling": f"{weekly_stats.daily_cycling[i]:.0f}",
                    })
            
            if daily_summary_data:
                st.dataframe(daily_summary_data, use_container_width=True, hide_index=True)
            else:
                st.info("No activity data available for the selected week.")

            # Weekly statistics
            st.markdown("### 📊 Weekly Statistics")
            if weekly_stats.days_with_data > 0:
                stat_col1, stat_col2 = st.columns(2)
                with stat_col1:
                    st.markdown(f"**Highest Walking Duration:** {weekly_stats.highest_walking_duration:.0f} min")
                    st.markdown(f"**Lowest Walking Duration:** {weekly_stats.lowest_walking_duration:.0f} min")
                    st.markdown(f"**Highest Sitting Duration:** {weekly_stats.highest_sitting_duration:.0f} min")
                with stat_col2:
                    st.markdown(f"**Total Walking:** {weekly_stats.total_walking:.0f} min")
                    st.markdown(f"**Total Sitting:** {weekly_stats.total_sitting:.0f} min")
                    st.markdown(f"**Average Daily:** {weekly_stats.average_daily_duration:.0f} min")
                
                # Weekly insights
                st.markdown("### 💡 Weekly Insights")
                insights = generate_comparison_insights(weekly_stats=weekly_stats)
                for insight in insights:
                    st.markdown(f"- {insight}")

    # TAB 3: Period Comparison
    with tab3:
        st.markdown("### Custom Period Comparison")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Period A**")
            period_a_start = st.date_input(
                "Start Date (Period A)",
                value=pd.to_datetime(available_dates[-1]).date(),
                help="Select start date for Period A",
            )
            period_a_end = st.date_input(
                "End Date (Period A)",
                value=pd.to_datetime(available_dates[-1]).date(),
                help="Select end date for Period A",
            )
        with col_p2:
            st.markdown("**Period B**")
            period_b_start = st.date_input(
                "Start Date (Period B)",
                value=pd.to_datetime(available_dates[0]).date(),
                help="Select start date for Period B",
            )
            period_b_end = st.date_input(
                "End Date (Period B)",
                value=pd.to_datetime(available_dates[0]).date(),
                help="Select end date for Period B",
            )

        if period_a_start and period_a_end and period_b_start and period_b_end:
            period_comparison = compare_custom_periods(
                df,
                period_a_start.isoformat(),
                period_a_end.isoformat(),
                period_b_start.isoformat(),
                period_b_end.isoformat(),
            )
            
            # Period summary cards
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            col_p1, col_p2, col_p3 = st.columns(3, gap="medium")
            with col_p1:
                render_kpi_card(
                    label="Period A Total",
                    value=f"{period_comparison.period_a_total:.0f} min",
                    hint=f"{period_comparison.period_a_start} to {period_comparison.period_a_end}",
                )
            with col_p2:
                render_kpi_card(
                    label="Period B Total",
                    value=f"{period_comparison.period_b_total:.0f} min",
                    hint=f"{period_comparison.period_b_start} to {period_comparison.period_b_end}",
                )
            with col_p3:
                diff_indicator = "🟢" if period_comparison.total_difference > 0 else "🔴" if period_comparison.total_difference < 0 else "⚪"
                render_kpi_card(
                    label="Difference",
                    value=f"{diff_indicator} {period_comparison.total_difference:+.0f} min",
                    hint="Period B vs Period A",
                )

            # Period comparison table
            st.markdown("### 📋 Activity Breakdown")
            period_table_data = [
                {
                    "Activity": "Walking",
                    "Period A": f"{period_comparison.period_a_walking:.0f}",
                    "Period B": f"{period_comparison.period_b_walking:.0f}",
                    "Difference": f"{period_comparison.walking_difference:+.0f}",
                },
                {
                    "Activity": "Sitting",
                    "Period A": f"{period_comparison.period_a_sitting:.0f}",
                    "Period B": f"{period_comparison.period_b_sitting:.0f}",
                    "Difference": f"{period_comparison.sitting_difference:+.0f}",
                },
                {
                    "Activity": "Standing",
                    "Period A": f"{period_comparison.period_a_standing:.0f}",
                    "Period B": f"{period_comparison.period_b_standing:.0f}",
                    "Difference": f"{period_comparison.standing_difference:+.0f}",
                },
                {
                    "Activity": "Running",
                    "Period A": f"{period_comparison.period_a_running:.0f}",
                    "Period B": f"{period_comparison.period_b_running:.0f}",
                    "Difference": f"{period_comparison.running_difference:+.0f}",
                },
                {
                    "Activity": "Cycling",
                    "Period A": f"{period_comparison.period_a_cycling:.0f}",
                    "Period B": f"{period_comparison.period_b_cycling:.0f}",
                    "Difference": f"{period_comparison.cycling_difference:+.0f}",
                },
            ]
            st.dataframe(period_table_data, use_container_width=True, hide_index=True)

            # Period insights
            st.markdown("### 💡 Period Comparison Insights")
            insights = generate_comparison_insights(period_comparison=period_comparison)
            for insight in insights:
                st.markdown(f"- {insight}")

    render_non_medical_disclaimer()


def render_ai_activity_diary_page(db_manager: DatabaseManager) -> None:
    """AI Activity Diary page with daily and weekly narrative generation."""
    render_page_hero(
        eyebrow="Page 5 of 7 • GenAI Narration",
        title="AI Activity Diary",
        subtitle="Generate natural-language daily activity diary entries powered by the Gemini API.",
    )

    df = db_manager.get_all_activity_records()

    if df.empty:
        st.info("📭 No activity data available. Upload activity records to generate diary narratives.")
        if st.button("📤 Go to Upload Activity", type="primary"):
            st.session_state["selected_page"] = "Upload Activity"
            st.rerun()
        render_non_medical_disclaimer()
        return

    # Import required modules
    from modules.ai_narrator import (
        is_gemini_configured,
        get_gemini_model_name,
        generate_daily_narrative,
        generate_weekly_narrative,
    )
    from modules.activity_analytics import calculate_activity_statistics

    # Gemini API status banner
    if is_gemini_configured():
        model_name = get_gemini_model_name()
        st.success(f"✅ **Gemini API Configured:** Using model `{model_name}`")
    else:
        st.warning(
            "⚠️ **Gemini API not configured.** Add `GEMINI_API_KEY` to your `.env` file. "
            "Fallback template narratives will be used instead."
        )

    # Tabs for daily and weekly narratives
    tab1, tab2 = st.tabs(["📅 Daily Narrative", "📊 Weekly Summary"])

    # TAB 1: Daily Narrative
    with tab1:
        st.markdown("### Generate Daily Activity Narrative")
        st.markdown(
            "Select a date with recorded activity data and generate a personalized diary entry. "
            "The narrative is grounded in your actual recorded activity durations and patterns."
        )

        available_dates = sorted(df["activity_date"].unique(), reverse=True)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            selected_date = st.selectbox(
                "Select Date",
                options=available_dates,
                help="Choose a date to generate a narrative for",
            )
        with col2:
            tone = st.selectbox(
                "Narrative Tone",
                options=["Reflective & Clear", "Casual & Friendly", "Professional & Concise"],
                help="Select the tone/style of the narrative",
            )
        with col3:
            st.markdown("<div style='height: 1.9rem;'></div>", unsafe_allow_html=True)
            generate_button = st.button("✨ Generate Narrative", type="primary", use_container_width=True)

        if generate_button and selected_date:
            with st.spinner("Generating daily narrative..."):
                # Get daily statistics
                from modules.activity_analytics import calculate_daily_summary
                
                # Filter data for selected date
                daily_df = df[df["activity_date"] == selected_date]
                daily_summary = calculate_daily_summary(df, selected_date)
                
                # Build statistics dictionary
                daily_stats = {
                    "total_minutes": daily_summary.total_minutes,
                    "total_hours": daily_summary.total_hours,
                    "total_sessions": daily_summary.total_sessions,
                    "walking_minutes": daily_summary.walking_minutes,
                    "sitting_minutes": daily_summary.sitting_minutes,
                    "standing_minutes": daily_summary.standing_minutes,
                    "running_minutes": daily_summary.running_minutes,
                    "cycling_minutes": daily_summary.cycling_minutes,
                    "activity_percentages": daily_summary.activity_percentages,
                    "top_activity": daily_summary.most_frequent_activity,
                }

                # Get previous day statistics if available
                previous_day_stats = None
                date_index = available_dates.index(selected_date)
                if date_index < len(available_dates) - 1:
                    prev_date = available_dates[date_index + 1]
                    prev_summary = calculate_daily_summary(df, prev_date)
                    previous_day_stats = {
                        "date": prev_date,
                        "walking_minutes": prev_summary.walking_minutes,
                        "sitting_minutes": prev_summary.sitting_minutes,
                        "standing_minutes": prev_summary.standing_minutes,
                        "running_minutes": prev_summary.running_minutes,
                        "cycling_minutes": prev_summary.cycling_minutes,
                    }

                # Generate narrative
                response = generate_daily_narrative(
                    activity_date=selected_date,
                    daily_stats=daily_stats,
                    previous_day_stats=previous_day_stats,
                    tone=tone,
                )

                if response.success:
                    st.markdown("---")
                    st.markdown(f"### 📝 Daily Diary Entry: {selected_date}")
                    st.markdown(
                        f"""
                        <div class="ap-card" style="padding: 1.5rem;">
                            <div style="line-height: 1.8; color: #E2E8F0;">
                                {response.narrative_text.replace(chr(10), '<br><br>')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    # Show metadata
                    col_meta1, col_meta2 = st.columns(2)
                    with col_meta1:
                        st.caption(f"🤖 Generated by: {response.model_used}")
                    with col_meta2:
                        st.caption(f"🎨 Tone: {tone}")
                    
                    if response.error_message:
                        st.info(f"ℹ️ {response.error_message}")
                else:
                    st.error(f"❌ Failed to generate narrative: {response.error_message}")

    # TAB 2: Weekly Summary
    with tab2:
        st.markdown("### Generate Weekly Activity Summary")
        st.markdown(
            "Select a week start date and generate a comprehensive summary of your activity patterns "
            "across the entire week."
        )

        min_date = df["activity_date"].min()
        
        col_w1, col_w2 = st.columns([2, 1])
        with col_w1:
            week_start_date = st.date_input(
                "Week Start Date",
                value=pd.to_datetime(min_date).date(),
                help="Select the starting date for 7-day analysis",
            )
        with col_w2:
            st.markdown("<div style='height: 1.9rem;'></div>", unsafe_allow_html=True)
            generate_weekly_button = st.button(
                "✨ Generate Weekly Summary",
                type="primary",
                use_container_width=True,
            )

        if generate_weekly_button and week_start_date:
            with st.spinner("Generating weekly summary..."):
                from modules.activity_comparison import generate_weekly_comparison
                
                # Get weekly statistics
                weekly_stats_obj = generate_weekly_comparison(df, week_start_date.isoformat(), num_days=7)
                
                # Build statistics dictionary
                weekly_stats = {
                    "total_walking": weekly_stats_obj.total_walking,
                    "total_sitting": weekly_stats_obj.total_sitting,
                    "total_standing": weekly_stats_obj.total_standing,
                    "total_running": weekly_stats_obj.total_running,
                    "total_cycling": weekly_stats_obj.total_cycling,
                    "days_with_data": weekly_stats_obj.days_with_data,
                    "average_daily": weekly_stats_obj.average_daily_duration,
                    "highest_walking": weekly_stats_obj.highest_walking_duration,
                    "lowest_walking": weekly_stats_obj.lowest_walking_duration,
                    "highest_sitting": weekly_stats_obj.highest_sitting_duration,
                    "dates": weekly_stats_obj.dates,
                    "daily_totals": weekly_stats_obj.daily_totals,
                }

                # Generate narrative
                response = generate_weekly_narrative(
                    week_start=week_start_date.isoformat(),
                    weekly_stats=weekly_stats,
                )

                if response.success:
                    st.markdown("---")
                    st.markdown(f"### 📊 Weekly Summary: Week of {week_start_date}")
                    st.markdown(
                        f"""
                        <div class="ap-card" style="padding: 1.5rem;">
                            <div style="line-height: 1.8; color: #E2E8F0;">
                                {response.narrative_text.replace(chr(10), '<br><br>')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    st.caption(f"🤖 Generated by: {response.model_used}")
                    
                    if response.error_message:
                        st.info(f"ℹ️ {response.error_message}")
                else:
                    st.error(f"❌ Failed to generate weekly summary: {response.error_message}")

    render_non_medical_disclaimer()


def render_ai_assistant_page(db_manager: DatabaseManager) -> None:
    """AI Assistant page with conversational Q&A about activity data."""
    render_page_hero(
        eyebrow="Page 6 of 7 • Conversational Q&A",
        title="AI Assistant",
        subtitle="Ask natural-language questions about your recorded activity durations and schedules.",
    )

    df = db_manager.get_all_activity_records()

    if df.empty:
        st.info("📭 No activity data available. Upload activity records to ask questions.")
        if st.button("📤 Go to Upload Activity", type="primary"):
            st.session_state["selected_page"] = "Upload Activity"
            st.rerun()
        render_non_medical_disclaimer()
        return

    # Import AI assistant functions
    from modules.ai_assistant import (
        answer_activity_question,
        AssistantMessage,
    )
    from modules.ai_narrator import is_gemini_configured, get_gemini_model_name

    # Initialize conversation history in session state
    if "assistant_conversation" not in st.session_state:
        st.session_state["assistant_conversation"] = []

    # Gemini API status
    if is_gemini_configured():
        model_name = get_gemini_model_name()
        st.success(f"✅ **AI Assistant Active:** Using model `{model_name}`")
    else:
        st.warning(
            "⚠️ **Gemini API not configured.** Add `GEMINI_API_KEY` to your `.env` file. "
            "Data-only responses will be provided without conversational narratives."
        )

    # Main chat interface
    st.markdown("### 💬 Ask Questions About Your Activities")
    st.markdown(
        "Ask questions like: *'How much time did I spend walking today?'*, "
        "*'What was my most frequent activity yesterday?'*, or "
        "*'Compare my sitting time this week to last week.'*"
    )

    # Suggested questions
    with st.expander("💡 Suggested Questions"):
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("**Daily Questions:**")
            st.markdown("- How much time did I spend walking today?")
            st.markdown("- What activities did I do yesterday?")
            st.markdown("- Show me my sitting time for Monday")
        with col_q2:
            st.markdown("**Weekly Questions:**")
            st.markdown("- What was my total activity time this week?")
            st.markdown("- Compare my walking time between today and yesterday")
            st.markdown("- What was my most frequent activity this week?")

    st.markdown("---")

    # Chat input
    user_question = st.chat_input(
        "Ask a question about your activities...",
        key="assistant_chat_input",
    )

    # Display conversation history
    if st.session_state["assistant_conversation"]:
        st.markdown("### 📝 Conversation")
        
        for msg in st.session_state["assistant_conversation"]:
            if msg.role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg.content)
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg.content)

    # Process new question
    if user_question:
        # Add user message to conversation
        st.session_state["assistant_conversation"].append(
            AssistantMessage(role="user", content=user_question)
        )
        
        # Display user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_question)

        # Generate assistant response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = answer_activity_question(
                    question=user_question,
                    activity_df=df,
                    conversation_history=st.session_state["assistant_conversation"],
                )

                if response.success:
                    st.markdown(response.answer)
                    
                    # Show retrieved data if available
                    if response.retrieved_data:
                        with st.expander("📊 Retrieved Data"):
                            st.json(response.retrieved_data)
                else:
                    st.error(f"❌ {response.error_message}")
                    response_text = f"I apologize, but I encountered an error: {response.error_message}"

        # Add assistant response to conversation
        st.session_state["assistant_conversation"].append(
            AssistantMessage(
                role="assistant",
                content=response.answer if response.success else f"Error: {response.error_message}"
            )
        )
        
        # Keep only last 10 messages (5 exchanges) to avoid token limit
        if len(st.session_state["assistant_conversation"]) > 10:
            st.session_state["assistant_conversation"] = st.session_state["assistant_conversation"][-10:]
        
        st.rerun()

    # Clear conversation button
    if st.session_state["assistant_conversation"]:
        st.markdown("---")
        col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 2])
        with col_clear1:
            if st.button("🗑️ Clear Conversation", type="secondary"):
                st.session_state["assistant_conversation"] = []
                st.rerun()

    render_non_medical_disclaimer()


# Advanced Reports Page - Imported from dedicated module
from components.reports_page import render_advanced_reports_page


def render_ai_settings_page() -> None:
    """AI Settings and Provider Configuration page."""
    from modules.llm_provider import (
        get_llm_manager,
        test_provider_connection,
        switch_provider,
    )
    from components.ui_components import render_feature_card
    
    render_page_hero(
        eyebrow="Multi-LLM Configuration",
        title="AI Settings",
        subtitle="Configure and manage AI providers (Groq and Google Gemini) for activity narratives and intelligent assistant.",
    )
    
    # Get provider manager
    manager = get_llm_manager()
    statuses = manager.get_provider_status()
    current_provider = manager.get_configured_provider()
    
    # Provider Selection Section
    st.markdown("### ?? AI Provider Selection")
    st.markdown(
        "Choose which AI provider to use for generating activity narratives and answering questions. "
        "**Auto** mode automatically selects the best available provider (Groq ? Gemini ? Fallback)."
    )
    
    col_provider1, col_provider2 = st.columns([2, 1])
    
    with col_provider1:
        provider_options = ["auto", "groq", "gemini"]
        provider_labels = {
            "auto": "?? Automatic (Recommended)",
            "groq": "? Groq (Fast & Efficient)",
            "gemini": "?? Google Gemini (Advanced)",
        }
        
        selected_provider = st.radio(
            "Select AI Provider",
            options=provider_options,
            format_func=lambda x: provider_labels[x],
            index=provider_options.index(current_provider),
            help="Auto mode tries Groq first, then falls back to Gemini if needed",
        )
        
        if selected_provider != current_provider:
            if st.button("?? Save Provider Selection", type="primary"):
                if switch_provider(selected_provider):
                    st.success(f"? Switched to {provider_labels[selected_provider]}")
                    st.rerun()
                else:
                    st.error("? Failed to switch provider. Check logs.")
    
    with col_provider2:
        st.markdown("#### Current Settings")
        st.info(f"**Active:** {provider_labels[current_provider]}")
    
    st.markdown("---")
    
    # Provider Status Section
    st.markdown("### ?? Provider Connection Status")
    
    col_groq, col_gemini = st.columns(2, gap="large")
    
    # Groq Status
    with col_groq:
        st.markdown("#### ? Groq")
        
        groq_status = statuses.get("groq")
        if groq_status and groq_status.connected:
            st.success(f"? **Connected**")
            st.markdown(f"**Model:** `{groq_status.model}`")
        else:
            st.error("? **Not Configured**")
            if groq_status and groq_status.error:
                st.caption(f"Error: {groq_status.error}")
        
        if st.button("?? Test Groq Connection", key="test_groq"):
            with st.spinner("Testing Groq connection..."):
                result = test_provider_connection("groq")
                if result.connected:
                    st.success(f"? Groq is working! Model: {result.model}")
                else:
                    st.error(f"? Connection failed: {result.error}")
    
    # Gemini Status
    with col_gemini:
        st.markdown("#### ?? Google Gemini")
        
        gemini_status = statuses.get("gemini")
        if gemini_status and gemini_status.connected:
            st.success(f"? **Connected**")
            st.markdown(f"**Model:** `{gemini_status.model}`")
        else:
            st.error("? **Not Configured**")
            if gemini_status and gemini_status.error:
                st.caption(f"Error: {gemini_status.error}")
        
        if st.button("?? Test Gemini Connection", key="test_gemini"):
            with st.spinner("Testing Gemini connection..."):
                result = test_provider_connection("gemini")
                if result.connected:
                    st.success(f"? Gemini is working! Model: {result.model}")
                else:
                    st.error(f"? Connection failed: {result.error}")
    
    st.markdown("---")
    
    # Features Overview
    st.markdown("### ? AI Features")
    
    col_feat1, col_feat2, col_feat3 = st.columns(3, gap="medium")
    
    with col_feat1:
        render_feature_card(
            icon="??",
            title="AI Activity Diary",
            description="Generate daily and weekly activity narratives",
            status="active",
        )
    
    with col_feat2:
        render_feature_card(
            icon="??",
            title="AI Assistant",
            description="Ask questions about your activity data",
            status="active",
        )
    
    with col_feat3:
        render_feature_card(
            icon="??",
            title="Tool-Based Agent",
            description="Intelligent agent with database tools",
            status="active",
        )
    
    render_non_medical_disclaimer()
