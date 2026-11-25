"""Tests for AI Narrator module (PROCESS 5)."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from modules.ai_narrator import (
    build_daily_narrative_context,
    build_weekly_narrative_context,
    generate_daily_narrative,
    generate_weekly_narrative,
    is_gemini_configured,
    get_gemini_model_name,
    validate_narrative_response,
    _generate_fallback_narrative,
    _generate_fallback_weekly_narrative,
)


class TestGeminiConfiguration:
    """Test Gemini API configuration functions."""

    def test_is_gemini_configured_with_valid_key(self, monkeypatch):
        """Test that is_gemini_configured returns True with valid API key."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_12345")
        assert is_gemini_configured() is True

    def test_is_gemini_configured_with_placeholder(self, monkeypatch):
        """Test that placeholder API key returns False."""
        monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")
        assert is_gemini_configured() is False

    def test_is_gemini_configured_missing(self, monkeypatch):
        """Test that missing API key returns False."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        assert is_gemini_configured() is False

    def test_get_gemini_model_name_default(self, monkeypatch):
        """Test default model name."""
        monkeypatch.delenv("GEMINI_MODEL", raising=False)
        assert get_gemini_model_name() == "gemini-2.0-flash-exp"

    def test_get_gemini_model_name_custom(self, monkeypatch):
        """Test custom model name from environment."""
        monkeypatch.setenv("GEMINI_MODEL", "gemini-custom-model")
        assert get_gemini_model_name() == "gemini-custom-model"


class TestNarrativeContextBuilding:
    """Test context building functions for LLM prompts."""

    def test_build_daily_narrative_context_basic(self):
        """Test building daily context with basic stats."""
        daily_stats = {
            "walking_minutes": 45,
            "sitting_minutes": 120,
            "standing_minutes": 30,
            "running_minutes": 0,
            "cycling_minutes": 0,
            "total_minutes": 195,
            "total_hours": 3.25,
            "total_sessions": 5,
            "activity_percentages": {
                "Walking": 23.1,
                "Sitting": 61.5,
                "Standing": 15.4,
            },
            "top_activity": "Sitting",
        }

        context = build_daily_narrative_context("2025-01-15", daily_stats)

        assert "2025-01-15" in context
        assert "45 minutes" in context
        assert "Walking" in context
        assert "Sitting: 61.5%" in context
        assert "Largest activity category: Sitting" in context

    def test_build_daily_narrative_context_with_comparison(self):
        """Test building daily context with previous day comparison."""
        daily_stats = {
            "walking_minutes": 60,
            "sitting_minutes": 100,
            "standing_minutes": 40,
            "running_minutes": 10,
            "cycling_minutes": 0,
            "total_minutes": 210,
            "total_hours": 3.5,
            "total_sessions": 6,
            "activity_percentages": {"Walking": 28.6, "Sitting": 47.6},
            "top_activity": "Sitting",
        }

        previous_stats = {
            "date": "2025-01-14",
            "walking_minutes": 45,
            "sitting_minutes": 120,
            "standing_minutes": 30,
            "running_minutes": 5,
            "cycling_minutes": 0,
        }

        context = build_daily_narrative_context("2025-01-15", daily_stats, previous_stats)

        assert "COMPARISON WITH PREVIOUS RECORDED DAY" in context
        assert "2025-01-14" in context
        assert "increased by 15 minutes" in context  # walking increase
        assert "decreased by 20 minutes" in context  # sitting decrease

    def test_build_weekly_narrative_context(self):
        """Test building weekly narrative context."""
        weekly_stats = {
            "total_walking": 300,
            "total_sitting": 600,
            "total_standing": 200,
            "total_running": 50,
            "total_cycling": 30,
            "days_with_data": 5,
            "average_daily": 236,
            "highest_walking": 80,
            "lowest_walking": 40,
            "highest_sitting": 150,
            "dates": ["2025-01-13", "2025-01-14", "2025-01-15"],
            "daily_totals": [200, 250, 230],
        }

        context = build_weekly_narrative_context("2025-01-13", weekly_stats)

        assert "2025-01-13" in context
        assert "300 minutes" in context
        assert "Days with recorded data: 5" in context
        assert "Highest walking duration: 80 minutes" in context
        assert "2025-01-13: 200 minutes recorded" in context


class TestFallbackNarratives:
    """Test fallback template narratives."""

    def test_generate_fallback_narrative_basic(self):
        """Test basic fallback narrative generation."""
        daily_stats = {
            "total_minutes": 180,
            "total_hours": 3.0,
            "total_sessions": 4,
            "walking_minutes": 60,
            "sitting_minutes": 90,
            "standing_minutes": 30,
            "running_minutes": 0,
            "cycling_minutes": 0,
            "top_activity": "Sitting",
        }

        narrative = _generate_fallback_narrative("2025-01-15", daily_stats)

        assert "2025-01-15" in narrative
        assert "180 minutes" in narrative
        assert "3.0 hours" in narrative
        assert "4 sessions" in narrative
        assert "60 minutes of walking" in narrative
        assert "Sitting accounted for the largest portion" in narrative

    def test_generate_fallback_narrative_with_comparison(self):
        """Test fallback narrative with previous day comparison."""
        daily_stats = {
            "total_minutes": 200,
            "total_hours": 3.3,
            "total_sessions": 5,
            "walking_minutes": 70,
            "sitting_minutes": 100,
            "standing_minutes": 30,
            "running_minutes": 0,
            "cycling_minutes": 0,
            "top_activity": "Sitting",
        }

        previous_stats = {
            "walking_minutes": 50,
            "sitting_minutes": 120,
            "standing_minutes": 30,
        }

        narrative = _generate_fallback_narrative("2025-01-15", daily_stats, previous_stats)

        assert "walking increased by 20 minutes" in narrative
        assert "sitting decreased by 20 minutes" in narrative

    def test_generate_fallback_weekly_narrative(self):
        """Test fallback weekly narrative generation."""
        weekly_stats = {
            "days_with_data": 5,
            "average_daily": 240,
            "total_walking": 350,
            "total_sitting": 700,
            "total_standing": 250,
            "highest_walking": 90,
            "highest_sitting": 180,
        }

        narrative = _generate_fallback_weekly_narrative("2025-01-13", weekly_stats)

        assert "2025-01-13" in narrative
        assert "5 days" in narrative
        assert "240 minutes per day" in narrative
        assert "Walking: 350 minutes" in narrative
        assert "highest walking duration was 90 minutes" in narrative


class TestNarrativeValidation:
    """Test narrative validation functions."""

    def test_validate_narrative_response_valid(self):
        """Test validation of a good narrative."""
        narrative = (
            "On January 15, 2025, you recorded 180 minutes of activity. "
            "Your day included walking for 60 minutes, sitting for 90 minutes, "
            "and standing for 30 minutes. Sitting was your most frequent activity. "
            "This represents a balanced day of recorded activities."
        )

        assert validate_narrative_response(narrative) is True

    def test_validate_narrative_response_too_short(self):
        """Test validation fails for short narratives."""
        narrative = "You walked today."
        assert validate_narrative_response(narrative) is False

    def test_validate_narrative_response_empty(self):
        """Test validation fails for empty narratives."""
        assert validate_narrative_response("") is False
        assert validate_narrative_response("   ") is False

    def test_validate_narrative_response_medical_terms(self):
        """Test validation fails for medical terminology."""
        medical_narratives = [
            "Based on your activity, I diagnose you with low activity syndrome.",
            "You should seek treatment for your sedentary behavior.",
            "This disease requires medication to treat properly.",
            "Physical therapy would help your condition.",
        ]

        for narrative in medical_narratives:
            # Pad to meet length requirement
            padded = narrative + " " * (100 - len(narrative))
            assert validate_narrative_response(padded) is False


class TestDailyNarrativeGeneration:
    """Test daily narrative generation with mocked Gemini API."""

    @patch("modules.ai_narrator.is_gemini_configured")
    def test_generate_daily_narrative_no_api_key(self, mock_configured):
        """Test fallback when API key is not configured."""
        mock_configured.return_value = False

        daily_stats = {
            "total_minutes": 150,
            "total_hours": 2.5,
            "total_sessions": 3,
            "walking_minutes": 50,
            "sitting_minutes": 80,
            "standing_minutes": 20,
            "running_minutes": 0,
            "cycling_minutes": 0,
            "top_activity": "Sitting",
        }

        response = generate_daily_narrative("2025-01-15", daily_stats)

        assert response.success is True
        assert response.model_used == "fallback_template"
        assert "2025-01-15" in response.narrative_text
        assert response.error_message is not None

    @patch("modules.ai_narrator.create_genai_client")
    @patch("modules.ai_narrator.is_gemini_configured")
    def test_generate_daily_narrative_with_gemini_success(
        self, mock_configured, mock_client
    ):
        """Test successful narrative generation with Gemini API."""
        mock_configured.return_value = True

        # Mock Gemini client and response
        mock_response = MagicMock()
        mock_response.text = (
            "On January 15, 2025, you recorded 150 minutes of activity across 3 sessions. "
            "Your day included walking for 50 minutes, sitting for 80 minutes, and standing for 20 minutes. "
            "Sitting was your most frequent activity, accounting for the majority of your recorded time. "
            "This represents a typical day of mixed activities."
        )

        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_client_instance

        daily_stats = {
            "total_minutes": 150,
            "total_hours": 2.5,
            "total_sessions": 3,
            "walking_minutes": 50,
            "sitting_minutes": 80,
            "standing_minutes": 20,
            "running_minutes": 0,
            "cycling_minutes": 0,
            "activity_percentages": {"Walking": 33.3, "Sitting": 53.3, "Standing": 13.3},
            "top_activity": "Sitting",
        }

        response = generate_daily_narrative("2025-01-15", daily_stats)

        assert response.success is True
        assert "150 minutes" in response.narrative_text
        assert mock_client_instance.models.generate_content.called

    @patch("modules.ai_narrator.create_genai_client")
    @patch("modules.ai_narrator.is_gemini_configured")
    def test_generate_daily_narrative_api_error(self, mock_configured, mock_client):
        """Test handling of API errors with fallback."""
        mock_configured.return_value = True
        mock_client.side_effect = Exception("API connection error")

        daily_stats = {
            "total_minutes": 150,
            "total_hours": 2.5,
            "total_sessions": 3,
            "walking_minutes": 50,
            "sitting_minutes": 80,
            "standing_minutes": 20,
            "running_minutes": 0,
            "cycling_minutes": 0,
            "top_activity": "Sitting",
        }

        response = generate_daily_narrative("2025-01-15", daily_stats)

        assert response.success is False
        assert response.model_used == "fallback_template"
        assert "API connection error" in response.error_message
        assert "2025-01-15" in response.narrative_text  # Fallback narrative


class TestWeeklyNarrativeGeneration:
    """Test weekly narrative generation."""

    @patch("modules.ai_narrator.is_gemini_configured")
    def test_generate_weekly_narrative_no_api_key(self, mock_configured):
        """Test fallback when API key is not configured."""
        mock_configured.return_value = False

        weekly_stats = {
            "total_walking": 300,
            "total_sitting": 500,
            "total_standing": 200,
            "total_running": 50,
            "total_cycling": 20,
            "days_with_data": 5,
            "average_daily": 214,
            "highest_walking": 80,
            "lowest_walking": 40,
            "highest_sitting": 130,
            "dates": ["2025-01-13", "2025-01-14"],
            "daily_totals": [200, 240],
        }

        response = generate_weekly_narrative("2025-01-13", weekly_stats)

        assert response.success is True
        assert response.model_used == "fallback_template"
        assert "2025-01-13" in response.narrative_text

    @patch("modules.ai_narrator.create_genai_client")
    @patch("modules.ai_narrator.is_gemini_configured")
    def test_generate_weekly_narrative_with_gemini_success(
        self, mock_configured, mock_client
    ):
        """Test successful weekly narrative generation with Gemini API."""
        mock_configured.return_value = True

        mock_response = MagicMock()
        mock_response.text = (
            "During the week of January 13, 2025, you recorded activity on 5 days. "
            "Your weekly totals included 300 minutes of walking, 500 minutes of sitting, "
            "and 200 minutes of standing. Your average daily duration was 214 minutes. "
            "The highest walking duration was 80 minutes, showing consistent movement throughout the week."
        )

        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_client_instance

        weekly_stats = {
            "total_walking": 300,
            "total_sitting": 500,
            "total_standing": 200,
            "total_running": 50,
            "total_cycling": 20,
            "days_with_data": 5,
            "average_daily": 214,
            "highest_walking": 80,
            "lowest_walking": 40,
            "highest_sitting": 130,
            "dates": ["2025-01-13", "2025-01-14"],
            "daily_totals": [200, 240],
        }

        response = generate_weekly_narrative("2025-01-13", weekly_stats)

        assert response.success is True
        assert "300 minutes" in response.narrative_text
        assert mock_client_instance.models.generate_content.called
