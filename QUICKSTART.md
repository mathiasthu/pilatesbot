# Quick Start Guide

Get the Pilates booking bot up and running in 5 minutes!

## Where Should I Run This?

**Need help deciding where to run the bot?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed options:
- VPS/Cloud Server (most reliable) - $5/month
- Raspberry Pi (one-time $50)
- Your computer (free)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

## Step 2: Setup Telegram Bot (5 minutes)

The bot sends you notifications via Telegram. Follow these steps:

### Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send: `/newbot`
3. Follow prompts to name your bot (e.g., "Pilates Booking Bot")
4. Save the **Bot Token** (looks like: `123456789:ABCdefGHI...`)

### Get Your Chat ID

1. Search for your bot and send it a message: "Hello"
2. Open this URL in browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Find `"chat":{"id":123456789` - this is your **Chat ID**

### Configure Bot

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Add your credentials:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
ENABLE_NOTIFICATIONS=true
```

## Step 3: Test Telegram Notifications

```bash
python3 test_telegram.py
```

You should receive a test message on Telegram! If not, check your token and chat ID.

## Step 4: Test Bot Setup

```bash
python3 test_setup.py
```

This verifies:
- Configuration is valid
- All dependencies are installed
- Timezone is correct (Vietnam)
- Target booking dates are calculated properly

All checks should pass ✓

## Step 5: Run a Test Booking (Manual)

**⚠️ IMPORTANT**: This will attempt to book actual sessions! Only run when ready.

```bash
python3 pilates_bot.py
```

The bot will:
- Open a browser window (you can watch it work)
- Navigate to Acuity Scheduling
- Try to book Mon/Thu/Sat sessions for next week at 3:40 PM
- Fill in Thoon Nay's information
- Log everything to `pilates_bot.log`

Watch the browser and check if it successfully:
1. Finds "Midday Flow"
2. Selects dates and times
3. Fills the form
4. Submits bookings

## Step 6: Set Up Automated Weekly Scheduling

Once you've verified it works, automate it!

**Linux/Mac/VPS:**
```bash
./setup_cron.sh
```

Press Enter to accept default (Monday 12:01 AM).

**Windows:**
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#setup---windows) for Task Scheduler setup.

## Verification

**Check cron job is scheduled:**
```bash
crontab -l
```

Should show:
```
1 0 * * 1 cd /home/user/pilatesbot && python3 pilates_bot.py >> cron.log 2>&1
```

## What Gets Booked?

The bot automatically books these sessions **1 week in advance**:

- **Monday** at 3:40 PM - Midday Flow
- **Thursday** at 3:40 PM - Midday Flow
- **Saturday** at 3:40 PM - Midday Flow

**When:** Every Monday at 12:01 AM Vietnam time
**For:** Thoon Nay (+4540161703, fidomathias078@gmail.com)

## Monitoring

**View logs:**
```bash
tail -f pilates_bot.log  # Main log
tail -f cron.log          # Cron execution log
```

**Check what will be booked:**
```bash
python3 test_setup.py
```

Shows target dates for next booking.

## Troubleshooting

### Telegram not working
```bash
# Test again
python3 test_telegram.py

# Check .env file has correct token and chat ID
cat .env
```

### Bot can't find sessions

1. Set `headless: false` in `config.yaml` to watch browser
2. Check `pilates_bot.log` for errors
3. Website structure may have changed - see logs for which selector failed

### Cron job not running

```bash
# Verify cron is set up
crontab -l

# Check cron service (Linux)
sudo service cron status

# View cron execution log
tail -f cron.log
```

## Important Notes

✓ Books **1 week ahead** to secure the 4 limited spots per session
✓ Runs **Monday 12:01 AM** Vietnam time automatically
✓ Sends **Telegram notifications** for success/failures/alternatives
✓ Logs everything for troubleshooting

## What's Next?

**You're done!** The bot is now fully automated and will:

1. ⏰ Wake up every Monday at 12:01 AM
2. 🎯 Book next week's Mon/Thu/Sat sessions
3. 📱 Send Telegram notifications
4. 📝 Log all actions

**Just check Telegram or logs occasionally to ensure bookings succeed!**

---

## More Information

- **Full Documentation:** [README.md](README.md)
- **Deployment Options:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Telegram Setup:** [DEPLOYMENT_GUIDE.md#-setup-telegram-bot-required-for-all-options](DEPLOYMENT_GUIDE.md#-setup-telegram-bot-required-for-all-options)
