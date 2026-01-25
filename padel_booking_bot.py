"""
SPEED-OPTIMIZED Padel Powers Automatic Booking Bot
Optimized for competitive booking at midnight
Every millisecond counts!
"""

import time
from datetime import datetime, timedelta
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import sys

# Import configuration
from config import (
    LOCATION, TARGET_START_HOUR, TARGET_END_HOUR, DURATION_MINUTES,
    WAIT_FOR_MIDNIGHT, DAYS_IN_ADVANCE, HEADLESS,
    LOGIN_EMAIL, LOGIN_PASSWORD,
    MAX_REFRESH_ATTEMPTS, MIDNIGHT_MONITOR_MINUTES,
    LOG_LEVEL, LOG_FILE
)

# Setup logging
handlers = [logging.StreamHandler(sys.stdout)]
if LOG_FILE:
    handlers.append(logging.FileHandler(LOG_FILE))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


class PadelBookingBotFast:
    """Speed-optimized bot for competitive booking"""

    def __init__(self, location="Smíchov"):
        self.location = location
        self.driver = None
        self.prague_tz = pytz.timezone('Europe/Prague')

    def setup_driver(self, headless=False):
        """Setup Chrome with performance optimizations"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        # Performance optimizations
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources

        if headless:
            chrome_options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)  # Set timeout for page loads
        logger.info("Chrome driver initialized with performance optimizations")

    def get_target_date(self, from_date=None):
        """Calculate the target booking date

        Args:
            from_date: Optional datetime to calculate from (used for midnight booking)
                      If None, uses current time
        """
        if from_date is None:
            from_date = datetime.now(self.prague_tz)

        target_date = from_date + timedelta(days=DAYS_IN_ADVANCE)
        return target_date.strftime('%Y-%m-%d')

    def wait_until_midnight(self):
        """Wait until exactly midnight Prague time - PRE-LOAD PAGE"""
        now = datetime.now(self.prague_tz)

        # Calculate next midnight
        tomorrow = now + timedelta(days=1)
        midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

        seconds_until_midnight = (midnight - now).total_seconds()

        logger.info(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Next midnight: {midnight.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Time until midnight: {seconds_until_midnight:.1f} seconds")

        # PRE-LOAD THE PAGE 5 seconds before midnight
        if seconds_until_midnight > 10:
            wait_time = seconds_until_midnight - 5
            logger.info(f"Waiting {wait_time:.1f} seconds before pre-loading page...")
            time.sleep(wait_time)

            # Pre-load the page - calculate from MIDNIGHT date, not current time!
            logger.info("PRE-LOADING page 5 seconds before midnight...")
            self.setup_driver(headless=HEADLESS)
            # IMPORTANT: Calculate target date from midnight (tomorrow), not current time
            target_date = self.get_target_date(from_date=midnight)
            logger.info(f"Booking date: {target_date} (Midnight {midnight.strftime('%Y-%m-%d')} + {DAYS_IN_ADVANCE} days)")
            url = f"https://www.padelpowers.com/rezervace/court-booking/reservation/?location={self.location}&date={target_date}"
            self.driver.get(url)

            # Wait for page to load with better error handling
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".timeslots-container"))
                )
                logger.info("Page pre-loaded!")
            except TimeoutException:
                logger.warning("Timeslots container not found during pre-load, but continuing...")
                # Take a screenshot for debugging
                try:
                    self.driver.save_screenshot("/home/jakub-stejskal/projects/personal/padel/captures/preload_error.png")
                    logger.info("Screenshot saved to captures/preload_error.png")
                except Exception as e:
                    logger.error(f"Could not save screenshot: {e}")

            logger.info("Ready to refresh at midnight...")

            # Wait remaining time
            remaining = (midnight - datetime.now(self.prague_tz)).total_seconds()
            logger.info(f"Waiting final {remaining:.1f} seconds until midnight...")
            time.sleep(max(0, remaining))
        else:
            time.sleep(max(0, seconds_until_midnight))

        logger.info("IT'S MIDNIGHT! REFRESHING PAGE...")
        # Refresh to get new slots
        try:
            self.driver.refresh()
            logger.info("Page refreshed successfully")
        except Exception as e:
            logger.error(f"Error during refresh: {e}")
            # Try to reload the page if refresh fails
            try:
                logger.info("Attempting to reload page instead...")
                target_date = self.get_target_date(from_date=midnight)
                url = f"https://www.padelpowers.com/rezervace/court-booking/reservation/?location={self.location}&date={target_date}"
                self.driver.get(url)
                logger.info("Page reloaded successfully")
            except Exception as e2:
                logger.error(f"Error reloading page: {e2}")
                raise

    def find_first_available_slot(self, start_hour=18, end_hour=21):
        """Find FIRST available slot in target range - OPTIMIZED FOR SPEED"""
        logger.info(f"Finding first slot between {start_hour}:00-{end_hour}:00...")

        # Minimal wait - slots should be there immediately after refresh
        wait = WebDriverWait(self.driver, 2)

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.timeslots-container')))

            # Get all slots at once (faster than iterating)
            slots = self.driver.find_elements(By.CSS_SELECTOR, 'button.btn.text-nowrap.btn-outline-primary.btn-sm')

            for slot in slots:
                # Skip disabled slots immediately
                if slot.get_attribute('disabled') is not None:
                    continue

                try:
                    # Extract time (first div)
                    time_divs = slot.find_elements(By.TAG_NAME, 'div')
                    if not time_divs:
                        continue

                    slot_time = time_divs[0].text.strip()
                    hour = int(slot_time.split(':')[0])

                    if start_hour <= hour < end_hour:
                        price = time_divs[1].text.strip() if len(time_divs) > 1 else "N/A"
                        logger.info(f"FOUND: {slot_time} - {price}")
                        return {'element': slot, 'time': slot_time, 'price': price}

                except (ValueError, IndexError):
                    continue

            logger.warning("No slots found in target range!")
            return None

        except TimeoutException:
            logger.error("Timeslots container not found!")
            return None

    def book_slot_fast(self, slot_info):
        """SPEED-OPTIMIZED booking flow"""
        try:
            slot = slot_info['element']
            slot_time = slot_info['time']

            logger.info(f"CLICKING: {slot_time}")

            # Use JavaScript click immediately - faster & bypasses overlays
            # No need to check for cookie banner - JS click works regardless!
            self.driver.execute_script("arguments[0].click();", slot)

            # Wait minimal time for courts to appear
            time.sleep(0.1)

            # STEP 1: Click duration button FAST with JavaScript
            logger.info("Clicking 60 min...")
            try:
                wait = WebDriverWait(self.driver, 2)
                # Wait until element exists
                duration_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, f'//button[contains(text(), "{DURATION_MINUTES} min")]'))
                )
                # JavaScript click - faster & bypasses any overlays
                self.driver.execute_script("arguments[0].click();", duration_button)
                logger.info("✓ Duration clicked")
            except TimeoutException:
                # Fallback to searching
                buttons = self.driver.find_elements(By.CSS_SELECTOR, '.ii-timeslots-container button.btn.px-4.py-2')
                for btn in buttons:
                    if f"{DURATION_MINUTES} min" in btn.text:
                        self.driver.execute_script("arguments[0].click();", btn)
                        break

            # Wait minimal time for modal
            time.sleep(0.1)

            # STEP 2: Login FAST
            logger.info("Logging in...")
            if LOGIN_EMAIL and LOGIN_PASSWORD:
                try:
                    wait = WebDriverWait(self.driver, 2)

                    # Wait for modal
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.modal.fade.show')))

                    # Find and fill email - no waits between actions
                    email = self.driver.find_element(By.CSS_SELECTOR, '.modal input[type="text"][autocomplete="on"].form-control')
                    email.send_keys(LOGIN_EMAIL)

                    # Password
                    pwd = self.driver.find_element(By.CSS_SELECTOR, '.modal input[type="password"][autocomplete="on"].form-control')
                    pwd.send_keys(LOGIN_PASSWORD)

                    # Click login button
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, '.modal button[type="submit"].btn-primary')
                    self.driver.execute_script("arguments[0].click();", login_btn)

                    logger.info("✓ Login submitted!")
                    time.sleep(1)
                    return True

                except Exception as e:
                    logger.error(f"Login error: {e}")
                    return False
            else:
                logger.warning("No credentials - manual login required")
                return False

        except Exception as e:
            logger.error(f"Booking error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_fast(self, wait_for_midnight=True, headless=False, start_hour=18, end_hour=21, max_refresh_attempts=30, monitor_minutes=10):
        """OPTIMIZED execution flow with auto-refresh and extended monitoring"""
        try:
            if wait_for_midnight:
                # This pre-loads the page!
                self.wait_until_midnight()
            else:
                logger.info("Starting immediately (test mode)")
                self.setup_driver(headless=headless)
                target_date = self.get_target_date()
                url = f"https://www.padelpowers.com/rezervace/court-booking/reservation/?location={self.location}&date={target_date}"
                self.driver.get(url)
                time.sleep(0.5)

            # PHASE 1: Fast polling (~30 seconds at 0.8s intervals)
            slot = None
            logger.info("=" * 60)
            logger.info("PHASE 1: Fast polling for immediate slot availability")
            logger.info("=" * 60)

            for attempt in range(1, max_refresh_attempts + 1):
                logger.info(f"Fast attempt {attempt}/{max_refresh_attempts}: Checking for slots...")

                # Find available slot
                slot = self.find_first_available_slot(start_hour=start_hour, end_hour=end_hour)

                if slot:
                    logger.info(f"✓ SLOT FOUND on fast attempt {attempt}!")
                    break

                # No slot found - refresh and try again
                if attempt < max_refresh_attempts:
                    logger.warning(f"No slots found. Refreshing... ({attempt}/{max_refresh_attempts})")
                    time.sleep(0.8)  # Wait 0.8 seconds between refreshes
                    self.driver.refresh()

            # PHASE 2: Extended monitoring for pre-booked slots that expire
            if not slot and wait_for_midnight and monitor_minutes > 0:
                logger.info("=" * 60)
                logger.info(f"PHASE 2: Extended monitoring for {monitor_minutes} minutes")
                logger.info("(Pre-booked slots expire if not confirmed within 5 minutes)")
                logger.info("=" * 60)

                start_time = time.time()
                end_time = start_time + (monitor_minutes * 60)
                slow_attempt = 0

                while time.time() < end_time:
                    slow_attempt += 1
                    elapsed = time.time() - start_time
                    remaining = (end_time - time.time()) / 60

                    logger.info(f"Extended check {slow_attempt} ({elapsed:.0f}s elapsed, {remaining:.1f} min remaining)...")

                    self.driver.refresh()
                    time.sleep(1)  # Wait for page to load

                    slot = self.find_first_available_slot(start_hour=start_hour, end_hour=end_hour)

                    if slot:
                        logger.info(f"✓ SLOT FOUND after {elapsed:.0f} seconds of extended monitoring!")
                        break

                    # Wait 10 seconds before next check
                    logger.info("No slots yet. Waiting 10 seconds before next check...")
                    time.sleep(10)

                if not slot:
                    logger.error(f"No slots found after {monitor_minutes} minutes of monitoring!")

            if not slot:
                logger.error("Giving up - no slots found!")
                input("Press Enter to close...")
                return False

            # Book it!
            if self.book_slot_fast(slot):
                logger.info("=" * 60)
                logger.info("SUCCESS! Slot booked (or login completed)")
                logger.info("Complete any remaining steps in browser")
                logger.info("=" * 60)
                input("Press Enter to close browser...")
                return True
            else:
                logger.error("Booking failed")
                input("Press Enter to close...")
                return False

        except KeyboardInterrupt:
            logger.info("\nInterrupted by user")
            return False
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Run speed-optimized bot"""
    logger.info("=" * 60)
    logger.info("SPEED-OPTIMIZED Padel Booking Bot")
    logger.info("=" * 60)
    logger.info(f"Location: {LOCATION}")
    logger.info(f"Target time: {TARGET_START_HOUR}:00 - {TARGET_END_HOUR}:00")
    logger.info(f"Duration: {DURATION_MINUTES} minutes")
    logger.info(f"Days in advance: {DAYS_IN_ADVANCE}")
    logger.info(f"Wait for midnight: {WAIT_FOR_MIDNIGHT}")
    logger.info(f"Auto-refresh: {MAX_REFRESH_ATTEMPTS} attempts")
    logger.info(f"Extended monitoring: {MIDNIGHT_MONITOR_MINUTES} minutes")
    logger.info("=" * 60)

    bot = PadelBookingBotFast(location=LOCATION)
    success = bot.run_fast(
        wait_for_midnight=WAIT_FOR_MIDNIGHT,
        headless=HEADLESS,
        start_hour=TARGET_START_HOUR,
        end_hour=TARGET_END_HOUR,
        max_refresh_attempts=MAX_REFRESH_ATTEMPTS,
        monitor_minutes=MIDNIGHT_MONITOR_MINUTES
    )

    return success


if __name__ == "__main__":
    main()
