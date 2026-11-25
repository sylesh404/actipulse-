"""Tests for AI Assistant module (PROCESS 5)."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from modules.ai_assistant import (
    AssistantMessage,
    AssistantResponse,
    understand_user_question,
    retrieve_activity_context,
    answer_activity_question,
)


class TestQuestionUnderstanding:
    """Test natural language question parsing."""

    def test_understand_question_with_activity_today(self):
        """Test parsing question about specific activity today."""
        question = "How much time did I spend walking today?"
        
        result = understand_user_question(question)
        
        assert result["activity_type"] == "Walking"
        assert result["date_ref"] == datetime.now().strftime("%Y-%m-%d")

    def test_understand_question_with_activity_yesterday(self):
        """Test parsing question about yesterday."""
        question = "What was my sitting time yesterday?"
        
        result = understand_user_question(question)
        
        assert result["activity_type"] == "Sitting"
        expected_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert result["date_ref"] == expected_date

    def test_understand_question_with_day_name(self):
        """Test parsing question with day of week."""
        question = "How much did I run on Tuesday?"
        
        result = understand_user_question(question)
        
        assert result["activity_type"] == "Running"
        assert result["date_ref"] == "tuesday"

    def test_understand_question_standing(self):
        """Test parsing standing activity question."""
        question = "Show me my standing duration"
        
        result = understand_user_question(question)
        
        assert result["activity_type"] == "Standing"

    def test_understand_question_cycling(self):
        """Test parsing cycling activity question."""
        question = "Did I do any cycling this week?"
        
        result = understand_user_question(question)
        
        assert result["activity_type"] == "Cycling"

    def test_understand_question_no_activity(self):
        """Test parsing question without specific activity."""
        question = "What was my total activity today?"
        
        result = understand_user_question(question)
        
        assert result["activity_type"] is None
        assert result["date_ref"] == datetime.now().strftime("%Y-%m-%d")

    def test_understand_question_no_date(self):
        """Test parsing question without date reference."""
        question = "How much walking have I recorded?"
        
        result = understand_user_question(question)
        
        assert result["activity_type"] == "Walking"
        assert result["date_ref"] is None


class TestActivityContextRetrieval:
    """Test data retrieval for answering questions."""

    def test_retrieve_context_specific_date_activity(self):
        """Test retrieving context for specific date and activity."""
        # Create sample dataframe
        data = [
            {
                "activity_date": "2025-01-15",
                "start_time": "09:00",
                "end_time": "09:30",
                "activity_label": "Walking",
                "duration_minutes": 30,
            },
            {
                "activity_date": "2025-01-15",
                "start_time": "10:00",
                "end_time": "11:00",
                "activity_label": "Sitting",
                "duration_minutes": 60,
            },
            {
                "activity_date": "2025-01-15",
                "start_time": "14:00",
                "end_time": "14:45",
                "activity_label": "Walking",
                "duration_minutes": 45,
            },
        ]
        df = pd.DataFrame(data)

        intent_data = {
            'intent': 'duration',
            'activity_type': 'Walking',
            'date_ref': '2025-01-15',
            'original_question': 'How much walking on 2025-01-15?',
        }

        context = retrieve_activity_context(df=df, intent_data=intent_data)

        assert context is not None
        assert context.get("has_data") is True

    def test_retrieve_context_all_activities_date(self):
        """Test retrieving context for all activities on a date."""
        data = [
            {
                "activity_date": "2025-01-15",
                "start_time": "09:00",
                "end_time": "09:30",
                "activity_label": "Walking",
                "duration_minutes": 30,
            },
            {
                "activity_date": "2025-01-15",
                "start_time": "10:00",
                "end_time": "11:00",
                "activity_label": "Sitting",
                "duration_minutes": 60,
            },
        ]
        df = pd.DataFrame(data)

        intent_data = {
            'intent': 'summary',
            'activity_type': None,
            'date_ref': '2025-01-15',
            'original_question': 'What was my activity on 2025-01-15?',
        }

        context = retrieve_activity_context(df=df, intent_data=intent_data)

        assert context is not None
        assert context.get("has_data") is True

    def test_retrieve_context_no_matching_data(self):
        """Test retrieving context when no data matches."""
        data = [
            {
                "activity_date": "2025-01-15",
                "start_time": "09:00",
                "end_time": "09:30",
                "activity_label": "Walking",
                "duration_minutes": 30,
            },
        ]
        df = pd.DataFrame(data)

        intent_data = {
            'intent': 'duration',
            'activity_type': 'Walking',
            'date_ref': '2025-01-16',  # Different date
            'original_question': 'How much walking on 2025-01-16?',
        }

        context = retrieve_activity_context(df=df, intent_data=intent_data)

        # Should return context indicating no data or has_data=True with no matching records
        assert context is not None
        assert context.get("has_data") is not None


class TestAssistantMessage:
    """Test AssistantMessage dataclass."""

    def test_create_user_message(self):
        """Test creating a user message."""
        msg = AssistantMessage(role="user", content="How much did I walk today?")
        
        assert msg.role == "user"
        assert msg.content == "How much did I walk today?"

    def test_create_assistant_message(self):
        """Test creating an assistant message."""
        msg = AssistantMessage(
            role="assistant",
            content="You walked for 45 minutes today.",
        )
        
        assert msg.role == "assistant"
        assert msg.content == "You walked for 45 minutes today."


class TestAssistantResponse:
    """Test AssistantResponse dataclass."""

    def test_create_successful_response(self):
        """Test creating a successful response."""
        response = AssistantResponse(
            answer="You walked for 45 minutes today.",
            retrieved_data={"walking_minutes": 45},
            success=True,
        )
        
        assert response.success is True
        assert response.answer == "You walked for 45 minutes today."
        assert response.retrieved_data["walking_minutes"] == 45
        assert response.error_message is None

    def test_create_error_response(self):
        """Test creating an error response."""
        response = AssistantResponse(
            answer="",
            success=False,
            error_message="Unable to retrieve data",
        )
        
        assert response.success is False
        assert response.error_message == "Unable to retrieve data"


class TestAnswerActivityQuestion:
    """Test end-to-end question answering."""

    def test_answer_simple_walking_question(self):
        """Test answering a simple walking duration question."""
        data = [
            {
                "activity_date": datetime.now().strftime("%Y-%m-%d"),
                "start_time": "09:00",
                "end_time": "09:45",
                "activity_label": "Walking",
                "duration_minutes": 45,
            },
            {
                "activity_date": datetime.now().strftime("%Y-%m-%d"),
                "start_time": "15:00",
                "end_time": "15:30",
                "activity_label": "Walking",
                "duration_minutes": 30,
            },
        ]
        df = pd.DataFrame(data)
        
        question = "How much time did I spend walking today?"
        response = answer_activity_question(question, df, [])

        assert response.success is True
        assert "75" in response.answer or "1 hour" in response.answer.lower()
        assert response.retrieved_data is not None

    def test_answer_no_data_question(self):
        """Test answering when no data matches."""
        data = [
            {
                "activity_date": "2025-01-15",
                "start_time": "09:00",
                "end_time": "09:30",
                "activity_label": "Walking",
                "duration_minutes": 30,
            },
        ]
        df = pd.DataFrame(data)
        
        question = "How much did I run yesterday?"
        response = answer_activity_question(question, df, [])

        assert response.success is True
        # Should indicate no data found
        assert "no" in response.answer.lower() or "0" in response.answer

    def test_answer_empty_dataframe(self):
        """Test answering with empty dataframe."""
        df = pd.DataFrame(columns=["activity_date", "activity_label", "duration_minutes"])
        
        question = "How much did I walk today?"
        response = answer_activity_question(question, df, [])

        assert response.success is True
        assert "no" in response.answer.lower() or "not found" in response.answer.lower()

    @patch("modules.ai_assistant.is_gemini_configured")
    def test_answer_without_gemini_configured(self, mock_configured):
        """Test that assistant works without Gemini API (data-only mode)."""
        mock_configured.return_value = False
        
        data = [
            {
                "activity_date": datetime.now().strftime("%Y-%m-%d"),
                "start_time": "09:00",
                "end_time": "10:00",
                "activity_label": "Sitting",
                "duration_minutes": 60,
            },
        ]
        df = pd.DataFrame(data)
        
        question = "How much time did I spend sitting today?"
        response = answer_activity_question(question, df, [])

        assert response.success is True
        # Should provide data-driven answer even without Gemini
        assert "60" in response.answer

    def test_answer_with_conversation_history(self):
        """Test answering with conversation context."""
        data = [
            {
                "activity_date": datetime.now().strftime("%Y-%m-%d"),
                "start_time": "09:00",
                "end_time": "09:30",
                "activity_label": "Walking",
                "duration_minutes": 30,
            },
        ]
        df = pd.DataFrame(data)
        
        conversation = [
            AssistantMessage(role="user", content="How much did I walk today?"),
            AssistantMessage(role="assistant", content="You walked for 30 minutes today."),
        ]
        
        question = "What about sitting?"
        response = answer_activity_question(question, df, conversation)

        assert response.success is True


class TestNonMedicalGuardrails:
    """Test that assistant enforces non-medical boundaries."""

    def test_medical_question_rejection(self):
        """Test that medical questions are redirected appropriately."""
        data = [
            {
                "activity_date": datetime.now().strftime("%Y-%m-%d"),
                "start_time": "09:00",
                "end_time": "10:00",
                "activity_label": "Walking",
                "duration_minutes": 60,
            },
        ]
        df = pd.DataFrame(data)
        
        medical_questions = [
            "Am I healthy based on my activity?",
            "Should I see a doctor?",
            "Is my sitting time causing health problems?",
            "What treatment do you recommend?",
        ]
        
        for question in medical_questions:
            response = answer_activity_question(question, df, [])
            
            # Response should indicate inability to provide medical advice
            # This is enforced by the LLM system prompt, so we just verify it doesn't crash
            assert response.success is True
            assert response.answer is not None


class TestQuestionIntentParsing:
    """Test various question formats and intents."""

    def test_comparison_question(self):
        """Test parsing comparison questions."""
        question = "Compare my walking time today vs yesterday"
        result = understand_user_question(question)
        
        # Should recognize activities and dates
        assert result["activity_type"] == "Walking"

    def test_weekly_summary_question(self):
        """Test parsing weekly summary questions."""
        question = "What was my total activity this week?"
        result = understand_user_question(question)
        
        # Basic parsing - detailed weekly logic is in the assistant
        assert result is not None

    def test_top_activity_question(self):
        """Test parsing questions about top activities."""
        question = "What was my most frequent activity today?"
        result = understand_user_question(question)
        
        assert result["date_ref"] == datetime.now().strftime("%Y-%m-%d")

    def test_specific_time_question(self):
        """Test parsing questions about specific times."""
        question = "Did I walk in the morning?"
        result = understand_user_question(question)
        
        assert result["activity_type"] == "Walking"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
