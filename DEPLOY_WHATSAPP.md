# Deploy FridgeFix WhatsApp Bot

## Step 1: Push to GitHub

```bash
git add .
git commit -m "FridgeFix WhatsApp bot ready for deployment"
git push origin main
```

## Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub**
3. Select your `fridgefix-whatsapp-bot` repository
4. Railway auto-detects Python app
5. Add environment variables:
   - `TWILIO_ACCOUNT_SID` = your SID
   - `TWILIO_AUTH_TOKEN` = your token
   - `TWILIO_WHATSAPP_NUMBER` = your WhatsApp number
6. Click **Deploy**

## Step 3: Get Your Railway URL

After deployment, Railway gives you a URL like:
```
https://fridgefix-bot-production.up.railway.app
```

## Step 4: Set Up Twilio WhatsApp

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to **Messaging** → **WhatsApp Sandbox Settings**
3. Set **When a message comes in** webhook to:
   ```
   https://your-railway-url/whatsapp
   ```
4. Save

## Step 5: Test Your Bot

1. Send a message to your Twilio WhatsApp number
2. Bot should respond with welcome message
3. Follow the conversation flow

## Troubleshooting

**Bot not responding:**
- Check Railway logs for errors
- Verify webhook URL is correct
- Ensure environment variables are set

**Wrong formatting:**
- Check app.py for `\n` line breaks
- Verify Twilio is using `/whatsapp` endpoint

**Phone validation failing:**
- Test with format: `+27821234567` or `0821234567`
- Check validate_sa_phone function

## Production Checklist

- [ ] GitHub repo created and pushed
- [ ] Railway deployed successfully
- [ ] Environment variables set
- [ ] Twilio webhook configured
- [ ] Bot tested with sample messages
- [ ] All 9 SA provinces recognized
- [ ] Gmail validation working
- [ ] Issue list displays correctly
- [ ] Confirmation message shows all details
- [ ] Exit/restart functionality works

## Support

- Twilio Docs: https://www.twilio.com/docs/whatsapp
- Railway Docs: https://docs.railway.app
- FridgeFix: support@fridgefix.co.za
