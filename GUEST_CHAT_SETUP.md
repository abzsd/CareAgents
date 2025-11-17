# Guest Chat Feature Setup

## Overview

The Guest Chat feature allows visitors to interact with an AI assistant before signing up. The chat interface appears as a floating button at the bottom-right of the landing page.

## Features

- **Beautiful Landing Page**: Modern, gradient-based design with hero section, features, stats, and CTA
- **Floating Chat Widget**: Bottom-right floating chat button with animation
- **Real-time AI Chat**: Powered by Claude AI (Anthropic)
- **Fallback Responses**: Graceful handling when API is unavailable
- **Mobile Responsive**: Works on all device sizes

## Setup Instructions

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install anthropic
   ```

2. **Configure API Key**:
   Add your Anthropic API key to `.env`:
   ```bash
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

3. **Run Backend**:
   ```bash
   python main.py
   ```
   The chat endpoint will be available at: `http://localhost:8000/api/chat/guest`

### Frontend Setup

The frontend is already configured and includes:

- `LandingPage.tsx` - Beautiful landing page
- `GuestChat.tsx` - Floating chat widget
- Updated `App.tsx` - Shows landing page to non-authenticated users

### Testing

1. **Start Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   yarn dev
   ```

3. **Access Application**:
   - Open: `http://localhost:5173`
   - You should see the beautiful landing page
   - Click the chat button at bottom-right to test guest chat

### Chat Features

The guest chat assistant can:
- Answer questions about CareAgent features
- Provide general platform information
- Encourage visitors to sign up
- Provide fallback responses when API is unavailable

### API Endpoints

- `POST /api/chat/guest` - Send chat message
- `GET /api/chat/health` - Check chat service health

### Fallback Behavior

If the Anthropic API is unavailable, the chat will provide helpful fallback responses based on keywords:
- `appointment` - Information about booking appointments
- `doctor` - Information about healthcare professionals
- `service` - Platform features and services
- `cost` - Pricing information
- `emergency` - Emergency guidance

## Customization

### Modify Chat Responses

Edit the system prompt in `backend/routes/chat.py`:

```python
self.system_prompt = """Your custom prompt here"""
```

### Modify Fallback Responses

Edit the `fallbackResponses` object in `frontend/src/components/GuestChat.tsx`:

```typescript
const fallbackResponses: Record<string, string> = {
  'custom_keyword': "Your custom response",
  // ...
};
```

### Styling

The chat widget uses Tailwind CSS with gradient colors matching the landing page theme. Modify colors in `GuestChat.tsx` to match your brand.

## Production Considerations

1. **API Key Security**: Use environment variables, never commit API keys
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Session Tracking**: Implement proper session management
4. **Cost Control**: Monitor API usage and set limits
5. **Error Logging**: Add comprehensive error logging
6. **Analytics**: Track chat engagement metrics

## Troubleshooting

### Chat not responding
- Check backend is running
- Verify ANTHROPIC_API_KEY is set correctly
- Check browser console for errors
- Verify API endpoint is accessible

### Styling issues
- Ensure Tailwind CSS is configured
- Check that all UI components are imported
- Verify lucide-react icons are installed

### CORS errors
- Backend CORS is configured for `*` in development
- Update CORS settings for production

## Future Enhancements

- [ ] Add chat history persistence
- [ ] Implement typing indicators
- [ ] Add file/image upload support
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Sentiment analysis
- [ ] Auto-complete suggestions
