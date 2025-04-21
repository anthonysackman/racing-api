from sanic import Blueprint, response, Request
import json
from pathlib import Path
from enum import Enum


class DisplayMode(str, Enum):
    ALL = "all"
    BASEBALL = "baseball"
    NASCAR = "nascar"


index_bp = Blueprint("index", url_prefix="/")
STATUS_FILE = Path(__file__).parent / "data" / "display_status.json"
DEFAULT_MODE = DisplayMode.ALL


@index_bp.get("/")
async def index(request: Request):
    current = DEFAULT_MODE
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            try:
                current = DisplayMode(json.load(f).get("mode", DEFAULT_MODE))
            except ValueError:
                current = DEFAULT_MODE
    options = "\n".join(
        f'<option value="{m.value}"{" selected" if m == current else ""}>{m.name.title()}</option>'
        for m in DisplayMode
    )
    return response.html(f"""
    <html>
    <head><title>ESP32 Sport Matrix Display</title></head>
    <body>
        <h1>ESP32 Sport Matrix Display</h1>
        <p>Current status: {(current.value).title()}</p>
        <form action="/set_mode" method="POST">
            <select name="mode">{options}</select>
            <button type="submit">Set Mode</button>
        </form>
    </body>
    </html>
    """)


@index_bp.post("/set_mode")
async def set_mode(request: Request):
    mode_str = request.form.get("mode", DEFAULT_MODE.value)
    try:
        mode = DisplayMode(mode_str)
    except ValueError:
        return response.text("Invalid mode", status=400)
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump({"mode": mode.value}, f)
    return response.redirect("/")


@index_bp.get("/status")
async def get_status(request: Request):
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            return response.json(json.load(f))
    return response.json({"mode": DEFAULT_MODE.value})
