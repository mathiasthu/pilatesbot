"""
Test script to verify Telegram notifications are working.
"""

import sys
from notifications import get_notifier

def main():
    print("=" * 60)
    print("Telegram Notification Test")
    print("=" * 60)
    print()

    print("Initializing Telegram notifier...")
    notifier = get_notifier()

    if not notifier.enabled:
        print()
        print("❌ FAILED: Telegram notifications are not enabled!")
        print()
        print("To enable:")
        print("1. Create .env file from .env.example")
        print("2. Add your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        print("3. Set ENABLE_NOTIFICATIONS=true")
        print()
        print("See DEPLOYMENT_GUIDE.md for detailed instructions.")
        return 1

    print("✓ Telegram notifier initialized")
    print(f"  - Bot token: {notifier.bot_token[:10]}...")
    print(f"  - Chat ID: {notifier.chat_id}")
    print()

    print("Sending test message...")
    success = notifier.send_message(
        "🎉 <b>Telegram Bot Test Successful!</b>\n\n"
        "Your Pilates booking bot is ready to send notifications! 🧘‍♀️"
    )

    print()
    if success:
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print()
        print("Check your Telegram app - you should have received a message!")
        print()
        print("Next steps:")
        print("1. Run: python3 test_setup.py")
        print("2. Run: python3 pilates_bot.py (to test full booking)")
        print("3. Setup cron: ./setup_cron.sh")
        print()
        return 0
    else:
        print("=" * 60)
        print("❌ FAILED!")
        print("=" * 60)
        print()
        print("Possible issues:")
        print("1. Wrong bot token or chat ID in .env")
        print("2. Bot not started (send /start to your bot first)")
        print("3. Internet connection issue")
        print("4. python-telegram-bot not installed")
        print()
        print("Check pilates_bot.log for detailed error messages")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
