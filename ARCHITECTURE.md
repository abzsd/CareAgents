# Landing Page & Guest Chat Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     http://localhost:5173                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  App.tsx                                                     │ │
│ │  ├── if (!user) → LandingPage.tsx                          │ │
│ │  └── if (user) → Dashboard (existing flow)                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                             │                                    │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  LandingPage.tsx                                            │ │
│ │  ├── Hero Section                                           │ │
│ │  ├── Features Section                                       │ │
│ │  ├── Stats Section                                          │ │
│ │  ├── CTA Section                                            │ │
│ │  ├── Footer                                                 │ │
│ │  └── <GuestChat /> ─────────────────────┐                  │ │
│ └─────────────────────────────────────────│─────────────────┘ │
│                                            │                    │
│ ┌──────────────────────────────────────────┼─────────────────┐ │
│ │  GuestChat.tsx                           │                 │ │
│ │  ├── Floating Button (open/close)       │                 │ │
│ │  ├── Chat Window                         │                 │ │
│ │  ├── Message History                     │                 │ │
│ │  ├── Input Field                         │                 │ │
│ │  └── Send Button ────────────────────────┘                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ POST /api/chat/guest
                             │ { message, history }
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│                   http://localhost:8000                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  main.py                                                     │ │
│ │  └── app.include_router(chat.router)                        │ │
│ └─────────────────────────┬───────────────────────────────────┘ │
│                           │                                      │
│ ┌─────────────────────────▼───────────────────────────────────┐ │
│ │  routes/chat.py                                             │ │
│ │  ├── POST /chat/guest ──────────────────┐                  │ │
│ │  └── GET  /chat/health                  │                  │ │
│ └─────────────────────────────────────────│─────────────────┘ │
│                                            │                    │
│ ┌──────────────────────────────────────────▼─────────────────┐ │
│ │  GuestChatAgent                                            │ │
│ │  ├── system_prompt (CareAgent info)                        │ │
│ │  ├── build messages from history                           │ │
│ │  └── call Anthropic API ────────────────────┐              │ │
│ └─────────────────────────────────────────────│─────────────┘ │
└───────────────────────────────────────────────│───────────────┘
                                                │
                                                │
                                                ▼
                        ┌─────────────────────────────────┐
                        │   ANTHROPIC API                  │
                        │   Claude 3.5 Sonnet             │
                        │                                  │
                        │   - Receives message + history   │
                        │   - Processes with system prompt │
                        │   - Returns AI response          │
                        └─────────────────────────────────┘
```

## Data Flow

### 1. User Opens Landing Page

```
User → Browser
    → http://localhost:5173
    → App.tsx checks auth
    → No user authenticated
    → Renders <LandingPage />
    → Renders <GuestChat />
```

### 2. User Clicks Chat Button

```
User clicks chat button
    → GuestChat.tsx
    → setIsOpen(true)
    → Chat window slides in
    → Shows welcome message
```

### 3. User Sends Message

```
User types message + clicks Send
    │
    ├─ Update local state (add user message)
    ├─ Show message in UI
    ├─ Show loading indicator
    │
    └─ POST http://localhost:8000/api/chat/guest
        {
          message: "What is CareAgent?",
          history: [
            { role: "assistant", content: "Hi! I'm..." },
            { role: "user", content: "What is CareAgent?" }
          ]
        }
```

### 4. Backend Processing

```
FastAPI receives request
    │
    ├─ routes/chat.py
    │   └─ guest_chat() endpoint
    │       │
    │       ├─ Validate request (Pydantic)
    │       ├─ Get GuestChatAgent instance
    │       │
    │       └─ agent.chat(message, history)
    │           │
    │           ├─ Build messages array
    │           ├─ Limit history to last 10 messages
    │           │
    │           └─ Call Anthropic API
    │               └─ client.messages.create(
    │                     model="claude-3-5-sonnet-20241022",
    │                     system=system_prompt,
    │                     messages=messages
    │                   )
    │
    └─ Return response
        {
          message: "CareAgent is a comprehensive...",
          session_id: "uuid-here"
        }
```

### 5. Frontend Updates

```
Receive response from API
    │
    ├─ Hide loading indicator
    ├─ Add assistant message to state
    ├─ Update history
    ├─ Auto-scroll to bottom
    │
    └─ Display AI response in chat window
```

### 6. Fallback Flow (if API fails)

```
API request fails
    │
    └─ catch block in GuestChat.tsx
        │
        ├─ Check user message for keywords
        │   ├─ "appointment" → Show appointment info
        │   ├─ "doctor" → Show doctor info
        │   ├─ "service" → Show services info
        │   └─ default → General help message
        │
        └─ Display fallback response
