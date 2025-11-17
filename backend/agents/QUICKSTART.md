# CareAgents Quick Start Guide

Get your AI agents up and running in 5 minutes!

## Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Anthropic API Key

## Step 1: Setup Environment

```bash
# Clone/navigate to the backend directory
cd backend

# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
# Required variables:
# - ANTHROPIC_API_KEY
# - POSTGRES_* (host, port, db, user, password)
# - REDIS_URL
```

## Step 2: Install Dependencies

```bash
# Install with uv (already done if you've run uv sync)
uv sync

# Or with pip
pip install -r requirements.txt
```

## Step 3: Start Required Services

### Option A: Using Docker

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Or individually
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name postgres postgres:15
docker run -d -p 6379:6379 --name redis redis:alpine
```

### Option B: Local Installation

```bash
# macOS
brew services start postgresql
brew services start redis

# Linux
sudo systemctl start postgresql
sudo systemctl start redis

# Verify
redis-cli ping  # Should return PONG
psql -l         # Should list databases
```

## Step 4: Initialize Database

```bash
# Create database
createdb careagents

# Run schema
psql -d careagents -f database/postgresql/scripts/create_tables.sql

# Verify
psql -d careagents -c "\dt"
```

## Step 5: Run the Application

```bash
# Using the agents-enabled server
python main_agents.py

# Or with uvicorn for development
uvicorn main_agents:app --reload --host 0.0.0.0 --port 8000
```

## Step 6: Test the Setup

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "CareAgents AI Backend",
  "version": "1.0.0"
}
```

### Test 2: WebSocket Connection

```bash
# Install websocat (WebSocket CLI client)
brew install websocat  # macOS
# or download from: https://github.com/vi/websocat

# Connect to chat WebSocket
websocat ws://localhost:8000/ws/chat/test-session-123
```

Then send a message:
```json
{"type": "chat_message", "message": "Hello!"}
```

### Test 3: REST API

```bash
# Test non-streaming chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What can you help me with?",
    "session_id": "test-123"
  }'
```

## Frontend Integration

### Step 1: Copy Frontend Files

The frontend service and hook have been created:
- `frontend/src/services/agentService.ts`
- `frontend/src/hooks/useAgentService.ts`

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
# or
yarn install
```

### Step 3: Use in Your Component

```tsx
import { useAgentService } from '../hooks/useAgentService';

function ChatComponent() {
  const {
    messages,
    isConnected,
    isTyping,
    currentResponse,
    sendMessage,
    error
  } = useAgentService({
    patientId: 'patient-123',
    autoConnect: true
  });

  return (
    <div>
      {/* Connection status */}
      {isConnected ? '🟢 Connected' : '🔴 Disconnected'}

      {/* Messages */}
      {messages.map((msg, i) => (
        <div key={i} className={msg.role}>
          {msg.content}
        </div>
      ))}

      {/* Streaming response */}
      {isTyping && (
        <div className="assistant typing">
          {currentResponse}
          <span className="cursor">▋</span>
        </div>
      )}

      {/* Error */}
      {error && <div className="error">{error}</div>}

      {/* Input */}
      <input
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            sendMessage(e.currentTarget.value);
            e.currentTarget.value = '';
          }
        }}
      />
    </div>
  );
}
```

## Common Issues

### Issue: "ANTHROPIC_API_KEY not found"
**Solution**: Add your API key to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Issue: "Redis connection refused"
**Solution**: Start Redis:
```bash
redis-server
# or
brew services start redis
```

### Issue: "PostgreSQL connection failed"
**Solution**: Check PostgreSQL is running and credentials are correct:
```bash
psql -h localhost -U postgres -d careagents
```

### Issue: "WebSocket connection failed"
**Solution**:
1. Check backend is running on port 8000
2. Check CORS settings allow your frontend origin
3. Try different browser/clear cache

## Next Steps

1. **Add Sample Data**: Insert test patients and records
2. **Configure Agents**: Edit `agents/config/prompts.yaml`
3. **Customize UI**: Build your chat interface
4. **Add Authentication**: Implement user auth
5. **Deploy**: See deployment guide

## Useful Commands

```bash
# Check Redis
redis-cli ping
redis-cli keys "chat:*"

# Check PostgreSQL
psql -d careagents -c "SELECT * FROM users LIMIT 5;"
psql -d careagents -c "SELECT * FROM patients LIMIT 5;"

# Monitor logs
tail -f backend.log

# Test WebSocket from browser console
const ws = new WebSocket('ws://localhost:8000/ws/chat/test-123');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({type: 'chat_message', message: 'Hello!'}));
```

## Production Checklist

Before deploying to production:

- [ ] Add authentication and authorization
- [ ] Enable HTTPS/WSS
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backup for PostgreSQL
- [ ] Set up Redis persistence
- [ ] Review and update CORS settings
- [ ] Add input validation and sanitization
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Configure environment-specific settings
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Implement session management
- [ ] Add audit logging for medical data access
- [ ] Configure data retention policies
- [ ] Set up health checks and alerts

## Support

For issues or questions:
1. Check the main [README](README.md)
2. Review the [API documentation](http://localhost:8000/docs)
3. Search existing issues
4. Create a new issue with logs and steps to reproduce

## Resources

- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Redis Documentation](https://redis.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

Happy building! 🚀
