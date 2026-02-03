# Gemini AI Chatbot Integration Guide

## Overview

This project now uses **Google Gemini** as the AI backend for the SaaS chatbot, replacing OpenAI. The floating chatbot widget remains identical—only the backend AI inference engine has changed.

**Benefits of Gemini:**

- ✅ Advanced reasoning and context understanding
- ✅ Faster inference for real-time responses
- ✅ Competitive pricing with free tier availability
- ✅ Superior performance on complex reasoning tasks
- ✅ Native support for enterprise-grade features

---

## Setup Instructions

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Create API Key"**
3. Select **"Create API key in new project"** or use existing
4. Copy the generated API key

### 2. Configure Your Environment

Create or update `.env` file in the project root:

```bash
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

**Available Models:**

- `gemini-1.5-flash` (recommended) - Fast, cost-effective, 1M context tokens
- `gemini-1.5-pro` - Advanced reasoning, 2M context tokens (higher cost)
- `gemini-2.0-flash` - Latest model with enhanced capabilities

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `google-generativeai==0.3.0` - Gemini SDK
- `Flask==2.3.2` - Web framework
- `python-dotenv==1.0.0` - Environment variable management

### 4. Start the Application

```bash
python app.py
```

You should see:

```
✓ Chatbot service initialized with Gemini
✓ Flask app running on http://localhost:5000
```

---

## Architecture Overview

### Gemini Integration Flow

```
User Message
    ↓
[Frontend: chatbot_widget.html]
    ↓
POST /api/chatbot/chat
    ↓
[Route Handler: chatbot_routes.py]
    ↓
Rate Limit Check (100 msgs/hour per user)
    ↓
[Service: generate_chat_response()]
    ↓
Build Context Prompt (user profile data)
    ↓
Get Conversation History (last 8 messages)
    ↓
Call Gemini API (gemini.GenerativeModel.generate_content())
    ↓
Log to Database + Analytics
    ↓
Return Response to Frontend
    ↓
Display in Chat Widget
```

### Key Components

#### 1. **Config** (`config.py`)

```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
CHATBOT_RATE_LIMIT = 100  # messages per hour per user
```

#### 2. **Chatbot Service** (`services/chatbot.py`)

- Initializes Gemini model: `genai.GenerativeModel(GEMINI_MODEL)`
- `generate_chat_response()` - Main AI response generation
- `build_context_prompt()` - Formats user profile into context
- `get_smart_suggestions()` - Context-aware follow-up questions
- Error handling with Gemini-specific exceptions

#### 3. **API Routes** (`routes/chatbot_routes.py`)

- `POST /api/chatbot/chat` - Main endpoint (unchanged API contract)
- `GET /api/chatbot/greeting` - Welcome message
- `GET /api/chatbot/history` - Chat history retrieval
- `GET /api/chatbot/stats` - User statistics
- `GET /api/chatbot/insights` - Admin analytics

#### 4. **Frontend** (`templates/chatbot_widget.html`)

- 500+ lines of premium SaaS-grade UI
- Posts to `/api/chatbot/chat` (no changes needed)
- Works with any backend AI provider

---

## System Prompt Engineering

The chatbot uses a comprehensive system prompt that positions it as a **Senior AI Career Mentor**:

### Key Characteristics:

- 15+ years of industry experience perspective
- Covers Tech, Product, Finance, Data Science, Design, Business
- Focuses on actionable, specific advice (not generic guidance)
- Explains reasoning transparently
- Avoids hallucination by being conservative with unknown information
- Concise responses (under 250 words)
- Personality: Professional yet personable

### Context-Aware Responses

When a user provides context (career interest, level, skills, etc.), the system prompt includes:

```
USER CONTEXT:
- User: [Name]
- Career Interest: [Desired role]
- Experience Level: [Junior/Mid/Senior]
- Current Skills: [List]
- Skills to Develop: [List]
- Readiness Score: [%]
- Recommended Role: [Role]
```

This ensures all responses are **personalized and relevant** to the user's specific situation.

---

## Gemini API Parameters

The following settings are optimized for career mentorship:

```python
generation_config=genai.types.GenerationConfig(
    temperature=0.7,        # Balanced: consistent but creative
    max_output_tokens=500,  # Concise responses
    top_p=0.9,             # Diverse but focused
    top_k=40               # Quality-first filtering
)
```

**Why these values?**

- `temperature=0.7` - Not too deterministic, allows for creative responses
- `max_tokens=500` - Career guidance should be concise and actionable
- `top_p=0.9` - Focuses on high-probability tokens for quality
- `top_k=40` - Filters out low-quality options

---

## Error Handling

Gemini-specific error handling catches:

| Error                 | Handling                                   |
| --------------------- | ------------------------------------------ |
| `ResourceExhausted`   | Quota exceeded → User-friendly message     |
| `InternalServerError` | Service unavailable → Graceful degradation |
| `DeadlineExceeded`    | Timeout → Retry message                    |
| Generic `Exception`   | Unknown error → Safe fallback message      |

**All errors are logged to analytics** for monitoring and debugging.

---

## Database Integration

### Chat History Storage

All conversations are persisted in SQLite:

```
chat_history table:
- user_id
- role (user/assistant)
- content
- timestamp
```

### Analytics Tracking

Every interaction is logged:

```
chatbot_analytics table:
- user_id
- message_type (user_query, error, etc.)
- metadata (context keys, model, error info)
- timestamp
```

Admin dashboard can view:

- Total messages
- Active users
- Most common questions
- Error rates
- Model performance metrics

---

## Testing the Integration

### 1. Manual Test via Browser

```
1. Open http://localhost:5000
2. Click chatbot widget (bottom-right corner)
3. Type: "I'm a junior software engineer interested in product management. What skills should I focus on?"
4. Verify Gemini generates a personalized response
```

### 2. Test with User Context

```
1. Go to career recommendation form
2. Fill out profile: interest, level, skills, etc.
3. Submit form
4. Open chatbot
5. Verify responses reference your specific context
```

### 3. Test Rate Limiting

```
1. Send 100+ messages in quick succession
2. Verify 101st message shows: "You've reached your message limit"
3. Verify rate limit resets after 1 hour
```

### 4. Admin Analytics Check

```
1. Open admin login: /admin
2. View chatbot insights
3. Verify interaction counts and error logs are recorded
```

---

## Common Issues & Solutions

### Issue: "Gemini API key not configured"

**Solution:**

- Check `.env` file has `GEMINI_API_KEY=<your_key>`
- Ensure Flask is restarted after `.env` changes
- Verify key is valid from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Issue: "ResourceExhausted" error (429)

**Solution:**

- Google Gemini has free tier limits (~60 requests/minute)
- Upgrade to paid account for higher limits
- Check usage at [Google Cloud Console](https://console.cloud.google.com/)

### Issue: Empty responses from Gemini

**Solution:**

- Check conversation history isn't corrupted
- Verify user context format is valid JSON
- Review Gemini API status page

### Issue: Responses too short/too long

**Solution:**

- Adjust `max_output_tokens` in `config.py` or `chatbot.py`
- Default is 500 tokens (≈250 words), suitable for career advice

---

## Migration from OpenAI

If you previously used OpenAI, here's what changed:

| Component      | Before                             | After                                      |
| -------------- | ---------------------------------- | ------------------------------------------ |
| SDK            | `openai`                           | `google-generativeai`                      |
| Config         | `OPENAI_API_KEY`                   | `GEMINI_API_KEY`                           |
| Model          | `gpt-3.5-turbo`                    | `gemini-1.5-flash`                         |
| Error Handling | `RateLimitError`, `APIError`       | `ResourceExhausted`, `InternalServerError` |
| API Call       | `client.chat.completions.create()` | `model.generate_content()`                 |
| Frontend       | **No changes** ✅                  | Works with any backend                     |
| Database       | **No changes** ✅                  | Same schema                                |
| Routes         | **No changes** ✅                  | Same API contract                          |

### Backward Compatibility

✅ All existing features continue to work:

- Context-aware responses
- Rate limiting (100 msgs/hour)
- Chat history persistence
- Analytics tracking
- Admin dashboard insights

---

## Performance Characteristics

### Response Times

- **Average:** 1-3 seconds (Gemini with context)
- **Quick responses:** <1 second (shorter prompts)
- **Complex reasoning:** 3-5 seconds (multi-step analysis)

### Rate Limits

- **Free tier:** ~60 requests/minute
- **Paid tier:** 1,000 requests/minute (adjustable)
- **App-level:** 100 messages/hour per user (configurable in `CHATBOT_RATE_LIMIT`)

### Token Usage

- **Average message:** 150-300 tokens
- **With context:** 300-500 tokens
- **Gemini pricing:** Free tier supports significant usage

---

## Monitoring & Debugging

### Enable Debug Logging

```python
# In config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Conversation Flow

