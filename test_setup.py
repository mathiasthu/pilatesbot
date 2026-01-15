"""
Test script to verify the bot setup without making actual bookings.
"""

import sys
import yaml
from datetime import datetime
import pytz

def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✓ Configuration loaded successfully")
        print(f"  - Booking URL: {config['booking_url']}")
        print(f"  - User: {config['user_info']['first_name']} {config['user_info']['last_name']}")
        print(f"  - Session: {config['session']['name']}")
        print(f"  - Days: {', '.join(config['session']['days'])}")
        print(f"  - Time: {config['session']['time']}")
        return True
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def test_timezone():
    """Test timezone configuration."""
    print("\nTesting timezone...")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        tz = pytz.timezone(config['timezone'])
        now = datetime.now(tz)
        print(f"✓ Timezone configured: {config['timezone']}")
        print(f"  - Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return True
    except Exception as e:
        print(f"✗ Failed to configure timezone: {e}")
        return False

def test_dependencies():
    """Test required Python dependencies."""
    print("\nTesting dependencies...")
    all_ok = True

    # Test Playwright
    try:
        from playwright.async_api import async_playwright
        print("✓ Playwright installed")
    except ImportError:
        print("✗ Playwright not installed. Run: pip install playwright && playwright install chromium")
        all_ok = False

    # Test PyYAML
    try:
        import yaml
        print("✓ PyYAML installed")
    except ImportError:
        print("✗ PyYAML not installed. Run: pip install pyyaml")
        all_ok = False

    # Test pytz
    try:
        import pytz
        print("✓ pytz installed")
    except ImportError:
        print("✗ pytz not installed. Run: pip install pytz")
        all_ok = False

    # Test dotenv
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv not installed. Run: pip install python-dotenv")
        all_ok = False

    return all_ok

def test_env():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()

        notifications_enabled = os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'
        if notifications_enabled:
            print("✓ WhatsApp notifications enabled")
            if os.getenv('TWILIO_ACCOUNT_SID'):
                print("  - Twilio Account SID: configured")
            else:
                print("  - Twilio Account SID: NOT configured")
            if os.getenv('TWILIO_AUTH_TOKEN'):
                print("  - Twilio Auth Token: configured")
            else:
                print("  - Twilio Auth Token: NOT configured")
        else:
            print("⚠ WhatsApp notifications disabled (set ENABLE_NOTIFICATIONS=true in .env to enable)")
        return True
    except Exception as e:
        print(f"⚠ Environment file not found or invalid: {e}")
        print("  This is OK - notifications will be disabled")
        return True

def test_target_dates():
    """Test target date calculation."""
    print("\nTesting target date calculation...")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        tz = pytz.timezone(config['timezone'])
        now = datetime.now(tz)
        weeks_ahead = config['booking']['weeks_ahead']

        from datetime import timedelta
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = now + timedelta(days=days_until_monday + (weeks_ahead - 1) * 7)

        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        print(f"✓ Target dates (booking {weeks_ahead} week(s) ahead):")
        for day_name in config['session']['days']:
            target_weekday = day_mapping[day_name]
            target_date = next_monday + timedelta(days=target_weekday)
            print(f"  - {day_name}: {target_date.strftime('%Y-%m-%d')} at {config['session']['time']}")

        return True
    except Exception as e:
        print(f"✗ Failed to calculate target dates: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Pilates Booking Bot - Setup Test")
    print("=" * 60)

    results = []
    results.append(("Configuration", test_config()))
    results.append(("Timezone", test_timezone()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Environment", test_env()))
    results.append(("Target Dates", test_target_dates()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All tests passed! The bot is ready to run.")
        print("\nNext steps:")
        print("1. Run manually to test: python3 pilates_bot.py")
        print("2. Set up automated scheduling: ./setup_cron.sh")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above before running the bot.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
