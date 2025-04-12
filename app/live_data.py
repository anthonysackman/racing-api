import requests
import datetime
from pytz import timezone

EASTERN = timezone("US/Eastern")
PACIFIC = timezone("US/Pacific")
LIVE_URL = "https://cf.nascar.com/live/feeds/live-feed.json"


def format_datetime_from_eastern_to_pst(dt_str):
    try:
        dt_naive = datetime.datetime.fromisoformat(dt_str)
        dt_eastern = EASTERN.localize(dt_naive)
        dt_pacific = dt_eastern.astimezone(PACIFIC)
        return dt_pacific.strftime("%B %d, %I:%M %p")
    except Exception as e:
        print(f"[Datetime parse error] {e}")
        return None


def format_event_schedule(events):
    for event in events:
        start_time = event.get("start_time_utc")
        if start_time:
            formatted = format_datetime_from_eastern_to_pst(start_time)
            if formatted:
                event["start_time_utc_formatted"] = formatted


def get_live_race_data():
    try:
        response = requests.get(LIVE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and data.get("race_id"):
            if "schedule" in data:
                format_event_schedule(data["schedule"])
            # Format main date fields
            for key in [
                "date_scheduled",
                "race_date",
                "qualifying_date",
                "tunein_date",
            ]:
                if key in data and data[key]:
                    formatted = format_datetime_from_eastern_to_pst(data[key])
                    if formatted:
                        data[f"{key}_formatted"] = formatted
            return data

        return None  # No live race
    except Exception as e:
        print(f"[ERROR] Failed to fetch live feed: {e}")
        return None
