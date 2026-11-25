"""Multi-LLM daily activity narrative generation with Groq and Gemini support.

Enhanced version of ai_narrator.py with centralized LLM provider management.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from modules.llm_provider import get_llm_manager, LLMResponse

logger = logging.getLogger(__name__)

NON_MEDICAL_SYSTEM_GUARDRAIL = (
    "You are ActiPulse AI, a personal physical activity diary narrator. "
    "Your role is to describe recorded physical activities, durations, and daily patterns clearly and objectively. "
    "\n\nSTRICT RULES YOU MUST FOLLOW:\n"
    "1. Only describe recorded physical activities (walking, sitting, standing, running, cycling).\n"
    "2. NEVER diagnose medical conditions or predict diseases.\n"
    "3. NEVER make health assessments or fitness evaluations.\n"
    "4. NEVER infer a person's health status from activity duration.\n"
    "5. NEVER provide treatment recommendations.\n"
    "6. NEVER describe increased activity as 'good' or decreased activity as 'bad' in a medical sense.\n"
    "7. NEVER fabricate missing activity records - state when data is unavailable.\n"
    "8. NEVER assume unrecorded time means inactivity.\n"
    "9. Focus on factual descriptions of recorded durations and patterns.\n"
    "10. If asked about health or medical topics, politely explain you only summarize activity logs.\n"
    "\nYour narratives should be informative, clear, and grounded in the actual recorded data provided."
)


@dataclass(frozen=True)
class NarrativeResponse:
    """Generated narrative response with metadata."""

    narrative_text: str
    provider_used: str
    model_used: str
    success: bool
    error_message: str | None = None


def build_daily_narrative_context(
    activity_date: str,
    daily_stats: dict[str, Any],
    previous_day_stats: dict[str, Any] | None = None,
) -> str:
    """Build structured context for daily narrative generation.
    
    Args:
        activity_date: Date of the activities (YYYY-MM-DD)
        daily_stats: Dictionary with daily activity statistics
        previous_day_stats: Optional previous day statistics for comparison
        
    Returns:
        Formatted context string for LLM
    """
    context_parts = [
        f"Date: {activity_date}",
        "",
        "RECORDED ACTIVITY STATISTICS:",
        f"- Walking: {daily_stats.get('walking_minutes', 0):.0f} minutes",
        f"- Sitting: {daily_stats.get('sitting_minutes', 0):.0f} minutes",
        f"- Standing: {daily_stats.get('standing_minutes', 0):.0f} minutes",
        f"- Running: {daily_stats.get('running_minutes', 0):.0f} minutes",
        f"- Cycling: {daily_stats.get('cycling_minutes', 0):.0f} minutes",
        f"- Total recorded duration: {daily_stats.get('total_minutes', 0):.0f} minutes ({daily_stats.get('total_hours', 0):.1f} hours)",
        f"- Number of activity sessions: {daily_stats.get('total_sessions', 0)}",
        "",
        "ACTIVITY DISTRIBUTION:",
    ]
    
    # Add activity percentages
    for activity, percentage in daily_stats.get('activity_percentages', {}).items():
        context_parts.append(f"- {activity}: {percentage:.1f}%")
    
    if daily_stats.get('top_activity'):
        context_parts.append(f"\nLargest activity category: {daily_stats.get('top_activity')}")
    
    # Add previous day comparison if available
    if previous_day_stats:
        context_parts.extend([
            "",
            "COMPARISON WITH PREVIOUS RECORDED DAY:",
            f"Previous date: {previous_day_stats.get('date', 'Unknown')}",
        ])
        
        for activity in ['walking', 'sitting', 'standing', 'running', 'cycling']:
            prev_val = previous_day_stats.get(f'{activity}_minutes', 0)
            curr_val = daily_stats.get(f'{activity}_minutes', 0)
            diff = curr_val - prev_val
            
            if diff != 0:
                direction = "increased" if diff > 0 else "decreased"
                context_parts.append(
                    f"- {activity.capitalize()}: {direction} by {abs(diff):.0f} minutes"
                )
            elif curr_val > 0:
                context_parts.append(f"- {activity.capitalize()}: remained unchanged")
    else:
        context_parts.append("\nNo previous recorded day available for comparison.")
    
    return "\n".join(context_parts)


def build_weekly_narrative_context(
    week_start: str,
    weekly_stats: dict[str, Any],
) -> str:
    """Build structured context for weekly narrative generation.
    
    Args:
        week_start: Start date of the week (YYYY-MM-DD)
        weekly_stats: Dictionary with weekly activity statistics
        
    Returns:
        Formatted context string for LLM
    """
    context_parts = [
        f"Week starting: {week_start}",
        "",
        "WEEKLY ACTIVITY SUMMARY:",
        f"- Total walking: {weekly_stats.get('total_walking', 0):.0f} minutes",
        f"- Total sitting: {weekly_stats.get('total_sitting', 0):.0f} minutes",
        f"- Total standing: {weekly_stats.get('total_standing', 0):.0f} minutes",
        f"- Total running: {weekly_stats.get('total_running', 0):.0f} minutes",
        f"- Total cycling: {weekly_stats.get('total_cycling', 0):.0f} minutes",
        f"- Days with recorded data: {weekly_stats.get('days_with_data', 0)}",
        f"- Average daily duration: {weekly_stats.get('average_daily', 0):.0f} minutes",
        "",
        "ACTIVITY HIGHLIGHTS:",
        f"- Highest walking duration: {weekly_stats.get('highest_walking', 0):.0f} minutes",
        f"- Lowest walking duration: {weekly_stats.get('lowest_walking', 0):.0f} minutes",
        f"- Highest sitting duration: {weekly_stats.get('highest_sitting', 0):.0f} minutes",
        "",
        "DAILY BREAKDOWN:",
    ]
    
    # Add daily totals if available
    dates = weekly_stats.get('dates', [])
    daily_totals = weekly_stats.get('daily_totals', [])
    
    for date, total in zip(dates, daily_totals):
        if total > 0:
            context_parts.append(f"- {date}: {total:.0f} minutes recorded")
        else:
            context_parts.append(f"- {date}: No recorded activity data")
    
    return "\n".join(context_parts)


def generate_daily_narrative(
    activity_date: str,
    daily_stats: dict[str, Any],
    previous_day_stats: dict[str, Any] | None = None,
    tone: str = "Reflective & Clear",
    preferred_provider: str | None = None,
) -> NarrativeResponse:
    """Generate a natural-language daily activity narrative using configured LLM.
    
    Args:
        activity_date: Date of the activities
        daily_stats: Verified daily statistics from analytics engine
        previous_day_stats: Optional previous day statistics
        tone: Narrative tone/style
        preferred_provider: Optional preferred provider ('groq' or 'gemini')
        
    Returns:
        NarrativeResponse with generated narrative or error
    """
    manager = get_llm_manager()
    
    # Check if any provider is available
    if not manager.is_groq_configured() and not manager.is_gemini_configured():
        return NarrativeResponse(
            narrative_text=_generate_fallback_narrative(activity_date, daily_stats, previous_day_stats),
            provider_used="fallback_template",
            model_used="template",
            success=True,
            error_message="No LLM provider configured - using template narrative",
        )
    
    # Build context from verified statistics
    context = build_daily_narrative_context(activity_date, daily_stats, previous_day_stats)
    
    # Create prompt
    prompt = f"""Generate a personal daily activity diary entry based on the following recorded activity data.

