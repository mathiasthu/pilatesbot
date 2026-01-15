# Quick Start Guide

Get the Pilates booking bot up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

## Step 2: Test Your Setup

```bash
python3 test_setup.py
```

This will verify:
- Configuration is valid
- All dependencies are installed
- Timezone is correct
- Target dates are calculated properly

## Step 3: Run a Test Booking (Manual)

**IMPORTANT**: This will attempt to book actual sessions! Only run if you're ready to book.

```bash
python3 pilates_bot.py
```

The bot will:
- Open a browser window (you can watch the process)
- Navigate to Acuity Scheduling
- Attempt to book Mon/Thu/Sat sessions for next week
- Log all actions to `pilates_bot.log`

## Step 4: Set Up Automated Scheduling

Once you've verified the bot works, set up the weekly cron job:

```bash
./setup_cron.sh
```

Press Enter to accept the default schedule (Monday 12:01 AM), or enter a custom cron expression.

## Verification

Check that the cron job is scheduled:

```bash
crontab -l
```

You should see a line like:
```
1 0 * * 1 cd /home/user/pilatesbot && /usr/bin/python3 pilates_bot.py >> /home/user/pilatesbot/cron.log 2>&1
```

## Next Week's Schedule

The bot will automatically book these sessions:

- **Monday** at 3:40 PM - Midday Flow
- **Thursday** at 3:40 PM - Midday Flow
- **Saturday** at 3:40 PM - Midday Flow

All bookings are for **1 week in advance** (next week's sessions).

## Enable WhatsApp Notifications (Optional)

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Twilio credentials:
   ```bash
   nano .env
   ```

3. Set `ENABLE_NOTIFICATIONS=true` and add your Twilio account details

4. Test notifications by running the bot manually

## Troubleshooting

### Bot doesn't find sessions

1. Set `headless: false` in `config.yaml` to watch the browser
2. Check `pilates_bot.log` for errors
3. Verify the Acuity Scheduling URL is still valid
4. Website structure may have changed - update selectors in `pilates_bot.py`

### Cron job not running

```bash
# Check cron service
sudo service cron status

# View cron logs
tail -f cron.log
```

## Important Notes

- The bot books **1 week in advance** to secure the limited 4 spots per session
- It runs every **Monday at 12:01 AM** Vietnam time
- Sessions are for **Thoon Nay** with the configured contact info
- Alternative sessions require confirmation before booking (configurable)

## What's Next?

The bot is now fully automated! It will:

1. Wake up every Monday at 12:01 AM
2. Book next week's Mon/Thu/Sat sessions
3. Send WhatsApp notifications (if configured)
4. Log everything to `pilates_bot.log` and `cron.log`

**You don't need to do anything else!** Just check the logs occasionally to ensure bookings are successful.

---

For detailed documentation, see [README.md](README.md)
