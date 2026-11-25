"""Intelligent AI Agent with tool-based activity data retrieval.

Implements structured tool calling for precise activity data queries with
multi-LLM support (Groq and Gemini).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal
import json

import pandas as pd

from modules.llm_provider import get_llm_manager
from modules.activity_analytics import (
    calculate_daily_summary,
    calculate_activity_distribution,
)
from modules.activity_comparison import (
    compare_two_days,
    generate_weekly_comparison,
)

logger = logging.getLogger(__name__)

NON_MEDICAL_SYSTEM_GUARDRAIL = (
    "You are ActiPulse AI Assistant, an intelligent activity data analyst. "
    "Your role is to answer questions about recorded physical activities using verified data. "
    "\n\nSTRICT RULES:\n"
    "1. Answer ONLY based on the retrieved activity data provided.\n"
    "2. NEVER diagnose medical conditions or make health assessments.\n"
    "3. NEVER fabricate activity data - state when data is missing.\n"
    "4. NEVER assume unrecorded time means inactivity.\n"
    "5. Focus on factual responses about recorded activity durations.\n"
    "6. If asked about health topics, politely decline and explain your role.\n"
    "\nProvide clear, concise, conversational answers grounded in the data."
)


@dataclass(frozen=True)
class AgentMessage:
    """Structured chat message for AI Agent conversation."""
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class ToolResult:
    """Result from a tool execution."""
    tool_name: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class AgentResponse:
    """AI Agent response with tool execution trace."""
    answer: str
    provider_used: str
    model_used: str
    tools_used: list[str]
    tool_results: list[ToolResult]
    success: bool
    error_message: str | None = None


class ActivityTools:
    """Activity data retrieval tools for AI Agent."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with activity DataFrame."""
        self.df = df
    
    def get_available_dates(self) -> ToolResult:
        """Get list of dates with recorded activity data."""
        if self.df.empty:
            return ToolResult(
                tool_name="get_available_dates",
                success=False,
                error="No activity data available",
            )
        
        dates = sorted(self.df["activity_date"].unique().tolist(), reverse=True)
        return ToolResult(
            tool_name="get_available_dates",
            success=True,
            data={"dates": dates, "count": len(dates)},
        )
    
    def get_activity_records(self, date: str) -> ToolResult:
        """Get all activity records for a specific date."""
        if self.df.empty:
            return ToolResult(
                tool_name="get_activity_records",
                success=False,
                error="No activity data available",
            )
        
        date_df = self.df[self.df["activity_date"] == date]
        if date_df.empty:
            return ToolResult(
                tool_name="get_activity_records",
                success=True,
                data={"date": date, "records": [], "message": f"No records found for {date}"},
            )
        
        records = date_df[["start_time", "end_time", "activity_label", "duration_minutes"]].to_dict("records")
        return ToolResult(
            tool_name="get_activity_records",
            success=True,
            data={"date": date, "records": records, "count": len(records)},
        )
    
    def get_daily_summary(self, date: str) -> ToolResult:
        """Get comprehensive daily activity summary."""
        if self.df.empty:
            return ToolResult(
                tool_name="get_daily_summary",
                success=False,
                error="No activity data available",
            )
        
        if date not in self.df["activity_date"].unique():
            return ToolResult(
                tool_name="get_daily_summary",
                success=True,
                data={"date": date, "message": f"No data for {date}"},
            )
        
        summary = calculate_daily_summary(self.df, date)
        return ToolResult(
            tool_name="get_daily_summary",
            success=True,
            data={
                "date": date,
                "total_minutes": summary.total_minutes,
                "total_hours": summary.total_hours,
                "walking_minutes": summary.walking_minutes,
                "sitting_minutes": summary.sitting_minutes,
                "standing_minutes": summary.standing_minutes,
                "running_minutes": summary.running_minutes,
                "cycling_minutes": summary.cycling_minutes,
                "total_sessions": summary.total_sessions,
                "top_activity": summary.most_frequent_activity,
                "activity_percentages": summary.activity_percentages,
            },
        )
    
    def get_activity_duration(self, date: str, activity: str) -> ToolResult:
        """Get total duration for specific activity on a date."""
        if self.df.empty:
            return ToolResult(
                tool_name="get_activity_duration",
                success=False,
                error="No activity data available",
            )
        
        # Normalize activity name
        activity = activity.capitalize()
        
        date_df = self.df[
            (self.df["activity_date"] == date) &
            (self.df["activity_label"] == activity)
        ]
        
        if date_df.empty:
            return ToolResult(
                tool_name="get_activity_duration",
                success=True,
                data={
                    "date": date,
                    "activity": activity,
                    "duration_minutes": 0,
                    "message": f"No {activity} recorded on {date}",
                },
            )
        
        duration = date_df["duration_minutes"].sum()
        return ToolResult(
            tool_name="get_activity_duration",
            success=True,
            data={
                "date": date,
                "activity": activity,
                "duration_minutes": duration,
                "duration_hours": duration / 60,
                "session_count": len(date_df),
            },
        )
    
    def compare_days(self, date1: str, date2: str) -> ToolResult:
        """Compare activities between two dates."""
        if self.df.empty:
            return ToolResult(
                tool_name="compare_days",
                success=False,
                error="No activity data available",
            )
        
        try:
            comparison = compare_two_days(self.df, date1, date2)
            
            activities = []
            for comp in comparison.comparisons:
                activities.append({
                    "activity": comp.activity_label,
                    "date1_duration": comp.previous_duration,
                    "date2_duration": comp.current_duration,
                    "difference": comp.absolute_difference,
                    "status": comp.change_status,
                })
            
            return ToolResult(
                tool_name="compare_days",
                success=True,
                data={
                    "date1": date1,
                    "date2": date2,
                    "date1_total": comparison.previous_total,
                    "date2_total": comparison.current_total,
                    "total_difference": comparison.total_difference,
                    "activities": activities,
                },
            )
        except Exception as e:
            return ToolResult(
                tool_name="compare_days",
                success=False,
                error=str(e),
            )
    
    def get_weekly_summary(self, start_date: str) -> ToolResult:
        """Get weekly activity summary starting from date."""
        if self.df.empty:
            return ToolResult(
                tool_name="get_weekly_summary",
                success=False,
                error="No activity data available",
            )
        
        try:
            weekly = generate_weekly_comparison(self.df, start_date, num_days=7)
            
            return ToolResult(
                tool_name="get_weekly_summary",
                success=True,
                data={
                    "start_date": start_date,
                    "total_walking": weekly.total_walking,
                    "total_sitting": weekly.total_sitting,
                    "total_standing": weekly.total_standing,
                    "total_running": weekly.total_running,
                    "total_cycling": weekly.total_cycling,
                    "average_daily": weekly.average_daily_duration,
                    "days_with_data": weekly.days_with_data,
                    "highest_walking": weekly.highest_walking_duration,
                    "lowest_walking": weekly.lowest_walking_duration,
                },
            )
        except Exception as e:
            return ToolResult(
                tool_name="get_weekly_summary",
                success=False,
                error=str(e),
            )
    
    def get_activity_distribution(self, date: str | None = None) -> ToolResult:
        """Get activity distribution for date or all data."""
        if self.df.empty:
            return ToolResult(
                tool_name="get_activity_distribution",
                success=False,
                error="No activity data available",
            )
        
        if date:
            subset_df = self.df[self.df["activity_date"] == date]
            if subset_df.empty:
                return ToolResult(
                    tool_name="get_activity_distribution",
                    success=True,
                    data={"date": date, "message": f"No data for {date}", "distribution": []},
                )
        else:
            subset_df = self.df
        
        distribution = calculate_activity_distribution(subset_df)
        
        dist_data = []
        for item in distribution:
            dist_data.append({
                "activity": item.activity_label,
                "duration_minutes": item.total_minutes,
                "percentage": item.percentage,
                "sessions": item.session_count,
            })
        
        return ToolResult(
            tool_name="get_activity_distribution",
            success=True,
            data={
                "date": date,
                "distribution": dist_data,
            },
        )
    
    def get_most_recorded_activity(self, date: str | None = None) -> ToolResult:
        """Get most frequently recorded activity by duration."""
        if self.df.empty:
            return ToolResult(
                tool_name="get_most_recorded_activity",
                success=False,
                error="No activity data available",
            )
        
        if date:
            subset_df = self.df[self.df["activity_date"] == date]
        else:
            subset_df = self.df
        
        if subset_df.empty:
            return ToolResult(
                tool_name="get_most_recorded_activity",
                success=True,
                data={"message": "No data available"},
            )
        
        # Group by activity and sum durations
        activity_totals = subset_df.groupby("activity_label")["duration_minutes"].sum()
        most_recorded = activity_totals.idxmax()
        max_duration = activity_totals.max()
        
        return ToolResult(
            tool_name="get_most_recorded_activity",
            success=True,
            data={
                "date": date,
                "activity": most_recorded,
                "duration_minutes": max_duration,
                "duration_hours": max_duration / 60,
            },
        )


