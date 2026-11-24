from flask import Blueprint

api_bp = Blueprint("api", __name__)

from app.api import routes


api_bp.register_blueprint(
    routes.payment_bp,
    url_prefix="/payments"
)