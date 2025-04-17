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


def clean_last_name(name):
    for i, c in enumerate(name):
        if not (c.isalnum() or c == "'"):
            return name[:i]
    return name


def get_live_race_data():
    try:
        response = requests.get(LIVE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("vehicles"):
            return None  # No live race data

        # Format time_of_day_os
        if "time_of_day_os" in data:
            formatted = format_datetime_from_eastern_to_pst(data["time_of_day_os"][:19])
            if formatted:
                data["time_of_day_os_formatted"] = formatted

        top_3 = sorted(data["vehicles"], key=lambda v: v.get("running_position", 999))[
            :3
        ]
        formatted_vehicles = []

        for v in top_3:
            driver = v.get("driver", {})
            first = driver.get("first_name", "")
            last = driver.get("last_name", "")
            short_name = f"{first[:1]}, {clean_last_name(last)}"

            formatted_vehicles.append(
                {
                    "driver_name": driver.get("full_name"),
                    "short_display_name": short_name,
                    "position": v.get("running_position"),
                    "laps_completed": v.get("laps_completed"),
                    "last_lap_time": v.get("last_lap_time"),
                    "last_lap_speed": v.get("last_lap_speed"),
                    "vehicle_number": v.get("vehicle_number"),
                }
            )

        data["vehicles"] = formatted_vehicles
        return data

    except Exception as e:
        print(f"[ERROR] Failed to fetch live race feed: {e}")
        return None
