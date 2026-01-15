#!/bin/bash

# Pilates Bot Cron Setup Script
# This script sets up a cron job to run the booking bot weekly

set -e

echo "=== Pilates Booking Bot - Cron Setup ==="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BOT_SCRIPT="$SCRIPT_DIR/pilates_bot.py"
PYTHON_PATH=$(which python3)

# Check if Python script exists
if [ ! -f "$BOT_SCRIPT" ]; then
    echo "Error: pilates_bot.py not found in $SCRIPT_DIR"
    exit 1
fi

# Default schedule: Every Monday at 12:01 AM Vietnam time
# Cron format: minute hour day month weekday
# 1 0 * * 1 = At 00:01 on Monday

read -p "Enter cron schedule (default: 1 0 * * 1 for Monday 12:01 AM): " CRON_SCHEDULE
CRON_SCHEDULE=${CRON_SCHEDULE:-"1 0 * * 1"}

# Create the cron command
CRON_CMD="cd $SCRIPT_DIR && $PYTHON_PATH $BOT_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

# Check if cron job already exists
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$BOT_SCRIPT" || true)

if [ ! -z "$EXISTING_CRON" ]; then
    echo "Found existing cron job:"
    echo "$EXISTING_CRON"
    echo ""
    read -p "Do you want to replace it? (y/n): " REPLACE
    if [ "$REPLACE" != "y" ]; then
        echo "Cancelled. No changes made."
        exit 0
    fi
    # Remove existing cron job
    (crontab -l 2>/dev/null | grep -v -F "$BOT_SCRIPT") | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_CMD") | crontab -

echo ""
echo "✓ Cron job added successfully!"
echo ""
echo "Schedule: $CRON_SCHEDULE"
echo "Command: $CRON_CMD"
echo ""
echo "Your cron jobs:"
crontab -l
echo ""
echo "Logs will be written to: $SCRIPT_DIR/cron.log"
echo ""
echo "To remove this cron job, run:"
echo "  crontab -e"
echo "Then delete the line containing 'pilates_bot.py'"
echo ""
echo "=== Setup Complete ==="
