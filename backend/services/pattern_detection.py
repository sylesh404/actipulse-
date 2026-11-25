"""Intelligent Unusual Pattern Detection Service - Feature 2

Statistical analysis engine for detecting unusual activity patterns.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Configurable thresholds
SIGNIFICANT_DEVIATION_THRESHOLD = 1.5  # Standard deviations
MODERATE_DEVIATION_THRESHOLD = 1.0
MINIMUM_HISTORICAL_SAMPLES = 5  # Minimum days needed for baseline
PERCENTAGE_CHANGE_THRESHOLD = 30  # Percentage


@dataclass
class DetectedPattern:
    """Represents a detected unusual activity pattern."""
    pattern_id: str
    pattern_type: str
    activity: str
    date: str
    current_value: float
    baseline_value: float
    absolute_difference: float
    percentage_difference: Optional[float]
    severity: str  # "minor", "moderate", "significant"
    detection_method: str
    explanation: str
    statistical_details: Dict[str, Any]
    supporting_records: List[int]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "activity": self.activity,
            "date": self.date,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "absolute_difference": self.absolute_difference,
            "percentage_difference": self.percentage_difference,
            "severity": self.severity,
            "detection_method": self.detection_method,
            "explanation": self.explanation,
            "statistical_details": self.statistical_details,
            "supporting_records": self.supporting_records,
        }


@dataclass
class HistoricalBaseline:
    """Statistical baseline from historical data."""
    activity: str
    metric: str
    median: float
    mean: float
    std_dev: float
    q1: float
    q3: float
    iqr: float
    min_value: float
    max_value: float
    sample_size: int
    date_range: Tuple[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity": self.activity,
            "metric": self.metric,
            "median": self.median,
            "mean": self.mean,
            "std_dev": self.std_dev,
            "q1": self.q1,
            "q3": self.q3,
            "iqr": self.iqr,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "sample_size": self.sample_size,
            "date_range": list(self.date_range),
        }


def calculate_historical_baseline(
    df: pd.DataFrame,
    activity: str,
    metric: str = "duration",
    exclude_date: Optional[str] = None,
    days_back: int = 30,
) -> Optional[HistoricalBaseline]:
    """Calculate statistical baseline from historical data.
    
    Args:
        df: Activity records DataFrame
        activity: Activity label
        metric: Metric to analyze ('duration', 'session_count', etc.)
        exclude_date: Date to exclude (typically current analysis date)
        days_back: Number of days to look back
        
    Returns:
        HistoricalBaseline or None if insufficient data
    """
    if df.empty:
        return None
    
    # Filter by activity
    activity_df = df[df["activity_label"] == activity].copy()
    
    if activity_df.empty:
        return None
    
    # Exclude specific date if provided
    if exclude_date:
        activity_df = activity_df[activity_df["activity_date"] != exclude_date]
    
    # Filter by date range
    if days_back:
        latest_date = activity_df["activity_date"].max()
        cutoff_date = (pd.to_datetime(latest_date) - timedelta(days=days_back)).strftime("%Y-%m-%d")
        activity_df = activity_df[activity_df["activity_date"] >= cutoff_date]
    
    # Group by date and calculate daily values
    if metric == "duration":
        daily_values = activity_df.groupby("activity_date")["duration_minutes"].sum()
    elif metric == "session_count":
        daily_values = activity_df.groupby("activity_date").size()
    elif metric == "avg_session_duration":
        daily_values = activity_df.groupby("activity_date")["duration_minutes"].mean()
    else:
        logger.warning(f"Unknown metric: {metric}")
        return None
    
    # Need minimum samples
    if len(daily_values) < MINIMUM_HISTORICAL_SAMPLES:
        logger.info(f"Insufficient historical data: {len(daily_values)} days < {MINIMUM_HISTORICAL_SAMPLES}")
        return None
    
    # Calculate statistics
    values = daily_values.values
    
    return HistoricalBaseline(
        activity=activity,
        metric=metric,
        median=float(np.median(values)),
        mean=float(np.mean(values)),
        std_dev=float(np.std(values)),
        q1=float(np.percentile(values, 25)),
        q3=float(np.percentile(values, 75)),
        iqr=float(np.percentile(values, 75) - np.percentile(values, 25)),
        min_value=float(np.min(values)),
        max_value=float(np.max(values)),
        sample_size=len(values),
        date_range=(daily_values.index.min(), daily_values.index.max()),
    )


def detect_unusual_duration(
    df: pd.DataFrame,
    activity: str,
    target_date: str,
    baseline: HistoricalBaseline,
) -> Optional[DetectedPattern]:
    """Detect unusual duration patterns.
    
    Args:
        df: Activity records DataFrame
        activity: Activity label
        target_date: Date to analyze
        baseline: Historical baseline
        
    Returns:
        DetectedPattern or None
    """
    # Get current day's duration
    day_df = df[(df["activity_date"] == target_date) & (df["activity_label"] == activity)]
    
    if day_df.empty:
        current_duration = 0.0
    else:
        current_duration = day_df["duration_minutes"].sum()
    
    # Calculate deviation
    absolute_diff = current_duration - baseline.median
    
    # Avoid division by zero
    if baseline.median > 0:
        percentage_diff = (absolute_diff / baseline.median) * 100
    else:
        percentage_diff = None
    
    # Calculate Z-score using median and IQR (more robust than mean/std)
    if baseline.iqr > 0:
        z_score = (current_duration - baseline.median) / (baseline.iqr / 1.349)  # IQR to std conversion
    else:
        z_score = 0.0
    
    # Determine severity
    if abs(z_score) >= SIGNIFICANT_DEVIATION_THRESHOLD:
        severity = "significant"
    elif abs(z_score) >= MODERATE_DEVIATION_THRESHOLD:
        severity = "moderate"
    elif percentage_diff and abs(percentage_diff) >= PERCENTAGE_CHANGE_THRESHOLD:
        severity = "minor"
    else:
        return None  # Not unusual enough
    
    # Generate explanation
    direction = "increase" if absolute_diff > 0 else "decrease"
    explanation = (
        f"Recorded {activity.lower()} duration on {target_date} was {current_duration:.0f} minutes, "
        f"compared with historical median of {baseline.median:.0f} minutes. "
        f"This represents a {abs(absolute_diff):.0f}-minute {direction}"
    )
    
    if percentage_diff:
        explanation += f" ({abs(percentage_diff):.1f}%)"
    
    explanation += f" in recorded duration."
    
    pattern_id = f"duration_{activity}_{target_date}".replace(" ", "_").lower()
    
    return DetectedPattern(
        pattern_id=pattern_id,
        pattern_type="unusual_duration",
        activity=activity,
        date=target_date,
        current_value=current_duration,
        baseline_value=baseline.median,
        absolute_difference=absolute_diff,
        percentage_difference=percentage_diff,
        severity=severity,
        detection_method="median_deviation_iqr",
        explanation=explanation,
        statistical_details={
            "z_score": z_score,
            "baseline_mean": baseline.mean,
            "baseline_std": baseline.std_dev,
            "baseline_iqr": baseline.iqr,
            "sample_size": baseline.sample_size,
        },
        supporting_records=day_df["id"].tolist() if not day_df.empty else [],
    )


def detect_session_duration_changes(
    df: pd.DataFrame,
    activity: str,
    target_date: str,
) -> Optional[DetectedPattern]:
    """Detect unusual session duration patterns.
    
    Args:
        df: Activity records DataFrame
        activity: Activity label
        target_date: Date to analyze
        
    Returns:
        DetectedPattern or None
    """
    # Get baseline for average session duration
    baseline = calculate_historical_baseline(
        df, activity, metric="avg_session_duration", exclude_date=target_date
    )
    
    if not baseline:
        return None
    
    # Get current day's average session duration
    day_df = df[(df["activity_date"] == target_date) & (df["activity_label"] == activity)]
    
    if day_df.empty:
        return None
    
    current_avg = day_df["duration_minutes"].mean()
    
    # Calculate deviation
    absolute_diff = current_avg - baseline.median
    
    if baseline.median > 0:
        percentage_diff = (absolute_diff / baseline.median) * 100
    else:
        percentage_diff = None
    
    # Only report significant changes
    if percentage_diff and abs(percentage_diff) >= PERCENTAGE_CHANGE_THRESHOLD:
        direction = "longer" if absolute_diff > 0 else "shorter"
        
        explanation = (
            f"Average {activity.lower()} session duration on {target_date} was "
            f"{current_avg:.0f} minutes, compared with historical median of "
            f"{baseline.median:.0f} minutes. Sessions were {abs(percentage_diff):.1f}% {direction} "
            f"than typical."
        )
        
        pattern_id = f"session_duration_{activity}_{target_date}".replace(" ", "_").lower()
        
        return DetectedPattern(
            pattern_id=pattern_id,
            pattern_type="unusual_session_duration",
            activity=activity,
            date=target_date,
            current_value=current_avg,
            baseline_value=baseline.median,
            absolute_difference=absolute_diff,
            percentage_difference=percentage_diff,
            severity="moderate" if abs(percentage_diff) >= 50 else "minor",
            detection_method="median_comparison",
            explanation=explanation,
            statistical_details={
                "session_count": len(day_df),
                "baseline_sample_size": baseline.sample_size,
            },
            supporting_records=day_df["id"].tolist(),
        )
    
    return None


def detect_activity_distribution_changes(
    df: pd.DataFrame,
    target_date: str,
) -> List[DetectedPattern]:
    """Detect major changes in activity distribution.
    
    Args:
        df: Activity records DataFrame
        target_date: Date to analyze
        
    Returns:
        List of detected patterns
    """
    patterns = []
    
    # Get current day's distribution
    day_df = df[df["activity_date"] == target_date]
    
    if day_df.empty:
        return patterns
    
    current_dist = day_df.groupby("activity_label")["duration_minutes"].sum()
    total_duration = current_dist.sum()
    
    if total_duration == 0:
        return patterns
    
    current_percentages = (current_dist / total_duration * 100).to_dict()
    
    # Get historical distribution (last 30 days excluding target)
    historical_df = df[df["activity_date"] != target_date].copy()
    
    if not historical_df.empty:
        # Filter to last 30 days
        latest = historical_df["activity_date"].max()
        cutoff = (pd.to_datetime(latest) - timedelta(days=30)).strftime("%Y-%m-%d")
        historical_df = historical_df[historical_df["activity_date"] >= cutoff]
        
        if len(historical_df["activity_date"].unique()) >= MINIMUM_HISTORICAL_SAMPLES:
            hist_dist = historical_df.groupby("activity_label")["duration_minutes"].sum()
            hist_total = hist_dist.sum()
            
            if hist_total > 0:
                hist_percentages = (hist_dist / hist_total * 100).to_dict()
                
                # Compare distributions
                for activity in current_percentages:
                    current_pct = current_percentages[activity]
                    hist_pct = hist_percentages.get(activity, 0)
                    
                    pct_change = current_pct - hist_pct
                    
                    # Significant distribution change
                    if abs(pct_change) >= 15:  # 15% points
                        direction = "increased" if pct_change > 0 else "decreased"
                        
                        explanation = (
                            f"On {target_date}, {activity.lower()} accounted for "
                            f"{current_pct:.1f}% of recorded activity, compared with "
                            f"historical average of {hist_pct:.1f}%. This represents a "
                            f"{abs(pct_change):.1f} percentage point {direction} in activity distribution."
                        )
                        
                        pattern = DetectedPattern(
                            pattern_id=f"distribution_{activity}_{target_date}".replace(" ", "_").lower(),
                            pattern_type="distribution_change",
                            activity=activity,
                            date=target_date,
                            current_value=current_pct,
                            baseline_value=hist_pct,
                            absolute_difference=pct_change,
                            percentage_difference=None,  # Not applicable for percentages
                            severity="significant" if abs(pct_change) >= 25 else "moderate",
                            detection_method="percentage_point_comparison",
                            explanation=explanation,
                            statistical_details={
                                "current_duration": current_dist[activity],
                                "historical_sample_days": len(historical_df["activity_date"].unique()),
                            },
                            supporting_records=day_df[day_df["activity_label"] == activity]["id"].tolist(),
                        )
                        patterns.append(pattern)
    
    return patterns


def detect_all_patterns_for_date(
    df: pd.DataFrame,
    target_date: str,
    activities: Optional[List[str]] = None,
) -> List[DetectedPattern]:
    """Detect all unusual patterns for a specific date.
    
    Args:
        df: Activity records DataFrame
        target_date: Date to analyze
        activities: Optional list of activities to analyze (default: all)
        
    Returns:
        List of all detected patterns
    """
    all_patterns = []
    
    if activities is None:
        activities = df["activity_label"].unique().tolist()
    
    # Duration patterns
    for activity in activities:
        baseline = calculate_historical_baseline(df, activity, exclude_date=target_date)
        
        if baseline:
            pattern = detect_unusual_duration(df, activity, target_date, baseline)
            if pattern:
                all_patterns.append(pattern)
            
            # Session duration patterns
            session_pattern = detect_session_duration_changes(df, activity, target_date)
            if session_pattern:
                all_patterns.append(session_pattern)
    
    # Distribution changes
    dist_patterns = detect_activity_distribution_changes(df, target_date)
    all_patterns.extend(dist_patterns)
    
    return all_patterns


def get_pattern_overview(df: pd.DataFrame, days: int = 7) -> Dict[str, Any]:
    """Get overview of unusual patterns over recent period.
    
    Args:
        df: Activity records DataFrame
        days: Number of recent days to analyze
        
    Returns:
        Pattern overview summary
    """
    if df.empty:
        return {
            "has_patterns": False,
            "message": "No activity data available for pattern detection.",
        }
    
    # Get recent dates
    latest_date = df["activity_date"].max()
    start_date = (pd.to_datetime(latest_date) - timedelta(days=days-1)).strftime("%Y-%m-%d")
    
    recent_dates = pd.date_range(start=start_date, end=latest_date, freq="D")
    recent_dates = [d.strftime("%Y-%m-%d") for d in recent_dates]
    
    all_patterns = []
    dates_with_data = []
    
    for date in recent_dates:
        if date in df["activity_date"].values:
            dates_with_data.append(date)
            patterns = detect_all_patterns_for_date(df, date)
            all_patterns.extend(patterns)
    
    # Group by severity
    severity_counts = {
        "significant": len([p for p in all_patterns if p.severity == "significant"]),
        "moderate": len([p for p in all_patterns if p.severity == "moderate"]),
        "minor": len([p for p in all_patterns if p.severity == "minor"]),
    }
    
    # Group by pattern type
    type_counts = {}
    for pattern in all_patterns:
        type_counts[pattern.pattern_type] = type_counts.get(pattern.pattern_type, 0) + 1
    
    return {
        "has_patterns": len(all_patterns) > 0,
        "total_patterns": len(all_patterns),
        "date_range": {"start": start_date, "end": latest_date},
        "dates_with_data": len(dates_with_data),
        "dates_missing_data": len(recent_dates) - len(dates_with_data),
        "severity_distribution": severity_counts,
        "pattern_types": type_counts,
        "patterns": [p.to_dict() for p in all_patterns],
    }
