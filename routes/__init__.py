from flask import Blueprint

from routes.main import main_bp
from routes.auth import auth_bp
from routes.cards import cards_bp
from routes.admin import admin_bp
from routes.api import api_bp


def register_routes(app):
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cards_bp, url_prefix="/cards")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    for rule in app.url_map.iter_rules():
        app.logger.debug(f"Route registered: {rule}")