def parse_question_intent(question: str) -> dict[str, Any]:
    """Parse user question to extract intent and parameters.
    
    Args:
        question: User's natural language question
        
    Returns:
        Dictionary with intent and extracted parameters
    """
    question_lower = question.lower()
    
    # Extract dates
    dates = []
    
    # Check for relative dates
    if 'today' in question_lower:
        dates.append(datetime.now().strftime("%Y-%m-%d"))
    if 'yesterday' in question_lower:
        dates.append((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
    
    # Extract YYYY-MM-DD format dates
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    found_dates = re.findall(date_pattern, question)
    dates.extend(found_dates)
    
    # Extract activity type
    activity_patterns = {
        'Walking': ['walk', 'walking'],
        'Sitting': ['sit', 'sitting'],
        'Standing': ['stand', 'standing'],
        'Running': ['run', 'running'],
        'Cycling': ['cycle', 'cycling', 'bike', 'biking'],
    }
    
    activity = None
    for activity_name, patterns in activity_patterns.items():
        if any(p in question_lower for p in patterns):
            activity = activity_name
            break
    
    # Determine intent
    intent = "general"
    if any(word in question_lower for word in ['compare', 'comparison', 'versus', 'vs', 'between']):
        intent = "compare_days"
    elif any(word in question_lower for word in ['week', 'weekly', '7 days', 'seven days']):
        intent = "weekly_summary"
    elif any(word in question_lower for word in ['distribution', 'breakdown', 'percentage']):
        intent = "distribution"
    elif any(word in question_lower for word in ['most', 'highest', 'top', 'maximum']):
        intent = "most_recorded"
    elif 'how much' in question_lower or 'how long' in question_lower:
        if activity:
            intent = "activity_duration"
        else:
            intent = "daily_summary"
    elif 'summary' in question_lower or 'summarize' in question_lower:
        intent = "daily_summary"
    elif 'available' in question_lower or 'recorded dates' in question_lower:
        intent = "available_dates"
    elif 'records' in question_lower or 'activities' in question_lower:
        intent = "activity_records"
    
    return {
        "intent": intent,
        "dates": dates,
        "activity": activity,
        "original_question": question,
    }


def execute_tools(
    intent_data: dict[str, Any],
    tools: ActivityTools,
    conversation_history: list[AgentMessage] | None = None,
) -> list[ToolResult]:
    """Execute appropriate tools based on parsed intent.
    
    Args:
        intent_data: Parsed intent and parameters
        tools: ActivityTools instance
        conversation_history: Optional conversation context
        
    Returns:
        List of tool execution results
    """
    intent = intent_data["intent"]
    dates = intent_data["dates"]
    activity = intent_data["activity"]
    
    results = []
    
    # Execute tools based on intent
    if intent == "available_dates":
        results.append(tools.get_available_dates())
    
    elif intent == "activity_records" and dates:
        results.append(tools.get_activity_records(dates[0]))
    
    elif intent == "daily_summary" and dates:
        results.append(tools.get_daily_summary(dates[0]))
    
    elif intent == "activity_duration" and dates and activity:
        results.append(tools.get_activity_duration(dates[0], activity))
    
    elif intent == "compare_days" and len(dates) >= 2:
        results.append(tools.compare_days(dates[0], dates[1]))
    
    elif intent == "weekly_summary" and dates:
        results.append(tools.get_weekly_summary(dates[0]))
    
    elif intent == "distribution":
        date = dates[0] if dates else None
        results.append(tools.get_activity_distribution(date))
    
    elif intent == "most_recorded":
        date = dates[0] if dates else None
        results.append(tools.get_most_recorded_activity(date))
    
    else:
        # Default: try to get available dates and latest summary
        results.append(tools.get_available_dates())
        dates_result = results[0]
        if dates_result.success and dates_result.data and dates_result.data.get("dates"):
            latest_date = dates_result.data["dates"][0]
            results.append(tools.get_daily_summary(latest_date))
    
    return results


def format_tool_results_for_llm(tool_results: list[ToolResult]) -> str:
    """Format tool execution results for LLM context.
    
    Args:
        tool_results: List of tool results
        
    Returns:
        Formatted string for LLM
    """
    parts = ["VERIFIED ACTIVITY DATA (from database):"]
    
    for result in tool_results:
        if not result.success:
            parts.append(f"\n{result.tool_name}: {result.error}")
            continue
        
        parts.append(f"\n{result.tool_name}:")
        if result.data:
            parts.append(json.dumps(result.data, indent=2))
    
    return "\n".join(parts)


def generate_agent_response(
    question: str,
    tool_results: list[ToolResult],
    conversation_history: list[AgentMessage] | None = None,
    preferred_provider: str | None = None,
) -> AgentResponse:
    """Generate natural language response from tool results using LLM.
    
    Args:
        question: User's question
        tool_results: Tool execution results
        conversation_history: Optional conversation history
        preferred_provider: Optional preferred LLM provider
        
    Returns:
        AgentResponse with final answer
    """
    manager = get_llm_manager()
    
    # Check if any provider is available
    if not manager.is_groq_configured() and not manager.is_gemini_configured():
        return AgentResponse(
            answer=_generate_fallback_response(question, tool_results),
            provider_used="fallback_template",
            model_used="template",
            tools_used=[r.tool_name for r in tool_results],
            tool_results=tool_results,
            success=True,
            error_message="No LLM provider configured - using template response",
        )
    
    # Format tool results for LLM
    tool_context = format_tool_results_for_llm(tool_results)
    
    # Build prompt
    prompt = f"""Answer the following question about recorded physical activity data.

USER QUESTION: {question}

{tool_context}

Provide a clear, conversational answer based ONLY on the verified data above. If the data doesn't contain the information needed, say so. Do not make assumptions or fabricate data.

Keep your response concise and friendly (2-4 sentences)."""

    # Generate response
    llm_response = manager.generate(
        prompt=prompt,
        system_instruction=NON_MEDICAL_SYSTEM_GUARDRAIL,
        temperature=0.5,
        max_tokens=300,
        preferred_provider=preferred_provider,
    )
    
    if llm_response.success:
        return AgentResponse(
            answer=llm_response.text,
            provider_used=llm_response.provider_used,
            model_used=llm_response.model_used,
            tools_used=[r.tool_name for r in tool_results],
            tool_results=tool_results,
            success=True,
        )
    else:
        return AgentResponse(
            answer=_generate_fallback_response(question, tool_results),
            provider_used="fallback_template",
            model_used="template",
            tools_used=[r.tool_name for r in tool_results],
            tool_results=tool_results,
            success=False,
            error_message=llm_response.error_message,
        )


def _generate_fallback_response(question: str, tool_results: list[ToolResult]) -> str:
    """Generate template-based response when LLM is unavailable."""
    if not tool_results:
        return "I couldn't retrieve any activity data to answer your question."
    
    # Find first successful result
    for result in tool_results:
        if result.success and result.data:
            # Format based on tool type
            if result.tool_name == "get_daily_summary":
                data = result.data
                return (
                    f"On {data['date']}, you recorded {data['total_minutes']:.0f} minutes "
                    f"({data['total_hours']:.1f} hours) of activity including "
                    f"{data['walking_minutes']:.0f} minutes of walking."
                )
            
            elif result.tool_name == "get_activity_duration":
                data = result.data
                return (
                    f"On {data['date']}, you recorded {data['duration_minutes']:.0f} minutes "
                    f"of {data['activity']}."
                )
            
            elif result.tool_name == "compare_days":
                data = result.data
                return (
                    f"Comparing {data['date1']} and {data['date2']}: "
                    f"Total activity was {data['date1_total']:.0f} minutes vs "
                    f"{data['date2_total']:.0f} minutes (difference: {data['total_difference']:+.0f} minutes)."
                )
            
            elif result.tool_name == "get_weekly_summary":
                data = result.data
                return (
                    f"For the week starting {data['start_date']}, you recorded "
                    f"{data['total_walking']:.0f} minutes of walking across "
                    f"{data['days_with_data']} days."
                )
    
    return "I found your activity data but couldn't generate a detailed response. Please try rephrasing your question."


def answer_activity_question_v2(
    question: str,
    df: pd.DataFrame,
    conversation_history: list[AgentMessage] | None = None,
    preferred_provider: str | None = None,
) -> AgentResponse:
    """Main entry point for AI Agent activity questions.
    
    Args:
        question: User's natural language question
        df: DataFrame with activity records
        conversation_history: Optional conversation history
        preferred_provider: Optional preferred LLM provider
        
    Returns:
        AgentResponse with answer and tool execution trace
    """
    # Parse question intent
    intent_data = parse_question_intent(question)
    
    # Initialize tools
    tools = ActivityTools(df)
    
    # Execute appropriate tools
    tool_results = execute_tools(intent_data, tools, conversation_history)
    
    # Generate response from tool results
    return generate_agent_response(question, tool_results, conversation_history, preferred_provider)
