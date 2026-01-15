# Running Pilates Bot on MacBook - Complete Guide

This guide will help you set up and run the Pilates booking bot on your MacBook.

## Prerequisites

Your MacBook needs to be:
- **On at booking time** (Monday 12:01 AM Vietnam time)
- Or you can adjust the schedule to run when your Mac is typically on
- Connected to the internet

## Step 1: Install Homebrew (Package Manager)

Open **Terminal** (search for Terminal in Spotlight with Cmd+Space).

Check if Homebrew is already installed:
```bash
brew --version
```

If not installed, install it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the prompts. After installation, you may need to add Homebrew to your PATH:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

## Step 2: Install Python 3

```bash
# Install Python 3
brew install python@3.11

# Verify installation
python3 --version
# Should show Python 3.11.x or higher
```

## Step 3: Install Git

```bash
# Install Git
brew install git

# Verify installation
git --version
```

## Step 4: Clone the Repository

```bash
# Navigate to your home directory
cd ~

# Clone the repository
git clone https://github.com/mathiasthu/pilatesbot.git

# Navigate into the project
cd pilatesbot

# Verify files are there
ls -la
```

You should see files like `pilates_bot.py`, `config.yaml`, etc.

## Step 5: Install Python Dependencies

```bash
# Make sure you're in the pilatesbot directory
cd ~/pilatesbot

# Install required Python packages
pip3 install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install Playwright system dependencies (if needed)
playwright install-deps chromium
```

This may take a few minutes to download everything.

## Step 6: Setup Telegram Bot

### Create Your Telegram Bot

1. **Open Telegram** on your phone or Mac
2. Search for **@BotFather** (it has a blue checkmark)
3. Send: `/newbot`
4. **Bot name:** "Pilates Booking Bot" (or any name you like)
5. **Bot username:** Must end in `bot`, e.g., `thoon_pilates_bot`
6. BotFather will reply with your **Bot Token**:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
7. **Copy this token** - you'll need it in a moment

### Get Your Chat ID

1. Search for your bot (e.g., `@thoon_pilates_bot`)
2. Click **Start** or send any message like "Hello"
3. Open this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. You'll see JSON like this:
   ```json
   {"ok":true,"result":[{"message":{"chat":{"id":987654321,...
   ```
5. Find the number after `"chat":{"id":` - this is your **Chat ID** (e.g., `987654321`)

### Configure the Bot

```bash
# Make sure you're in the pilatesbot directory
cd ~/pilatesbot

# Copy the example environment file
cp .env.example .env

# Open the file in TextEdit (or use nano/vim)
open -e .env
```

**Edit the `.env` file** and add your credentials:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
ENABLE_NOTIFICATIONS=true
```

Save and close the file (Cmd+S, then Cmd+Q).

## Step 7: Test Your Setup

### Test 1: Configuration Test

```bash
cd ~/pilatesbot
python3 test_setup.py
```

You should see all checks passing with ✓ marks:
```
✓ PASS: Configuration
✓ PASS: Timezone
✓ PASS: Dependencies
✓ PASS: Environment
✓ PASS: Target Dates
```

### Test 2: Telegram Notification Test

```bash
python3 test_telegram.py
```

You should receive a message on Telegram! 📱

If you get an error:
- Check your bot token and chat ID in `.env`
- Make sure you started the bot on Telegram (click "Start")
- Verify `ENABLE_NOTIFICATIONS=true`

## Step 8: Test Booking (Optional but Recommended)

**⚠️ WARNING:** This will attempt to make **REAL bookings**!

Only run this if you're ready to book sessions for next week.

```bash
python3 pilates_bot.py
```

The bot will:
1. Open a Chrome browser window (you can watch it work!)
2. Navigate to Acuity Scheduling
3. Try to find and book "Midday Flow" sessions
4. Fill in the form with Thoon Nay's information
5. Attempt to submit the bookings

**Watch the browser** and check if:
- ✓ It finds "Midday Flow"
- ✓ It selects dates (next week's Mon/Thu/Sat)
- ✓ It clicks on time slots (3:40 PM)
- ✓ It fills the form
- ✓ It submits successfully

**Check the log file:**
```bash
tail -20 pilates_bot.log
```

Look for "Successfully booked" or error messages.

### If the test fails:

1. **Website structure changed?**
   - Set `headless: false` in `config.yaml` (already set by default)
   - Watch what the browser does
   - Check logs: `tail -50 pilates_bot.log`

2. **Can't find elements?**
   - The website may have changed its structure
   - You may need to update selectors in `pilates_bot.py`

## Step 9: Setup Automated Scheduling

Now that everything works, let's automate it!

### Option A: Run When Mac is Awake (Recommended for MacBook)

Since MacBooks typically sleep at night, you have two options:

**Option 1: Keep Mac awake Monday nights** (see Step 10)
**Option 2: Run at a different time when your Mac is awake**

### Set Up the Cron Job

```bash
# Open crontab editor
EDITOR=nano crontab -e
```

**If your Mac is awake at midnight Monday:**
```bash
# Add this line (runs Monday 12:01 AM Vietnam time)
1 0 * * 1 cd ~/pilatesbot && /opt/homebrew/bin/python3 pilates_bot.py >> ~/pilatesbot/cron.log 2>&1
```

**If you want to run at a different time:**
Examples (all times in Vietnam timezone):
```bash
# Monday 8:00 AM Vietnam time
0 8 * * 1 cd ~/pilatesbot && /opt/homebrew/bin/python3 pilates_bot.py >> ~/pilatesbot/cron.log 2>&1

