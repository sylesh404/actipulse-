# PROCESS 5 Quick Start Guide

## 🎉 AI-Powered Activity Diary & Assistant

ActiPulse AI now includes intelligent AI features powered by Google's Gemini API!

---

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install google-genai
```

### 2. Configure API Key

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Add to `.env` file:

```env
GEMINI_API_KEY=AIza...your_actual_key_here
GEMINI_MODEL=gemini-2.0-flash-exp  # Optional
```

3. Restart Streamlit:

```bash
streamlit run app.py
```

### 3. Start Using AI Features

**Page 5: AI Activity Diary**
- Navigate to "📝 AI Activity Diary"
- Select a date with recorded activity
- Choose narrative tone
- Click "Generate Narrative"
- View your personalized daily diary entry!

**Page 6: AI Assistant**
- Navigate to "💬 AI Assistant"
- Ask questions like:
  - "How much time did I spend walking today?"
  - "What was my sitting time yesterday?"
  - "Show me my standing duration on Monday"
- Get instant answers grounded in your data!

---

## Features at a Glance

### ✨ AI Activity Diary
- 📅 Daily diary entries with natural language narratives
- 📊 Weekly summaries with pattern analysis
- 🎨 3 narrative tones: Reflective, Casual, Professional
- 📈 Automatic previous-day comparisons
- 🔄 Fallback templates when API unavailable

### 💬 AI Assistant
- 🗣️ Natural language question answering
- 📊 Data-grounded responses (no invented numbers!)
- 🧠 Conversation history (last 10 messages)
- 💡 Suggested questions
- 🔍 Retrieved data display for transparency

### 🛡️ Safety Features
- ✅ 10-point non-medical guardrail system
- ✅ No diagnoses, health assessments, or medical advice
- ✅ Narrative validation for medical terms
- ✅ Disclaimer on all AI pages
- ✅ Python-first analytics (LLM never invents numbers)

---

## Usage Examples

### Daily Narrative Example

**Input:**
- Date: 2025-01-24
- Tone: Reflective & Clear

**Output:**
```
On January 24, 2025, you recorded 180 minutes (3.0 hours) of activity 
across 4 sessions. Your day included walking for 60 minutes, sitting 
for 90 minutes, and standing for 30 minutes. Sitting accounted for 
the largest portion of your recorded activity duration, representing 
50% of your total time.

Compared with your previous recorded day, walking increased by 
15 minutes while sitting decreased by 20 minutes. This shift suggests 
a slightly more active pattern than the day before.
```

### Assistant Q&A Example

**Question:** "How much time did I spend walking today?"

**Answer:**
```
You walked for 75 minutes today across 2 sessions. This represents 
35% of your total recorded activity time for the day.
```

**Retrieved Data:**
```json
{
  "walking_minutes": 75,
  "session_count": 2,
  "percentage_of_total": 35.0,
  "date": "2025-01-24"
}
```

---

## Fallback Mode (No API Key Required)

If you don't have a Gemini API key:
- ✅ Application still works fully
- ✅ Template-based narratives provided
- ✅ Data retrieval and analysis functional
- ✅ Assistant provides data-only responses
- ⚠️ Warning banners displayed
- 📝 All features remain accessible

---

## Troubleshooting

### "Gemini API Not Configured" Warning

**Solution:** Add `GEMINI_API_KEY` to `.env` file and restart Streamlit.

### "API Connection Error"

**Check:**
1. API key is valid and not expired
2. Internet connection is working
3. No firewall blocking Google API domains

**Workaround:** Fallback templates used automatically

### Empty Narratives

**Check:**
1. Selected date has recorded activity data
2. Database contains activity records
3. Upload activity data first (Page 2)

---

## Best Practices

### For Daily Narratives
1. Upload activity data regularly
2. Generate narratives after each day
3. Try different tones for variety
4. Review previous-day comparisons for trends

### For AI Assistant
1. Ask specific questions about dates and activities
2. Use suggested questions as templates
3. Review retrieved data for accuracy
4. Clear conversation when switching topics

### For Data Quality
1. Upload complete activity records
2. Avoid gaps in data
3. Use consistent activity labels
4. Verify uploaded data in Analytics page

---

## Privacy & Security

- ✅ API key stored locally in `.env` (never committed)
- ✅ Only activity statistics sent to Gemini (no personal data)
- ✅ No conversation history stored externally
- ✅ Generated narratives not saved to cloud
- ✅ All processing local except LLM API calls

**Data Sent to Gemini:**
- Activity durations (numbers only)
- Activity labels (walking, sitting, etc.)
- Dates (YYYY-MM-DD format)

**Data NOT Sent:**
- User identity
- Location data
- Contact information
- Full activity logs

---

## Performance Tips

### Faster Response Times
- Use fallback templates (instant responses)
- Clear conversation history regularly
- Ask focused, specific questions
- Avoid overly complex queries

### Better Narratives
- Ensure complete data for selected dates
- Include previous day data for comparisons
- Use weekly summaries for broader insights
- Experiment with different tones

---

## Technical Details

**Model:** gemini-2.0-flash-exp (default)  
**Temperature:** 0.7 (narratives), 0.5 (assistant)  
**Max Tokens:** 800 (daily), 1000 (weekly), 300 (assistant)  
**Context:** Data-grounded using Python analytics  
**Fallback:** Template-based narratives  

**System Prompt:**
- 10-point non-medical guardrail
- Enforced at every API call
- Prevents medical advice/diagnoses
- Ensures factual descriptions only

---

## Support

**Documentation:**
- `PROCESS5_COMPLETION_REPORT.md` - Full technical details
- `README.md` - Application overview
- `.env.example` - Configuration template

**Testing:**
```bash
python -m pytest tests/test_ai_narrator.py -v  # 20 tests
python -m pytest tests/test_ai_assistant.py -v  # 24 tests
python test_process5_integration.py  # Quick integration check
```

**Common Issues:**
1. "ModuleNotFoundError: google.genai" → Run `pip install google-genai`
2. "API Key Not Set" → Add `GEMINI_API_KEY` to `.env`
3. "No data found" → Upload activity records first

---

## Next Steps

1. ✅ Upload activity data (Page 2)
2. ✅ View analytics (Page 3)
3. ✅ Generate AI diary entries (Page 5)
4. ✅ Ask AI assistant questions (Page 6)
5. 🔜 Export reports (Page 7 - Coming in PROCESS 6)

---

## Feedback

The AI features are designed to be:
- **Safe:** No medical advice, strict guardrails
- **Accurate:** Python-first analytics, grounded responses
- **Transparent:** Retrieved data always visible
- **Reliable:** Fallback templates when API unavailable

Enjoy your AI-powered activity diary! 🎉

---

**Version:** 1.0.0 (PROCESS 5 Complete)  
**Last Updated:** January 24, 2025  
**Status:** ✅ Production Ready
