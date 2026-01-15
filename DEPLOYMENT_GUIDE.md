# Deployment Guide - Where and How to Run the Pilates Bot

This guide explains **where** you can run the bot and **exactly how** to set it up on each platform.

## 🎯 Where Can I Run This Bot?

The bot needs to run 24/7 on a system that:
- Has Python 3.8+
- Has internet connection
- Can run scheduled tasks (cron jobs)
- Stays on at least during booking time (Monday 12:01 AM Vietnam time)

### Recommended Options (Best to Worst)

| Option | Cost | Difficulty | Reliability | Best For |
|--------|------|------------|-------------|----------|
| **VPS/Cloud Server** | $5-10/month | Medium | ⭐⭐⭐⭐⭐ | Most reliable, always on |
| **Raspberry Pi** | $35 one-time | Easy | ⭐⭐⭐⭐ | Home server, low power |
| **Old Laptop/PC** | Free | Easy | ⭐⭐⭐ | If you have spare hardware |
| **Your Main Computer** | Free | Easy | ⭐⭐ | Must be on Monday midnight |

---

## Option 1: VPS/Cloud Server (RECOMMENDED)

**Best for: Reliability and "set it and forget it"**

A VPS (Virtual Private Server) runs 24/7 in the cloud. This is the most reliable option.

### Providers (Cheapest to Most Expensive)

1. **Vultr** - $2.50-5/month (Recommended)
2. **DigitalOcean** - $4-6/month
3. **Linode (Akamai)** - $5/month
4. **AWS Lightsail** - $3.50-5/month
5. **Google Cloud** - $10/month (with free tier first year)

### Step-by-Step Setup (Vultr Example)

#### 1. Create a VPS