{context}

Create a natural, {tone.lower()} narrative that includes:
1. A brief overview of the day's recorded activities
2. A breakdown of walking, sitting, standing, and other activities
3. Mention which activity occupied the most time
4. If previous day data is available, describe the changes in duration
5. Highlight any interesting patterns or observations

Keep the narrative factual and grounded in the provided statistics. Do NOT make medical interpretations or health assessments. Focus on describing the recorded activity patterns objectively.

Write in second person ("you"), in a friendly and informative tone. Keep it concise (3-5 paragraphs)."""

    # Generate using LLM provider
    llm_response = manager.generate(
        prompt=prompt,
        system_instruction=NON_MEDICAL_SYSTEM_GUARDRAIL,
        temperature=0.7,
        max_tokens=800,
        preferred_provider=preferred_provider,
    )
    
    if llm_response.success:
        return NarrativeResponse(
            narrative_text=llm_response.text,
            provider_used=llm_response.provider_used,
            model_used=llm_response.model_used,
            success=True,
        )
    else:
        # Fallback to template if LLM fails
        return NarrativeResponse(
            narrative_text=_generate_fallback_narrative(activity_date, daily_stats, previous_day_stats),
            provider_used="fallback_template",
            model_used="template",
            success=False,
            error_message=llm_response.error_message,
        )


def generate_weekly_narrative(
    week_start: str,
    weekly_stats: dict[str, Any],
    preferred_provider: str | None = None,
) -> NarrativeResponse:
    """Generate a natural-language weekly activity summary using configured LLM.
    
    Args:
        week_start: Start date of the week
        weekly_stats: Verified weekly statistics from comparison engine
        preferred_provider: Optional preferred provider ('groq' or 'gemini')
        
    Returns:
        NarrativeResponse with generated narrative or error
    """
    manager = get_llm_manager()
    
    # Check if any provider is available
    if not manager.is_groq_configured() and not manager.is_gemini_configured():
        return NarrativeResponse(
            narrative_text=_generate_fallback_weekly_narrative(week_start, weekly_stats),
            provider_used="fallback_template",
            model_used="template",
            success=True,
            error_message="No LLM provider configured - using template narrative",
        )
    
    # Build context from verified statistics
    context = build_weekly_narrative_context(week_start, weekly_stats)
    
    # Create prompt
    prompt = f"""Generate a weekly activity summary based on the following recorded activity data.

