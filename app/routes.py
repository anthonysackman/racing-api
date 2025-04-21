from sanic import Blueprint, response, Request
import json
from pathlib import Path

# Import other routes or blueprints if needed here
# from .nascar.routes import bp as nascar_bp
# from .baseball.routes import bp as baseball_bp

app = Blueprint("main")
STATUS_FILE = Path(__file__).parent / "data" / "display_status.json"


@app.get("/")
async def index(request: Request):
    current = "all"
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            current = json.load(f).get("mode", "all")
    return response.html(f"""
    <html>
    <head><title>ESP32 Sport Matrix Display</title></head>
    <body>
        <h1>ESP32 Sport Matrix Display</h1>
        <p>Current status: {current}</p>
        <form action="/set_mode" method="POST">
            <select name="mode">
                <option value="all">All</option>
                <option value="baseball">Baseball</option>
                <option value="nascar">NASCAR</option>
            </select>
            <button type="submit">Set Mode</button>
        </form>
    </body>
    </html>
    """)


@app.post("/set_mode")
async def set_mode(request: Request):
    mode = request.form.get("mode", "all")
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump({"mode": mode}, f)
    return response.redirect("/")


@app.get("/status")
async def get_status(request: Request):
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            return response.json(json.load(f))
    return response.json({"mode": "all"})
