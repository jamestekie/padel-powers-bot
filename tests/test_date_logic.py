"""
Test script to verify the date calculation logic
"""

from datetime import datetime, timedelta
import pytz

DAYS_IN_ADVANCE = 14
prague_tz = pytz.timezone('Europe/Prague')

# Simulate running on Jan 6 at 11:50 PM
current_time = datetime(2026, 1, 6, 23, 50, 0, tzinfo=prague_tz)

# Calculate midnight
tomorrow = current_time + timedelta(days=1)
midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

# Calculate target date FROM MIDNIGHT (not from current time)
target_date = midnight + timedelta(days=DAYS_IN_ADVANCE)

print("=" * 60)
print("DATE LOGIC TEST")
print("=" * 60)
print(f"Current time:    {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Next midnight:   {midnight.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Days in advance: {DAYS_IN_ADVANCE}")
print(f"Target date:     {target_date.strftime('%Y-%m-%d')}")
print("=" * 60)
print()
print("✓ CORRECT!" if target_date.strftime('%Y-%m-%d') == '2026-01-21' else "✗ WRONG!")
print()
print("Expected: 2026-01-21 (Jan 7 midnight + 14 days)")
print(f"Got:      {target_date.strftime('%Y-%m-%d')}")
print()

# Test with current date logic (OLD - WRONG)
old_target = current_time + timedelta(days=DAYS_IN_ADVANCE)
print("Old logic (from current time):")
print(f"  Current time + 14 = {old_target.strftime('%Y-%m-%d')} ✗ WRONG")
print()
print("New logic (from midnight):")
print(f"  Midnight + 14 = {target_date.strftime('%Y-%m-%d')} ✓ CORRECT")
