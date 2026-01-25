"""
Cancellation Scanner for Padel Powers
Scans today + next N days for available slots on weekdays during configured hours.
Automatically books the first available slot found.
"""

import time
from datetime import datetime, timedelta, date
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging
import sys

from config import (
    LOCATION, HEADLESS,
    LOGIN_EMAIL, LOGIN_PASSWORD,
    LOG_LEVEL, LOG_FILE,
    SCANNER_WEEKDAYS, SCANNER_START_TIME, SCANNER_END_TIME,
    SCANNER_DAYS_AHEAD, SCANNER_DURATION_MINUTES
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


def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM string to minutes since midnight"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def get_weekday_name(weekday: int) -> str:
    """Get weekday name from number (0=Monday)"""
    names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return names[weekday]


class CancellationScanner:
    """Scans multiple days for cancelled/available slots and books the first match"""

    def __init__(self, location: str = "Smíchov"):
        self.location = location
        self.driver = None
        self.prague_tz = pytz.timezone('Europe/Prague')
        self.start_minutes = time_to_minutes(SCANNER_START_TIME)
        self.end_minutes = time_to_minutes(SCANNER_END_TIME)

    def setup_driver(self, headless: bool = False):
        """Setup Chrome with performance optimizations"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.page_load_strategy = 'eager'

        if headless:
            chrome_options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        logger.info("Chrome driver initialized")

    def get_dates_to_scan(self) -> list[date]:
        """Return list of weekday dates from today to today + SCANNER_DAYS_AHEAD"""
        today = datetime.now(self.prague_tz).date()
        dates = []

        for i in range(SCANNER_DAYS_AHEAD + 1):  # +1 to include today
            check_date = today + timedelta(days=i)
            if check_date.weekday() in SCANNER_WEEKDAYS:
                dates.append(check_date)

        return dates

    def navigate_to_date(self, target_date: date):
        """Navigate to booking page for specific date"""
        date_str = target_date.strftime('%Y-%m-%d')
        url = f"https://www.padelpowers.com/rezervace/court-booking/reservation/?location={self.location}&date={date_str}"
        self.driver.get(url)
        time.sleep(0.5)  # Brief wait for page load

    def find_available_slots(self) -> list[dict]:
        """Find all available slots in the configured time window"""
        slots_found = []

        try:
            wait = WebDriverWait(self.driver, 5)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.timeslots-container')))

            # Get all slot buttons
            slots = self.driver.find_elements(
                By.CSS_SELECTOR,
                'button.btn.text-nowrap.btn-outline-primary.btn-sm'
            )

            for slot in slots:
                # Skip disabled (booked) slots
                if slot.get_attribute('disabled') is not None:
                    continue

                try:
                    time_divs = slot.find_elements(By.TAG_NAME, 'div')
                    if not time_divs:
                        continue

                    slot_time = time_divs[0].text.strip()
                    slot_minutes = time_to_minutes(slot_time)

                    # Check if slot is within configured time window
                    if self.start_minutes <= slot_minutes < self.end_minutes:
                        price = time_divs[1].text.strip() if len(time_divs) > 1 else "N/A"
                        slots_found.append({
                            'element': slot,
                            'time': slot_time,
                            'price': price
                        })

                except (ValueError, IndexError):
                    continue

        except TimeoutException:
            logger.debug("Timeslots container not found on this page")

        return slots_found

    def scan_all_dates(self) -> dict | None:
        """Scan all dates and return first available slot with its date"""
        dates = self.get_dates_to_scan()

        logger.info(f"Scanning {len(dates)} weekdays from today to +{SCANNER_DAYS_AHEAD} days")
        logger.info(f"Time window: {SCANNER_START_TIME} - {SCANNER_END_TIME}")
        logger.info(f"Weekdays: {[get_weekday_name(d) for d in SCANNER_WEEKDAYS]}")
        logger.info("-" * 60)

        for target_date in dates:
            weekday_name = get_weekday_name(target_date.weekday())
            logger.info(f"Checking {target_date} ({weekday_name})...")

            self.navigate_to_date(target_date)
            available_slots = self.find_available_slots()

            if available_slots:
                logger.info(f"  Found {len(available_slots)} available slot(s)!")
                for slot in available_slots:
                    logger.info(f"    - {slot['time']} ({slot['price']})")

                # Return first available slot
                first_slot = available_slots[0]
                first_slot['date'] = target_date
                return first_slot
            else:
                logger.info("  No available slots in time window")

        return None

    def book_slot(self, slot_info: dict) -> bool:
        """Book the slot - reuses booking logic from main bot"""
        try:
            slot = slot_info['element']
            slot_time = slot_info['time']
            slot_date = slot_info['date']

            logger.info(f"Booking slot: {slot_date} at {slot_time}")

            # Click slot using JavaScript (faster, bypasses overlays)
            self.driver.execute_script("arguments[0].click();", slot)
            time.sleep(0.1)

            # Click duration button
            logger.info(f"Selecting {SCANNER_DURATION_MINUTES} min duration...")
            try:
                wait = WebDriverWait(self.driver, 5)
                duration_button = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//button[contains(text(), "{SCANNER_DURATION_MINUTES} min")]')
                    )
                )
                self.driver.execute_script("arguments[0].click();", duration_button)
                logger.info("Duration selected")
            except TimeoutException:
                # Fallback to searching all buttons
                buttons = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    '.ii-timeslots-container button.btn.px-4.py-2'
                )
                for btn in buttons:
                    if f"{SCANNER_DURATION_MINUTES} min" in btn.text:
                        self.driver.execute_script("arguments[0].click();", btn)
                        break

            time.sleep(0.1)

            # Login
            logger.info("Logging in...")
            if LOGIN_EMAIL and LOGIN_PASSWORD:
                try:
                    wait = WebDriverWait(self.driver, 5)
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.modal.fade.show')))

                    # Fill email
                    email_input = self.driver.find_element(
                        By.CSS_SELECTOR,
                        '.modal input[type="text"][autocomplete="on"].form-control'
                    )
                    email_input.send_keys(LOGIN_EMAIL)

                    # Fill password
                    pwd_input = self.driver.find_element(
                        By.CSS_SELECTOR,
                        '.modal input[type="password"][autocomplete="on"].form-control'
                    )
                    pwd_input.send_keys(LOGIN_PASSWORD)

                    # Click login button
                    login_btn = self.driver.find_element(
                        By.CSS_SELECTOR,
                        '.modal button[type="submit"].btn-primary'
                    )
                    self.driver.execute_script("arguments[0].click();", login_btn)

                    logger.info("Login submitted!")
                    time.sleep(1)
                    return True

                except Exception as e:
                    logger.error(f"Login error: {e}")
                    return False
            else:
                logger.warning("No credentials configured - manual login required")
                return False

        except Exception as e:
            logger.error(f"Booking error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """Main entry point - scan all dates and book first available slot"""
        try:
            logger.info("=" * 60)
            logger.info("Padel Powers Cancellation Scanner")
            logger.info("=" * 60)
            logger.info(f"Location: {self.location}")
            logger.info(f"Duration: {SCANNER_DURATION_MINUTES} minutes")
            logger.info("=" * 60)

            self.setup_driver(headless=HEADLESS)

            # Scan all dates
            slot = self.scan_all_dates()

            if slot:
                logger.info("=" * 60)
                logger.info(f"SLOT FOUND: {slot['date']} at {slot['time']} ({slot['price']})")
                logger.info("=" * 60)

                # Book the slot
                if self.book_slot(slot):
                    logger.info("=" * 60)
                    logger.info("SUCCESS! Booking initiated")
                    logger.info("Complete any remaining steps in browser (payment, etc.)")
                    logger.info("=" * 60)
                    input("Press Enter to close browser...")
                    return True
                else:
                    logger.error("Booking failed")
                    input("Press Enter to close browser...")
                    return False
            else:
                logger.info("=" * 60)
                logger.info("No available slots found in the configured time window")
                logger.info("=" * 60)
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
    """Run the cancellation scanner"""
    scanner = CancellationScanner(location=LOCATION)
    return scanner.run()


if __name__ == "__main__":
    main()
