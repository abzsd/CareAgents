# Voice Chat Quick Start Guide

## 🎯 What's Been Implemented

A real-time voice chat feature has been integrated into the Patient Appointment Dashboard using Google's Gemini Live API. Patients can now talk to a medical AI assistant and receive spoken responses.

## 🚀 Quick Start

### 1. Start the Backend

```bash
cd backend
source .venv/bin/activate  # or `.venv/bin/activate` on Windows
python main.py
```

The server will start on `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173` (or similar)

### 3. Use Voice Chat

1. **Navigate to the Patient Dashboard**
   - Log in as a patient
   - Go to the appointment dashboard

2. **Click the Green Microphone Button**
   - You'll see it at the bottom center of the screen
   - A modal will open with the voice chat interface

3. **Start Talking**
   - Click "Start Talking" button
   - Speak your question (e.g., "What are my upcoming appointments?")
   - Click "Stop Talking" when done
   - Wait for the AI response to play

## 📋 Features

✅ **Real-time voice streaming** - Audio is sent to Gemini as you speak
✅ **Automatic response playback** - AI responses play automatically
✅ **Visual feedback** - See connection status and recording state
✅ **Turn-based conversation** - Wait for response before speaking again
✅ **Error handling** - Graceful handling of connection issues

## 🔧 How It Works

### Backend (`/api/v1/ws/voice-chat`)
- WebSocket endpoint for bidirectional audio streaming
- Connects to Gemini Live API
- Handles audio format conversion (WebM ↔ PCM)

### Frontend
- **VoiceChat Component**: Manages recording and playback
- Uses MediaRecorder API for capturing audio
- Uses Web Audio API for playing responses
- Base64 encoding for audio transmission

### Message Flow
```
User Speaks → Browser captures audio → WebSocket → Backend → Gemini API
                                                                  ↓
User Hears ← Browser plays audio ← WebSocket ← Backend ← Audio Response
```

## 🎤 Usage Tips

### Best Practices
1. **Speak clearly** - The AI works best with clear speech
2. **Wait for response** - Don't interrupt while AI is speaking
3. **Use headphones** - Prevents echo and feedback
4. **Short questions** - Keep questions concise for better results

### Example Questions
- "What are my upcoming appointments?"
- "When is my next appointment with Dr. Johnson?"
- "What medications am I currently taking?"
- "Show me my recent health data"

## 🐛 Troubleshooting

### "Microphone access denied"
**Solution**: Grant microphone permission in your browser settings

### "Connection error"
**Solution**:
- Ensure backend is running on port 8000
- Check that `GOOGLE_API_KEY` is set in `backend/.env`
- Verify your internet connection

### "No audio response"
**Solution**:
- Check browser console for errors
- Try using headphones
- Ensure speakers are not muted

### WebSocket connection fails
**Solution**:
- Restart the backend server
- Check for port conflicts (8000)
- Verify CORS settings in `main.py`

## 📝 Configuration

### Change Voice
Edit `backend/routes/voice_chat.py`:

```python
config = {
    "response_modalities": ["AUDIO"],
    "speech_config": {
        "voice_config": {
            "prebuilt_voice_config": {
                "voice_name": "Puck"  # Try: Aoede, Charon, Fenrir, Kore, Puck
            }
        }
    }
}
```

### Adjust Recording Quality
Edit `frontend/src/components/VoiceChat.tsx`:

```typescript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    channelCount: 1,
    sampleRate: 24000,  // Increase for better quality
    echoCancellation: true,
    noiseSuppression: true,
  },
});
```

## 🔐 Security Notes

⚠️ **Important**:
- The `GOOGLE_API_KEY` is stored in backend only (never exposed to frontend)
- In production, add authentication to the WebSocket endpoint
- Consider implementing rate limiting for API calls

## 📊 Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome  | ✅ Full | Recommended |
| Firefox | ✅ Full | Works well |
| Safari  | ✅ Full | Requires HTTPS in production |
| Edge    | ✅ Full | Works well |

## 🎨 UI Components

### Buttons
- **Blue chat icon**: Text-based chat
- **Green microphone icon**: Voice chat

### Status Indicators
- **Green dot**: Connected to server
- **Red dot**: Disconnected
- **Pulsing animation**: Recording or playing

### Modal Layout
- Header with close button
- Main area with microphone icon
- Control buttons
- Instructions panel

## 🔄 Next Steps

### Potential Enhancements
1. **Voice Activity Detection**: Auto-detect when user stops speaking
2. **Conversation History**: Show transcript of the conversation
3. **Multi-language**: Support multiple languages
4. **Session Persistence**: Resume conversations later
5. **Medical Context**: Integrate patient health records for context-aware responses

## 📖 Additional Resources

- [Full Implementation Guide](VOICE_CHAT_IMPLEMENTATION.md)
- [Gemini Live API Docs](https://ai.google.dev/gemini-api/docs/live)
- Backend Code: `backend/routes/voice_chat.py`
- Frontend Code: `frontend/src/components/VoiceChat.tsx`

## 💡 Key Files

```
CareAgents/
├── backend/
│   ├── routes/
│   │   └── voice_chat.py          # WebSocket endpoint
│   ├── main.py                     # Updated to include voice_chat router
│   └── .env                        # GOOGLE_API_KEY configuration
└── frontend/
    └── src/
        └── components/
            ├── VoiceChat.tsx       # Voice chat component
            └── PatientAppointmentDashboard.tsx  # Updated with voice button
```

## ✅ Testing Checklist

- [ ] Backend starts without errors
- [ ] WebSocket endpoint accessible at `ws://localhost:8000/api/v1/ws/voice-chat`
- [ ] Frontend shows green microphone button
- [ ] Clicking microphone opens modal
- [ ] "Start Talking" button works
- [ ] Audio recording starts
- [ ] "Stop Talking" sends audio
- [ ] AI response plays back
- [ ] Connection status updates correctly
- [ ] Errors are handled gracefully

## 🆘 Support

If you encounter issues:
1. Check the browser console (F12) for JavaScript errors
2. Check the backend logs for Python errors
3. Verify `GOOGLE_API_KEY` is valid
4. Ensure all dependencies are installed
5. Test with a simple question first

---

**Happy chatting! 🎤**
