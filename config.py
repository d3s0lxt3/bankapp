import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    LOG_CONFIG_PATH = os.path.join(BASE_DIR, "config", "logging.conf")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///data/bankapp.sqlite3"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_HOME = "/var/www/html/bankapp"
    LOG_DIR = os.path.join(APP_HOME, "logs")
    SSTI_SIMULATE = True
    ALLOWED_EXTENSIONS = {"jpg", "png", "pdf"}
