from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from core.utils import contains_ssti_markers
from core.audit import record
from core.database import get_db_session
from core.models import CardRequest, Card
from datetime import date, timedelta
from random import randint
import json

cards_bp = Blueprint("cards", __name__, template_folder="../templates")


def fake_stacktrace(payload):
    snippet = (payload or "")[:200].replace("\n", "\\n")
    trace = [
        "Traceback (most recent call last):",
        '  File "/opt/bankapp/app.py", line 123, in render_template_safe',
        f'    render("{snippet}...")',
        "TemplateError: Failed to render template at user input (simulated)",
    ]
    return "\n".join(trace)


def generate_card_number():
    return "".join(str(randint(0, 9)) for _ in range(16))


def generate_cvv():
    return "".join(str(randint(0, 9)) for _ in range(3))


def generate_expiry_date():
    return date.today() + timedelta(days=365 * 3)


@cards_bp.route("/", methods=["GET"])
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    with get_db_session() as db:
        cards = db.query(Card).filter_by(user_id=user_id).all()

    return render_template("cards.html", cards=cards)


@cards_bp.route("/apply", methods=["GET", "POST"])
def apply():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template("apply_card.html")

    fio = request.form.get("fio", "")
    phone = request.form.get("phone", "")
    comments = request.form.get("comments", "")
    card_type = request.form.get("type", "Visa Classic")
    client_ip = request.remote_addr

    if contains_ssti_markers(fio) or contains_ssti_markers(comments):
        trace = fake_stacktrace(fio if contains_ssti_markers(fio) else comments)
        record(
            "ssti_detected",
            source_ip=client_ip,
            details={"payload": (fio or comments)[:512]},
            level="WARN",
        )
        current_app.logger.warning(
            json.dumps(
                {
                    "event": "ssti_detected",
                    "source_ip": client_ip,
                    "payload_snippet": (fio or comments)[:512],
                },
                ensure_ascii=False,
            )
        )
        return render_template("apply_card.html", alert=True, sstiex=trace), 400

    with get_db_session() as db:
        cr = CardRequest(
            user_id=user_id,
            fio=fio[:400],
            phone=phone[:80],
            comments=comments[:2000],
            status="submitted",
        )
        db.add(cr)
        db.commit()
        record(
            "card_request_submitted",
            source_ip=client_ip,
            details={"id": cr.id, "fio": fio[:80]},
        )

        new_card = Card(
            user_id=user_id,
            card_type=card_type,
            card_number=generate_card_number(),
            cvv=generate_cvv(),
            expiry_date=generate_expiry_date(),
            balance=0.0,
        )
        db.add(new_card)
        db.commit()

    return render_template("apply_card.html", success=True), 200
