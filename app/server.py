from sanic import Sanic
from routes import nascar_bp

app = Sanic("NASCARAPI")
app.blueprint(nascar_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
