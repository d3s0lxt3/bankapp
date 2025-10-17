from functools import wraps
from flask import session, redirect, url_for, request, current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger("app")


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(hash_value: str, password: str) -> bool:
    return check_password_hash(hash_value, password)


def login_user(user_id: int):
    session.clear()
    session["user_id"] = user_id
    logger.info("User %s logged in (session set)", user_id)


def logout_user():
    session.clear()
    logger.info("Session cleared (logout)")


def current_user_id():
    return session.get("user_id")


def login_required(redirect_endpoint="auth.login"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                next_url = request.path
                logger.debug(
                    "Unauthorized access to %s, redirecting to login", next_url
                )
                return redirect(url_for(redirect_endpoint, next=next_url))
            return func(*args, **kwargs)

        return wrapper

    return decorator
