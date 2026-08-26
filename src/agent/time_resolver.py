"""
Time resolution for FortyGuard API requests.

Resolves the latest completed provider-supported observation hour
for a given timezone.
"""

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


def resolve_latest_observation_time(timezone_name="America/Phoenix"):
    """
    Resolve the latest completed FortyGuard-supported observation hour.

    Args:
        timezone_name: IANA timezone name

    Returns:
        dict with start_date, start_time, filter_type for FortyGuard API
    """
    tz = ZoneInfo(timezone_name)
    now_local = datetime.now(tz)

    # Floor to the most recent completed hour
    latest_completed = now_local.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

    return {
        "start_date": latest_completed.strftime("%Y-%m-%d"),
        "start_time": latest_completed.strftime("%H:%M"),
        "filter_type": 1
    }


def format_observation_time(api_date_time):
    """Format API date_time dict into human-readable ISO string."""
    tz_offset = "-07:00"  # Phoenix is always GMT-7 (no DST)
    return f"{api_date_time['start_date']}T{api_date_time['start_time']}:00{tz_offset}"
