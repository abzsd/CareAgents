# CareAgents - AI Agents for Healthcare Management

This directory contains the AI agent implementation for the CareAgents Healthcare Management System. The system uses Anthropic's Claude for intelligent conversation and medical record analysis.

## Architecture Overview

### Components

1. **ChatAgent** - Conversational AI with memory
   - Handles general healthcare queries
   - Maintains conversation context using Redis
   - Temperature: 0.7 (more creative responses)
   - Supports streaming responses

2. **RecordAgent** - Medical records analysis
   - Fetches and summarizes patient records
   - Analyzes health vitals and trends
   - Temperature: 0.1 (deterministic, focused responses)
   - Specialized for medical data

3. **PostgreSQL Tools** - Database query tools
   - Secure patient data access
   - Optimized queries for medical records
   - Support for vitals, prescriptions, and reports

4. **Streaming Service** - WebSocket message buffer
   - Real-time communication with frontend
   - Message queuing and routing
   - Support for multiple concurrent sessions

5. **Agent Orchestrator** - Coordination layer
   - Routes queries to appropriate agents
   - Manages agent lifecycle
   - Handles streaming and error recovery

## Directory Structure

```
agents/
├── __init__.py
├── chat_agent.py              # Conversational AI agent
├── record_agent.py            # Medical records agent
├── config/
│   ├── __init__.py
│   └── prompts.yaml           # Agent prompts and configuration
├── tools/
│   ├── __init__.py
│   └── postgres_tools.py      # PostgreSQL query tools
└── services/
    ├── __init__.py
    ├── streaming_service.py   # WebSocket service
    └── agent_orchestrator.py  # Agent coordination
```

## Setup Instructions

### Prerequisites

1. **PostgreSQL** - For patient data storage
2. **Redis** - For chat memory and session management
3. **Anthropic API Key** - For Claude AI access

### Installation

1. Install dependencies (already done via uv):
```bash
uv sync
```

2. Configure environment variables in `.env`:
```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=careagents
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_URL=redis://localhost:6379

# Anthropic
ANTHROPIC_API_KEY=your-api-key-here
```

3. Start required services:
```bash
# Start PostgreSQL (if not running)
# brew services start postgresql  # macOS
# sudo service postgresql start   # Linux

# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

4. Initialize database:
```bash
# Run the SQL schema
psql -h localhost -U postgres -d careagents -f database/postgresql/scripts/create_tables.sql
```

5. Run the application:
```bash
# Using the agents-enabled main file
python main_agents.py

# Or with uvicorn
uvicorn main_agents:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### WebSocket Endpoints

#### Chat WebSocket
```
WS /ws/chat/{session_id}?patient_id={patient_id}
```

**Message Format (Send):**
```json
{
  "type": "chat_message",
  "message": "What are my recent vitals?",
  "patient_id": "optional-patient-id"
}
```

**Response Format (Receive):**
```json
{
  "type": "stream_chunk",
  "chunk": "Your recent vitals show..."
}
```

#### Generic Agent WebSocket
```
WS /ws/agent/{session_id}?user_id={user_id}
```

### REST API Endpoints

#### Chat (Non-streaming)
```http
POST /api/chat
Content-Type: application/json

{
  "message": "How do I access my medical records?",
  "patient_id": "patient-123",
  "session_id": "optional-session-id"
}
```

#### Patient Summary
```http
POST /api/records/summary
Content-Type: application/json

{
  "patient_id": "patient-123",
  "request_type": "summary"
}
```

#### Vitals Analysis
```http
POST /api/records/vitals
Content-Type: application/json

{
  "patient_id": "patient-123",
  "request_type": "vitals",
  "vital_type": "blood_pressure",  // optional
  "days": 30
}
```

#### Prescription Summary
```http
POST /api/records/prescriptions
Content-Type: application/json

{
  "patient_id": "patient-123",
  "request_type": "prescriptions"
}
```

#### Clear Session
```http
DELETE /api/session/{session_id}
```

## Agent Configuration

All agent prompts and settings are configured in [config/prompts.yaml](config/prompts.yaml).

### Key Configuration Options

```yaml
general:
  model: "claude-3-5-sonnet-20241022"
  max_tokens: 4096
  temperature:
    chat_agent: 0.7      # More creative
    record_agent: 0.1    # Deterministic

chat_agent:
  system_prompt: |
    You are a helpful AI healthcare assistant...

record_agent:
  system_prompt: |
    You are a specialized medical records AI assistant...
```

