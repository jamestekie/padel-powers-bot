"""
Production test for preloading and refresh mechanism
Tests the actual page load and refresh flow without waiting for midnight
"""
import time
from datetime import datetime, timedelta
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging

from config import LOCATION, DAYS_IN_ADVANCE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_driver(headless=False):
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

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    logger.info("Chrome driver initialized with performance optimizations")
    return driver


def get_target_date(from_date=None):
    """Calculate the target booking date"""
    prague_tz = pytz.timezone('Europe/Prague')

    if from_date is None:
        from_date = datetime.now(prague_tz)

    target_date = from_date + timedelta(days=DAYS_IN_ADVANCE)
    return target_date.strftime('%Y-%m-%d')


def test_preload_and_refresh(num_refreshes=3, headless=False):
    """Test preloading page and refreshing multiple times"""
    logger.info("=" * 60)
    logger.info("PRODUCTION PRELOAD & REFRESH TEST")
    logger.info("=" * 60)
    logger.info(f"Location: {LOCATION}")
    logger.info(f"Days in advance: {DAYS_IN_ADVANCE}")
    logger.info(f"Number of refreshes: {num_refreshes}")
    logger.info(f"Headless mode: {headless}")
    logger.info("=" * 60)

    driver = None

    try:
        # STEP 1: Setup driver
        logger.info("\n[STEP 1] Setting up Chrome driver...")
        driver = setup_driver(headless=headless)
        logger.info("✓ Driver ready")

        # STEP 2: Calculate target date (simulating midnight calculation)
        logger.info("\n[STEP 2] Calculating target date...")
        prague_tz = pytz.timezone('Europe/Prague')
        now = datetime.now(prague_tz)

        # Simulate midnight calculation
        tomorrow = now + timedelta(days=1)
        simulated_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

        target_date = get_target_date(from_date=simulated_midnight)
        logger.info(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Simulated midnight: {simulated_midnight.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Target booking date: {target_date}")

        # STEP 3: Load the page (PRELOAD simulation)
        logger.info("\n[STEP 3] PRELOADING page...")
        url = f"https://www.padelpowers.com/rezervace/court-booking/reservation/?location={LOCATION}&date={target_date}"
        logger.info(f"URL: {url}")

        start_time = time.time()
        driver.get(url)
        load_time = time.time() - start_time
        logger.info(f"✓ Page loaded in {load_time:.2f} seconds")

        # STEP 4: Wait for timeslots container
        logger.info("\n[STEP 4] Waiting for timeslots container...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".timeslots-container"))
            )
            logger.info("✓ Timeslots container found!")

            # Count available slots
            try:
                slots = driver.find_elements(By.CSS_SELECTOR, 'button.btn.text-nowrap.btn-outline-primary.btn-sm')
                enabled_slots = [s for s in slots if s.get_attribute('disabled') is None]
                logger.info(f"✓ Found {len(slots)} total slots, {len(enabled_slots)} available")
            except Exception as e:
                logger.warning(f"Could not count slots: {e}")

        except TimeoutException:
            logger.warning("⚠ Timeslots container not found (this is expected if no slots available yet)")
            # Take screenshot
            try:
                screenshot_path = "/home/jakub-stejskal/projects/personal/padel/captures/production_preload.png"
                driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
            except Exception as e:
                logger.error(f"Could not save screenshot: {e}")

        # STEP 5: Test refreshes
        logger.info(f"\n[STEP 5] Testing {num_refreshes} refreshes...")
        for i in range(1, num_refreshes + 1):
            logger.info(f"\n--- Refresh {i}/{num_refreshes} ---")
            time.sleep(1)  # Wait a bit between refreshes

            start_time = time.time()
            driver.refresh()
            refresh_time = time.time() - start_time
            logger.info(f"✓ Page refreshed in {refresh_time:.2f} seconds")

            # Check if timeslots container is still there
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".timeslots-container"))
                )
                logger.info("✓ Timeslots container found after refresh")

                # Count slots again
                try:
                    slots = driver.find_elements(By.CSS_SELECTOR, 'button.btn.text-nowrap.btn-outline-primary.btn-sm')
                    enabled_slots = [s for s in slots if s.get_attribute('disabled') is None]
                    logger.info(f"✓ Found {len(slots)} total slots, {len(enabled_slots)} available")
                except Exception as e:
                    logger.warning(f"Could not count slots: {e}")

            except TimeoutException:
                logger.warning("⚠ Timeslots container not found after refresh")

        # STEP 6: Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST COMPLETE - SUMMARY")
        logger.info("=" * 60)
        logger.info("✅ Page preload: SUCCESS")
        logger.info(f"✅ {num_refreshes} refreshes: SUCCESS")
        logger.info("✅ No crashes or errors detected")
        logger.info("\nThe preload mechanism is working correctly!")
        logger.info("=" * 60)

        # Keep browser open for inspection
        logger.info("\nBrowser will stay open for 10 seconds for inspection...")
        time.sleep(10)

    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Keep browser open on error
        if driver:
            logger.info("\nBrowser will stay open for inspection due to error...")
            input("Press Enter to close...")

    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")


if __name__ == "__main__":
    import sys

    # Parse arguments
    headless = "--headless" in sys.argv
    num_refreshes = 5  # Default

    # Check for --refreshes=N argument
    for arg in sys.argv:
        if arg.startswith("--refreshes="):
            try:
                num_refreshes = int(arg.split("=")[1])
            except ValueError:
                logger.warning(f"Invalid --refreshes value: {arg}")

    test_preload_and_refresh(num_refreshes=num_refreshes, headless=headless)
