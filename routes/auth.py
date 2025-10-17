from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
)
from core.database import get_db_session
from core.models import User
from core.security import hash_password, verify_password, login_user, logout_user
from core.audit import record

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    with get_db_session() as db:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(user.password_hash, password):
            login_user(user.id)
            record(
                "login_succeeded",
                source_ip=request.remote_addr,
                user=username,
                details="login ok",
            )
            return redirect(url_for("main.index"))
    record(
        "login_failed",
        source_ip=request.remote_addr,
        user=username,
        details="invalid credentials",
    )
    return render_template("login.html", error="Неверный логин или пароль")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    if not username or not email or not password:
        return render_template("register.html", error="Заполните все поля")

    if password != confirm:
        return render_template("register.html", error="Пароли не совпадают")

    with get_db_session() as db:
        if (
            db.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        ):
            return render_template(
                "register.html",
                error="Пользователь с таким именем или email уже существует",
            )

        user = User(username=username, email=email, fullname=username)
        user.password_hash = hash_password(password)
        db.add(user)
        db.commit()
        record(
            "user_registered",
            source_ip=request.remote_addr,
            user=username,
            details={"email": email},
        )
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    user_id = session.get("user_id")
    logout_user()
    record("logout", source_ip=request.remote_addr, user=str(user_id))
    return redirect(url_for("main.index"))
