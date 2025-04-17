import requests
from datetime import datetime, timedelta

BASE_URL = "https://statsapi.mlb.com/api/v1"


def get_team_id_by_name(name):
    res = requests.get(f"{BASE_URL}/teams?sportId=1")
    teams = res.json().get("teams", [])
    for team in teams:
        if name.lower() in (team["name"].lower(), team["teamName"].lower()):
            return team["id"]
    return None


def get_last_game(team_id):
    today = datetime.today().strftime("%Y-%m-%d")
    res = requests.get(f"{BASE_URL}/schedule?teamId={team_id}&endDate={today}&limit=10")
    for date in reversed(res.json().get("dates", [])):
        for game in date["games"]:
            if game["status"]["detailedState"] == "Final":
                return game
    return None


def get_next_game(team_id):
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(tomorrow)
    res = requests.get(
        f"{BASE_URL}/schedule?teamId={team_id}&startDate={tomorrow}&limit=5"
    )
    print(res.json())
    for date in res.json().get("dates", []):
        for game in date["games"]:
            if game["status"]["detailedState"] == "Scheduled":
                return game
    return None


def get_live_game(team_id):
    today = datetime.today().strftime("%Y-%m-%d")
    res = requests.get(
        f"{BASE_URL}/schedule?teamId={team_id}&startDate={today}&endDate={today}"
    )
    for date in res.json().get("dates", []):
        for game in date["games"]:
            if game["status"]["abstractGameState"] == "Live":
                return game
    return None
