import requests
from .schedule import get_last_race_for_series


def get_last_completed_race_id(series_id: int):
    race = get_last_race_for_series(series_id)
    if race and isinstance(race, dict):
        return race.get("race_id")
    return None


def fetch_standings(series_id: int, race_id: int):
    url = f"https://cf.nascar.com/live/feeds/series_{series_id}/{race_id}/live_points.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[Standings] Error: {e}")
        return None
