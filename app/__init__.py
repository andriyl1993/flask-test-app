from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from app.config import Config
from app.database import init_database
from app.api import api_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_database(app)

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return {"status": "ok"}

    return app
