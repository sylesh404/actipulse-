"""Smart Activity Timeline Page - Feature 1

Interactive timeline visualization of daily activities.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

from components.ui_components import (
    render_page_hero,
    render_kpi_card,
    render_athletic_header,
    render_non_medical_disclaimer,
)
from backend.services.activity_timeline import (
    get_daily_timeline,
    get_activity_sessions,
    filter_timeline_by_time_range,
    get_timeline_statistics,
    validate_timeline_records,
    get_time_range_presets,
)
from database.database import DatabaseManager


# Activity colors (sports-tech palette)
ACTIVITY_COLORS = {
    "Walking": "#AFFA00",
    "Sitting": "#CFED89",
    "Standing": "#FFFFFF",
    "Running": "#7FBF00",
    "Cycling": "#9FD500",
    "Other": "#B4FF1A",
}


def create_timeline_chart(sessions, time_range=(0, 24)):
    """Create interactive Plotly timeline chart."""
    if not sessions:
        fig = go.Figure()
        fig.add_annotation(
            text="No activity sessions for selected date and filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#9CA3AF"),
        )
        fig.update_layout(
            paper_bgcolor="#000000",
            plot_bgcolor="#1C1C1C",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig
    
    # Create figure
    fig = go.Figure()
    
    # Add session bars
    for i, session in enumerate(sessions):
        # Handle overnight sessions for display
        display_end = session.end_hour if session.end_hour <= 24 else 24
        
        hover_text = (
            f"<b>{session.activity_label}</b><br>"
            f"Start: {session.start_time}<br>"
            f"End: {session.end_time}<br>"
            f"Duration: {session.duration_minutes:.0f} min<br>"
        )
        
        if session.is_overnight:
            hover_text += "<i>Crosses midnight</i><br>"
        if session.overlaps_with:
            hover_text += f"<i>Overlaps with session(s) {', '.join(map(str, session.overlaps_with))}</i>"
        
        # Main bar
        fig.add_trace(go.Bar(
            x=[display_end - session.start_hour],
            y=[session.activity_label],
            base=[session.start_hour],
            orientation='h',
            name=session.activity_label,
            marker=dict(
                color=ACTIVITY_COLORS.get(session.activity_label, "#AFFA00"),
                line=dict(
                    color="#000000" if session.overlaps_with else "rgba(0,0,0,0)",
                    width=2 if session.overlaps_with else 0,
                )
            ),
            hovertemplate=hover_text + "<extra></extra>",
            showlegend=False,
        ))
        
        # Add text label for duration
        mid_point = (session.start_hour + display_end) / 2
        fig.add_annotation(
            x=mid_point,
            y=session.activity_label,
            text=f"{session.duration_minutes:.0f}m",
            showarrow=False,
            font=dict(size=10, color="#000000", weight=700),
            bgcolor="rgba(0,0,0,0)",
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="ACTIVITY TIMELINE",
            font=dict(size=18, color="#FFFFFF", family="Sora"),
            x=0.02,
        ),
        paper_bgcolor="#000000",
        plot_bgcolor="#1C1C1C",
        height=max(400, len(set(s.activity_label for s in sessions)) * 80),
        xaxis=dict(
            title="Time of Day (24-hour)",
            range=time_range,
            gridcolor="#2A2A2A",
            color="#9CA3AF",
            dtick=2,
            ticksuffix=":00",
        ),
        yaxis=dict(
            title="",
            gridcolor="#2A2A2A",
            color="#FFFFFF",
            categoryorder="total ascending",
        ),
        hoverlabel=dict(
            bgcolor="#1C1C1C",
            bordercolor="#AFFA00",
            font=dict(color="#FFFFFF", family="Inter"),
        ),
        barmode='overlay',
        bargap=0.3,
        margin=dict(l=120, r=40, t=60, b=60),
    )
    
    return fig


def render_timeline_page(db_manager: DatabaseManager) -> None:
    """Render the Smart Activity Timeline page."""
    render_page_hero(
        eyebrow="FEATURE 1 • SMART ANALYTICS",
        title="ACTIVITY TIMELINE",
        subtitle="Interactive visualization of your daily activity patterns. See when activities occurred, how long they lasted, and how your day unfolded.",
    )
    
    df = db_manager.get_all_activity_records()
    
    if df.empty:
        st.info("📭 No activity data available. Upload activity records to view timeline.")
        if st.button("📤 Go to Upload Activity", type="primary"):
            st.session_state["selected_page"] = "Upload Activity"
            st.rerun()
        render_non_medical_disclaimer()
        return
    
    # Get available dates
    available_dates = sorted(df["activity_date"].unique(), reverse=True)
    
    # Filters Section
    st.markdown("---")
    render_athletic_header("TIMELINE CONTROLS", "Select date, activities, and time range")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        selected_date = st.selectbox(
            "📅 Select Date",
            options=available_dates,
            help="Choose a date to view activity timeline",
        )
    
    with col2:
        all_activities = ["All"] + sorted(df["activity_label"].unique().tolist())
        activity_filter = st.selectbox(
            "🏃 Filter by Activity",
            options=all_activities,
            help="Filter timeline by specific activity",
        )
    
    with col3:
        time_presets = get_time_range_presets()
        preset_names = ["Full Day (24h)", "Morning (6-12)", "Afternoon (12-18)", 
                       "Evening (18-24)", "Night (0-6)", "Work Hours (9-17)", "Early Morning (5-9)"]
        preset_map = {
            "Full Day (24h)": "full_day",
            "Morning (6-12)": "morning",
            "Afternoon (12-18)": "afternoon",
            "Evening (18-24)": "evening",
            "Night (0-6)": "night",
            "Work Hours (9-17)": "work_hours",
            "Early Morning (5-9)": "early_morning",
        }
        
        time_range_option = st.selectbox(
            "🕐 Time Range",
            options=preset_names,
            help="Select time range to focus on",
        )
        
        preset_key = preset_map[time_range_option]
        time_range = (time_presets[preset_key]["start"], time_presets[preset_key]["end"])
    
    st.markdown("---")
    
    # Get timeline data
    filter_activity = None if activity_filter == "All" else activity_filter
    sessions = get_activity_sessions(df, selected_date, filter_activity)
    
    # Apply time range filter
    if sessions:
        sessions = filter_timeline_by_time_range(sessions, time_range[0], time_range[1])
    
    # Get statistics
    stats = get_timeline_statistics(df, selected_date)
    
    # Statistics Cards
    if stats:
        st.markdown("### 📊 DAILY OVERVIEW")
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
        
        with col1:
            render_kpi_card(
                "TOTAL DURATION",
                f"{stats.total_duration:.0f} MIN",
                f"{stats.total_duration/60:.1f} hours",
                "⏱️"
            )
        
        with col2:
            render_kpi_card(
                "SESSIONS",
                str(stats.session_count),
                "recorded intervals",
                "📋"
            )
        
        with col3:
            render_kpi_card(
                "TOP ACTIVITY",
                stats.most_frequent_activity.upper(),
                "by duration",
                "🏆"
            )
        
        with col4:
            render_kpi_card(
                "FIRST SESSION",
                stats.earliest_session,
                "earliest start",
                "🌅"
            )
        
        with col5:
            render_kpi_card(
                "LAST SESSION",
                stats.latest_session,
                "latest end",
                "🌙"
            )
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Timeline Visualization
    render_athletic_header("INTERACTIVE TIMELINE", f"Showing {len(sessions)} session(s) for {selected_date}")
    
    if sessions:
        fig = create_timeline_chart(sessions, time_range)
        st.plotly_chart(fig, use_container_width=True)
        
        # Activity Distribution
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            st.markdown("### 🎯 ACTIVITY DISTRIBUTION")
            
            if stats:
                dist_data = []
                for activity, duration in stats.activity_distribution.items():
                    percentage = (duration / stats.total_duration * 100) if stats.total_duration > 0 else 0
                    dist_data.append({
                        "Activity": activity,
                        "Duration (min)": f"{duration:.0f}",
                        "Duration (hrs)": f"{duration/60:.2f}",
                        "Percentage": f"{percentage:.1f}%",
                    })
                
                st.dataframe(dist_data, use_container_width=True, hide_index=True)
        
        with col_right:
            st.markdown("### ⚠️ DATA QUALITY")
            
            validation = validate_timeline_records(df, selected_date)
            
            if validation["valid"] and not validation["issues"]:
                st.success("✅ **All sessions validated successfully**")
                st.markdown(f"- Total sessions: **{validation['total_sessions']}**")
                st.markdown("- No overlaps detected")
                st.markdown("- No data quality issues")
            else:
                for issue in validation["issues"]:
                    if issue["severity"] == "warning":
                        st.warning(f"⚠️ **{issue['message']}**")
                    elif issue["severity"] == "info":
                        st.info(f"ℹ️ **{issue['message']}**")
                    else:
                        st.error(f"❌ **{issue['message']}**")
        
        # Session Details
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 📋 SESSION DETAILS")
        
        session_data = []
        for session in sessions:
            session_data.append({
                "ID": session.id,
                "Activity": session.activity_label,
                "Start": session.start_time,
                "End": session.end_time,
                "Duration": f"{session.duration_minutes:.0f} min",
                "Overnight": "Yes" if session.is_overnight else "No",
                "Issues": "Overlaps" if session.overlaps_with else "None",
            })
        
        st.dataframe(session_data, use_container_width=True, hide_index=True)
        
    else:
        st.markdown(
            """
            <div class="ap-card" style="text-align: center; padding: 3rem 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">📭</div>
                <div class="ap-section-title" style="margin-bottom: 0.75rem;">NO SESSIONS IN SELECTED RANGE</div>
                <p class="ap-section-desc">
                    Try selecting a different date, activity filter, or time range.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    render_non_medical_disclaimer()
