# FridgeFix WhatsApp Chatbot

A WhatsApp chatbot for scheduling refrigerator repair services using Twilio and Flask.

## Quick Start

### 1. Get Twilio Credentials
1. Sign up at [twilio.com](https://www.twilio.com) (free trial with $15 credit)
2. Go to Console Dashboard
3. Copy your **Account SID** and **Auth Token**
4. Get a **WhatsApp-enabled phone number**

### 2. Update .env File
Edit `.env` and add your Twilio credentials:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

### 3. Deploy to Railway (Easiest)

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Connect your GitHub account and select this repo
4. Add environment variables from your `.env` file
5. Railway will auto-deploy

**Your URL will be:** `https://your-project-name.up.railway.app`

### 4. Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to **Messaging** → **WhatsApp Sandbox Settings**
3. Set **When a message comes in** to: `https://your-project-name.up.railway.app/whatsapp`
4. Save

### 5. Test the Bot

Send a message to your Twilio WhatsApp number to start!

## Alternative Deployment Options

**Heroku:**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

**Render:**
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repo
4. Add environment variables
5. Deploy

## How It Works

The chatbot conversation flow:
1. Asks for customer name
2. Requests phone number
3. Gets email address
4. Collects issue description
5. Gets full address
6. Offers time slot options (1-4)
7. Confirms and submits service request

## Files

- `app.py` - Flask server with chatbot logic
- `requirements.txt` - Python dependencies
- `.env` - Environment variables
- `Procfile` - Heroku/Railway deployment config
- `index.html` - Web interface (optional)

## Support

For Twilio help: [twilio.com/docs](https://www.twilio.com/docs)
