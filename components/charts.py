"""Plotly chart styling with premium sports-tech athletic color scheme."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ACTIPULSE ATHLETIC COLOR PALETTE
ACTIPULSE_COLORWAY = [
    "#AFFA00",  # Fit Green Neon (Primary)
    "#CFED89",  # Fit Green Light
    "#7FBF00",  # Athletic Green
    "#9FD500",  # Vibrant Green
    "#6B9B00",  # Deep Green
    "#B4FF1A",  # Bright Neon
    "#8FCC33",  # Sport Green
    "#A3E635",  # Lime Green
]


def apply_actipulse_chart_theme(fig: go.Figure, title: str | None = None) -> go.Figure:
    """Apply premium athletic sports-tech styling to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(
                size=18,
                color="#FFFFFF",
                family="Sora, Inter, sans-serif",
                weight=700
            ),
            x=0.02,
        ) if title else None,
        colorway=ACTIPULSE_COLORWAY,
        paper_bgcolor="#000000",
        plot_bgcolor="#1C1C1C",
        font=dict(family="Inter, sans-serif", color="#FFFFFF", size=13, weight=500),
        margin=dict(l=40, r=40, t=60 if title else 30, b=40),
        xaxis=dict(
            gridcolor="#2A2A2A",
            zerolinecolor="#333333",
            color="#9CA3AF",
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            gridcolor="#2A2A2A",
            zerolinecolor="#333333",
            color="#9CA3AF",
            showgrid=True,
            gridwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#1C1C1C",
            bordercolor="#AFFA00",
            font=dict(color="#FFFFFF", family="Inter, sans-serif", size=12),
        ),
        legend=dict(
            bgcolor="rgba(28, 28, 28, 0.9)",
            bordercolor="#333333",
            borderwidth=1,
            font=dict(color="#FFFFFF", size=12),
        ),
    )
    return fig


