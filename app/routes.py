from sanic import Blueprint, response
from .schedule import get_schedule_for_series

nascar_bp = Blueprint("nascar", url_prefix="/nascar")


@nascar_bp.get("/race/<series_id:int>")
async def get_upcoming_race(request, series_id):
    races = get_schedule_for_series(series_id)
    for race in races:
        if race.get("is_today_race") or race.get("is_next_race"):
            return response.json(race)
    return response.json({"error": "No upcoming race found"}, status=404)
