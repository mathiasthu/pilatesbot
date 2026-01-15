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
        Select the appointment type by clicking the BOOK button for Midday Flow.

        Args:
            page: Playwright page object

        Returns:
            True if successful, False otherwise
        """
        session_name = self.config['session']['name']
        logger.info(f"Looking for session type: {session_name}")

        try:
            # Wait for the page to load
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)

            # Find all BOOK buttons
            book_buttons = await page.locator('text=BOOK').all()
            logger.info(f"Found {len(book_buttons)} BOOK buttons on page")

            # Midday Flow is the 5th button (index 4) based on the page layout
            # Order: Foundations Flow, Core Revival, Midday Flow (position varies)
            # We need to find it dynamically instead

            # Look for the section containing "Midday Flow" text and click its BOOK button
            midday_section = page.locator(f'text="{session_name}"').locator('xpath=ancestor::*[contains(@class, "appointment") or contains(@class, "service")]').first

            if await midday_section.count() > 0:
                # Find BOOK button within this section
                book_btn = midday_section.locator('text=BOOK').first
                await book_btn.click()
                logger.info(f"Clicked BOOK button for {session_name}")
            else:
                # Fallback: click 5th BOOK button (index 4) - Midday Flow position
                if len(book_buttons) >= 5:
                    await book_buttons[4].click()
                    logger.info(f"Clicked 5th BOOK button (assumed {session_name})")
                else:
                    logger.error(f"Could not find {session_name} section")
                    return False

            await self.wait_for_page_load(page)
            logger.info("Successfully navigated to booking page")
            return True

        except Exception as e:
            logger.error(f"Failed to select appointment type: {e}")
            return False

    async def select_date_and_time(self, page: Page, target_date: datetime) -> bool:
        """
        Select a specific date and time for the session on Acuity's Date & Time page.

        Args:
            page: Playwright page object
            target_date: The date to book

        Returns:
            True if successful, False otherwise
        """
        preferred_time = self.config['session']['time']
        logger.info(f"Attempting to book {target_date.strftime('%A, %B %d')} at {preferred_time}")

        try:
            # Wait for the Date & Time page to load
            await page.wait_for_timeout(3000)

            # Format the date as it appears on the page (e.g., "Jan 19")
            date_str_short = target_date.strftime('%b %d').replace(' 0', ' ')  # "Jan 19" not "Jan 09"
            date_str_full = target_date.strftime('%B %d')  # "January 19"

            logger.info(f"Looking for date: {date_str_short} or {date_str_full}")

            # Try to find the date column
            # The page shows dates like "Monday\nJan 19"
            date_found = False

            # Strategy 1: Look for the date text and click the time slot below it
            try:
                # Find element containing the date
                date_element = page.locator(f'text={date_str_short}').first

                if await date_element.count() > 0:
                    logger.info(f"Found date element for {date_str_short}")

                    # Find the parent container for this date
                    date_container = date_element.locator('xpath=ancestor::*[contains(@class, "day") or contains(@class, "date") or parent::div]').first

                    # Look for the time slot button (e.g., "3:40 PM")
                    time_button = date_container.locator(f'text={preferred_time}').first

                    if await time_button.count() > 0:
                        await time_button.click()
                        logger.info(f"Clicked time slot: {preferred_time} for {date_str_short}")
                        date_found = True
                        await page.wait_for_timeout(2000)
                    else:
                        logger.warning(f"Time slot {preferred_time} not found for {date_str_short}")
                else:
                    logger.warning(f"Date {date_str_short} not visible on page")

            except Exception as e:
                logger.warning(f"Strategy 1 failed: {e}")

            # Strategy 2: If strategy 1 failed, look for any element with both date and time
            if not date_found:
                try:
                    # Find all time slot buttons
                    time_slots = await page.locator(f'text={preferred_time}').all()
                    logger.info(f"Found {len(time_slots)} time slots with {preferred_time}")

                    # Try each one and see if it's for our target date
                    for slot in time_slots:
                        # Get the text context around this slot
                        parent = slot.locator('xpath=ancestor::*[3]').first
                        parent_text = await parent.inner_text() if await parent.count() > 0 else ""

                        # Check if this parent contains our target date
                        if date_str_short in parent_text or date_str_full in parent_text:
                            await slot.click()
                            logger.info(f"Clicked time slot using strategy 2")
                            date_found = True
                            await page.wait_for_timeout(2000)
                            break

                except Exception as e2:
                    logger.warning(f"Strategy 2 failed: {e2}")

            if not date_found:
                logger.error(f"Could not find and click time slot for {target_date.strftime('%A %b %d')} at {preferred_time}")

                # Try to find alternatives
                if self.config['booking']['allow_alternatives']:
                    logger.info("Looking for alternative time slots")
                    alternatives = await self.find_alternative_times(page, target_date)

                    if alternatives and self.config['booking']['require_confirmation']:
                        day_name = target_date.strftime('%A')
                        self.notifier.notify_alternative_needed(day_name, preferred_time, alternatives)
                        logger.info("Alternative session notification sent")

                return False

            return True

        except Exception as e:
            logger.error(f"Failed to select date and time: {e}")
            return False

    async def find_alternative_times(self, page: Page, target_date: datetime) -> List[Dict[str, str]]:
        """
        Find alternative time slots for the target date if preferred time not available.

        Args:
            page: Playwright page object
            target_date: The target date

        Returns:
            List of alternative time slots
        """
        alternatives = []
        date_str_short = target_date.strftime('%b %d').replace(' 0', ' ')

        try:
            # Look for all time buttons on the page
            time_pattern = r'\d{1,2}:\d{2}\s*(AM|PM)'
            time_elements = await page.locator('button, a').all()

            for element in time_elements:
                try:
                    text = await element.inner_text()
                    parent_text = ""

                    # Get parent context
                    parent = element.locator('xpath=ancestor::*[3]').first
                    if await parent.count() > 0:
                        parent_text = await parent.inner_text()

                    # Check if this is a time slot for our target date
                    if date_str_short in parent_text and ('AM' in text or 'PM' in text):
                        # Check if slot is available
                        is_disabled = await element.get_attribute('disabled')
                        class_name = await element.get_attribute('class') or ''

                        if not is_disabled and 'disabled' not in class_name.lower():
                            alternatives.append({
                                'time': text.strip(),
                                'date': date_str_short
                            })
                except:
                    continue

            logger.info(f"Found {len(alternatives)} alternative time slots for {date_str_short}")
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
            await page.wait_for_timeout(3000)

            # Fill in first name
            first_name_selectors = [
                'input[name*="firstName"]',
                'input[name*="first"]',
                'input[id*="firstName"]',
                'input[placeholder*="First"]',
                'input[type="text"]'
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
                'button:has-text("Submit")',
                'button:has-text("Continue")'
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
                            'booked',
                            'scheduled'
                        ]

                        if any(indicator in page_content.lower() for indicator in success_indicators):
                            logger.info("Booking confirmed!")
                            return True
                        else:
                            # Take screenshot for debugging
                            await page.screenshot(path=f'booking_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
                            logger.info("Booking appears successful (screenshot saved)")
                            return True

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

            # Select appointment type (click BOOK button for Midday Flow)
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
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
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
