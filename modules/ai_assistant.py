"""Interactive Q&A assistant over recorded physical activity data.

PROCESS 5 implementation: Conversational AI assistant using Google's Gemini API
with data-grounded RAG workflow, natural language understanding, and strict
non-medical guardrails.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal

import pandas as pd

from modules.ai_narrator import (
    NON_MEDICAL_SYSTEM_GUARDRAIL,
    is_gemini_configured,
    create_genai_client,
    get_gemini_model_name,
)
from modules.activity_analytics import (
    calculate_total_duration,
    calculate_activity_duration_by_label,
    calculate_daily_summary,
    calculate_activity_distribution,
)
from modules.activity_comparison import (
    compare_two_days,
    generate_weekly_comparison,
)
from google.genai import types

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AssistantMessage:
    """Structured chat message for the AI Assistant conversation."""

    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class AssistantResponse:
    """AI Assistant response with grounded data."""

    answer: str
    retrieved_data: dict[str, Any] | None = None
    success: bool = True
    error_message: str | None = None


def get_assistant_guardrail() -> str:
    """Return the system-level non-medical guardrail instruction."""
    return NON_MEDICAL_SYSTEM_GUARDRAIL


def understand_user_question(question: str) -> dict[str, Any]:
    """Parse user question to extract intent, activity type, and dates.
    
    Args:
        question: Natural language question from user
        
    Returns:
        Dictionary with extracted intent and parameters
    """
    question_lower = question.lower()
    
    # Extract activity type
    activity_type = None
    activity_patterns = {
        'walking': ['walk', 'walking'],
        'sitting': ['sit', 'sitting'],
        'standing': ['stand', 'standing'],
        'running': ['run', 'running'],
        'cycling': ['cycle', 'cycling', 'bike', 'biking'],
    }
    
    for activity_label, patterns in activity_patterns.items():
        for pattern in patterns:
            if pattern in question_lower:
                activity_type = activity_label.capitalize()
                break
        if activity_type:
            break
    
    # Extract date references
    date_ref = None
    if 'today' in question_lower:
        date_ref = datetime.now().strftime("%Y-%m-%d")
    elif 'yesterday' in question_lower:
        date_ref = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif 'monday' in question_lower:
        date_ref = "monday"
    elif 'tuesday' in question_lower:
        date_ref = "tuesday"
    elif 'wednesday' in question_lower:
        date_ref = "wednesday"
    elif 'thursday' in question_lower:
        date_ref = "thursday"
    elif 'friday' in question_lower:
        date_ref = "friday"
    elif 'saturday' in question_lower:
        date_ref = "saturday"
    elif 'sunday' in question_lower:
        date_ref = "sunday"
    
    # Try to extract date in YYYY-MM-DD format
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    date_matches = re.findall(date_pattern, question)
    if date_matches:
        date_ref = date_matches[0]
    
    # Determine intent
    intent = "general"
    if any(word in question_lower for word in ['compare', 'comparison', 'versus', 'vs']):
        intent = "compare"
    elif any(word in question_lower for word in ['week', 'weekly', 'seven days', '7 days']):
        intent = "weekly"
    elif any(word in question_lower for word in ['most', 'highest', 'longest', 'maximum']):
        intent = "maximum"
    elif any(word in question_lower for word in ['distribution', 'breakdown', 'percentage']):
        intent = "distribution"
    elif 'how much' in question_lower or 'how long' in question_lower:
        intent = "duration"
    elif 'summary' in question_lower or 'summarize' in question_lower:
        intent = "summary"
    
    return {
        'intent': intent,
        'activity_type': activity_type,
        'date_ref': date_ref,
        'original_question': question,
    }


def retrieve_activity_context(
    df: pd.DataFrame,
    intent_data: dict[str, Any],
) -> dict[str, Any]:
    """Retrieve relevant activity statistics based on parsed intent.
    
    Args:
        df: DataFrame with activity records
        intent_data: Parsed intent from understand_user_question
        
    Returns:
        Dictionary with retrieved statistics
    """
    if df is None or df.empty:
        return {'has_data': False, 'message': 'No activity data available.'}
    
    context = {'has_data': True}
    intent = intent_data['intent']
    activity_type = intent_data['activity_type']
    date_ref = intent_data['date_ref']
    
    # Get available dates
    available_dates = sorted(df["activity_date"].unique(), reverse=True)
    context['available_dates'] = available_dates
    
    # Handle specific intents
    if intent == "duration" and date_ref:
        # Get duration for specific date
        if date_ref in available_dates:
            daily_df = df[df["activity_date"] == date_ref]
            if activity_type:
                duration = calculate_activity_duration_by_label(daily_df, activity_type)
                context['duration'] = duration
                context['activity'] = activity_type
                context['date'] = date_ref
            else:
                duration = calculate_total_duration(daily_df)
                context['total_duration'] = duration
                context['date'] = date_ref
        else:
            context['message'] = f"No data found for {date_ref}"
    
    elif intent == "compare":
        # Compare two dates if both specified
        if len(available_dates) >= 2:
            prev_date = available_dates[1] if len(available_dates) > 1 else available_dates[0]
            curr_date = available_dates[0]
            comparison = compare_two_days(df, prev_date, curr_date)
            context['comparison'] = {
                'previous_date': prev_date,
                'current_date': curr_date,
                'previous_total': comparison.previous_total,
                'current_total': comparison.current_total,
                'difference': comparison.total_difference,
                'activities': [
                    {
                        'activity': c.activity_label,
                        'previous': c.previous_duration,
                        'current': c.current_duration,
                        'difference': c.absolute_difference,
                        'status': c.change_status,
                    }
                    for c in comparison.comparisons
                ]
            }
    
    elif intent == "weekly":
        # Get weekly stats
        if available_dates:
            start_date = available_dates[-1]
            weekly = generate_weekly_comparison(df, start_date, num_days=7)
            context['weekly'] = {
                'start_date': start_date,
                'total_walking': weekly.total_walking,
                'total_sitting': weekly.total_sitting,
                'total_standing': weekly.total_standing,
                'average_daily': weekly.average_daily_duration,
                'days_with_data': weekly.days_with_data,
                'highest_walking': weekly.highest_walking_duration,
            }
    
    elif intent == "maximum":
        # Find maximum duration
        if activity_type:
            # Get all durations for this activity
            activity_df = df[df["activity_label"] == activity_type].copy()
            if not activity_df.empty:
                daily_sums = activity_df.groupby("activity_date")["duration_minutes"].sum()
                max_date = daily_sums.idxmax()
                max_duration = daily_sums.max()
                context['maximum'] = {
                    'activity': activity_type,
                    'date': max_date,
                    'duration': max_duration,
                }
    
    elif intent == "distribution":
        # Get activity distribution for specific date or overall
        if date_ref and date_ref in available_dates:
            daily_df = df[df["activity_date"] == date_ref]
            distribution = calculate_activity_distribution(daily_df)
            context['distribution'] = [
                {
                    'activity': item.activity_label,
                    'duration': item.total_minutes,
                    'percentage': item.percentage,
                }
                for item in distribution
            ]
            context['date'] = date_ref
        else:
            distribution = calculate_activity_distribution(df)
            context['distribution'] = [
                {
                    'activity': item.activity_label,
                    'duration': item.total_minutes,
                    'percentage': item.percentage,
                }
                for item in distribution
            ]
    
    elif intent == "summary":
        # Get summary for date or recent period
        if date_ref and date_ref in available_dates:
            summary = calculate_daily_summary(df, date_ref)
            context['summary'] = {
                'date': date_ref,
                'total_minutes': summary.total_minutes,
                'walking': summary.walking_minutes,
                'sitting': summary.sitting_minutes,
                'standing': summary.standing_minutes,
                'sessions': summary.total_sessions,
                'top_activity': summary.most_frequent_activity,
            }
        elif available_dates:
            # Get latest date summary
            latest_date = available_dates[0]
            summary = calculate_daily_summary(df, latest_date)
            context['summary'] = {
                'date': latest_date,
                'total_minutes': summary.total_minutes,
                'walking': summary.walking_minutes,
                'sitting': summary.sitting_minutes,
                'standing': summary.standing_minutes,
                'sessions': summary.total_sessions,
                'top_activity': summary.most_frequent_activity,
            }
    
    return context


def generate_assistant_response(
    question: str,
    context_data: dict[str, Any],
    conversation_history: list[AssistantMessage] | None = None,
) -> AssistantResponse:
    """Generate natural language response using Gemini with grounded data.
    
    Args:
        question: User's question
        context_data: Retrieved activity context data
        conversation_history: Optional conversation history
        
    Returns:
        AssistantResponse with grounded answer
    """
    if not context_data.get('has_data', False):
        return AssistantResponse(
            answer="I don't have any activity data to analyze yet. Please upload your activity records first.",
            success=True,
        )
    
    if not is_gemini_configured():
        return AssistantResponse(
            answer=_generate_fallback_response(question, context_data),
            retrieved_data=context_data,
            success=True,
            error_message="Gemini API not configured - using template response",
        )
    
    try:
        client = create_genai_client()
        model_name = get_gemini_model_name()
        
        # Build grounded context
        grounded_context = _format_context_for_llm(context_data)
        
        # Build prompt
        prompt = f"""Answer the following question about recorded physical activity data.

