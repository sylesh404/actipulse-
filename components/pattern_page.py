"""Pattern Detection Page - AI-Powered Activity Intelligence."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.services.pattern_detection import (
    calculate_historical_baseline,
    detect_all_patterns_for_date,
    get_pattern_overview,
)
from components.ui_components import render_non_medical_disclaimer, render_page_hero
from database.database import DatabaseManager

if TYPE_CHECKING:
    from backend.services.pattern_detection import DetectedPattern

# Pattern severity colors
SEVERITY_COLORS = {
    "significant": "#FF4444",  # Red
    "moderate": "#FFAA00",  # Orange
    "minor": "#AFFA00",  # Neon green
}

SEVERITY_ICONS = {
    "significant": "🔴",
    "moderate": "🟠",
    "minor": "🟢",
}


def render_pattern_detection_page(db_manager: DatabaseManager) -> None:
    """Render the Pattern Detection page with AI-powered insights."""
    render_page_hero(
        eyebrow="ActiPulse AI • Advanced Intelligence",
        title="🔍 Intelligent Pattern Detection",
        subtitle=(
            "AI-powered statistical analysis detecting unusual activity patterns, "
            "significant deviations, and behavioral changes in your movement data."
        ),
    )

    # Date selector
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        analysis_date = st.date_input(
            "Analysis Date",
            value=date.today(),
            max_value=date.today(),
            help="Select a date to analyze for unusual patterns",
        )
    
    with col2:
        lookback_days = st.selectbox(
            "Historical Context",
            options=[7, 14, 30, 60, 90],
            index=2,
            format_func=lambda x: f"{x} days baseline",
            help="Number of historical days to use as baseline for comparison",
        )
    
    with col3:
        st.markdown("<div style='height: 1.9rem;'></div>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze Patterns", type="primary", use_container_width=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Perform analysis
    if analyze_btn or "last_pattern_analysis" in st.session_state:
        with st.spinner("🧠 Running AI pattern detection..."):
            patterns = detect_all_patterns_for_date(
                db_manager=db_manager,
                target_date=analysis_date.isoformat(),
                lookback_days=lookback_days,
            )
            
            st.session_state["last_pattern_analysis"] = {
                "date": analysis_date,
                "lookback": lookback_days,
                "patterns": patterns,
            }

    # Display results
    if "last_pattern_analysis" in st.session_state:
        analysis = st.session_state["last_pattern_analysis"]
        patterns = analysis["patterns"]
        
        if not patterns:
            st.info(
                f"✅ **No unusual patterns detected** on {analysis['date'].strftime('%B %d, %Y')}\n\n"
                f"All activities fall within normal ranges based on {analysis['lookback']}-day baseline."
            )
        else:
            # Summary cards
            _render_pattern_summary_cards(patterns)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Detailed pattern list
            _render_pattern_details(patterns)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # Visualization
            _render_pattern_visualization(patterns, analysis['date'])

    else:
        st.info("👆 Select a date and click **Analyze Patterns** to detect unusual activity patterns.")

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Pattern overview section
    _render_pattern_overview_section(db_manager)

    render_non_medical_disclaimer()


def _render_pattern_summary_cards(patterns: list[DetectedPattern]) -> None:
    """Render summary KPI cards for detected patterns."""
    severity_counts = {"significant": 0, "moderate": 0, "minor": 0}
    
    for pattern in patterns:
        severity_counts[pattern.severity] += 1
    
    total_patterns = len(patterns)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="ap-metric-card">
                <div class="ap-metric-label">TOTAL PATTERNS</div>
                <div class="ap-metric-value">{total_patterns}</div>
                <div class="ap-metric-delta">Detected anomalies</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="ap-metric-card">
                <div class="ap-metric-label">SIGNIFICANT</div>
                <div class="ap-metric-value" style="color: {SEVERITY_COLORS['significant']};">{severity_counts['significant']}</div>
                <div class="ap-metric-delta">&gt; 1.5 std deviation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="ap-metric-card">
                <div class="ap-metric-label">MODERATE</div>
                <div class="ap-metric-value" style="color: {SEVERITY_COLORS['moderate']};">{severity_counts['moderate']}</div>
                <div class="ap-metric-delta">&gt; 1.0 std deviation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="ap-metric-card">
                <div class="ap-metric-label">MINOR</div>
                <div class="ap-metric-value" style="color: {SEVERITY_COLORS['minor']};">{severity_counts['minor']}</div>
                <div class="ap-metric-delta">&gt; 30% change</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_pattern_details(patterns: list[DetectedPattern]) -> None:
    """Render detailed list of detected patterns."""
    st.markdown("### 📋 Detected Patterns")
    
    # Sort by severity (significant first)
    severity_order = {"significant": 0, "moderate": 1, "minor": 2}
    sorted_patterns = sorted(patterns, key=lambda p: severity_order[p.severity])
    
    for idx, pattern in enumerate(sorted_patterns, 1):
        severity_color = SEVERITY_COLORS[pattern.severity]
        severity_icon = SEVERITY_ICONS[pattern.severity]
        
        # Build the card
        with st.expander(
            f"{severity_icon} **{pattern.pattern_type.replace('_', ' ').title()}** – "
            f"{pattern.activity_label} – {pattern.severity.upper()}",
            expanded=(pattern.severity == "significant"),
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {pattern.description}")
                st.markdown(f"**Confidence:** {pattern.confidence:.0%}")
                
                if pattern.additional_context:
                    st.markdown("**Context:**")
                    for key, value in pattern.additional_context.items():
                        st.markdown(f"- {key.replace('_', ' ').title()}: {value}")
            
            with col2:
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #1C1C1C 0%, #000000 100%);
                        border-left: 4px solid {severity_color};
                        padding: 1rem;
                        border-radius: 0.5rem;
                    ">
                        <div style="font-size: 0.75rem; color: #9CA3AF; font-weight: 600; margin-bottom: 0.5rem;">
                            SEVERITY
                        </div>
                        <div style="font-size: 1.5rem; color: {severity_color}; font-weight: 700; margin-bottom: 0.25rem;">
                            {pattern.severity.upper()}
                        </div>
                        <div style="font-size: 0.875rem; color: #CFED89;">
                            {pattern.activity_label}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _render_pattern_visualization(patterns: list[DetectedPattern], analysis_date: date) -> None:
    """Render visualization of detected patterns."""
    st.markdown("### 📊 Pattern Visualization")
    
    # Group patterns by activity
    activity_patterns = {}
    for pattern in patterns:
        activity = pattern.activity_label
        if activity not in activity_patterns:
            activity_patterns[activity] = []
        activity_patterns[activity].append(pattern)
    
    # Create horizontal bar chart
    activities = []
    significant_counts = []
    moderate_counts = []
    minor_counts = []
    
    for activity, activity_pattern_list in sorted(activity_patterns.items()):
        activities.append(activity)
        
        severity_counts = {"significant": 0, "moderate": 0, "minor": 0}
        for p in activity_pattern_list:
            severity_counts[p.severity] += 1
        
        significant_counts.append(severity_counts["significant"])
        moderate_counts.append(severity_counts["moderate"])
        minor_counts.append(severity_counts["minor"])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=activities,
        x=significant_counts,
        name="Significant",
        orientation="h",
        marker=dict(color=SEVERITY_COLORS["significant"]),
    ))
    
    fig.add_trace(go.Bar(
        y=activities,
        x=moderate_counts,
        name="Moderate",
        orientation="h",
        marker=dict(color=SEVERITY_COLORS["moderate"]),
    ))
    
    fig.add_trace(go.Bar(
        y=activities,
        x=minor_counts,
        name="Minor",
        orientation="h",
        marker=dict(color=SEVERITY_COLORS["minor"]),
    ))
    
    fig.update_layout(
        barmode="stack",
        title=f"Pattern Distribution by Activity – {analysis_date.strftime('%B %d, %Y')}",
        xaxis_title="Number of Patterns Detected",
        yaxis_title="Activity Type",
        height=max(300, len(activities) * 60),
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="#FFFFFF", family="Inter, sans-serif"),
        title_font=dict(size=16, color="#AFFA00", weight=600),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(28, 28, 28, 0.8)",
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        xaxis=dict(
            gridcolor="#1C1C1C",
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="#1C1C1C",
            showgrid=False,
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_pattern_overview_section(db_manager: DatabaseManager) -> None:
    """Render the pattern overview section showing trends."""
    st.markdown("### 📈 Pattern Overview")
    
    # Get pattern overview for last 30 days
    overview = get_pattern_overview(db_manager, days=30)
    
    if not overview:
        st.info("No patterns detected in the last 30 days. All activities are within normal ranges.")
        return
    
    # Convert to DataFrame for visualization
    overview_data = []
    for date_str, date_patterns in overview.items():
        for pattern in date_patterns:
            overview_data.append({
                "date": date_str,
                "activity": pattern.activity_label,
                "type": pattern.pattern_type,
                "severity": pattern.severity,
                "confidence": pattern.confidence,
            })
    
    if not overview_data:
        st.info("No patterns detected in the last 30 days.")
        return
    
    df = pd.DataFrame(overview_data)
    
    # Daily pattern count chart
    daily_counts = df.groupby("date").size().reset_index(name="count")
    daily_counts["date"] = pd.to_datetime(daily_counts["date"])
    daily_counts = daily_counts.sort_values("date")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_counts["date"],
        y=daily_counts["count"],
        mode="lines+markers",
        line=dict(color="#AFFA00", width=3),
        marker=dict(color="#AFFA00", size=8),
        fill="tozeroy",
        fillcolor="rgba(175, 250, 0, 0.1)",
        name="Patterns Detected",
    ))
    
    fig.update_layout(
        title="Daily Pattern Detection Trend (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Number of Patterns",
        height=350,
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="#FFFFFF", family="Inter, sans-serif"),
        title_font=dict(size=16, color="#AFFA00", weight=600),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(
            gridcolor="#1C1C1C",
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="#1C1C1C",
            showgrid=True,
            zeroline=True,
            zerolinecolor="#1C1C1C",
        ),
        hovermode="x unified",
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Pattern type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        type_counts = df["type"].value_counts()
        
        fig_type = go.Figure(data=[go.Bar(
            x=type_counts.values,
            y=[t.replace("_", " ").title() for t in type_counts.index],
            orientation="h",
            marker=dict(
                color="#AFFA00",
                line=dict(color="#CFED89", width=1),
            ),
        )])
        
        fig_type.update_layout(
            title="Pattern Types (Last 30 Days)",
            xaxis_title="Count",
            height=300,
            plot_bgcolor="#000000",
            paper_bgcolor="#000000",
            font=dict(color="#FFFFFF", family="Inter, sans-serif"),
            title_font=dict(size=14, color="#AFFA00", weight=600),
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(gridcolor="#1C1C1C", showgrid=True),
            yaxis=dict(gridcolor="#1C1C1C", showgrid=False),
        )
        
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        severity_counts = df["severity"].value_counts()
        
        colors_map = {
            "significant": SEVERITY_COLORS["significant"],
            "moderate": SEVERITY_COLORS["moderate"],
            "minor": SEVERITY_COLORS["minor"],
        }
        
        severity_colors = [colors_map.get(s, "#AFFA00") for s in severity_counts.index]
        
        fig_severity = go.Figure(data=[go.Pie(
            labels=[s.upper() for s in severity_counts.index],
            values=severity_counts.values,
            marker=dict(colors=severity_colors, line=dict(color="#000000", width=2)),
            textfont=dict(color="#FFFFFF", size=14),
            hole=0.4,
        )])
        
        fig_severity.update_layout(
            title="Severity Distribution (Last 30 Days)",
            height=300,
            plot_bgcolor="#000000",
            paper_bgcolor="#000000",
            font=dict(color="#FFFFFF", family="Inter, sans-serif"),
            title_font=dict(size=14, color="#AFFA00", weight=600),
            showlegend=True,
            legend=dict(bgcolor="rgba(28, 28, 28, 0.8)"),
            margin=dict(l=20, r=20, t=60, b=20),
        )
        
        st.plotly_chart(fig_severity, use_container_width=True)