```

## Component Hierarchy

```
App
└── LandingPage
    ├── Navigation
    │   ├── Logo
    │   └── Sign In Button
    │
    ├── Hero Section
    │   ├── Badge (AI-Powered)
    │   ├── Headline (gradient)
    │   ├── Description
    │   ├── CTAs
    │   │   ├── Get Started Button
    │   │   └── Try Guest Chat Button
    │   ├── Stats
    │   └── Preview Card
    │
    ├── Features Section
    │   ├── Feature Card 1 (Secure)
    │   ├── Feature Card 2 (24/7 Support)
    │   └── Feature Card 3 (Expert Doctors)
    │
    ├── Stats Banner
    │   ├── Stat 1 (500+ Patients)
    │   ├── Stat 2 (100+ Doctors)
    │   ├── Stat 3 (10k+ Consultations)
    │   └── Stat 4 (98% Satisfaction)
    │
    ├── Final CTA
    │   └── Get Started Button
    │
    ├── Footer
    │   ├── Logo
    │   ├── Copyright
    │   └── Links
    │
    └── GuestChat
        ├── Floating Button
        └── Chat Window (when open)
            ├── Header
            │   ├── Avatar
            │   ├── Title
            │   └── Close Button
            ├── Messages Area
            │   ├── Welcome Message
            │   ├── User Messages
            │   ├── AI Messages
            │   └── Typing Indicator
            └── Input Area
                ├── Text Input
                └── Send Button
```

## State Management

### Frontend State (React)

```typescript
// GuestChat.tsx
const [isOpen, setIsOpen] = useState(false)
const [messages, setMessages] = useState<Message[]>([...])
const [input, setInput] = useState('')
const [isLoading, setIsLoading] = useState(false)

// LandingPage.tsx
const [loading, setLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
```

### Backend State

```python
# Singleton instance
_guest_agent: Optional[GuestChatAgent] = None

# Created once and reused
def get_guest_agent() -> GuestChatAgent:
    global _guest_agent
    if _guest_agent is None:
        _guest_agent = GuestChatAgent(api_key=...)
    return _guest_agent
```

## API Endpoints

### POST /api/chat/guest

**Request**:
```json
{
  "message": "What is CareAgent?",
  "history": [
    { "role": "assistant", "content": "Hi! How can I help?" },
    { "role": "user", "content": "What is CareAgent?" }
  ]
}
```

**Response**:
```json
{
  "message": "CareAgent is a comprehensive healthcare management platform...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Status Codes**:
- `200`: Success
- `500`: Server error (API key missing, Anthropic API error, etc.)

### GET /api/chat/health

**Response**:
```json
{
  "status": "healthy",
  "service": "Guest Chat",
  "model": "claude-3-5-sonnet-20241022"
}
```

## Environment Variables

```bash
# Backend (.env)
ANTHROPIC_API_KEY=sk-ant-xxxxx
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=careagents
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

## Key Technologies

### Frontend
- **React 18**: UI library
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Vite**: Build tool
- **Lucide React**: Icons
- **Radix UI**: Components

### Backend
- **FastAPI**: Web framework
- **Anthropic SDK**: AI integration
- **Pydantic**: Data validation
- **AsyncPG**: PostgreSQL driver
- **Uvicorn**: ASGI server

## Security Layers

```
User Input
    ↓
Frontend Validation
    ↓
API Request (HTTPS in production)
    ↓
Backend Validation (Pydantic)
    ↓
Rate Limiting (TODO for production)
    ↓
API Key Authentication (Anthropic)
    ↓
Response Sanitization
    ↓
User Display
```

## Performance Optimizations

1. **Frontend**:
   - Component lazy loading
   - Message history limit (local state)
   - Debounced input (if needed)
   - CSS transitions (GPU accelerated)

2. **Backend**:
   - Singleton agent instance
   - History limit (last 10 messages)
   - Async/await throughout
   - Connection pooling (PostgreSQL)

3. **API**:
   - Short max_tokens (2048)
   - Temperature tuned for efficiency
   - No tool use (simpler responses)

## Error Handling

### Frontend
```typescript
try {
  const response = await fetch('/api/chat/guest', ...)
  // Handle response
} catch (error) {
  // Fallback to keyword-based responses
  // Display user-friendly error message
}
```

### Backend
```python
try:
    response = await client.messages.create(...)
    return response_text
except Exception as e:
    print(f"Error: {str(e)}")
    return fallback_message
```

## Monitoring Points

1. **Frontend**:
   - Chat button clicks
   - Messages sent
   - Response times
   - Error rates

2. **Backend**:
   - API endpoint hits
   - Response times
   - Anthropic API errors
   - Token usage

3. **Business**:
   - Guest chat engagement
   - Conversion rate (guest → signup)
   - Common questions
   - User satisfaction

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
