import requests
from .schedule import get_last_completed_race


def get_last_completed_race_id(series_id: int):
    schedule = get_last_completed_race(series_id)
    for race in schedule:
        if race.get("is_last_race"):
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