1. Go to [Vultr.com](https://www.vultr.com/) and sign up
2. Click "Deploy New Server"
3. Choose:
   - **Server Type**: Cloud Compute - Shared CPU
   - **Location**: Singapore (closest to Vietnam)
   - **OS**: Ubuntu 22.04 LTS
   - **Plan**: $5/month (1 CPU, 1GB RAM) - plenty for this bot
4. Click "Deploy Now"
5. Wait 2-3 minutes for server to be ready
6. Note your server's IP address and root password

#### 2. Connect to Your Server

**On Windows:**
```bash
# Download and install PuTTY from putty.org
# Or use Windows Terminal with SSH:
ssh root@YOUR_SERVER_IP
```

**On Mac/Linux:**
```bash
ssh root@YOUR_SERVER_IP
```

Enter the password when prompted.

#### 3. Initial Server Setup

```bash
# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install -y python3 python3-pip git

# Install Playwright system dependencies
apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libasound2
```

#### 4. Clone and Setup the Bot

```bash
# Clone your repository
git clone https://github.com/mathiasthu/pilatesbot.git
cd pilatesbot

# Install Python dependencies
pip3 install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

#### 5. Configure the Bot

```bash
# Create environment file
cp .env.example .env
nano .env
```

Add your Telegram credentials (see "Setup Telegram Bot" section below).

Press `Ctrl+X`, then `Y`, then `Enter` to save.

#### 6. Test the Bot

```bash
# First, test the setup
python3 test_setup.py

# If all passes, do a test run (WILL ATTEMPT TO BOOK!)
python3 pilates_bot.py
```

Watch for any errors. Check the logs:
```bash
tail -f pilates_bot.log
```

#### 7. Setup Automated Scheduling

```bash
# Run the cron setup script
./setup_cron.sh
# Press Enter to accept default schedule (Monday 12:01 AM)

# Verify cron job
crontab -l
```

#### 8. Keep It Running (Optional - for monitoring)

Install a process manager to restart the bot if it crashes:

```bash
# Install PM2 (optional, for monitoring)
apt install -y npm
npm install -g pm2

# Or just rely on cron - it will run every Monday anyway
```

### VPS Management

**View logs remotely:**
```bash
ssh root@YOUR_SERVER_IP
cd pilatesbot
tail -f pilates_bot.log
```

**Update the bot:**
```bash
ssh root@YOUR_SERVER_IP
cd pilatesbot
git pull
```

**Cost:** ~$5/month, always on, very reliable

---

## Option 2: Raspberry Pi (HOME SERVER)

**Best for: One-time cost, home automation enthusiast**

### What You Need

- Raspberry Pi 4 (2GB+ RAM) - $35-55
- MicroSD card (16GB+) - $10
- Power supply - $8
- Total: ~$50-75 one-time

### Setup Steps

#### 1. Install Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash "Raspberry Pi OS Lite (64-bit)" to SD card
3. Enable SSH in settings before flashing
4. Insert SD card into Pi and power on

#### 2. Connect to Pi

Find your Pi's IP address from your router, then:

```bash
ssh pi@YOUR_PI_IP
# Default password: raspberry
```

#### 3. Setup the Bot

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip git chromium-browser chromium-codecs-ffmpeg

# Clone repository
git clone https://github.com/mathiasthu/pilatesbot.git
cd pilatesbot

# Install Python packages
pip3 install -r requirements.txt

# Install Playwright
playwright install chromium
```

#### 4. Configure and Test

```bash
# Setup environment
cp .env.example .env
nano .env  # Add your Telegram credentials

# Test
python3 test_setup.py
python3 pilates_bot.py  # Test run
```

#### 5. Setup Cron

```bash
./setup_cron.sh
```

#### 6. Keep Pi Running

- Plug Pi into router via Ethernet (more reliable than WiFi)
- Leave Pi powered on 24/7 (uses ~5W, costs ~$0.50/month electricity)
- Check logs occasionally: `ssh pi@YOUR_PI_IP "tail pilatesbot/pilates_bot.log"`

**Pros:** One-time cost, runs at home
**Cons:** Depends on home internet, power outages affect it

---

## Option 3: Old Laptop/Desktop (HOME COMPUTER)

**Best for: Using spare hardware you already have**

### Requirements

- Windows, Mac, or Linux computer
- Python 3.8+ installed
- Must stay on during booking time (or all the time)

### Setup - Windows

#### 1. Install Python

1. Download [Python 3.11+](https://www.python.org/downloads/)
2. Run installer, **CHECK "Add Python to PATH"**
3. Verify: Open CMD and type `python --version`

#### 2. Install Git

1. Download [Git for Windows](https://git-scm.com/download/win)
2. Install with default options

#### 3. Clone and Setup

Open **Git Bash** or **PowerShell**:

```bash
# Clone repository
git clone https://github.com/mathiasthu/pilatesbot.git
cd pilatesbot

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure
copy .env.example .env
notepad .env  # Add your Telegram credentials

# Test
python test_setup.py
python pilates_bot.py  # Test run
```

#### 4. Setup Windows Task Scheduler

1. Open Task Scheduler (search in Start menu)
2. Click "Create Basic Task"
3. Name: "Pilates Booking Bot"
4. Trigger: Weekly, Monday, 12:01 AM
5. Action: Start a program
   - Program: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`
   - Arguments: `pilates_bot.py`
   - Start in: `C:\path\to\pilatesbot`
6. Click Finish

### Setup - Mac

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Clone and setup
git clone https://github.com/mathiasthu/pilatesbot.git
cd pilatesbot
pip3 install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
nano .env  # Add Telegram credentials

# Test
python3 test_setup.py
python3 pilates_bot.py
```

Setup cron job:
```bash
crontab -e
# Add this line:
1 0 * * 1 cd /Users/yourname/pilatesbot && /usr/local/bin/python3 pilates_bot.py >> /Users/yourname/pilatesbot/cron.log 2>&1
```

### Setup - Linux

Same as VPS setup above, but no need to SSH - just run commands directly in terminal.

**Pros:** Free, uses existing hardware
**Cons:** Computer must stay on, consumes more power than Pi/VPS

---

## 🤖 Setup Telegram Bot (REQUIRED FOR ALL OPTIONS)

Follow these steps to create your Telegram bot and get credentials:

### Step 1: Create a Telegram Bot

1. Open Telegram app on your phone or computer
2. Search for **@BotFather** (official Telegram bot)
3. Start a chat and send: `/newbot`
4. Follow the prompts:
   - **Bot name:** "Pilates Booking Bot" (or any name)
   - **Username:** Must end in "bot", e.g., `thoon_pilates_bot`
5. BotFather will reply with your **Bot Token**: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
6. **SAVE THIS TOKEN** - you'll need it for `.env` file

### Step 2: Get Your Chat ID

1. Search for your new bot by username (e.g., `@thoon_pilates_bot`)
2. Click "Start" or send any message to your bot (e.g., "Hello")
3. Open this URL in your browser (replace with your token):
   ```
   https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/getUpdates
   ```
4. You'll see JSON response. Look for `"chat":{"id":987654321` - this number is your **Chat ID**
5. **SAVE THIS CHAT ID**

### Step 3: Configure `.env` File

Add these to your `.env` file:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
ENABLE_NOTIFICATIONS=true
```

### Step 4: Test Notifications

Run a quick test:

```python
# test_telegram.py (create this file)
from notifications import get_notifier

notifier = get_notifier()
notifier.send_message("🎉 <b>Telegram Bot is working!</b>")
```

Run it:
```bash
python3 test_telegram.py
```

You should receive a message on Telegram!

---

## ⚙️ Configuration Checklist

Before running the bot, verify these files:

### 1. config.yaml ✓
Already configured with:
- User info (Thoon Nay, phone, email)
- Session details (Midday Flow, Mon/Thu/Sat, 3:40 PM)
- Timezone (Vietnam)

### 2. .env (YOU MUST CREATE THIS)
```bash
cp .env.example .env
nano .env  # or notepad .env on Windows
```

Add:
```
TELEGRAM_BOT_TOKEN=your_actual_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here
ENABLE_NOTIFICATIONS=true
```

---

## 🧪 Testing Your Setup

### 1. Test Configuration
```bash
python3 test_setup.py
```

Should show all checks passing.

### 2. Test Notifications
```bash
# Create test file
cat > test_telegram.py << 'EOF'
from notifications import get_notifier
notifier = get_notifier()
notifier.send_message("🧘‍♀️ Test message from Pilates Bot!")
EOF

python3 test_telegram.py
```

Check your Telegram - you should get a message!

### 3. Dry Run (Optional - NO BOOKING)

Want to see the bot work without booking? Modify `config.yaml` temporarily:

```yaml
browser:
  headless: false  # Watch the browser
  timeout: 30000
```

Then add this to `pilates_bot.py` right before `await self.submit_booking(page)`:

```python
logger.info("DRY RUN - Would submit booking here")
return True  # Skip actual submission
```

### 4. Live Test (WILL ACTUALLY BOOK!)

**WARNING:** This will attempt real bookings!

```bash
python3 pilates_bot.py
```

Watch the output and check logs:
```bash
tail -f pilates_bot.log
```

---

## 📅 Scheduling Summary

The bot is configured to run:
- **When:** Every Monday at 12:01 AM
- **Timezone:** Vietnam (UTC+7)
- **Books for:** Next week's Mon/Thu/Sat sessions
- **Time:** 3:40 PM sessions

### Verify Scheduling

**Linux/Mac/VPS:**
```bash
crontab -l
# Should show:
# 1 0 * * 1 cd /path/to/pilatesbot && python3 pilates_bot.py >> cron.log 2>&1
```

**Windows:**
Open Task Scheduler and check for "Pilates Booking Bot" task

---

## 🔍 Monitoring & Maintenance

### Check Logs Remotely (VPS/Pi)

```bash
# SSH to your server
ssh user@server-ip

# View latest logs
cd pilatesbot
tail -20 pilates_bot.log

# Watch logs in real-time
tail -f pilates_bot.log

# Check cron execution log
tail cron.log
```

### Check if Bot Ran Successfully

Look for these in logs:
```
✓ "Successfully booked X sessions"
✓ "Booking confirmed"
✓ "Telegram message sent"
```

### Common Issues

**Bot didn't run:**
- Check cron is working: `crontab -l`
- Check system time: `date`
- Check logs: `tail cron.log`

**Can't find session type:**
- Website structure may have changed
- Run with `headless: false` to watch browser
- Check selector in `pilates_bot.py`

**Telegram not working:**
- Verify token/chat ID in `.env`
- Check notifications enabled: `ENABLE_NOTIFICATIONS=true`
- Test with `test_telegram.py`

---

## 💰 Cost Comparison

| Option | Setup Time | Monthly Cost | Reliability |
|--------|------------|--------------|-------------|
| **VPS (Vultr)** | 30 mins | $5 | Best ⭐⭐⭐⭐⭐ |
| **Raspberry Pi** | 1 hour | $0.50 | Great ⭐⭐⭐⭐ |
| **Old Laptop** | 20 mins | $2-5 | Good ⭐⭐⭐ |
| **Your Computer** | 15 mins | $0 | Okay ⭐⭐ |

---

## 🎯 My Recommendation

**If you want "set and forget":** Get a **$5/month VPS** (Vultr Singapore)
- 30 minutes setup
- Never think about it again
- Most reliable
- Access logs from anywhere

**If you want minimal cost:** Use a **Raspberry Pi 4**
- $50 one-time
- $0.50/month electricity
- Good reliability
- Fun project

**If you want free:** Use your **main computer**
- Must keep it on Monday nights
- Less reliable
- Good for testing first

---

## 📞 Support

**Check everything is working:**

1. Telegram notifications: `python3 test_telegram.py`
2. Configuration: `python3 test_setup.py`
3. Logs: `tail -f pilates_bot.log`
4. Cron job: `crontab -l`

**Something not working?**

1. Check logs first
2. Verify `.env` file has correct credentials
3. Test internet connection
4. Ensure system time is correct: `date`

---

## ✅ Final Checklist

Before leaving it to run automatically:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browser installed (`playwright install chromium`)
- [ ] `.env` file created with Telegram credentials
- [ ] `ENABLE_NOTIFICATIONS=true` in `.env`
- [ ] Test setup passed (`python3 test_setup.py`)
- [ ] Telegram test worked (received test message)
- [ ] **One successful test booking** (if you're ready)
- [ ] Cron job configured (`crontab -l` or Task Scheduler)
- [ ] Logs accessible (`tail pilates_bot.log`)

**You're all set!** The bot will automatically book sessions every Monday at 12:01 AM Vietnam time. 🎉
