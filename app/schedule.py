import os
import json
import requests
import datetime
from pytz import timezone

EASTERN = timezone("US/Eastern")
PACIFIC = timezone("US/Pacific")
YEAR = "2025"
URL = f"https://cf.nascar.com/cacher/{YEAR}/race_list_basic.json"
CACHE_FILE = os.path.join("data", "schedule.json")


def format_datetime_from_eastern_to_pst(dt_str):
    try:
        dt_naive = datetime.datetime.fromisoformat(dt_str)
        dt_eastern = EASTERN.localize(dt_naive)
        dt_pacific = dt_eastern.astimezone(PACIFIC)
        return dt_pacific.strftime("%B %d, %I:%M %p")
    except Exception as e:
        print(f"[Datetime parse error] {e}")
        return None


def add_formatted_dates_to_race(race):
    fields = ["date_scheduled", "race_date", "qualifying_date", "tunein_date"]
    for field in fields:
        if field in race and race[field]:
            formatted = format_datetime_from_eastern_to_pst(race[field])
            if formatted:
                race[f"{field}_formatted"] = formatted

    if "schedule" in race:
        for event in race["schedule"]:
            start_time = event.get("start_time_utc")
            if start_time:
                formatted = format_datetime_from_eastern_to_pst(start_time)
                if formatted:
                    event["start_time_utc_formatted"] = formatted


def fetch_and_cache_schedule():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return data
    except Exception as e:
        print(f"[ERROR] Fetch failed: {e}")
        return None


def load_cached_schedule():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def is_data_stale(schedule_data):
    now = datetime.datetime.now(tz=PACIFIC)
    for races in schedule_data.values():
        for race in races:
            date_str = race.get("race_date") or race.get("date_scheduled")
            try:
                race_time = datetime.datetime.fromisoformat(date_str)
                if race_time > now:
                    return False
            except:
                continue
    return True


def ensure_schedule():
    if not os.path.exists(CACHE_FILE):
        return fetch_and_cache_schedule()
    mtime = os.path.getmtime(CACHE_FILE)
    file_age = (
        datetime.datetime.now(tz=PACIFIC)
        - datetime.datetime.fromtimestamp(mtime, tz=PACIFIC)
    ).total_seconds()
    cached = load_cached_schedule()
    if file_age > 86400 or is_data_stale(cached):
        return fetch_and_cache_schedule()
    return cached


def get_schedule_for_series(series_id):
    data = ensure_schedule()
    if not data:
        return []

    series_key = f"series_{series_id}"
    races = sorted(data.get(series_key, []), key=lambda r: r.get("race_date", ""))
    today = datetime.datetime.now(tz=PACIFIC).date()

    next_race = None
    min_future_diff = None

    for race in races:
        race["is_today_race"] = False
        race["is_next_race"] = False

        try:
            race_date = datetime.datetime.fromisoformat(race["race_date"]).date()
        except:
            continue

        add_formatted_dates_to_race(race)

        if race_date == today:
            race["is_today_race"] = True
            return [race]
        elif race_date > today:
            diff = (race_date - today).days
            if min_future_diff is None or diff < min_future_diff:
                next_race = race
                min_future_diff = diff

    if next_race:
        next_race["is_next_race"] = True
        return [next_race]

    return []


def get_last_race_for_series(series_id):
    data = ensure_schedule()
    if not data:
        return None

    series_key = f"series_{series_id}"
    races = sorted(
        data.get(series_key, []), key=lambda r: r.get("race_date", ""), reverse=True
    )
    today = datetime.datetime.now(tz=PACIFIC).date()

    for race in races:
        try:
            race_date = datetime.datetime.fromisoformat(race["race_date"]).date()
        except:
            continue

        if race_date < today:
            add_formatted_dates_to_race(race)
            race["is_last_race"] = True
            return race

    return None
