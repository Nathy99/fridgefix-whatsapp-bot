# GitHub Setup Instructions

## Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `fridgefix-whatsapp-bot`
3. Description: `FridgeFix WhatsApp Chatbot for scheduling repairs`
4. Choose **Public** (so Railway can access it)
5. Click **Create repository**

## Step 2: Push to GitHub

Copy and run these commands in your terminal:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fridgefix-whatsapp-bot.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub**
3. Select your `fridgefix-whatsapp-bot` repository
4. Railway will auto-detect it's a Python app
5. Add environment variables:
   - `TWILIO_ACCOUNT_SID` = your SID
   - `TWILIO_AUTH_TOKEN` = your token
   - `TWILIO_WHATSAPP_NUMBER` = your WhatsApp number
6. Click **Deploy**

## Step 4: Get Your Deployment URL

After deployment, Railway will give you a URL like:
```
https://fridgefix-bot-production.up.railway.app
```

## Step 5: Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com)
2. **Messaging** → **WhatsApp Sandbox Settings**
3. Set webhook to: `https://your-railway-url/whatsapp`
4. Save

## Done!

Your chatbot is now live on WhatsApp. Send a message to test it!

## Auto-Deploy on Push

Every time you push to GitHub, Railway will automatically redeploy your bot.

To make changes:
```bash
git add .
git commit -m "Your changes"
git push
```

Railway will automatically redeploy within seconds.