## Usage Examples

### Python Client Example

```python
import asyncio
import websockets
import json

async def chat_with_agent():
    uri = "ws://localhost:8000/ws/chat/my-session-123"

    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "chat_message",
            "message": "Show me my recent prescriptions",
            "patient_id": "patient-123"
        }))

        # Receive streaming response
        full_response = ""
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "stream_chunk":
                print(data["chunk"], end="", flush=True)
                full_response += data["chunk"]

            elif data["type"] == "stream_end":
                print("\n\nComplete response received!")
                break

asyncio.run(chat_with_agent())
```

### Frontend Integration (TypeScript/React)

See the frontend integration guide below for React/TypeScript examples.

## Tools Available to Agents

Agents have access to the following PostgreSQL query tools:

1. **query_patient_by_id** - Get patient demographics and basic info
2. **query_patient_records** - Get comprehensive medical records
3. **query_health_vitals** - Query vital signs with filters
4. **query_prescriptions** - Get prescription information
5. **query_medical_reports** - Get medical reports and lab results

These tools are automatically available to both ChatAgent and RecordAgent.

## Memory Management

### Chat Memory (Redis)

- **Storage**: Conversation history stored in Redis
- **TTL**: 7 days (configurable)
- **Key Format**: `chat:session:{session_id}`
- **Context Storage**: `chat:context:{session_id}`

### Session Management

```python
# Clear a session
await orchestrator.clear_session(session_id)

# Sessions auto-expire after 7 days of inactivity
```

## Streaming Architecture

The streaming service provides real-time communication between backend agents and frontend clients:

1. **Client connects** via WebSocket
2. **Session established** with unique session_id
3. **Messages queued** in ConnectionManager
4. **Agent processes** query with streaming
5. **Chunks sent** to client in real-time
6. **Stream ends** with completion signal

### Message Types

- `connected` - Connection established
- `chat_message` - User message
- `chat_response` - Complete response (non-streaming)
- `stream_start` - Stream beginning
- `stream_chunk` - Response chunk
- `stream_end` - Stream completion
- `error` - Error occurred
- `typing` - Typing indicator

## Error Handling

The system includes comprehensive error handling:

- **Network errors** - Automatic reconnection support
- **Database errors** - Graceful degradation
- **API errors** - Retry logic with exponential backoff
- **WebSocket errors** - Connection cleanup

## Security Considerations

1. **Authentication**: Implement JWT/session auth before production
2. **Patient Privacy**: All queries validate patient_id access
3. **Rate Limiting**: Add rate limits for API endpoints
4. **Data Encryption**: Use TLS for WebSocket connections
5. **Input Validation**: All inputs validated via Pydantic models

## Performance Optimization

- **Connection Pooling**: PostgreSQL uses asyncpg pool (2-10 connections)
- **Redis Pipelining**: Batch operations when possible
- **Lazy Initialization**: Agents initialized on first use
- **Streaming**: Reduces memory usage for long responses

## Monitoring and Debugging

### Logging

Add logging to track agent behavior:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In your code
logger.info(f"Processing query for session: {session_id}")
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues

1. **Redis connection failed**
   - Ensure Redis is running: `redis-cli ping`
   - Check REDIS_URL in .env

2. **PostgreSQL connection failed**
   - Verify database exists: `psql -l`
   - Check credentials in .env

3. **Anthropic API errors**
   - Verify API key is valid
   - Check API rate limits

4. **WebSocket disconnects**
   - Check for network issues
   - Increase timeout if needed
   - Review client-side reconnection logic

## Next Steps

### Frontend Integration

Create a chat service in your frontend:

```typescript
// See frontend/src/services/agentService.ts (to be created)
```

### Enhancements

- [ ] Add user authentication
- [ ] Implement rate limiting
- [ ] Add metrics and monitoring
- [ ] Create admin dashboard
- [ ] Add multi-language support
- [ ] Implement feedback mechanism

## Contributing

When adding new agents or tools:

1. Create agent class extending base functionality
2. Add tool definitions to `tools/`
3. Update `config/prompts.yaml`
4. Register in `agent_orchestrator.py`
5. Add API endpoints in `main_agents.py`
6. Update this README

## License

Copyright © 2024 CareAgents. All rights reserved.
