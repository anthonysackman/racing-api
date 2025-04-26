import requests
from datetime import datetime, timedelta
import logging
import pytz

logger = logging.getLogger("baseball")
logger.setLevel(logging.DEBUG)

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
    pacific = pytz.timezone("US/Pacific")
    today = datetime.now(pacific).strftime("%Y-%m-%d")
    logger.warning(f"Fetching schedule for {today} and team ID {team_id}")
    res = requests.get(
        f"{BASE_URL}/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate={today}"
    )
    logger.warning(f"Schedule response: {res.status_code}")
    schedule = res.json()
    logger.warning(f"Schedule data: {schedule}")

    for date in schedule.get("dates", []):
        for game in date.get("games", []):
            status = game.get("status", {})
            logger.warning(f"Checking gamePk={game.get('gamePk')}, status={status}")
            if status.get("abstractGameState") in ["Live", "In Progress"]:
                logger.warning(f"Found live game: {game}")
                return game

    logger.warning("No live game found.")
    return None


def get_live_game_details(team_id):
    logger.warning(f"Getting live game details for team ID: {team_id}")
    game = get_live_game(team_id)
    if not game:
        logger.warning("No live game returned from get_live_game")
        return None

    gamePk = game.get("gamePk")
    logger.warning(f"Fetching live data for gamePk: {gamePk}")
    res = requests.get(f"https://statsapi.mlb.com/api/v1.1/game/{gamePk}/feed/live")
    logger.warning(f"Feed response status: {res.status_code}")
    data = res.json()

    latest_play = data["liveData"]["plays"]["allPlays"][-1]
    batter_info = latest_play["matchup"]["batter"]
    pitcher = latest_play["matchup"]["pitcher"]["fullName"]
    batter = batter_info["fullName"]
    batter_id = batter_info["id"]

    pitch = None
    for play in reversed(data["liveData"]["plays"]["allPlays"]):
        for event in reversed(play.get("playEvents", [])):
            if event.get("type") == "pitch" and "pitchData" in event:
                pitch = event
                latest_play = play
                break
        if pitch:
            break

    if not pitch:
        logger.warning("No pitch data found in any plays")
        return None

    home_team = data["gameData"]["teams"]["home"]["name"]
    away_team = data["gameData"]["teams"]["away"]["name"]
    home_score = latest_play["result"]["homeScore"]
    away_score = latest_play["result"]["awayScore"]

    count = latest_play["count"]
    balls = count["balls"]
    strikes = count["strikes"]
    outs = count["outs"]
    inning = latest_play["about"]["inning"]
    half_inning = "Top" if latest_play["about"]["isTopInning"] else "Bottom"

    player_res = requests.get(
        f"https://statsapi.mlb.com/api/v1/people/{batter_id}?hydrate=stats(group=[hitting],type=[season])"
    )
    batter_data = player_res.json()
    batting_avg = (
        batter_data["people"][0]
        .get("stats", [{}])[0]
        .get("splits", [{}])[0]
        .get("stat", {})
        .get("avg", "N/A")
    )

    at_bats = 0
    hits = 0
    last_result = ""
    for play in data["liveData"]["plays"]["allPlays"]:
        matchup = play.get("matchup", {})
        result = play.get("result", {})
        if matchup.get("batter", {}).get("id") != batter_id:
            continue
        event_type = result.get("eventType", "")
        event = result.get("event", "")
        if event_type in [
            "single",
            "double",
            "triple",
            "home_run",
            "field_out",
            "grounded_into_double_play",
            "force_out",
            "strikeout",
        ]:
            at_bats += 1
            last_result = event
        if event_type in ["single", "double", "triple", "home_run"]:
            hits += 1

    todays_line = f"{hits}-for-{at_bats}"
    if last_result:
        todays_line += f", {last_result.lower()}"

    coords = pitch["pitchData"]["coordinates"]
    x = coords["pX"]
    y = coords["pZ"]
    zone_top = pitch["pitchData"]["strikeZoneTop"]
    zone_bottom = pitch["pitchData"]["strikeZoneBottom"]

    def map_to_zone(
        x, y, top, bottom, zone_width=3.0, strike_width=10, strike_height=15
    ):
        col = int((x + zone_width / 2) / zone_width * strike_width)
        col = max(0, min(strike_width - 1, col))
        row = int((1 - (y - bottom) / (top - bottom)) * strike_height)
        row = max(0, min(strike_height - 1, row))
        return col, row

    col, row = map_to_zone(x, y, zone_top, zone_bottom)

    return {
        "pitcher": pitcher,
        "batter": batter,
        "pitch_type": pitch["details"]["type"]["description"],
        "pitch_speed": pitch["pitchData"].get("startSpeed", "N/A"),
        "outcome": pitch["details"]["description"],
        "matrix_location": {"x": col, "y": row},
        "count": {"balls": balls, "strikes": strikes, "outs": outs},
        "inning": {"half": half_inning, "number": inning},
        "score": {away_team: away_score, home_team: home_score},
        "batting_avg": batting_avg,
        "todays_line": todays_line,
    }