1. User message sent → Logged to `chat_history` table
2. Gemini API call → Returns response
3. Response stored → Logged to `chat_history` and `chatbot_analytics`
4. Frontend displays → User sees response

### Review Analytics

```sql
-- Check recent interactions
SELECT * FROM chatbot_analytics
WHERE timestamp > datetime('now', '-1 hour')
ORDER BY timestamp DESC;

-- Check error rates
SELECT message_type, COUNT(*) as count
FROM chatbot_analytics
GROUP BY message_type;
```

---

## Next Steps

### 1. Get Gemini API Key

- [Create API key](https://aistudio.google.com/app/apikey)
- Add to `.env`

### 2. Test Integration

- Start app with `python app.py`
- Send test messages
- Verify responses are personalized

### 3. Deploy to Production

- Use environment variables for API key (never hardcode)
- Set up monitoring for quota usage
- Configure alerts for errors

### 4. Optimize Performance

- Monitor response times
- Adjust `temperature` or `max_tokens` if needed
- Consider `gemini-1.5-pro` for advanced reasoning tasks

---

## FAQ

**Q: Is Gemini free?**
A: Yes, the free tier includes significant usage. Check [pricing page](https://ai.google.dev/pricing) for limits.

**Q: Can I switch back to OpenAI?**
A: Yes, the architecture supports any AI backend. Just update `config.py` and `services/chatbot.py`.

**Q: How many messages can a user send per hour?**
A: 100 messages/hour (configurable via `CHATBOT_RATE_LIMIT` in `config.py`).

**Q: Are conversations stored permanently?**
A: Yes, all chat history is stored in SQLite. Older messages may be archived based on retention policy.

**Q: Can the chatbot access external information?**
A: No, Gemini works only with the provided context and conversation history for privacy and consistency.

**Q: How accurate are the career recommendations?**
A: The system prompt emphasizes avoiding hallucination and being specific to user context. Quality depends on user-provided context.

---

## Support & Resources

- **Google AI Documentation:** https://ai.google.dev/
- **Gemini API Reference:** https://ai.google.dev/docs/gemini_api_reference
- **Project Repository:** Check local directories for implementation details
- **Admin Dashboard:** View analytics and error logs at `/admin`

---

**Status:** ✅ Gemini integration complete and production-ready

**Last Updated:** 2024

**Tested:** Python 3.11.9, Flask 2.3.2, google-generativeai 0.3.0