# Sunday 8:00 PM Vietnam time (more reliable if Mac is on)
0 20 * * 0 cd ~/pilatesbot && /opt/homebrew/bin/python3 pilates_bot.py >> ~/pilatesbot/cron.log 2>&1

# Monday 10:00 PM Vietnam time (late evening)
0 22 * * 1 cd ~/pilatesbot && /opt/homebrew/bin/python3 pilates_bot.py >> ~/pilatesbot/cron.log 2>&1
```

**Cron format explained:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, where 0 and 7 are Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter`

**Verify cron job is set:**
```bash
crontab -l
```

You should see your scheduled job listed.

## Step 10: Keep Your Mac Awake for Bookings

MacBooks typically sleep when closed or inactive. Here are your options:

### Option A: Prevent Sleep on Monday Nights

**Use an app like Amphetamine (Free from Mac App Store):**

1. Install [Amphetamine](https://apps.apple.com/us/app/amphetamine/id937984704) from App Store
2. Set up a trigger:
   - Open Amphetamine preferences
   - Go to "Triggers"
   - Create new trigger: "Time-based"
   - Schedule: Monday 11:50 PM to 12:30 AM
   - This keeps your Mac awake during booking time

### Option B: Use caffeinate Command

Create a helper script:

```bash
# Create a script to keep Mac awake
cat > ~/pilatesbot/keep_awake_and_run.sh << 'EOF'
#!/bin/bash
# Keep Mac awake for 30 minutes and run the booking bot
caffeinate -t 1800 python3 ~/pilatesbot/pilates_bot.py
EOF

chmod +x ~/pilatesbot/keep_awake_and_run.sh
```

Then update your cron job to use this script:
```bash
crontab -e
```

Change the line to:
```bash
1 0 * * 1 cd ~/pilatesbot && /bin/bash keep_awake_and_run.sh >> cron.log 2>&1
```

### Option C: Change Booking Time

**Run the bot at a time when your Mac is typically on:**

```bash
# Edit cron to run at a different time
crontab -e
```

Good times when MacBook is usually awake:
- **Sunday 8:00 PM:** `0 20 * * 0`
- **Monday 8:00 AM:** `0 8 * * 1`
- **Monday 10:00 AM:** `0 10 * * 1`

**Note:** You're booking 1 week ahead, so as long as you book before spots fill up (which happens fast since there are only 4 spots), timing is flexible!

### Option D: Don't Let Mac Sleep (Not Recommended)

```bash
# Keep Mac awake always (not recommended, drains battery)
sudo pmset -a disablesleep 1

# To undo later:
sudo pmset -a disablesleep 0
```

## Step 11: Verify Automated Setup

Let's make sure everything is configured correctly:

```bash
# 1. Check cron job is set
crontab -l

# 2. Check Python path is correct
which python3
# Should show: /opt/homebrew/bin/python3 (or /usr/local/bin/python3)

# 3. Check bot files exist
ls -la ~/pilatesbot/pilates_bot.py

# 4. Test configuration
cd ~/pilatesbot
python3 test_setup.py

# 5. Check logs directory is writable
touch ~/pilatesbot/test.log && rm ~/pilatesbot/test.log
```

All commands should succeed without errors.

## Monitoring & Maintenance

### Check if Bot Ran Successfully

```bash
# View main log
tail -50 ~/pilatesbot/pilates_bot.log

# View cron execution log
tail -50 ~/pilatesbot/cron.log

# Search for successful bookings
grep -i "successfully booked" ~/pilatesbot/pilates_bot.log

# Check latest run
tail -100 ~/pilatesbot/cron.log
```

### Check Telegram Messages

The easiest way to monitor is via Telegram! You'll get messages about:
- ✅ Successful bookings
- ⚠️ Alternative times needed
- ❌ Errors

### View Logs in Real-Time

While the bot is running:
```bash
tail -f ~/pilatesbot/pilates_bot.log
```

Press `Ctrl+C` to stop watching.

### Manual Test Run

Run the bot manually anytime:
```bash
cd ~/pilatesbot
python3 pilates_bot.py
```

## What Gets Booked?

The bot books **next week's sessions**:
- **Monday** 3:40 PM - Midday Flow
- **Thursday** 3:40 PM - Midday Flow
- **Saturday** 3:40 PM - Midday Flow

**Example:** If bot runs on January 15, 2026, it books:
- January 22 (Mon)
- January 25 (Thu)
- January 27 (Sat)

## Troubleshooting

### "Command not found: python3"

```bash
# Try with full path
/opt/homebrew/bin/python3 --version

# Or install Python
brew install python@3.11
```

### "playwright: command not found"

```bash
# Install Playwright
pip3 install playwright
playwright install chromium
```

### Cron job not running

1. **Check cron syntax:**
   ```bash
   crontab -l
   ```

2. **Check Mac didn't sleep:**
   - Use Amphetamine or caffeinate
   - Or schedule when Mac is awake

3. **Check Python path in cron:**
   ```bash
   which python3
   ```
   Use full path in crontab (e.g., `/opt/homebrew/bin/python3`)

4. **Check cron logs:**
   ```bash
   tail -100 ~/pilatesbot/cron.log
   ```

### Bot can't find sessions

1. **Set headless mode off** to watch browser:
   ```bash
   nano ~/pilatesbot/config.yaml
   ```
   Change `headless: true` to `headless: false`

2. **Run manually** to see what happens:
   ```bash
   cd ~/pilatesbot
   python3 pilates_bot.py
   ```

3. **Check logs** for specific errors:
   ```bash
   tail -100 ~/pilatesbot/pilates_bot.log
   ```

### Mac goes to sleep

Use one of these solutions:
- Install Amphetamine and set Monday night trigger
- Use `caffeinate` command in script
- Change booking time to when Mac is awake
- Keep Mac plugged in and set Energy Saver settings

### Permission denied errors

```bash
# Make scripts executable
chmod +x ~/pilatesbot/setup_cron.sh
chmod +x ~/pilatesbot/keep_awake_and_run.sh

# Check file permissions
ls -la ~/pilatesbot/
```

## Tips for MacBook Users

1. **Keep Mac plugged in** on Monday nights if running at midnight
2. **Close lid but keep Mac on:** System Settings → Lock Screen → Turn display off: Never (when plugged in)
3. **Check battery:** Make sure Mac won't die during booking
4. **Stable internet:** Connect via Ethernet or ensure strong WiFi
5. **Test first:** Run `python3 pilates_bot.py` manually before automating
6. **Check Telegram:** Easiest way to monitor - you'll get notifications!
7. **Update macOS carefully:** Test bot after OS updates

## Energy Saver Settings (Optional)

To prevent sleep when plugged in:

1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Battery** (or **Energy Saver**)
3. Click **Power Adapter** settings
4. Set:
   - **Prevent automatic sleeping when display is off:** ON (when plugged in)
   - **Wake for network access:** ON

Or use Terminal:
```bash
# Prevent sleep when plugged in
sudo pmset -c sleep 0
sudo pmset -c disablesleep 0

# Restore default later
sudo pmset -c sleep 10
```

## Quick Reference Commands

```bash
# Navigate to bot directory
cd ~/pilatesbot

# Run bot manually
python3 pilates_bot.py

# Test setup
python3 test_setup.py

# Test Telegram
python3 test_telegram.py

# View logs
tail -50 pilates_bot.log

# View cron log
tail -50 cron.log

# Edit cron schedule
crontab -e

# List cron jobs
crontab -l

# Update bot from git
git pull
```

## Updating the Bot

If I make updates to the bot:

```bash
cd ~/pilatesbot
git pull origin claude/pilates-booking-bot-E0pu9
pip3 install -r requirements.txt
```

## Summary Checklist

- [ ] Homebrew installed
- [ ] Python 3.11+ installed
- [ ] Repository cloned to `~/pilatesbot`
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] Telegram bot created with @BotFather
- [ ] `.env` file configured with bot token and chat ID
- [ ] `test_setup.py` passes all checks
- [ ] `test_telegram.py` sends message successfully
- [ ] `pilates_bot.py` successfully books (test run)
- [ ] Cron job configured (`crontab -l` shows entry)
- [ ] Mac sleep settings configured (stays awake for booking)
- [ ] Telegram notifications working

## You're All Set! 🎉

Your MacBook will now automatically book Pilates sessions every week!

**What happens next:**
1. Bot runs on schedule (Monday 12:01 AM, or your custom time)
2. Books Mon/Thu/Sat sessions for next week
3. Sends you Telegram notifications
4. Logs everything for troubleshooting

**Check occasionally:**
- Telegram messages for booking confirmations
- `tail ~/pilatesbot/pilates_bot.log` to see logs

**Need help?** Check logs first, they're very detailed!

---

**Pro Tip:** Set a calendar reminder for yourself every Monday morning to check Telegram and verify bookings went through. Once you see it working reliably for a few weeks, you can stop checking!