def build_empty_state_figure(message: str = "Activity visualizations will appear here once data is loaded.") -> go.Figure:
    """Create a clean empty-state Plotly figure for foundation placeholders."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=13, color="#64748B"),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_actipulse_chart_theme(fig)


def build_activity_distribution_donut(distribution_data: list[dict]) -> go.Figure:
    """Create interactive donut chart for activity distribution.
    
    Args:
        distribution_data: List of dicts with 'activity_label', 'total_minutes', 'percentage'
        
    Returns:
        Styled Plotly donut chart
    """
    if not distribution_data:
        return build_empty_state_figure("No activity data to display")
    
    labels = [item["activity_label"] for item in distribution_data]
    values = [item["total_minutes"] for item in distribution_data]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo="label+percent",
        textposition="auto",
        hovertemplate="<b>%{label}</b><br>Duration: %{value:.1f} min<br>Percentage: %{percent}<extra></extra>",
    )])
    
    return apply_actipulse_chart_theme(fig, title="Activity Distribution")


def build_activity_duration_bar(distribution_data: list[dict]) -> go.Figure:
    """Create bar chart showing total duration by activity type.
    
    Args:
        distribution_data: List of dicts with 'activity_label', 'total_minutes'
        
    Returns:
        Styled Plotly bar chart
    """
    if not distribution_data:
        return build_empty_state_figure("No activity data to display")
    
    labels = [item["activity_label"] for item in distribution_data]
    values = [item["total_minutes"] for item in distribution_data]
    
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        text=[f"{v:.0f} min" for v in values],
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Duration: %{y:.1f} minutes<extra></extra>",
    )])
    
    fig.update_layout(
        xaxis_title="Activity Type",
        yaxis_title="Total Duration (minutes)",
        showlegend=False,
    )
    
    return apply_actipulse_chart_theme(fig, title="Total Duration by Activity")


def build_time_period_bar(time_period_data: dict[str, float]) -> go.Figure:
    """Create bar chart showing activity duration by time of day.
    
    Args:
        time_period_data: Dict mapping time period names to total minutes
        
    Returns:
        Styled Plotly bar chart
    """
    if not time_period_data or all(v == 0 for v in time_period_data.values()):
        return build_empty_state_figure("No time period data to display")
    
    # Sort periods chronologically
    period_order = ["Early Morning", "Morning", "Afternoon", "Evening", "Night"]
    periods = [p for p in period_order if p in time_period_data]
    values = [time_period_data[p] for p in periods]
    
    fig = go.Figure(data=[go.Bar(
        x=periods,
        y=values,
        text=[f"{v:.0f} min" for v in values],
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Duration: %{y:.1f} minutes<extra></extra>",
        marker=dict(color=ACTIPULSE_COLORWAY[1]),
    )])
    
    fig.update_layout(
        xaxis_title="Time Period",
        yaxis_title="Total Duration (minutes)",
        showlegend=False,
    )
    
    return apply_actipulse_chart_theme(fig, title="Activity by Time of Day")


def build_daily_activity_line(daily_data: pd.DataFrame) -> go.Figure:
    """Create line chart showing activity trends over time.
    
    Args:
        daily_data: DataFrame with 'activity_date' and 'total_minutes' columns
        
    Returns:
        Styled Plotly line chart
    """
    if daily_data is None or daily_data.empty:
        return build_empty_state_figure("No daily trend data to display")
    
    fig = go.Figure(data=[go.Scatter(
        x=daily_data["activity_date"],
        y=daily_data["total_minutes"],
        mode="lines+markers",
        line=dict(color=ACTIPULSE_COLORWAY[0], width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>Total: %{y:.1f} minutes<extra></extra>",
    )])
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Duration (minutes)",
        showlegend=False,
    )
    
    return apply_actipulse_chart_theme(fig, title="Daily Activity Trend")


def build_activity_comparison_bar(comparison_data: dict[str, dict[str, float]]) -> go.Figure:
    """Create grouped bar chart comparing activities across categories.
    
    Args:
        comparison_data: Nested dict with categories and their activity breakdowns
        
    Returns:
        Styled Plotly grouped bar chart
    """
    if not comparison_data:
        return build_empty_state_figure("No comparison data to display")
    
    # Extract all unique activities
    all_activities = set()
    for category_data in comparison_data.values():
        all_activities.update(category_data.keys())
    
    activities = sorted(all_activities)
    categories = list(comparison_data.keys())
    
    fig = go.Figure()
    
    for activity in activities:
        values = [comparison_data[cat].get(activity, 0) for cat in categories]
        fig.add_trace(go.Bar(
            name=activity,
            x=categories,
            y=values,
            text=[f"{v:.0f}" if v > 0 else "" for v in values],
            textposition="auto",
        ))
    
    fig.update_layout(
        barmode="group",
        xaxis_title="Category",
        yaxis_title="Duration (minutes)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    
    return apply_actipulse_chart_theme(fig, title="Activity Comparison")


def build_day_comparison_chart(
    activities: list[str],
    previous_values: list[float],
    current_values: list[float],
    previous_label: str = "Previous",
    current_label: str = "Current",
) -> go.Figure:
    """Create grouped bar chart comparing two days of activities.
    
    Args:
        activities: List of activity labels
        previous_values: Durations for previous/baseline day
        current_values: Durations for current/target day
        previous_label: Label for previous data series
        current_label: Label for current data series
        
    Returns:
        Styled Plotly grouped bar chart
    """
    if not activities:
        return build_empty_state_figure("No activities to compare")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=previous_label,
        x=activities,
        y=previous_values,
        text=[f"{v:.0f}" for v in previous_values],
        textposition="auto",
        marker=dict(color=ACTIPULSE_COLORWAY[2]),
    ))
    
    fig.add_trace(go.Bar(
        name=current_label,
        x=activities,
        y=current_values,
        text=[f"{v:.0f}" for v in current_values],
        textposition="auto",
        marker=dict(color=ACTIPULSE_COLORWAY[0]),
    ))
    
    fig.update_layout(
        barmode="group",
        xaxis_title="Activity",
        yaxis_title="Duration (minutes)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    
    return apply_actipulse_chart_theme(fig, title="Day-to-Day Activity Comparison")


def build_weekly_trend_line(
    dates: list[str],
    daily_totals: list[float],
    activity_name: str = "Total Activity",
) -> go.Figure:
    """Create line chart showing weekly activity trend.
    
    Args:
        dates: List of date strings
        daily_totals: List of daily duration values
        activity_name: Name of the activity being charted
        
    Returns:
        Styled Plotly line chart
    """
    if not dates or not daily_totals:
        return build_empty_state_figure("No weekly data to display")
    
    fig = go.Figure(data=[go.Scatter(
        x=dates,
        y=daily_totals,
        mode="lines+markers",
        line=dict(color=ACTIPULSE_COLORWAY[1], width=3),
        marker=dict(size=10),
        hovertemplate="<b>%{x}</b><br>Duration: %{y:.0f} minutes<extra></extra>",
    )])
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Duration (minutes)",
        showlegend=False,
    )
    
    return apply_actipulse_chart_theme(fig, title=f"{activity_name} - Weekly Trend")


def build_weekly_stacked_bar(
    dates: list[str],
    walking_values: list[float],
    sitting_values: list[float],
    standing_values: list[float],
    other_values: list[float] | None = None,
) -> go.Figure:
    """Create stacked bar chart showing weekly activity distribution.
    
    Args:
        dates: List of date strings
        walking_values: Daily walking durations
        sitting_values: Daily sitting durations
        standing_values: Daily standing durations
        other_values: Optional daily other activity durations
        
    Returns:
        Styled Plotly stacked bar chart
    """
    if not dates:
        return build_empty_state_figure("No weekly data to display")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name="Walking",
        x=dates,
        y=walking_values,
        marker=dict(color=ACTIPULSE_COLORWAY[0]),
    ))
    
    fig.add_trace(go.Bar(
        name="Sitting",
        x=dates,
        y=sitting_values,
        marker=dict(color=ACTIPULSE_COLORWAY[1]),
    ))
    
    fig.add_trace(go.Bar(
        name="Standing",
        x=dates,
        y=standing_values,
        marker=dict(color=ACTIPULSE_COLORWAY[3]),
    ))
    
    if other_values:
        fig.add_trace(go.Bar(
            name="Other",
            x=dates,
            y=other_values,
            marker=dict(color=ACTIPULSE_COLORWAY[4]),
        ))
    
    fig.update_layout(
        barmode="stack",
        xaxis_title="Date",
        yaxis_title="Duration (minutes)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    
    return apply_actipulse_chart_theme(fig, title="Weekly Activity Distribution")
