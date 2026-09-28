from datetime import datetime
from zoneinfo import ZoneInfo

from langchain.tools import tool


@tool
def current_datetime(timezone: str = "Asia/Kolkata") -> dict:
    """Get the current date and time for a timezone."""

    try:
        current_time = datetime.now(ZoneInfo(timezone))

        return {
            "timezone": timezone,
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "day": current_time.strftime("%A"),
            "datetime": current_time.isoformat(),
        }

    except Exception as e:
        return {
            "error": f"Could not get current date and time: {str(e)}"
        }