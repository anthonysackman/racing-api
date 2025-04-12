from sanic import Blueprint, response
from .live_data import get_live_race_data  # Import from your helper module

nascar_bp = Blueprint("nascar", url_prefix="/nascar")


@nascar_bp.get("/race/<series_id:int>")
async def get_upcoming_race(request, series_id):
    from .schedule import get_schedule_for_series

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
