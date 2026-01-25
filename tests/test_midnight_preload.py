"""
Test the midnight preloading functionality by mocking the current time
"""
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytz
from padel_booking_bot import PadelBookingBotFast
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_preload_at_midnight():
    """Test preloading by mocking time to be just before midnight"""

    prague_tz = pytz.timezone('Europe/Prague')

    # Mock midnight scenario - 23:59:40 (20 seconds before midnight)
    # This gives us >10 seconds, so preload will trigger at 5 seconds before
    mock_now = datetime(2026, 1, 7, 23, 59, 40, tzinfo=prague_tz)
    expected_midnight = datetime(2026, 1, 8, 0, 0, 0, tzinfo=prague_tz)

    logger.info("=" * 60)
    logger.info("TESTING MIDNIGHT PRELOAD LOGIC")
    logger.info("=" * 60)
    logger.info(f"Mocked current time: {mock_now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Expected midnight: {expected_midnight.strftime('%Y-%m-%d %H:%M:%S')}")

    bot = PadelBookingBotFast(location="Smíchov")

    # Track the sequence of datetime.now() calls
    call_count = [0]

    def mock_datetime_now(tz=None):
        """Mock datetime.now() to simulate time progression"""
        call_count[0] += 1

        if call_count[0] == 1:
            # First call: initial check (23:59:40)
            logger.info(f"[Call {call_count[0]}] Returning initial time: 23:59:40")
            return mock_now
        elif call_count[0] == 2:
            # Second call: after preload wait (15 seconds passed), now at 23:59:55
            time_value = mock_now + timedelta(seconds=15)
            logger.info(f"[Call {call_count[0]}] Returning after preload wait: {time_value.strftime('%H:%M:%S')}")
            return time_value
        else:
            # Third+ calls: at or past midnight
            logger.info(f"[Call {call_count[0]}] Returning midnight: 00:00:00")
            return expected_midnight

    # Mock the driver to avoid actually opening a browser
    mock_driver = MagicMock()
    mock_wait = MagicMock()

    # Create a mock WebDriverWait that simulates successful page load
    def mock_webdriverwait(*args, **kwargs):
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = True
        return mock_wait_instance

    # Patch datetime.now, time.sleep, setup_driver, and WebDriverWait
    with patch('padel_booking_bot.datetime') as mock_datetime_class:
        # Configure mock datetime
        mock_datetime_class.now.side_effect = mock_datetime_now
        mock_datetime_class.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Patch time.sleep to avoid actual waiting
        with patch('padel_booking_bot.time.sleep') as mock_sleep:
            # Track sleep calls
            def log_sleep(seconds):
                logger.info(f"[SLEEP] Would sleep for {seconds:.1f} seconds")

            mock_sleep.side_effect = log_sleep

            # Patch setup_driver to avoid browser launch
            with patch.object(bot, 'setup_driver') as mock_setup:
                bot.driver = mock_driver

                # Patch WebDriverWait
                with patch('padel_booking_bot.WebDriverWait', side_effect=mock_webdriverwait):
                    logger.info("\n" + "=" * 60)
                    logger.info("RUNNING wait_until_midnight()...")
                    logger.info("=" * 60 + "\n")

                    # Run the preload function
                    bot.wait_until_midnight()

                    logger.info("\n" + "=" * 60)
                    logger.info("VERIFICATION")
                    logger.info("=" * 60)

                    # Verify the expected behavior
                    logger.info(f"✓ setup_driver was called: {mock_setup.called}")
                    logger.info(f"✓ driver.get was called: {mock_driver.get.called}")
                    logger.info(f"✓ driver.refresh was called: {mock_driver.refresh.called}")

                    # Check the URL that was loaded
                    if mock_driver.get.called:
                        loaded_url = mock_driver.get.call_args[0][0]
                        logger.info(f"✓ Loaded URL: {loaded_url}")

                        # Extract the date from the URL
                        if 'date=' in loaded_url:
                            date_part = loaded_url.split('date=')[1].split('&')[0] if '&' in loaded_url else loaded_url.split('date=')[1]
                            logger.info(f"✓ Booking date in URL: {date_part}")

                            # Verify the date calculation
                            # Midnight = 2026-01-08, + 14 days = 2026-01-22
                            from config import DAYS_IN_ADVANCE
                            expected_target = expected_midnight + timedelta(days=DAYS_IN_ADVANCE)
                            expected_date_str = expected_target.strftime('%Y-%m-%d')

                            logger.info(f"✓ Expected booking date: {expected_date_str}")
                            logger.info(f"✓ Date calculation correct: {date_part == expected_date_str}")

                            if date_part == expected_date_str:
                                logger.info("✅ SUCCESS! Preloading logic works correctly!")
                            else:
                                logger.error(f"❌ FAIL! Date mismatch. Expected {expected_date_str}, got {date_part}")

                    # Verify sleep was called appropriately
                    logger.info(f"\n✓ Sleep was called {mock_sleep.call_count} times:")
                    for i, call in enumerate(mock_sleep.call_args_list, 1):
                        logger.info(f"  {i}. Sleep({call[0][0]:.1f}s)")

                    logger.info("\n" + "=" * 60)
                    logger.info("TEST COMPLETE")
                    logger.info("=" * 60)


if __name__ == "__main__":
    test_preload_at_midnight()
