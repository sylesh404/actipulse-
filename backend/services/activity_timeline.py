"""Smart Activity Timeline Service - Feature 1

Provides interactive timeline visualization and analysis of recorded activities.
"""

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimelineSession:
    """Represents a single activity session on the timeline."""
    id: int
    activity_label: str
    start_time: str
    end_time: str
    duration_minutes: float
    start_hour: float  # For visualization (0-24)
    end_hour: float
    is_overnight: bool = False
    overlaps_with: List[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "activity_label": self.activity_label,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.duration_minutes,
            "start_hour": self.start_hour,
            "end_hour": self.end_hour,
            "is_overnight": self.is_overnight,
            "overlaps_with": self.overlaps_with or [],
        }


@dataclass
class TimelineStatistics:
    """Daily timeline statistics."""
    date: str
    total_duration: float
    session_count: int
    earliest_session: str
    latest_session: str
    most_frequent_activity: str
    activity_distribution: Dict[str, float]
    has_overnight_sessions: bool
    has_overlapping_sessions: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "total_duration": self.total_duration,
            "session_count": self.session_count,
            "earliest_session": self.earliest_session,
            "latest_session": self.latest_session,
            "most_frequent_activity": self.most_frequent_activity,
            "activity_distribution": self.activity_distribution,
            "has_overnight_sessions": self.has_overnight_sessions,
            "has_overlapping_sessions": self.has_overlapping_sessions,
        }


def parse_time_to_hours(time_str: str) -> float:
    """Convert HH:MM:SS time string to decimal hours (0-24)."""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
        return time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600
    except ValueError:
        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            return time_obj.hour + time_obj.minute / 60
        except ValueError:
            logger.warning(f"Invalid time format: {time_str}")
            return 0.0


def detect_overnight_session(start_time: str, end_time: str) -> bool:
    """Detect if session crosses midnight."""
    start_hours = parse_time_to_hours(start_time)
    end_hours = parse_time_to_hours(end_time)
    return end_hours < start_hours


def detect_overlapping_sessions(sessions: List[TimelineSession]) -> None:
    """Detect and mark overlapping sessions."""
    for i, session_a in enumerate(sessions):
        for j, session_b in enumerate(sessions[i + 1:], start=i + 1):
            # Check for overlap
            if not session_a.is_overnight and not session_b.is_overnight:
                # Simple overlap check
                if (session_a.start_hour < session_b.end_hour and 
                    session_a.end_hour > session_b.start_hour):
                    if session_a.overlaps_with is None:
                        session_a.overlaps_with = []
                    if session_b.overlaps_with is None:
                        session_b.overlaps_with = []
                    session_a.overlaps_with.append(session_b.id)
                    session_b.overlaps_with.append(session_a.id)


