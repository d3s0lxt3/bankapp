from flask import render_template, jsonify, request
import logging

logger = logging.getLogger("app")


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(
            "400 Bad Request: %s - %s", request.path, getattr(e, "description", "")
        )
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify(error="Bad Request"), 400
        return render_template("error.html", code=400, message="Bad request"), 400

    @app.errorhandler(403)
    def forbidden(e):
        logger.warning(
            "403 Forbidden: %s - %s", request.path, getattr(e, "description", "")
        )
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify(error="Forbidden"), 403
        return render_template("error.html", code=403, message="Forbidden"), 403

    @app.errorhandler(404)
    def not_found(e):
        logger.info("404 Not Found: %s", request.path)
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify(error="Not Found"), 404
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("500 Internal Server Error at %s: %s", request.path, e)
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify(error="Internal Server Error"), 500
        return render_template(
            "error.html", code=500, message="Internal server error"
        ), 500
