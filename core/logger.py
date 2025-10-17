import logging
import logging.config
import os

DEFAULT_LOG_DIR = "../bankapp/logs"
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "app.log")


def setup_logging(config_path=None):
    if config_path and os.path.exists(config_path):
        try:
            logging.config.fileConfig(config_path, disable_existing_loggers=False)
            logging.getLogger(__name__).info("Logging configured from %s", config_path)
            return
        except Exception as e:
            print("Failed to load logging config:", e)

    try:
        os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
    except Exception:
        pass

    handlers = [logging.FileHandler(DEFAULT_LOG_FILE), logging.StreamHandler()]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )

    logging.getLogger(__name__).info(
        "Logging configured with fallback (file=%s)", DEFAULT_LOG_FILE
    )
