from sanic import Sanic
from app.nascar.routes import nascar_bp
from app.baseball.routes import baseball_bp

app = Sanic("SportsAPI")
app.blueprint(nascar_bp)
app.blueprint(baseball_bp)
