"""
WhatsApp notification handler for the Pilates booking bot.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    """Handle WhatsApp notifications using Twilio API."""

    def __init__(self):
        self.enabled = os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_WHATSAPP_FROM')
        self.to_number = os.getenv('WHATSAPP_TO')

        self.client = None
        if self.enabled:
            try:
                from twilio.rest import Client
                if all([self.account_sid, self.auth_token, self.from_number, self.to_number]):
                    self.client = Client(self.account_sid, self.auth_token)
                    logger.info("WhatsApp notifications enabled")
                else:
                    logger.warning("WhatsApp notifications enabled but credentials missing")
                    self.enabled = False
            except ImportError:
                logger.warning("Twilio library not installed. Install with: pip install twilio")
                self.enabled = False
        else:
            logger.info("WhatsApp notifications disabled")

    def send_message(self, message: str) -> bool:
        """
        Send a WhatsApp message.

        Args:
            message: The message to send

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.info(f"[NOTIFICATION SKIPPED] {message}")
            return False

        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            logger.info(f"WhatsApp message sent: {msg.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
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
        alt_list = "\n".join([f"- {alt['time']}" for alt in alternatives])
        message = f"""🧘‍♀️ Pilates Booking Alert

Preferred session not available:
{day} at {preferred_time}

Available alternatives:
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
        booking_list = "\n".join([f"✓ {b['day']} at {b['time']}" for b in bookings])
        message = f"""✅ Pilates Sessions Booked Successfully!

Your sessions for next week:
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
        message = f"""❌ Pilates Booking Error

There was an issue booking your sessions:
{error_msg}

Please check the logs or book manually."""

        return self.send_message(message)


def get_notifier() -> WhatsAppNotifier:
    """Get a WhatsApp notifier instance."""
    return WhatsAppNotifier()
