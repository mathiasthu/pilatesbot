"""
Pilates Booking Bot - Automated session booking for Acuity Scheduling
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import yaml
import pytz
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout

from notifications import get_notifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pilates_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PilatesBookingBot:
    """Automated booking bot for Pilates sessions."""

    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the booking bot.

        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.notifier = get_notifier()
        self.timezone = pytz.timezone(self.config['timezone'])
        self.successful_bookings = []
        self.failed_bookings = []

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def get_target_dates(self) -> List[datetime]:
        """
        Calculate the target dates for booking based on configuration.

        Returns:
            List of datetime objects for the sessions to book
        """
        now = datetime.now(self.timezone)
        weeks_ahead = self.config['booking']['weeks_ahead']

        # Calculate the start of the target week
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = now + timedelta(days=days_until_monday + (weeks_ahead - 1) * 7)

        # Map day names to weekday numbers
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        target_dates = []
        for day_name in self.config['session']['days']:
            target_weekday = day_mapping[day_name]
            days_from_monday = target_weekday
            target_date = next_monday + timedelta(days=days_from_monday)
            target_dates.append(target_date)

        logger.info(f"Target booking dates: {[d.strftime('%Y-%m-%d %A') for d in target_dates]}")
        return target_dates

    async def wait_for_page_load(self, page: Page, timeout: int = 5000):
        """Wait for page to be fully loaded."""
        try:
            await page.wait_for_load_state('networkidle', timeout=timeout)
        except PlaywrightTimeout:
            # Continue even if timeout - page might be usable
            logger.warning("Page load timeout, continuing anyway")

    async def select_appointment_type(self, page: Page) -> bool:
        """
        Select the appointment type (e.g., 'Midday Flow').

        Args:
            page: Playwright page object

        Returns:
            True if successful, False otherwise
        """
        session_name = self.config['session']['name']
        logger.info(f"Looking for session type: {session_name}")

        try:
            # Wait for appointment types to load
            await page.wait_for_selector('text=' + session_name, timeout=10000)

            # Click on the session type
            await page.click(f'text={session_name}')
            logger.info(f"Selected appointment type: {session_name}")
            await self.wait_for_page_load(page)
            return True

        except Exception as e:
            logger.error(f"Failed to select appointment type: {e}")
            return False

    async def select_date_and_time(self, page: Page, target_date: datetime) -> bool:
        """
        Select a specific date and time for the session.

        Args:
            page: Playwright page object
            target_date: The date to book

        Returns:
            True if successful, False otherwise
        """
        preferred_time = self.config['session']['time']
        logger.info(f"Attempting to book {target_date.strftime('%A, %B %d')} at {preferred_time}")

        try:
            # Look for the calendar/date picker
            # This is site-specific and may need adjustment based on Acuity's UI

            # Try to find and click on the target date
            date_text = target_date.strftime('%B %d, %Y')  # e.g., "January 20, 2026"
            date_selector = f'text={date_text}'

            # Alternative: look for date in various formats
            day_num = target_date.strftime('%d').lstrip('0')  # Remove leading zero

            # Wait for calendar to be visible
            await page.wait_for_timeout(2000)

            # Try clicking on the date - Acuity typically uses a calendar widget
            # We may need to navigate to the correct month first
            date_clicked = False

            # Try multiple selectors for the date
            selectors = [
                f'[aria-label*="{target_date.strftime("%A, %B %d")}"]',
                f'button:has-text("{day_num}")',
                f'a:has-text("{day_num}")',
                f'text={day_num}'
            ]

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        await elements[0].click()
                        date_clicked = True
                        logger.info(f"Clicked date using selector: {selector}")
                        break
                except:
                    continue

            if not date_clicked:
                logger.warning("Could not click date, may already be on date selection")

            await self.wait_for_page_load(page)

            # Now look for the time slot
            time_clicked = await self.select_time_slot(page, preferred_time)

            if not time_clicked:
                # Try to find alternative times
                if self.config['booking']['allow_alternatives']:
                    logger.info("Preferred time not available, looking for alternatives")
                    alternatives = await self.find_alternative_times(page, preferred_time)

                    if alternatives and self.config['booking']['require_confirmation']:
                        # Send notification for confirmation
                        day_name = target_date.strftime('%A')
                        self.notifier.notify_alternative_needed(day_name, preferred_time, alternatives)
                        logger.info("Alternative session notification sent, skipping booking")
                        return False
                    elif alternatives:
                        # Book the first alternative
                        await self.select_time_slot(page, alternatives[0]['time'])
                        logger.info(f"Booked alternative time: {alternatives[0]['time']}")
                        return True

                return False

            return True

        except Exception as e:
            logger.error(f"Failed to select date and time: {e}")
            return False

    async def select_time_slot(self, page: Page, time_str: str) -> bool:
        """
        Click on a specific time slot.

        Args:
            page: Playwright page object
            time_str: Time string (e.g., "3:40 PM")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Look for the time slot button/link
            # Acuity typically shows times as clickable elements
            time_selectors = [
                f'button:has-text("{time_str}")',
                f'a:has-text("{time_str}")',
                f'[aria-label*="{time_str}"]',
                f'text={time_str}'
            ]

            for selector in time_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        # Check if the slot is available (not disabled or fully booked)
                        is_disabled = await element.get_attribute('disabled')
                        class_name = await element.get_attribute('class') or ''

                        if not is_disabled and 'disabled' not in class_name.lower() and 'full' not in class_name.lower():
                            await element.click()
                            logger.info(f"Selected time slot: {time_str}")
                            await self.wait_for_page_load(page)
                            return True
                        else:
                            logger.warning(f"Time slot {time_str} is not available")
                            return False
                except:
                    continue

            logger.warning(f"Time slot {time_str} not found")
            return False

        except Exception as e:
            logger.error(f"Error selecting time slot: {e}")
            return False

    async def find_alternative_times(self, page: Page, preferred_time: str) -> List[Dict[str, str]]:
        """
        Find alternative time slots if the preferred time is not available.

        Args:
            page: Playwright page object
            preferred_time: The preferred time that wasn't available

        Returns:
            List of alternative time slots
        """
        alternatives = []

        try:
            # Look for all available time slots on the page
            time_elements = await page.query_selector_all('button[class*="time"], a[class*="time"]')

            for element in time_elements:
                try:
                    text = await element.inner_text()
                    is_disabled = await element.get_attribute('disabled')
                    class_name = await element.get_attribute('class') or ''

                    # Check if this is an available time slot
                    if not is_disabled and 'disabled' not in class_name.lower() and 'full' not in class_name.lower():
                        # Extract time from text (e.g., "3:40 PM")
                        if 'AM' in text or 'PM' in text:
                            alternatives.append({
                                'time': text.strip(),
                                'element': element
                            })
                except:
                    continue

            logger.info(f"Found {len(alternatives)} alternative time slots")
            return alternatives[:5]  # Return up to 5 alternatives

        except Exception as e:
            logger.error(f"Error finding alternative times: {e}")
            return []

    async def fill_booking_form(self, page: Page) -> bool:
        """
        Fill out the booking form with user information.

        Args:
            page: Playwright page object

        Returns:
            True if successful, False otherwise
        """
        user_info = self.config['user_info']
        logger.info("Filling out booking form")

        try:
            # Wait for the form to be visible
            await page.wait_for_timeout(2000)

            # Fill in first name
            first_name_selectors = [
                'input[name*="firstName"]',
                'input[name*="first"]',
                'input[id*="firstName"]',
                'input[placeholder*="First"]'
            ]
            await self.fill_field(page, first_name_selectors, user_info['first_name'], "First Name")

            # Fill in last name
            last_name_selectors = [
                'input[name*="lastName"]',
                'input[name*="last"]',
                'input[id*="lastName"]',
                'input[placeholder*="Last"]'
            ]
            await self.fill_field(page, last_name_selectors, user_info['last_name'], "Last Name")

            # Fill in phone
            phone_selectors = [
                'input[name*="phone"]',
                'input[type="tel"]',
                'input[id*="phone"]',
                'input[placeholder*="Phone"]'
            ]
            await self.fill_field(page, phone_selectors, user_info['phone'], "Phone")

            # Fill in email
            email_selectors = [
                'input[name*="email"]',
                'input[type="email"]',
                'input[id*="email"]',
                'input[placeholder*="Email"]'
            ]
            await self.fill_field(page, email_selectors, user_info['email'], "Email")

            logger.info("Booking form filled successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to fill booking form: {e}")
            return False

    async def fill_field(self, page: Page, selectors: List[str], value: str, field_name: str):
        """
        Try multiple selectors to fill a form field.

        Args:
            page: Playwright page object
            selectors: List of CSS selectors to try
            value: Value to fill in
            field_name: Name of the field (for logging)
        """
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.fill(value)
                    logger.info(f"Filled {field_name}: {value}")
                    return
            except:
                continue

        logger.warning(f"Could not find field for {field_name}")

    async def submit_booking(self, page: Page) -> bool:
        """
        Submit the booking form.

        Args:
            page: Playwright page object

        Returns:
            True if successful, False otherwise
        """
        logger.info("Submitting booking")

        try:
            # Look for the submit button
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Schedule")',
                'button:has-text("Book")',
                'button:has-text("Confirm")',
                'input[type="submit"]',
                'button:has-text("Submit")'
            ]

            for selector in submit_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        logger.info("Clicked submit button")

                        # Wait for confirmation page
                        await page.wait_for_timeout(3000)

                        # Check for success indicators
                        page_content = await page.content()
                        success_indicators = [
                            'confirmation',
                            'confirmed',
                            'successfully',
                            'thank you',
                            'booked'
                        ]

                        if any(indicator in page_content.lower() for indicator in success_indicators):
                            logger.info("Booking confirmed!")
                            return True
                        else:
                            # Take screenshot for debugging
                            await page.screenshot(path=f'booking_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
                            return True  # Assume success if no error shown

                except:
                    continue

            logger.warning("Could not find submit button")
            return False

        except Exception as e:
            logger.error(f"Failed to submit booking: {e}")
            return False

    async def book_session(self, page: Page, target_date: datetime) -> bool:
        """
        Book a single session.

        Args:
            page: Playwright page object
            target_date: The date to book

        Returns:
            True if successful, False otherwise
        """
        try:
            # Navigate to booking page
            booking_url = self.config['booking_url']
            logger.info(f"Navigating to {booking_url}")
            await page.goto(booking_url)
            await self.wait_for_page_load(page)

            # Select appointment type
            if not await self.select_appointment_type(page):
                return False

            # Select date and time
            if not await self.select_date_and_time(page, target_date):
                return False

            # Fill booking form
            if not await self.fill_booking_form(page):
                return False

            # Submit booking
            if not await self.submit_booking(page):
                return False

            # Record successful booking
            booking_info = {
                'day': target_date.strftime('%A'),
                'date': target_date.strftime('%Y-%m-%d'),
                'time': self.config['session']['time']
            }
            self.successful_bookings.append(booking_info)
            logger.info(f"Successfully booked: {booking_info}")

            return True

        except Exception as e:
            logger.error(f"Error booking session for {target_date.strftime('%A')}: {e}")
            self.failed_bookings.append({
                'day': target_date.strftime('%A'),
                'date': target_date.strftime('%Y-%m-%d'),
                'error': str(e)
            })
            return False

    async def run(self):
        """Main bot execution."""
        logger.info("=== Pilates Booking Bot Started ===")

        try:
            # Get target dates
            target_dates = self.get_target_dates()

            # Start browser
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config['browser']['headless']
                )

                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                page = await context.new_page()
                page.set_default_timeout(self.config['browser']['timeout'])

                # Book each session
                for target_date in target_dates:
                    logger.info(f"\n--- Booking session for {target_date.strftime('%A, %B %d')} ---")
                    await self.book_session(page, target_date)

                    # Wait between bookings
                    await page.wait_for_timeout(2000)

                await browser.close()

            # Send notifications
            if self.successful_bookings:
                self.notifier.notify_booking_success(self.successful_bookings)
                logger.info(f"Successfully booked {len(self.successful_bookings)} sessions")

            if self.failed_bookings:
                error_msg = "\n".join([f"{b['day']}: {b['error']}" for b in self.failed_bookings])
                self.notifier.notify_error(error_msg)
                logger.warning(f"Failed to book {len(self.failed_bookings)} sessions")

            logger.info("=== Pilates Booking Bot Finished ===")

        except Exception as e:
            logger.error(f"Bot execution failed: {e}")
            self.notifier.notify_error(str(e))
            raise


async def main():
    """Main entry point."""
    bot = PilatesBookingBot()
    await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