{context}

Create a comprehensive summary that includes:
1. Overview of the week's recorded activities
2. Total durations for major activity categories
3. Patterns across the days with recorded data
4. Highest and lowest activity durations
5. Any notable trends or observations

Remember that days without recorded data should NOT be described as days with zero activity - simply note that those days lack recorded data. Keep the narrative factual and grounded in the provided statistics.

Write in second person ("you"), in a friendly and informative tone. Keep it concise (4-6 paragraphs)."""

    # Generate using LLM provider
    llm_response = manager.generate(
        prompt=prompt,
        system_instruction=NON_MEDICAL_SYSTEM_GUARDRAIL,
        temperature=0.7,
        max_tokens=1000,
        preferred_provider=preferred_provider,
    )
    
    if llm_response.success:
        return NarrativeResponse(
            narrative_text=llm_response.text,
            provider_used=llm_response.provider_used,
            model_used=llm_response.model_used,
            success=True,
        )
    else:
        # Fallback to template if LLM fails
        return NarrativeResponse(
            narrative_text=_generate_fallback_weekly_narrative(week_start, weekly_stats),
            provider_used="fallback_template",
            model_used="template",
            success=False,
            error_message=llm_response.error_message,
        )


def _generate_fallback_narrative(
    activity_date: str,
    daily_stats: dict[str, Any],
    previous_day_stats: dict[str, Any] | None = None,
) -> str:
    """Generate a template-based narrative when LLM is unavailable."""
    parts = [
        f"Your Activity Diary – {activity_date}",
        "",
        f"Today, you recorded {daily_stats.get('total_minutes', 0):.0f} minutes "
        f"({daily_stats.get('total_hours', 0):.1f} hours) of activity across "
        f"{daily_stats.get('total_sessions', 0)} sessions.",
        "",
    ]
    
    # Activity breakdown
    activities = []
    for activity in ['Walking', 'Sitting', 'Standing', 'Running', 'Cycling']:
        minutes = daily_stats.get(f'{activity.lower()}_minutes', 0)
        if minutes > 0:
            activities.append(f"{minutes:.0f} minutes of {activity.lower()}")
    
    if activities:
        parts.append("Your recorded activities included " + ", ".join(activities) + ".")
        parts.append("")
    
    # Top activity
    if daily_stats.get('top_activity'):
        parts.append(
            f"{daily_stats['top_activity']} accounted for the largest portion "
            f"of your recorded activity duration."
        )
        parts.append("")
    
    # Previous day comparison
    if previous_day_stats:
        changes = []
        for activity in ['walking', 'sitting', 'standing']:
            prev = previous_day_stats.get(f'{activity}_minutes', 0)
            curr = daily_stats.get(f'{activity}_minutes', 0)
            diff = curr - prev
            if diff > 0:
                changes.append(f"{activity} increased by {diff:.0f} minutes")
            elif diff < 0:
                changes.append(f"{activity} decreased by {abs(diff):.0f} minutes")
        
        if changes:
            parts.append(
                "Compared with your previous recorded day, " + ", ".join(changes) + "."
            )
    
    return "\n".join(parts)


def _generate_fallback_weekly_narrative(
    week_start: str,
    weekly_stats: dict[str, Any],
) -> str:
    """Generate a template-based weekly narrative when LLM is unavailable."""
    parts = [
        f"Weekly Activity Summary – Week of {week_start}",
        "",
        f"Over the selected week, you recorded activity data on "
        f"{weekly_stats.get('days_with_data', 0)} days, with an average of "
        f"{weekly_stats.get('average_daily', 0):.0f} minutes per day.",
        "",
        "Your weekly totals included:",
        f"- Walking: {weekly_stats.get('total_walking', 0):.0f} minutes",
        f"- Sitting: {weekly_stats.get('total_sitting', 0):.0f} minutes",
        f"- Standing: {weekly_stats.get('total_standing', 0):.0f} minutes",
        "",
        f"Your highest walking duration was {weekly_stats.get('highest_walking', 0):.0f} minutes, "
        f"and your highest sitting duration was {weekly_stats.get('highest_sitting', 0):.0f} minutes.",
    ]
    
    return "\n".join(parts)
