# Multi-LLM Integration - Quick Start Guide

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Install Groq SDK (already in requirements.txt)
pip install groq
```

### Step 2: Configure API Keys

#### Option A: Groq Only (Recommended for Testing)

1. Get a free API key from [Groq Console](https://console.groq.com)
2. Edit `.env` file:

```env
GROQ_API_KEY=your_actual_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
AI_PROVIDER=groq
```

#### Option B: Gemini Only

1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Edit `.env` file:

```env
GEMINI_API_KEY=your_actual_gemini_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
AI_PROVIDER=gemini
```

#### Option C: Both (Recommended for Production)

```env
# Groq Configuration
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Gemini Configuration
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Auto mode (tries Groq first, falls back to Gemini)
AI_PROVIDER=auto
```

### Step 3: Test Provider Manager

```bash
python test_llm_provider.py
```

**Expected Output:**
```
Testing LLM Provider Manager...
✅ LLM Manager initialized successfully

📊 Provider Status:
  Groq: ✅ Configured
  Gemini: ✅ Configured

🎯 Active Provider: AUTO

🧪 Testing generation...
✅ Generation successful!
  Provider: groq
  Model: llama-3.3-70b-versatile
  Response: Hello from ActiPulse AI! ...

✨ Test complete!
```

### Step 4: Launch Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🎯 Testing the Features

### 1. AI Settings Page

Navigate to **⚙️ AI Settings** in the sidebar.

**What to Test:**
- [ ] Provider status shows correctly (Connected/Not Configured)
- [ ] Current provider is displayed
- [ ] Can switch between auto/groq/gemini
- [ ] "Test Groq Connection" button works
- [ ] "Test Gemini Connection" button works
- [ ] Provider selection persists after refresh

**Expected Behavior:**
- Configured providers show ✅ Connected
- Unconfigured providers show ❌ Not Configured
- Connection tests perform real API requests
- Provider switch updates .env file

### 2. AI Activity Diary (Enhanced)

Navigate to **📝 AI Activity Diary**.

**What to Test:**
- [ ] Generate daily narrative
- [ ] Check "Provider used" in response
- [ ] Generate weekly summary
- [ ] Try different narrative tones
- [ ] Switch provider and regenerate

**Current Implementation:**
- Uses original `ai_narrator.py` (Gemini only)
- **TODO**: Update to use `ai_narrator_v2.py` (multi-LLM)

### 3. AI Assistant (Agent)

Navigate to **💬 AI Assistant**.

**What to Test:**
- [ ] Ask: "How much time did I spend walking yesterday?"
- [ ] Ask: "Compare my sitting time between today and yesterday"
- [ ] Ask: "What was my most frequent activity this week?"
- [ ] Check if conversation context works
- [ ] Verify tool results (if shown)

**Current Implementation:**
- Uses original `ai_assistant.py`
- **TODO**: Update to use `ai_agent.py` (tool-based with multi-LLM)

---

## 🧪 Testing Scenarios

### Scenario 1: Groq Only

```env
GROQ_API_KEY=<your_key>
AI_PROVIDER=groq
```

**Expected:**
- All AI features use Groq
- Fast responses (Groq is very fast)
- Provider shows as "groq" in responses

### Scenario 2: Gemini Only

```env
GEMINI_API_KEY=<your_key>
AI_PROVIDER=gemini
```

**Expected:**
- All AI features use Gemini
- Slightly slower but high quality
- Provider shows as "gemini" in responses

### Scenario 3: Auto Mode (Both Configured)

```env
GROQ_API_KEY=<your_key>
GEMINI_API_KEY=<your_key>
AI_PROVIDER=auto
```

**Expected:**
- Features try Groq first
- Falls back to Gemini if Groq fails
- Provider shows which one was used

### Scenario 4: No API Keys

```env
# All keys commented out or set to placeholders
```

**Expected:**
- Features use template fallbacks
- Provider shows as "fallback_template"
- App still works, just without AI-generated text

---

## 🔧 Troubleshooting

### Issue: "Provider not configured"

**Solution:**
1. Check `.env` file has correct API key
2. Restart the application
3. API key should NOT be `your_..._api_key_here`

### Issue: "Connection test failed"

**Possible Causes:**
- Invalid API key
- Network issues
- API rate limit reached
- Provider service down

**Solution:**
1. Verify API key is correct
2. Check [Groq Status](https://status.groq.com)
3. Check [Google Status](https://status.cloud.google.com)
4. Try the other provider

### Issue: "Empty response from API"

**Solution:**
- Check API key permissions
- Verify model name is correct
- Try reducing max_tokens parameter
- Check provider documentation

### Issue: Streamlit won't start

**Solution:**
```bash
# Check if already running
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"}

