# AI Chatbot SaaS Setup Guide

## Overview

Your Smart Career Assistant now includes an AI-powered chatbot that provides real-time career guidance using OpenAI's GPT models. This is a SaaS-ready implementation with usage tracking, rate limiting, and multi-user support.

## Features

✅ **OpenAI Integration** - Uses GPT-3.5-turbo (configurable to GPT-4)
✅ **SaaS Ready** - Multi-user support with unique session IDs
✅ **Rate Limiting** - Prevents abuse (configurable per user)
✅ **Chat History** - Stores conversations in SQLite for each user
✅ **Context-Aware** - Uses user profile data for personalized responses
✅ **Modern UI** - Beautiful, responsive chat interface
✅ **Usage Analytics** - Track conversations for SaaS metrics

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The following packages were added:

- `openai==1.3.0` - OpenAI API client
- `python-dotenv==1.0.0` - Environment variable management

### 2. Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Create a new API key
4. Copy the key (you won't see it again!)

### 3. Configure Environment Variables

Create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
CHATBOT_MAX_HISTORY=20
CHATBOT_RATE_LIMIT=100
```

Or copy from the example:

```bash
cp .env.example .env
# Then edit .env with your API key
```

### 4. Start Your Application

```bash
python app.py
```

### 5. Access the Chatbot

Open your browser and navigate to:

```
http://localhost:5000/chatbot
```

## API Endpoints

### Send Message

```
POST /api/chatbot/message
Content-Type: application/json

{
    "message": "What should I learn for a data science career?",
    "user_context": {
        "name": "John",
        "interest": "Data Science",
        "level": "Intermediate",
        "known_skills": "Python, SQL"
    }
}

Response:
{
    "success": true,
    "message": "AI response here...",
    "tokens_used": 150
}
```

### Get Chat History

```
GET /api/chatbot/history?limit=20

Response:
{
    "success": true,
    "messages": [
        {
            "role": "user",
            "content": "Question...",
            "created_at": "2024-01-22 10:30:00"
        },
        {
            "role": "assistant",
            "content": "Answer...",
            "created_at": "2024-01-22 10:30:15"
        }
    ]
}
```

### Get Greeting

```
GET /api/chatbot/greeting

Response:
{
    "success": true,
    "message": "Hi there! I'm your AI Career Assistant..."
}
```

### Get User Statistics

```
GET /api/chatbot/stats

Response:
{
    "success": true,
    "stats": {
        "user_message_count": 42
    },
    "user_id": "user_abc123..."
}
```

### Clear Chat History

```
POST /api/chatbot/clear

Response:
{
    "success": true,
    "message": "Chat history cleared"
}
```

## How It Works

### 1. User Messages

- User sends a message through the web interface
- Message is validated (min 3 chars, max 2000 chars)
- Rate limiting checks if user hasn't exceeded 100 messages/hour

### 2. AI Processing

- Message is sent to OpenAI API with conversation history
- System prompt ensures career-focused responses
- User context (profile) is included for personalization

### 3. Data Storage

- User message stored in `chat_history` table
- AI response stored in `chat_history` table
- Each message linked to unique user ID (session-based)
- Timestamp recorded for analytics

### 4. Response Delivery

- AI response sent back to client
- Chat history updated in real-time
- Message count tracked for SaaS billing

## Database Schema

New table created: `chat_history`

```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,          -- Unique user identifier
    role TEXT NOT NULL,              -- 'user' or 'assistant'
    content TEXT NOT NULL,           -- Message content
    created_at TEXT NOT NULL        -- Timestamp
);

-- Index for faster queries
CREATE INDEX idx_user_created ON chat_history(user_id, created_at);
```

## SaaS Features

### Usage Tracking

Track conversations for each user:

```python
from database.models import get_chat_statistics
stats = get_chat_statistics(user_id="user_123")
# Returns: {'user_message_count': 42}
```

### Rate Limiting

- Default: 100 messages per 60 minutes per user
- Configurable via `CHATBOT_RATE_LIMIT` environment variable
- Returns 429 status code when exceeded

### Multi-User Support

- Each user gets unique session ID
- Complete conversation isolation
- User data never mixed between sessions

## Configuration Options

| Variable              | Default       | Description                    |
| --------------------- | ------------- | ------------------------------ |
| `OPENAI_API_KEY`      | -             | Your OpenAI API key (required) |
| `OPENAI_MODEL`        | gpt-3.5-turbo | Model to use (gpt-4 available) |
| `CHATBOT_MAX_HISTORY` | 20            | Messages to include in context |
| `CHATBOT_RATE_LIMIT`  | 100           | Messages per hour per user     |

## Cost Optimization

### Using GPT-3.5-turbo (Recommended for SaaS)

- Cost: ~$0.002 per 1K tokens
- Speed: Very fast
- Quality: Excellent for career guidance

### Using GPT-4

- Cost: ~$0.03 per 1K tokens
- Speed: Slower
- Quality: Superior reasoning

To switch models:

```
OPENAI_MODEL=gpt-4
```

## Production Deployment

### For Production:

1. Set strong `SECRET_KEY` in environment
2. Use Redis for rate limiting (instead of in-memory)
3. Add API authentication to endpoints
4. Implement usage billing/quotas
5. Add request logging and monitoring
6. Use environment variables for all secrets
7. Consider OpenAI's enterprise plan for high volume

### Example .env for Production:

```
OPENAI_API_KEY=sk-prod-key-here
OPENAI_MODEL=gpt-3.5-turbo
CHATBOT_RATE_LIMIT=500
SECRET_KEY=<generate-strong-random-key>
```

## Troubleshooting

### "API key not configured"

- Check that `.env` file exists
- Verify `OPENAI_API_KEY` is set correctly
- Ensure no extra spaces in the key

### "Rate limit exceeded"

- User sent more than 100 messages in 60 minutes
- Wait for the cooldown period
- Or increase `CHATBOT_RATE_LIMIT`

### "Invalid request format"

- Ensure JSON is valid
- Check that "message" field is present

### No response from AI

- Verify OpenAI API status: https://status.openai.com/
- Check API key validity
- Ensure you have sufficient API credits

## Next Steps

1. ✅ Test the chatbot locally
2. Add user authentication to track real users
3. Implement billing/usage tracking
4. Add Redis for distributed rate limiting
5. Integrate chat widget into main pages
6. Add analytics dashboard for admins
7. Deploy to production server

## Support & Resources

- OpenAI Docs: https://platform.openai.com/docs
- API Rate Limits: https://platform.openai.com/docs/guides/rate-limits
- Pricing: https://openai.com/pricing

---

**Created:** January 22, 2026
**Status:** Ready for testing and deployment