USER QUESTION: {question}

VERIFIED ACTIVITY DATA:
{grounded_context}

Provide a clear, conversational answer based ONLY on the verified data above. If the data doesn't contain the information needed to answer the question, say so. Do not make assumptions or fabricate data.

Keep your response concise and friendly (2-3 sentences usually sufficient)."""

        # Add conversation history if available
        contents = []
        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 4 messages for context
                contents.append(msg.content)
        contents.append(prompt)
        
        # Generate response
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=get_assistant_guardrail(),
                temperature=0.5,
                max_output_tokens=300,
            ),
        )
        
        if response and response.text:
            return AssistantResponse(
                answer=response.text.strip(),
                retrieved_data=context_data,
                success=True,
            )
        else:
            raise ValueError("Empty response from Gemini API")
            
    except Exception as e:
        logger.error(f"Failed to generate assistant response: {e}")
        return AssistantResponse(
            answer=_generate_fallback_response(question, context_data),
            retrieved_data=context_data,
            success=False,
            error_message=str(e),
        )


def _format_context_for_llm(context_data: dict[str, Any]) -> str:
    """Format retrieved context data for LLM consumption."""
    parts = []
    
    if 'duration' in context_data:
        parts.append(
            f"{context_data['activity']} duration on {context_data['date']}: "
            f"{context_data['duration']:.0f} minutes"
        )
    
    if 'total_duration' in context_data:
        parts.append(
            f"Total activity duration on {context_data['date']}: "
            f"{context_data['total_duration']:.0f} minutes"
        )
    
    if 'comparison' in context_data:
        comp = context_data['comparison']
        parts.append(
            f"Comparison between {comp['previous_date']} and {comp['current_date']}:"
        )
        parts.append(f"- Previous total: {comp['previous_total']:.0f} minutes")
        parts.append(f"- Current total: {comp['current_total']:.0f} minutes")
        parts.append(f"- Difference: {comp['difference']:+.0f} minutes")
        
        for activity in comp['activities']:
            if activity['difference'] != 0:
                parts.append(
                    f"- {activity['activity']}: {activity['status']} "
                    f"({activity['difference']:+.0f} minutes)"
                )
    
    if 'weekly' in context_data:
        weekly = context_data['weekly']
        parts.append(f"Weekly summary starting {weekly['start_date']}:")
        parts.append(f"- Total walking: {weekly['total_walking']:.0f} minutes")
        parts.append(f"- Total sitting: {weekly['total_sitting']:.0f} minutes")
        parts.append(f"- Average daily: {weekly['average_daily']:.0f} minutes")
        parts.append(f"- Days with data: {weekly['days_with_data']}")
    
    if 'maximum' in context_data:
        max_data = context_data['maximum']
        parts.append(
            f"Highest {max_data['activity']} duration: {max_data['duration']:.0f} minutes "
            f"on {max_data['date']}"
        )
    
    if 'distribution' in context_data:
        parts.append("Activity distribution:")
        for item in context_data['distribution']:
            parts.append(
                f"- {item['activity']}: {item['duration']:.0f} minutes ({item['percentage']:.1f}%)"
            )
    
    if 'summary' in context_data:
        summary = context_data['summary']
        parts.append(f"Summary for {summary['date']}:")
        parts.append(f"- Total: {summary['total_minutes']:.0f} minutes")
        parts.append(f"- Walking: {summary['walking']:.0f} minutes")
        parts.append(f"- Sitting: {summary['sitting']:.0f} minutes")
        parts.append(f"- Standing: {summary['standing']:.0f} minutes")
        parts.append(f"- Sessions: {summary['sessions']}")
        if summary.get('top_activity'):
            parts.append(f"- Top activity: {summary['top_activity']}")
    
    if 'message' in context_data:
        parts.append(context_data['message'])
    
    if 'available_dates' in context_data:
        dates = context_data['available_dates'][:5]  # First 5 dates
        parts.append(f"Available dates: {', '.join(dates)}")
    
    return "\n".join(parts) if parts else "No specific data retrieved."


def _generate_fallback_response(question: str, context_data: dict[str, Any]) -> str:
    """Generate template-based response when Gemini is unavailable."""
    if 'duration' in context_data:
        return (
            f"On {context_data['date']}, you recorded {context_data['duration']:.0f} minutes "
            f"of {context_data['activity']}."
        )
    
    if 'total_duration' in context_data:
        return (
            f"On {context_data['date']}, you recorded a total of "
            f"{context_data['total_duration']:.0f} minutes of activity."
        )
    
    if 'comparison' in context_data:
        comp = context_data['comparison']
        return (
            f"Comparing {comp['previous_date']} and {comp['current_date']}: "
            f"Total activity changed by {comp['difference']:+.0f} minutes "
            f"({comp['previous_total']:.0f} → {comp['current_total']:.0f} minutes)."
        )
    
    if 'weekly' in context_data:
        weekly = context_data['weekly']
        return (
            f"For the week starting {weekly['start_date']}, you recorded "
            f"{weekly['total_walking']:.0f} minutes of walking and "
            f"{weekly['total_sitting']:.0f} minutes of sitting across "
            f"{weekly['days_with_data']} days."
        )
    
    if 'summary' in context_data:
        summary = context_data['summary']
        return (
            f"On {summary['date']}, you recorded {summary['total_minutes']:.0f} minutes "
            f"of activity including {summary['walking']:.0f} minutes of walking."
        )
    
    return "I found your activity data, but I'm having trouble generating a detailed response. Please try rephrasing your question."


def maintain_conversation_context(
    messages: list[AssistantMessage],
    max_messages: int = 10,
) -> list[AssistantMessage]:
    """Maintain conversation history with size limit.
    
    Args:
        messages: List of conversation messages
        max_messages: Maximum messages to keep
        
    Returns:
        Trimmed message list
    """
    if len(messages) <= max_messages:
        return messages
    return messages[-max_messages:]


def answer_activity_question(
    question: str,
    df: pd.DataFrame,
    conversation_history: list[AssistantMessage] | None = None,
) -> AssistantResponse:
    """Main entry point for answering activity questions.
    
    Args:
        question: User's natural language question
        df: DataFrame with activity records
        conversation_history: Optional conversation history
        
    Returns:
        AssistantResponse with grounded answer
    """
    # Parse question
    intent_data = understand_user_question(question)
    
    # Retrieve relevant data
    context_data = retrieve_activity_context(df, intent_data)
    
    # Generate response
    return generate_assistant_response(question, context_data, conversation_history)