# Kill if needed
Stop-Process -Name streamlit -Force

# Restart
streamlit run app.py
```

---

## 📊 Performance Comparison

Based on typical usage:

| Provider | Speed | Quality | Free Tier | Best For |
|----------|-------|---------|-----------|----------|
| **Groq** | ⚡⚡⚡ Very Fast | ⭐⭐⭐ Good | ✅ Generous | Quick responses, high throughput |
| **Gemini** | ⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | ✅ Available | Complex reasoning, accuracy |
| **Auto** | ⚡⚡⚡/⚡⚡ | ⭐⭐⭐⭐ | ✅ Best of both | Production use, reliability |

**Recommendation:** Use **Auto mode** for best experience.

---

## 🎓 Key Features

### 1. Automatic Failover

```
User Request
    ↓
Try Groq
    ↓
Success? → Return Response
    ↓
No? → Try Gemini
    ↓
Success? → Return Response
    ↓
No? → Return Template
```

### 2. Tool-Based Agent

The new AI Agent uses verified database tools:

```python
# Tools available:
- get_available_dates()
- get_activity_records(date)
- get_daily_summary(date)
- get_activity_duration(date, activity)
- compare_days(date1, date2)
- get_weekly_summary(start_date)
- get_activity_distribution(date)
- get_most_recorded_activity(date)
```

**Benefits:**
- No hallucinations (data from database)
- Precise answers
- Traceable results
- Safe execution

### 3. Provider Metadata

Every AI response includes:
- `provider_used` - Which provider generated it
- `model_used` - Specific model name
- `success` - Whether generation succeeded
- `error_message` - If failed, why

---

## 📝 Configuration Reference

### Complete .env Template

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# AI Provider Selection (auto, groq, gemini)
AI_PROVIDER=auto

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
DATABASE_PATH=data/actipulse.db
```

### Available Models

**Groq:**
- `llama-3.3-70b-versatile` (Recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

**Gemini:**
- `gemini-2.0-flash-exp` (Recommended - latest)
- `gemini-1.5-flash`
- `gemini-1.5-pro`

---

## 🎯 Next Steps

1. **Configure API Keys** - Set up at least one provider
2. **Test Provider Manager** - Run `python test_llm_provider.py`
3. **Launch App** - Start Streamlit with `streamlit run app.py`
4. **Test AI Settings** - Verify connections and switching
5. **Try AI Features** - Generate narratives and ask questions

---

## 📧 Getting API Keys

### Groq (Free)

1. Visit https://console.groq.com
2. Sign up with email or GitHub
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy and paste into `.env`

**Free Tier:**
- Generous rate limits
- No credit card required
- Production-ready

### Google Gemini (Free)

1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Select or create project
5. Copy and paste into `.env`

**Free Tier:**
- 60 requests per minute
- No credit card required
- Suitable for testing and small-scale use

---

## ✨ Success Checklist

- [ ] Groq SDK installed
- [ ] API keys configured in `.env`
- [ ] `test_llm_provider.py` runs successfully
- [ ] Application starts without errors
- [ ] AI Settings page loads
- [ ] Provider status shows correctly
- [ ] Connection tests work
- [ ] Can switch providers
- [ ] AI features generate responses
- [ ] Provider metadata displayed

---

**Happy Testing! 🎉**

For issues or questions, check `AI_INTEGRATION_STATUS.md` for detailed status.
