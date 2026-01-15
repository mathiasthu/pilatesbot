"""
Telegram notification handler for the Pilates booking bot.
"""

import os
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handle Telegram notifications using python-telegram-bot."""

    def __init__(self):
        self.enabled = os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        self.bot = None
        if self.enabled:
            try:
                from telegram import Bot
                if self.bot_token and self.chat_id:
                    self.bot = Bot(token=self.bot_token)
                    logger.info("Telegram notifications enabled")
                else:
                    logger.warning("Telegram notifications enabled but credentials missing")
                    self.enabled = False
            except ImportError:
                logger.warning("python-telegram-bot library not installed. Install with: pip install python-telegram-bot")
                self.enabled = False
        else:
            logger.info("Telegram notifications disabled")

    async def send_message_async(self, message: str) -> bool:
        """
        Send a Telegram message asynchronously.

        Args:
            message: The message to send

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled or not self.bot:
            logger.info(f"[NOTIFICATION SKIPPED] {message}")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Telegram message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_message(self, message: str) -> bool:
        """
        Send a Telegram message (synchronous wrapper).

        Args:
            message: The message to send

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled or not self.bot:
            logger.info(f"[NOTIFICATION SKIPPED] {message}")
            return False

        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.send_message_async(message))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def notify_alternative_needed(self, day: str, preferred_time: str, alternatives: list) -> bool:
        """
        Notify about alternative session options.

        Args:
            day: The day that needs an alternative
            preferred_time: The preferred time that wasn't available
            alternatives: List of alternative sessions

        Returns:
            True if notification sent successfully
        """
        alt_list = "\n".join([f"• {alt['time']}" for alt in alternatives])
        message = f"""🧘‍♀️ <b>Pilates Booking Alert</b>

<b>Preferred session not available:</b>
{day} at {preferred_time}

<b>Available alternatives:</b>
{alt_list}

Please confirm which session to book or if none are suitable."""

        return self.send_message(message)

    def notify_booking_success(self, bookings: list) -> bool:
        """
        Notify about successful bookings.

        Args:
            bookings: List of successfully booked sessions

        Returns:
            True if notification sent successfully
        """
        booking_list = "\n".join([f"✅ {b['day']} at {b['time']}" for b in bookings])
        message = f"""✅ <b>Pilates Sessions Booked Successfully!</b>

<b>Your sessions for next week:</b>
{booking_list}

See you on the mat! 🧘‍♀️"""

        return self.send_message(message)

    def notify_error(self, error_msg: str) -> bool:
        """
        Notify about booking errors.

        Args:
            error_msg: Error message to send

        Returns:
            True if notification sent successfully
        """
        message = f"""❌ <b>Pilates Booking Error</b>

There was an issue booking your sessions:
<code>{error_msg}</code>

Please check the logs or book manually."""

        return self.send_message(message)


def get_notifier() -> TelegramNotifier:
    """Get a Telegram notifier instance."""
    return TelegramNotifier()
