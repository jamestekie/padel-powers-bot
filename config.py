"""
Configuration file for Padel Powers booking bot
Edit these settings to customize the bot's behavior
"""

# Login credentials
# Import from config_secret.py (create from config_secret.py.example)
try:
    from config_secret import LOGIN_EMAIL, LOGIN_PASSWORD
except ImportError:
    print("WARNING: config_secret.py not found. Copy config_secret.py.example to config_secret.py and add your credentials.")
    LOGIN_EMAIL = ""
    LOGIN_PASSWORD = ""

# Booking preferences
LOCATION = "Smíchov"  # Options: "Smíchov" or "Kraví hora"
TARGET_START_HOUR = 18  # Start of desired time range (18 = 6 PM)
TARGET_END_HOUR = 21    # End of desired time range (21 = 9 PM)
DURATION_MINUTES = 60   # Booking duration: 60, 90, or 120 minutes

# Timing
WAIT_FOR_MIDNIGHT = False  # Set to False for testing, True for production
DAYS_IN_ADVANCE = 14     # How many days in advance to book (14 days in advance is when padelpowers release new hours)

# Browser settings
HEADLESS = False  # Set to True to run without showing browser window


# Advanced settings
MAX_RETRY_ATTEMPTS = 3  # How many times to retry if booking fails
RETRY_DELAY_SECONDS = 1  # Delay between retries
PAGE_LOAD_TIMEOUT = 10  # Seconds to wait for page to load
BOOKING_TIMEOUT = 5     # Seconds to wait for booking confirmation

# Auto-refresh settings
MAX_REFRESH_ATTEMPTS = 30  # How many times to refresh if slots not available yet (30 = ~30 seconds)
MIDNIGHT_MONITOR_MINUTES = 10  # How long to keep checking after midnight (pre-booked slots expire if not confirmed in 5 min)

# Logging
LOG_LEVEL = 'INFO'  # Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_FILE = 'booking_bot.log'  # Set to None to disable file logging

# =============================================================================
# Cancellation Scanner Settings
# This scanner checks for cancelled slots across multiple days
# =============================================================================
SCANNER_WEEKDAYS = [0, 1, 2, 3, 4]  # Days to check: Monday=0 through Sunday=6
SCANNER_START_TIME = "17:30"        # Earliest slot time (HH:MM format)
SCANNER_END_TIME = "21:00"          # Latest slot start time (HH:MM format, exclusive)
SCANNER_DAYS_AHEAD = 14             # How many days ahead to scan (including today)
SCANNER_DURATION_MINUTES = 60       # Duration to book: 60, 90, or 120 minutes
