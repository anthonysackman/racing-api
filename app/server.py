from sanic import Sanic
from app.nascar.routes import nascar_bp
from app.baseball.routes import baseball_bp
from app.routes import index_bp
import json
from app.config_manager import config_manager


app = Sanic("SportsAPI")

# Register blueprints
app.blueprint(nascar_bp)
app.blueprint(baseball_bp)
app.blueprint(index_bp)


# Middleware to inject status into JSON responses
@app.middleware("response")
async def inject_status(request, res):
    if res.content_type == "application/json" and isinstance(res.body, bytes):
        try:
            data = json.loads(res.body)
            mode = config_manager.get_mode()
            data["status"] = mode
            res.body = json.dumps(data).encode()
            res.headers["Content-Length"] = str(len(res.body))
        except Exception:
            pass
