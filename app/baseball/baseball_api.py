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
    res = requests.get(
        f"{BASE_URL}/schedule?sportId=1&teamId={team_id}&startDate=2024-01-01&endDate={today}&limit=100"
    )
    for date in reversed(res.json().get("dates", [])):
        for game in date["games"]:
            if game["status"]["detailedState"] == "Final":
                return game
    return None


def get_next_game(team_id):
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    res = requests.get(
        f"{BASE_URL}/schedule?sportId=1&teamId={team_id}&startDate={tomorrow}&endDate={tomorrow}&limit=5"
    )
    for date in res.json().get("dates", []):
        for game in date["games"]:
            if game["status"]["detailedState"] == "Scheduled":
                return game
    return None


def get_live_game(team_id):
    today = datetime.today().strftime("%Y-%m-%d")
    res = requests.get(
        f"{BASE_URL}/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate={today}"
    )
    for date in res.json().get("dates", []):
        for game in date["games"]:
            if game["status"]["abstractGameState"] == "Live":
                return game
    return None


def get_live_game_details(team_id):
    game = get_live_game(team_id)
    if not game:
        return None

    gamePk = game["gamePk"]
    res = requests.get(f"{BASE_URL}.1/game/{gamePk}/feed/live")

    return res.json()
