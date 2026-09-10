from django import template
from django.conf import settings
from datetime import datetime
from django.utils import timezone
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

register = template.Library()

# Short month names in Thai (common abbreviations)
THAI_MONTH_SHORT = [
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.",
]


def _to_local(dt):
    """Convert a datetime to the project's local timezone (Asia/Bangkok).

    Uses django.utils.timezone.localtime which respects Django's timezone
    settings. If a naive datetime is passed, treat it as UTC then convert.
    """
    if not dt:
        return None
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    try:
        if timezone.is_naive(dt):
            # assume stored in UTC
            dt = timezone.make_aware(dt, timezone.utc)
        return timezone.localtime(dt, timezone.get_current_timezone())
    except Exception:
        # Fallback: try zoneinfo conversion if available
        try:
            tzname = getattr(settings, "TIME_ZONE", None)
            if tzname and ZoneInfo and getattr(dt, "tzinfo", None) is not None:
                return dt.astimezone(ZoneInfo(tzname))
        except Exception:
            pass
    return dt


@register.filter
def thai_date(value):
    """Format a date/datetime as Thai date (DD MMM YYYY BE)."""
    if not value:
        return ""
    dt = _to_local(value)
    try:
        day = dt.day
        month = THAI_MONTH_SHORT[dt.month - 1]
        year = dt.year + 543
        return f"{day} {month} {year}"
    except Exception:
        return value


@register.filter
def thai_datetime(value):
    """Format datetime as Thai date/time: 'DD MMM YYYY HH:MM' (BE year)."""
    if not value:
        return ""
    dt = _to_local(value)
    try:
        day = dt.day
        month = THAI_MONTH_SHORT[dt.month - 1]
        year = dt.year + 543
        hour = dt.hour
        minute = dt.minute
        return f"{day} {month} {year} {hour:02d}:{minute:02d}"
    except Exception:
        return value
