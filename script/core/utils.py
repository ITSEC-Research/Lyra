#!/usr/bin/env python3
"""
Utility functions for domain blocklist management.
"""

from datetime import datetime, timezone, timedelta

# Jakarta timezone
JAKARTA_TZ = timezone(timedelta(hours=7))

def get_jakarta_time():
    """Get current time in Jakarta timezone"""
    return datetime.now(JAKARTA_TZ)

def format_number(num):
    """Format number with thousand separators"""
    return f"{num:,}"

def format_datetime(dt_string):
    """Format datetime string to readable format in Jakarta timezone"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) == timedelta(0):
            dt = dt.replace(tzinfo=timezone.utc).astimezone(JAKARTA_TZ)
        return dt.strftime('%Y-%m-%d %H:%M:%S WIB')
    except:
        return dt_string
