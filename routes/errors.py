from flask import Blueprint, render_template, request
import logging

errors_bp = Blueprint("errors", __name__)

logger = logging.getLogger("app")


@errors_bp.app_errorhandler(404)
def not_found(e):
    logger.info("404: %s", request.path)
    return render_template("error.html", code=404, message="Страница не найдена"), 404


@errors_bp.app_errorhandler(500)
def server_error(e):
    logger.exception("500 at %s: %s", request.path, e)
    return render_template(
        "error.html", code=500, message="Внутренняя ошибка сервера"
    ), 500