def get_daily_timeline(df: pd.DataFrame, activity_date: str) -> List[TimelineSession]:
    """Get timeline sessions for a specific date.
    
    Args:
        df: DataFrame with activity records
        activity_date: Date string (YYYY-MM-DD)
        
    Returns:
        List of TimelineSession objects
    """
    if df.empty:
        return []
    
    # Filter by date
    daily_df = df[df["activity_date"] == activity_date].copy()
    
    if daily_df.empty:
        return []
    
    sessions = []
    for idx, row in daily_df.iterrows():
        start_hours = parse_time_to_hours(row["start_time"])
        end_hours = parse_time_to_hours(row["end_time"])
        is_overnight = detect_overnight_session(row["start_time"], row["end_time"])
        
        # Adjust end_hours for overnight sessions
        if is_overnight:
            end_hours += 24
        
        session = TimelineSession(
            id=row["id"],
            activity_label=row["activity_label"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration_minutes=row["duration_minutes"],
            start_hour=start_hours,
            end_hour=end_hours,
            is_overnight=is_overnight,
        )
        sessions.append(session)
    
    # Detect overlaps
    detect_overlapping_sessions(sessions)
    
    # Sort by start time
    sessions.sort(key=lambda s: s.start_hour)
    
    return sessions


def get_activity_sessions(
    df: pd.DataFrame,
    activity_date: str,
    activity_filter: Optional[str] = None,
) -> List[TimelineSession]:
    """Get filtered activity sessions.
    
    Args:
        df: DataFrame with activity records
        activity_date: Date string
        activity_filter: Optional activity label to filter by
        
    Returns:
        Filtered list of TimelineSession objects
    """
    sessions = get_daily_timeline(df, activity_date)
    
    if activity_filter and activity_filter.lower() != "all":
        sessions = [s for s in sessions if s.activity_label == activity_filter]
    
    return sessions


def filter_timeline_by_time_range(
    sessions: List[TimelineSession],
    start_hour: float,
    end_hour: float,
) -> List[TimelineSession]:
    """Filter timeline sessions by time range.
    
    Args:
        sessions: List of timeline sessions
        start_hour: Start hour (0-24)
        end_hour: End hour (0-24)
        
    Returns:
        Filtered sessions that overlap with the time range
    """
    filtered = []
    for session in sessions:
        # Check if session overlaps with time range
        if session.end_hour > start_hour and session.start_hour < end_hour:
            filtered.append(session)
    
    return filtered


def calculate_session_duration(start_time: str, end_time: str) -> float:
    """Calculate session duration in minutes.
    
    Args:
        start_time: Start time (HH:MM:SS)
        end_time: End time (HH:MM:SS)
        
    Returns:
        Duration in minutes
    """
    start_hours = parse_time_to_hours(start_time)
    end_hours = parse_time_to_hours(end_time)
    
    if end_hours < start_hours:
        # Overnight session
        duration_hours = (24 - start_hours) + end_hours
    else:
        duration_hours = end_hours - start_hours
    
    return duration_hours * 60


def get_timeline_statistics(df: pd.DataFrame, activity_date: str) -> Optional[TimelineStatistics]:
    """Calculate comprehensive timeline statistics.
    
    Args:
        df: DataFrame with activity records
        activity_date: Date string
        
    Returns:
        TimelineStatistics object or None if no data
    """
    sessions = get_daily_timeline(df, activity_date)
    
    if not sessions:
        return None
    
    # Calculate statistics
    total_duration = sum(s.duration_minutes for s in sessions)
    session_count = len(sessions)
    
    # Find earliest and latest
    earliest = min(sessions, key=lambda s: s.start_hour)
    latest = max(sessions, key=lambda s: s.end_hour)
    
    # Activity distribution
    activity_durations = {}
    for session in sessions:
        activity = session.activity_label
        activity_durations[activity] = activity_durations.get(activity, 0) + session.duration_minutes
    
    # Most frequent activity by duration
    most_frequent = max(activity_durations.items(), key=lambda x: x[1])[0] if activity_durations else "N/A"
    
    # Check for special conditions
    has_overnight = any(s.is_overnight for s in sessions)
    has_overlaps = any(s.overlaps_with for s in sessions)
    
    return TimelineStatistics(
        date=activity_date,
        total_duration=total_duration,
        session_count=session_count,
        earliest_session=earliest.start_time,
        latest_session=latest.end_time,
        most_frequent_activity=most_frequent,
        activity_distribution=activity_durations,
        has_overnight_sessions=has_overnight,
        has_overlapping_sessions=has_overlaps,
    )


def validate_timeline_records(df: pd.DataFrame, activity_date: str) -> Dict[str, Any]:
    """Validate timeline records for data quality issues.
    
    Args:
        df: DataFrame with activity records
        activity_date: Date string
        
    Returns:
        Validation report
    """
    sessions = get_daily_timeline(df, activity_date)
    
    if not sessions:
        return {
            "valid": True,
            "has_data": False,
            "issues": [],
        }
    
    issues = []
    
    # Check for overlaps
    overlapping = [s for s in sessions if s.overlaps_with]
    if overlapping:
        issues.append({
            "type": "overlapping_sessions",
            "severity": "warning",
            "count": len(overlapping),
            "message": f"{len(overlapping)} sessions have overlapping time periods",
            "affected_sessions": [s.id for s in overlapping],
        })
    
    # Check for overnight sessions
    overnight = [s for s in sessions if s.is_overnight]
    if overnight:
        issues.append({
            "type": "overnight_sessions",
            "severity": "info",
            "count": len(overnight),
            "message": f"{len(overnight)} sessions cross midnight",
            "affected_sessions": [s.id for s in overnight],
        })
    
    # Check for very short sessions (< 1 minute)
    short_sessions = [s for s in sessions if s.duration_minutes < 1]
    if short_sessions:
        issues.append({
            "type": "short_sessions",
            "severity": "warning",
            "count": len(short_sessions),
            "message": f"{len(short_sessions)} sessions have duration < 1 minute",
            "affected_sessions": [s.id for s in short_sessions],
        })
    
    # Check for very long sessions (> 12 hours)
    long_sessions = [s for s in sessions if s.duration_minutes > 720]
    if long_sessions:
        issues.append({
            "type": "long_sessions",
            "severity": "warning",
            "count": len(long_sessions),
            "message": f"{len(long_sessions)} sessions exceed 12 hours",
            "affected_sessions": [s.id for s in long_sessions],
        })
    
    return {
        "valid": len([i for i in issues if i["severity"] == "error"]) == 0,
        "has_data": True,
        "total_sessions": len(sessions),
        "issues": issues,
    }


def get_time_range_presets() -> Dict[str, Dict[str, float]]:
    """Get predefined time range presets for timeline zoom.
    
    Returns:
        Dictionary of preset names to hour ranges
    """
    return {
        "full_day": {"start": 0, "end": 24},
        "morning": {"start": 6, "end": 12},
        "afternoon": {"start": 12, "end": 18},
        "evening": {"start": 18, "end": 24},
        "night": {"start": 0, "end": 6},
        "work_hours": {"start": 9, "end": 17},
        "early_morning": {"start": 5, "end": 9},
    }
