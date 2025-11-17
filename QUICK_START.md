# Quick Start Guide - Beautiful Landing Page with Guest Chat

## 🚀 Get Started in 3 Steps

### Step 1: Configure Backend

```bash
cd backend

# Copy .env.example to .env if you haven't already
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-xxxxx
nano .env  # or use your preferred editor
```

**Get your API key**: https://console.anthropic.com/

### Step 2: Start Backend

```bash
# From backend directory
python main.py
```

You should see:
```
✓ Connected to PostgreSQL
✓ PostgreSQL connection test successful
Starting Healthcare Management System with PostgreSQL...
```

Backend will be running at: `http://localhost:8000`

### Step 3: Start Frontend

Open a new terminal:

```bash
cd frontend

# Start development server
yarn dev
```

Frontend will be running at: `http://localhost:5173`

## 🎉 You're Done!

Open your browser and visit: **http://localhost:5173**

You should see:
1. ✨ Beautiful landing page with gradients and animations
2. 💬 Floating chat button in bottom-right corner
3. 🤖 Click chat to talk with AI assistant

## 🧪 Test the Chat

1. Click the floating chat button (bottom-right)
2. Try these example messages:
   - "What is CareAgent?"
   - "How can I book an appointment?"
   - "What features do you offer?"
   - "Tell me about your doctors"

## 📊 Check Health Status

Visit these URLs to verify everything is working:

- Backend Health: http://localhost:8000/health
- Chat Service Health: http://localhost:8000/api/chat/health
- API Documentation: http://localhost:8000/docs

## 🐛 Troubleshooting

### Chat not responding?

**Check API Key**:
```bash
cd backend
python test_guest_chat.py
```

**Common issues**:
- ❌ "ANTHROPIC_API_KEY not configured" → Add key to `.env`
- ❌ "Failed to connect to PostgreSQL" → Start PostgreSQL or check connection
- ❌ CORS errors → Backend CORS is configured for development

### Backend won't start?

**Check PostgreSQL is running**:
```bash
# macOS with Homebrew
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Check connection
psql -U postgres -h localhost
```

**Missing dependencies?**:
```bash
cd backend
pip install -r requirements.txt
# or with uv
uv pip install -e .
```

### Frontend issues?

**Reinstall dependencies**:
```bash
cd frontend
rm -rf node_modules
yarn install
```

**Clear cache**:
```bash
rm -rf .vite
yarn dev
```

## 🎨 What You'll See

### Landing Page Features

1. **Navigation**: CareAgent logo and Sign In button
2. **Hero Section**:
   - Big headline with gradient text
   - Call-to-action buttons
   - Interactive dashboard preview
3. **Features**: Three cards showcasing key features
4. **Stats**: Impressive numbers (500+ patients, etc.)
5. **Final CTA**: Encouraging signup
6. **Footer**: Branding and links

### Chat Widget

1. **Floating Button**: Pulsing green indicator shows it's active
2. **Chat Window**: Beautiful gradient header with AI avatar
3. **Messages**: User messages in blue/purple, AI in white
4. **Smart AI**: Powered by Claude 3.5 Sonnet
5. **Fallbacks**: Works even if API is down

## 📱 Try on Mobile

The landing page is fully responsive! Try it on:
- iPhone/iPad (Safari)
- Android (Chrome)
- Desktop (any modern browser)

## 🔐 Security Notes

### For Development
- ✅ CORS is set to `*` (all origins)
- ✅ API keys in `.env` (not committed)

### For Production
- 🔒 Update CORS to your domain only
- 🔒 Use environment variables for secrets
- 🔒 Enable HTTPS/SSL
- 🔒 Add rate limiting
- 🔒 Set up monitoring

## 📚 Next Steps

1. **Customize Content**: Edit [LandingPage.tsx](frontend/src/components/LandingPage.tsx)
2. **Modify Chat Behavior**: Edit [chat.py](backend/routes/chat.py)
3. **Change Colors**: Update Tailwind classes in components
4. **Add Analytics**: Integrate Google Analytics or similar
5. **Deploy**: See deployment guides for Vercel (frontend) and Railway/Render (backend)

## 🆘 Need Help?

- **Setup Guide**: [GUEST_CHAT_SETUP.md](GUEST_CHAT_SETUP.md)
- **Full Summary**: [LANDING_PAGE_SUMMARY.md](LANDING_PAGE_SUMMARY.md)
- **Test Chat**: Run `python backend/test_guest_chat.py`
- **API Docs**: http://localhost:8000/docs

## 🎯 Key Files

```
frontend/src/components/
├── LandingPage.tsx    👈 Main landing page
├── GuestChat.tsx      👈 Chat widget
└── App.tsx            👈 Updated routing

backend/
├── main.py            👈 FastAPI app
└── routes/
    └── chat.py        👈 Chat API

Documentation/
├── QUICK_START.md              👈 This file
├── GUEST_CHAT_SETUP.md         👈 Detailed setup
└── LANDING_PAGE_SUMMARY.md     👈 Complete overview
```

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can see beautiful landing page
- [ ] Chat button visible in bottom-right
- [ ] Chat opens when clicked
- [ ] AI responds to messages
- [ ] No console errors

---

**Happy Coding! 🎊**

If everything works, you should have a beautiful, engaging landing page with AI-powered guest chat!
