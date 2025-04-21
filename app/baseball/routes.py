from sanic import Blueprint, response
from .baseball_api import (
    get_team_id_by_name,
    get_last_game,
    get_next_game,
    get_live_game,
    get_live_game_details,
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
    print(team_id)
    if not team_id:
        return response.json({"error": "Team not found"}, status=404)
    game = get_next_game(team_id)
    return response.json(game or {"error": "No upcoming game found"})


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
