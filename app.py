import os
from flask import Flask
from core.logger import setup_logging
from core.database import init_db
from routes.main import main_bp
from routes.auth import auth_bp
from routes.cards import cards_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object("config.Config")

    env_path = os.path.join(app.root_path, ".env")
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(env_path)

    setup_logging(app.config.get("LOG_CONFIG_PATH"))

    db_path = "/var/www/html/bankapp/data/bankapp.sqlite3"
    if not os.path.exists(db_path):
        print("[INIT] Database not found — initializing fresh schema and seeding data...")
        init_db(app)
    else:
        print("[INIT] Database already exists — skipping seeding.")
        init_db(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cards_bp, url_prefix="/cards")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
