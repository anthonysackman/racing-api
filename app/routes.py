from sanic import Blueprint, response
from .live_data import get_live_race_data
from .schedule import get_schedule_for_series, get_last_race_for_series
from .standings import get_last_completed_race_id, fetch_standings

nascar_bp = Blueprint("nascar", url_prefix="/nascar")


@nascar_bp.get("/race/<series_id:int>")
async def get_upcoming_race(request, series_id):
    races = get_schedule_for_series(series_id)
    for race in races:
        if race.get("is_today_race") or race.get("is_next_race"):
            return response.json(race)
    return response.json({"error": "No upcoming race found"}, status=404)


@nascar_bp.get("/race/live")
async def get_live_race(request):
    data = get_live_race_data()
    if data:
        return response.json(data)
    return response.json({"error": "No live race found"}, status=404)


@nascar_bp.get("/race/last/<series_id:int>")
async def get_last_race(request, series_id):
    race = get_last_race_for_series(series_id)
    if race:
        return response.json(race)
    return response.json({"error": "No past race found"}, status=404)


@nascar_bp.get("/standings/<series_id:int>")
async def get_series_standings(request, series_id):
    race_id = get_last_completed_race_id(series_id)
    if not race_id:
        return response.json({"error": "No completed race found"}, status=404)

    standings = fetch_standings(series_id, race_id, 10)
    if standings is None:
        return response.json({"error": "Failed to fetch standings"}, status=502)

    return response.json(standings)
