from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy(session_options={"expire_on_commit": False})
migrate = Migrate()


def init_database(app):
    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import Payment
