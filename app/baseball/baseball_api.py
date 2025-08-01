import requests
from datetime import datetime, timedelta
import logging
import pytz

logger = logging.getLogger("baseball")
logger.setLevel(logging.DEBUG)

BASE_URL = "https://statsapi.mlb.com/api/v1"

MLB_TEAMS = {
    108: {"name": "Angels", "color": (15, 0, 0)},
    109: {"name": "D-backs", "color": (13, 2, 2)},
    110: {"name": "Orioles", "color": (15, 8, 0)},
    111: {"name": "Red Sox", "color": (12, 2, 2)},
    112: {"name": "Cubs", "color": (0, 6, 15)},
    113: {"name": "Reds", "color": (15, 0, 0)},
    114: {"name": "Guardians", "color": (0, 0, 12)},
    115: {"name": "Rockies", "color": (4, 0, 13)},
    116: {"name": "Tigers", "color": (4, 3, 15)},
    117: {"name": "Astros", "color": (0, 3, 15)},
    118: {"name": "Royals", "color": (1, 5, 15)},
    119: {"name": "Dodgers", "color": (0, 6, 15)},
    120: {"name": "Nationals", "color": (0, 0, 15)},
    121: {"name": "Mets", "color": (1, 4, 15)},
    133: {"name": "Athletics", "color": (0, 8, 0)},
    134: {"name": "Pirates", "color": (0, 0, 0)},
    135: {"name": "Padres", "color": (8, 5, 0)},
    136: {"name": "Mariners", "color": (0, 5, 3)},
    137: {"name": "Giants", "color": (15, 6, 0)},
    138: {"name": "Cardinals", "color": (12, 1, 3)},
    139: {"name": "Rays", "color": (5, 11, 11)},
    140: {"name": "Rangers", "color": (0, 0, 15)},
    141: {"name": "Blue Jays", "color": (0, 6, 15)},
    142: {"name": "Twins", "color": (0, 0, 12)},
    143: {"name": "Phillies", "color": (15, 0, 0)},
    144: {"name": "Braves", "color": (1, 4, 12)},
    145: {"name": "White Sox", "color": (0, 0, 0)},
    146: {"name": "Marlins", "color": (0, 6, 11)},
    147: {"name": "Yankees", "color": (0, 0, 15)},
    158: {"name": "Brewers", "color": (1, 4, 12)},
}

PITCH_TYPE_MAP = {
    "Changeup": "Changeup",
    "Curveball": "Curve",
    "Cutter": "Cutter",
    "Eephus": "Eephus",
    "Fastball": "Fastball",
    "Forkball": "Forkball",
    "Four-Seam Fastball": "4-Seam Fastb",
    "Knuckle Curve": "Knuck Curve",
    "Sinker": "Sinker",
    "Slider": "Slider",
    "Slow Curve": "Slow Curve",
    "Slurve": "Slurve",
    "Splitter": "Splitter",
    "Sweeper": "Sweeper",
}

PITCH_OUTCOME_MAP = {
    "Ball": "Ball",
    "Ball In Dirt": "Ball (Dirt)",
    "Called Strike": "Called Strk",
    "Foul": "Foul",
    "Foul Bunt": "Foul Bunt",
    "Foul Tip": "Foul Tip",
    "Hit By Pitch": "HBP",
    "In play, no out": "In Play - No",
    "In play, out(s)": "In Play - Out",
    "In play, run(s)": "In Play - Run",
    "Missed Bunt": "Miss Bunt",
    "Pitchout": "Pitchout",
    "Swinging Strike": "Swing Strk",
    "Swinging Strike (Blocked)": "Sw Strk (Blk)",
}


def get_team_info(team_id):
    return MLB_TEAMS.get(team_id, {"name": f"Team {team_id}", "color": (15, 15, 15)})


def get_team_id_by_name(name):
    res = requests.get(f"{BASE_URL}/teams?sportId=1")
    teams = res.json().get("teams", [])
    for team in teams:
        team_name = team["name"].lower()
        team_team_name = team["teamName"].lower()
        search_name = name.lower()

        # Exact match first
        if search_name == team_name or search_name == team_team_name:
            return team["id"]

        # Check if search name is contained in team name or vice versa
        if (
            search_name in team_name
            or team_name in search_name
            or search_name in team_team_name
            or team_team_name in search_name
        ):
            return team["id"]
    return None


def get_last_game(team_id):
    now = datetime.today()
    today = now.strftime("%Y-%m-%d")

    # Dynamic season detection
    current_year = now.year
    if now.month <= 2:  # Jan-Feb: use previous year (off-season)
        season_start = f"{current_year - 1}-03-01"
    else:  # Mar-Dec: use current year
        season_start = f"{current_year}-03-01"

    res = requests.get(
        f"{BASE_URL}/schedule?sportId=1&teamId={team_id}&startDate={season_start}&endDate={today}&limit=100"
    )
    for date in reversed(res.json().get("dates", [])):
        for game in date["games"]:
            if game["status"]["detailedState"] == "Final":
                return game
    return None


def get_next_game(team_id):
    now = datetime.today()
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Search up to 30 days ahead to find next scheduled game
    end_search = (now + timedelta(days=30)).strftime("%Y-%m-%d")

    res = requests.get(
        f"{BASE_URL}/schedule?sportId=1&teamId={team_id}&startDate={tomorrow}&endDate={end_search}&limit=20"
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

    if res.status_code != 200:
        logger.warning(f"API returned status {res.status_code}")
        return None

    try:
        data = res.json()
    except Exception as e:
        logger.warning(f"Failed to parse JSON response: {e}")
        logger.warning(f"Response content: {res.text[:200]}...")
        return None

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

    # Get actual game scores from liveData, not play result scores
    try:
        home_score = data["liveData"]["linescore"]["teams"]["home"]["runs"]
        away_score = data["liveData"]["linescore"]["teams"]["away"]["runs"]
    except (KeyError, TypeError):
        # Fallback to play result if linescore isn't available
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
        col = (zone_width / 2 - x) / zone_width * strike_width
        row = (1 - (y - bottom) / (top - bottom)) * strike_height
        return int(col), int(row)

    col, row = map_to_zone(x, y, zone_top, zone_bottom)

    home_team_id = data["gameData"]["teams"]["home"]["id"]
    away_team_id = data["gameData"]["teams"]["away"]["id"]

    home_info = get_team_info(home_team_id)
    away_info = get_team_info(away_team_id)

    home_team = home_info["name"]
    away_team = away_info["name"]

    return {
        "batter": batter,
        "batting_avg": batting_avg,
        "colors": {
            "home": home_info["color"],
            "away": away_info["color"],
        },
        "count": {"balls": balls, "strikes": strikes, "outs": outs},
        "inning": {"half": half_inning, "number": inning},
        "matrix_location": {"x": col, "y": row},
        "outcome": PITCH_OUTCOME_MAP[pitch["details"]["description"]],
        "pitch_speed": pitch["pitchData"].get("startSpeed", "N/A"),
        "pitch_type": PITCH_TYPE_MAP[pitch["details"]["type"]["description"]],
        "pitcher": pitcher,
        "score": {away_team: away_score, home_team: home_score},
        "teams": {"home": home_team, "away": away_team},
        "todays_line": todays_line,
        "raw_pitch_type": pitch["details"]["type"]["description"],
        "raw_outcome": pitch["details"]["description"],
        "zone_top": zone_top,
        "zone_bottom": zone_bottom,
        "px": x,
        "pz": y,
    }
