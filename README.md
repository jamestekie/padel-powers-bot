# Padel Powers Auto-Booking Bot

Automatically reserves padel courts at Padel Powers at midnight (Prague time) when new slots are released, or scans for cancelled slots across multiple days.

## Features

**Midnight Booking Bot** (`padel_booking_bot.py`):
- Pre-loads page before midnight for fastest booking
- Books slots 14 days in advance (when new slots release)
- Fast polling phase + 10-minute extended monitoring for pre-booked slots that expire
- Auto-login and booking

**Cancellation Scanner** (`cancellation_scanner.py`):
- Scans today + next 14 days for available slots
- Filters by weekdays and time window (e.g., Mon-Fri, 17:30-21:00)
- Auto-books first available slot found

## Setup

1. **Install dependencies with uv:**
```bash
uv sync
```

2. **Create credentials file:**
```bash
cp config_secret.py.example config_secret.py
```

Edit `config_secret.py` with your Padel Powers login credentials:
```python
LOGIN_EMAIL = "your@email.com"
LOGIN_PASSWORD = "your_password"
```

3. **Configure settings in `config.py`:**
```python
# Main bot settings
LOCATION = "Smíchov"          # or "Kraví hora"
TARGET_START_HOUR = 18        # 6 PM
TARGET_END_HOUR = 21          # 9 PM
DURATION_MINUTES = 60         # 60, 90, or 120
WAIT_FOR_MIDNIGHT = True      # False for testing

# Cancellation scanner settings
SCANNER_WEEKDAYS = [0, 1, 2, 3, 4]  # Mon-Fri
SCANNER_START_TIME = "17:30"
SCANNER_END_TIME = "21:00"
SCANNER_DAYS_AHEAD = 14
```

## Usage

### Midnight Booking (new slot releases)

Run before midnight to book slots when they're released:

```bash
python padel_booking_bot.py
```

The bot will:
1. Wait until ~5 seconds before midnight
2. Pre-load the booking page
3. Refresh at midnight
4. Fast-poll for 30 seconds
5. If no slots, continue monitoring for 10 minutes (pre-booked slots expire if not confirmed in 5 min)
6. Auto-book first available slot

### Cancellation Scanner (find cancelled slots)

Run anytime to find slots that became available due to cancellations:

```bash
python cancellation_scanner.py
```

The scanner will:
1. Check each weekday from today to +14 days
2. Look for available slots in the configured time window
3. Auto-book the first available slot

## Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `LOCATION` | "Smíchov" | Booking location |
| `TARGET_START_HOUR` | 18 | Earliest hour (midnight bot) |
| `TARGET_END_HOUR` | 21 | Latest hour, exclusive (midnight bot) |
| `DURATION_MINUTES` | 60 | Booking duration: 60, 90, or 120 |
| `WAIT_FOR_MIDNIGHT` | False | Wait for midnight or run immediately |
| `DAYS_IN_ADVANCE` | 14 | Days ahead for midnight booking |
| `MIDNIGHT_MONITOR_MINUTES` | 10 | Extended monitoring after midnight |
| `HEADLESS` | False | Run browser without UI |
| `SCANNER_WEEKDAYS` | [0,1,2,3,4] | Days to scan (0=Mon, 6=Sun) |
| `SCANNER_START_TIME` | "17:30" | Earliest slot time (scanner) |
| `SCANNER_END_TIME` | "21:00" | Latest slot time (scanner) |
| `SCANNER_DAYS_AHEAD` | 14 | Days to scan ahead |

## Project Structure

```
padel/
├── padel_booking_bot.py      # Midnight booking bot
├── cancellation_scanner.py   # Cancellation scanner
├── config.py                 # Configuration settings
├── config_secret.py          # Credentials (not committed)
├── config_secret.py.example  # Credentials template
├── tests/                    # Test files
├── helpers/                  # Debug/inspection utilities
└── captures/                 # Screenshots for debugging
```

## Tips

- Run the midnight bot 2-3 minutes before midnight
- Keep `HEADLESS = False` to watch the booking and complete payment
- Test with `WAIT_FOR_MIDNIGHT = False` first

## Disclaimer

Use responsibly. Respect the website's terms of service.
