# Voice Chat Implementation with Gemini Live API

## Overview
This implementation integrates Google's Gemini Live API to provide real-time voice interaction in the Patient Appointment Dashboard. Patients can speak to the medical assistant and receive audio responses.

## Architecture

### Backend (FastAPI WebSocket)
**File**: `backend/routes/voice_chat.py`

#### Key Components:
1. **VoiceChatSession Class**: Manages bidirectional communication between client and Gemini Live API
2. **WebSocket Endpoint**: `/api/v1/ws/voice-chat`

#### Features:
- Real-time audio streaming
- Automatic turn detection (waits for user to stop talking)
- Bidirectional audio communication
- Error handling and reconnection support

#### Message Protocol:

**Client → Server:**
```json
{
  "type": "audio_data",
  "audio": "base64_encoded_audio"
}
```
Streams audio chunks while recording.

```json
{
  "type": "audio_end"
}
```
Signals that the user has stopped speaking, triggering Gemini's response.

```json
{
  "type": "stop"
}
```
Ends the session.

**Server → Client:**
```json
{
  "type": "session_started",
  "message": "Voice chat session connected"
}
```

```json
{
  "type": "audio_response",
  "audio": "base64_encoded_audio",
  "mime_type": "audio/pcm"
}
```

```json
{
  "type": "turn_complete"
}
```

```json
{
  "type": "error",
  "message": "error description"
}
```

### Frontend (React Component)
**File**: `frontend/src/components/VoiceChat.tsx`

#### Key Features:
1. **Microphone Access**: Uses `getUserMedia` API for audio capture
2. **Audio Recording**: MediaRecorder API with WebM format
3. **Audio Playback**: Web Audio API for playing responses
4. **Visual Feedback**: Real-time status indicators and animations

#### User Flow:
1. Click microphone button to start recording
2. Speak your question
3. Click stop when finished speaking
4. Wait for AI response (plays automatically)
5. Repeat as needed

### Integration in Dashboard
**File**: `frontend/src/components/PatientAppointmentDashboard.tsx`

#### UI Components:
- Green microphone button (bottom center of screen)
- Modal overlay with voice chat interface
- Visual status indicators
- Instructions panel

## Setup and Configuration

### Prerequisites
1. **Google API Key**: Required for Gemini Live API
   - Add to `backend/.env`: `GOOGLE_API_KEY=your_key_here`

2. **Python Dependencies** (already installed):
   - `google-genai>=1.0.0`
   - `websockets>=12.0`
   - `fastapi>=0.115.0`

3. **Browser Requirements**:
   - Microphone permission
   - WebSocket support
   - Web Audio API support
   - MediaRecorder API support

### Environment Variables
```bash
# backend/.env
GOOGLE_API_KEY=your_google_api_key_here
```

## Running the Application

### Backend:
```bash
cd backend
python main.py
```
Server runs on: `http://localhost:8000`

### Frontend:
```bash
cd frontend
npm run dev
```
Client runs on: `http://localhost:5173` (or similar)

## Testing the Voice Chat

1. **Start the Backend Server**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Dashboard**:
   - Navigate to the Patient Appointment Dashboard
   - You should see two floating buttons at the bottom:
     - Blue chat icon (text chat)
     - Green microphone icon (voice chat)

4. **Test Voice Interaction**:
   - Click the green microphone button
   - A modal will open showing the voice chat interface
   - Click "Start Talking"
   - Speak your question (e.g., "What are my upcoming appointments?")
   - Click "Stop Talking"
   - Wait for the AI response to play

## Audio Configuration

### Recording Settings:
- **Sample Rate**: 16000 Hz (optimal for speech)
- **Channels**: 1 (mono)
- **Format**: WebM (browser native)
- **Chunk Size**: 100ms intervals

### Gemini Live API Settings:
- **Model**: `gemini-live-2.5-flash-preview`
- **Response Modality**: AUDIO
- **Voice**: Aoede (configurable)

## Troubleshooting

### WebSocket Connection Issues:
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify `GOOGLE_API_KEY` is set in `.env`

### Microphone Access Denied:
- Grant microphone permission in browser
- Use HTTPS in production (required for getUserMedia)
- Check browser console for errors

### No Audio Response:
- Check browser console for decoding errors
- Verify audio format compatibility
- Ensure speakers/headphones are connected

### Audio Playback Issues:
- The audio from Gemini is in PCM format
- Browser may need specific codec support
- Try using headphones to avoid echo/feedback

## Key Implementation Details

### Turn Management:
The implementation uses a "push-to-talk" model:
1. User clicks "Start Talking" → begins recording
2. User clicks "Stop Talking" → sends `audio_end` signal
3. Gemini processes and responds
4. Response plays automatically
5. User can start talking again

### Audio Format Conversion:
- **Client → Server**: WebM → Base64 → Server
- **Server → Gemini**: Base64 → Binary PCM
- **Gemini → Client**: PCM → Base64 → Binary → Web Audio API

### Error Handling:
- WebSocket reconnection on disconnect
- Microphone permission errors
- Audio decoding errors
- Network timeouts

## Future Enhancements

1. **Continuous Conversation Mode**:
   - Automatic speech detection (VAD - Voice Activity Detection)
   - No need to click stop/start

2. **Voice Selection**:
   - Let users choose from different voice options
   - Configure voice parameters (speed, pitch)

3. **Conversation History**:
   - Display transcript of conversation
   - Save conversation for later review

4. **Multi-language Support**:
   - Automatic language detection
   - Real-time translation

5. **Advanced Audio Processing**:
   - Noise cancellation
   - Echo suppression
   - Audio quality enhancement

6. **Session Resumption**:
   - Save conversation context
   - Resume previous conversations

## Security Considerations

1. **API Key Protection**:
   - Never expose `GOOGLE_API_KEY` in frontend
   - Use environment variables
   - Rotate keys regularly

2. **Authentication**:
   - Implement user authentication
   - Validate user sessions before allowing voice chat

3. **Rate Limiting**:
   - Limit number of concurrent connections
   - Implement usage quotas

4. **Data Privacy**:
   - Audio data is not stored by default
   - Consider HIPAA compliance for medical data
   - Implement encryption for sensitive information

## API Documentation

### WebSocket Endpoint
**URL**: `ws://localhost:8000/api/v1/ws/voice-chat`

**Connection**: Upgrade from HTTP to WebSocket

**Authentication**: Currently none (add JWT in production)

**Message Format**: JSON

## Performance Optimization

1. **Audio Compression**: Use opus codec for better compression
2. **Chunk Size**: Adjust based on network latency
3. **Buffer Management**: Implement audio buffering for smooth playback
4. **Concurrent Connections**: Use connection pooling

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| WebSocket | ✅ | ✅ | ✅ | ✅ |
| MediaRecorder | ✅ | ✅ | ✅ | ✅ |
| Web Audio API | ✅ | ✅ | ✅ | ✅ |
| getUserMedia | ✅ | ✅ | ✅ | ✅ |

## References

- [Gemini Live API Documentation](https://ai.google.dev/gemini-api/docs/live)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## Support

For issues or questions:
1. Check backend logs: Look for errors in FastAPI console
2. Check frontend console: Browser developer tools
3. Verify environment variables are set correctly
4. Test WebSocket connection manually using tools like `wscat`
