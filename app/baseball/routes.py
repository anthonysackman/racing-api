from sanic import Blueprint, response
from .baseball_api import (
    get_team_id_by_name,
    get_last_game,
    get_next_game,
    get_next_games,
    get_live_game,
    get_live_game_details,
    get_standings,
)

baseball_bp = Blueprint("baseball", url_prefix="/baseball")


@baseball_bp.get("/last/<team_name>")
async def last_game(request, team_name):
    team_id = get_team_id_by_name(team_name)
    if not team_id:
        return response.json({"error": "Team not found"}, status=404)
    game = get_last_game(team_id)
    return response.json(game or {"error": "No completed game found"})


@baseball_bp.get("/next/<team_name>")
async def next_game(request, team_name):
    team_id = get_team_id_by_name(team_name)
    if not team_id:
        return response.json({"error": "Team not found"}, status=404)
    game = get_next_game(team_id)
    return response.json(game or {"error": "No upcoming game found"})


@baseball_bp.get("/schedule/<team_name>")
async def schedule(request, team_name):
    """Next X games for a team. Query param: limit (default 5)."""
    team_id = get_team_id_by_name(team_name)
    if not team_id:
        return response.json({"error": "Team not found"}, status=404)
    try:
        limit = int(request.args.get("limit", 5))
        limit = min(max(1, limit), 30)
    except (TypeError, ValueError):
        limit = 5
    games = get_next_games(team_id, limit=limit)
    return response.json(games)


@baseball_bp.get("/standings")
async def standings(request):
    """Standings for each AL/NL division. Query param: season (default current year)."""
    try:
        season = request.args.get("season")
        season = int(season) if season else None
    except (TypeError, ValueError):
        season = None
    data = get_standings(season=season)
    return response.json(data)


@baseball_bp.get("/live/<team_name>")
async def live_game(request, team_name):
    team_id = get_team_id_by_name(team_name)
    if not team_id:
        return response.json({"error": "Team not found"}, status=404)
    game = get_live_game(team_id)
    return response.json(game or {"error": "No live game found"})


@baseball_bp.get("/live/details/<team_name>")
async def live_details(request, team_name):
    team_id = get_team_id_by_name(team_name)
    if not team_id:
        return response.json({"error": "Team not found"}, status=404)

    data = get_live_game_details(team_id)
    if not data:
        return response.json({"error": "No live game found"}, status=404)

    # Optionally extract & format relevant fields here

    return response.json(data)
