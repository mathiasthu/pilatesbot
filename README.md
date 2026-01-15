# Pilates Booking Bot 🧘‍♀️

An automated bot that books Pilates sessions on Acuity Scheduling for "Midday Flow" classes every Monday, Thursday, and Saturday at 3:40 PM.

## Features

- **Automated Booking**: Books sessions for the upcoming week automatically
- **Smart Scheduling**: Runs every Monday at 12:01 AM (Vietnam time) to secure spots 1 week in advance
- **Alternative Session Detection**: Finds alternative times if preferred slot is unavailable
- **Telegram Notifications**: Sends alerts for successful bookings, alternatives needing confirmation, or errors
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Configurable**: Easy to customize via YAML configuration file

## Prerequisites

- Python 3.8 or higher
- Internet connection
- (Optional) Telegram account for notifications

## Installation

1. **Clone or navigate to the repository:**
   ```bash
   cd pilatesbot
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Configure the bot:**
   - Review and modify `config.yaml` if needed (user info is already set)
   - Copy `.env.example` to `.env` and add your Telegram credentials (optional):
     ```bash
     cp .env.example .env
     nano .env  # Edit with your credentials
     ```

## Configuration

### config.yaml

The main configuration file contains:

- **booking_url**: Acuity Scheduling URL (pre-configured)
- **user_info**: Name, phone, email (already set for Thoon Nay)
- **session**: Class name ("Midday Flow"), time (3:40 PM), days (Mon/Thu/Sat)
- **booking**: Settings for advance booking, alternatives, confirmations
- **browser**: Headless mode and timeout settings
- **timezone**: Set to Asia/Ho_Chi_Minh (Vietnam)

### Telegram Notifications (Optional)

To enable Telegram notifications:

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts to create your bot
3. Save the **Bot Token** provided by BotFather
4. Start a chat with your bot and send any message
5. Get your **Chat ID** from: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
6. Update `.env` with your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ENABLE_NOTIFICATIONS=true
   ```
7. Test notifications: `python3 test_telegram.py`

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#-setup-telegram-bot-required-for-all-options) for detailed instructions.

## Usage

### Manual Execution

Run the bot manually to test or book sessions immediately:

```bash
python3 pilates_bot.py
```

The bot will:
1. Calculate target dates for next week (Mon, Thu, Sat)
2. Open a browser and navigate to Acuity Scheduling
3. Select "Midday Flow" class
4. Book sessions at 3:40 PM for each day
5. Fill in user information
6. Submit bookings
7. Log results and send notifications

### Automated Scheduling (Recommended)

Set up a cron job to run the bot automatically every Monday at 12:01 AM:

```bash
./setup_cron.sh
```

This script will:
- Configure a cron job with the specified schedule
- Set up logging to `cron.log`
- Show existing cron jobs

**Default schedule**: Every Monday at 12:01 AM Vietnam time

To customize the schedule, edit the cron expression when prompted:
- Format: `minute hour day month weekday`
- Example: `1 0 * * 1` = Monday at 00:01
- Example: `0 20 * * 0` = Sunday at 20:00 (8 PM)

### Manual Cron Setup

Alternatively, set up cron manually:

```bash
crontab -e
```

Add this line:
```
1 0 * * 1 cd /home/user/pilatesbot && /usr/bin/python3 pilates_bot.py >> /home/user/pilatesbot/cron.log 2>&1
```

## Logs

The bot creates detailed logs in two locations:

1. **pilates_bot.log**: Main application log with timestamps
2. **cron.log**: Output from cron job executions

View logs:
```bash
tail -f pilates_bot.log
tail -f cron.log
```

## Troubleshooting

### Bot can't find session type or time slots

The Acuity Scheduling website structure may have changed. You can:

1. Run with `headless: false` in `config.yaml` to watch the browser
2. Check the logs for specific error messages
3. Take screenshots (automatically saved on errors)
4. Update the CSS selectors in `pilates_bot.py` if needed

### Sessions already booked

If running multiple times, the bot will attempt to book even if sessions are already reserved. Check your Acuity account to avoid double bookings.

### Cron job not running

Verify the cron job is set up:
```bash
crontab -l
```

Check cron is running:
```bash
sudo service cron status
```

Check logs for errors:
```bash
tail -f cron.log
```

### Telegram notifications not working

1. Verify credentials in `.env` (bot token and chat ID)
2. Check `ENABLE_NOTIFICATIONS=true`
3. Ensure you've sent a message to your bot (click "Start" button)
4. Test with: `python3 test_telegram.py`
5. Check logs for error messages: `tail pilates_bot.log`

## How It Works

1. **Calculate Target Dates**: Determines which Monday, Thursday, and Saturday to book (1 week ahead)
2. **Browser Automation**: Uses Playwright to control a Chromium browser
3. **Navigation**: Goes to Acuity Scheduling booking page
4. **Class Selection**: Finds and clicks "Midday Flow" appointment type
5. **Date & Time**: Selects the target date and 3:40 PM time slot
6. **Form Filling**: Enters name, phone, email
7. **Submission**: Submits the booking and waits for confirmation
8. **Alternative Handling**: If preferred time unavailable, finds alternatives and notifies
9. **Notifications**: Sends Telegram messages for success, alternatives, or errors
10. **Logging**: Records all actions and outcomes

## Booking Logic

- **Runs**: Every Monday at 12:01 AM Vietnam time
- **Books For**: Next week's Mon/Thu/Sat sessions
- **Advance Booking**: 1 week ahead (configurable)
- **Priority**: 3:40 PM time slot
- **Fallback**: Same day, different time (within 2 hours)
- **Confirmation**: Required for alternative sessions (configurable)

## Customization

### Change Booking Days

Edit `config.yaml`:
```yaml
session:
  days:
    - "Monday"
    - "Wednesday"  # Changed from Thursday
    - "Saturday"
```

### Change Booking Time

Edit `config.yaml`:
```yaml
session:
  time: "4:00 PM"  # Changed from 3:40 PM
```

### Change Run Schedule

Run `./setup_cron.sh` and enter a new cron expression, or edit crontab manually.

### Adjust Browser Behavior

Edit `config.yaml`:
```yaml
browser:
  headless: true  # false = see browser window
  timeout: 30000  # 30 seconds
```

## Security Notes

- Never commit your `.env` file with real credentials
- Store sensitive information only in `.env` (already in `.gitignore`)
- Review code before running on production systems
- Acuity Scheduling may block automated requests - use responsibly

## Booking Schedule Example

If bot runs on **Monday, January 15, 2026 at 12:01 AM**, it will book:

- Monday, January 22, 2026 at 3:40 PM
- Thursday, January 25, 2026 at 3:40 PM
- Saturday, January 27, 2026 at 3:40 PM

Next run on **Monday, January 22, 2026 at 12:01 AM** will book:

- Monday, January 29, 2026 at 3:40 PM
- Thursday, February 1, 2026 at 3:40 PM
- Saturday, February 3, 2026 at 3:40 PM

## Support

For issues or questions:
1. Check the logs first (`pilates_bot.log`)
2. Review the configuration (`config.yaml`)
3. Test manual execution: `python3 pilates_bot.py`
4. Verify cron setup: `crontab -l`

## License

Personal use project. Modify as needed.

---

Built with ❤️ for seamless Pilates session booking
