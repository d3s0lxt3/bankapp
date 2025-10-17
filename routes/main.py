from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from core.database import get_db_session
from core.models import User, CardRequest, AuditLog, Card
from core.audit import record
from core.security import login_required, current_user_id
from flask import render_template_string
import random, string, datetime

main_bp = Blueprint("main", __name__, template_folder="../templates")

@main_bp.route("/")
def index():
    return render_template("home.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "GET":
        return render_template("support.html")
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    category = request.form.get("category", "")
    message = request.form.get("message", "")
    record(
        "support_request",
        source_ip=request.remote_addr,
        user=email,
        details={"name": name, "category": category, "message": message},
    )
    return render_template(
        "support.html", message="Ваш запрос отправлен. Мы ответим по email."
    )


@main_bp.route("/dashboard")
def dashboard():
    uid = current_user_id()
    if not uid:
        return redirect(url_for("auth.login"))
    with get_db_session() as db:
        user = db.query(User).filter(User.id == uid).first()
        account = {
            "number": f"40817{100000000 + uid}",
            "balance": 0.00,
        }
        audits = (
            db.query(AuditLog)
            .filter(AuditLog.event.like("tx_%"))
            .order_by(AuditLog.ts.desc())
            .limit(8)
            .all()
        )
        recent = []
        for a in audits:
            details = a.details if isinstance(a.details, str) else str(a.details)
            recent.append(
                {
                    "timestamp": a.ts,
                    "description": a.event,
                    "amount": float(a.details.get("amount"))
                    if isinstance(a.details, dict) and a.details.get("amount")
                    else 0.0,
                    "status": "completed",
                }
            )
    return render_template(
        "dashboard.html", user=user, account=account, transactions=recent
    )


@main_bp.route("/transactions")
def transactions():
    uid = current_user_id()
    if not uid:
        return redirect(url_for("auth.login"))
    with get_db_session() as db:
        audits = (
            db.query(AuditLog)
            .filter(AuditLog.event.like("tx_%"))
            .order_by(AuditLog.ts.desc())
            .limit(200)
            .all()
        )
        txs = []
        for a in audits:
            details = a.details if isinstance(a.details, dict) else {}
            txs.append(
                {
                    "timestamp": a.ts,
                    "type": details.get("type", "debit"),
                    "counterparty": details.get("counterparty", "-"),
                    "amount": float(details.get("amount", 0)),
                    "comment": details.get("comment", ""),
                    "status": "completed",
                }
            )
    return render_template("transactions.html", transactions=txs)


@main_bp.route("/transfer", methods=["GET", "POST"])
def transfer():
    uid = current_user_id()
    if not uid:
        return redirect(url_for("auth.login"))
    if request.method == "GET":
        return render_template("transfer.html")
    recipient = request.form.get("recipient", "").strip()
    amount_raw = request.form.get("amount", "0").strip()
    comment = request.form.get("comment", "")
    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError()
    except Exception:
        return render_template("transfer.html", error="Неверная сумма")
    record(
        "tx_outgoing",
        source_ip=request.remote_addr,
        user=str(uid),
        details={
            "amount": amount,
            "counterparty": recipient,
            "comment": comment,
            "type": "debit",
        },
    )
    record(
        "tx_incoming",
        source_ip="internal",
        user=recipient,
        details={
            "amount": amount,
            "counterparty": f"user:{uid}",
            "comment": comment,
            "type": "credit",
        },
    )
    return render_template("transfer.html", success=True, message="Перевод отправлен")

@main_bp.route("/profile")
def profile():
    uid = current_user_id()
    if not uid:
        return redirect(url_for("auth.login"))
    with get_db_session() as db:
        user = db.query(User).filter(User.id == uid).first()
    return render_template("profile.html", user=user)

@main_bp.route("/apply_card", methods=["GET", "POST"])
@login_required()
def apply_card():
    uid = current_user_id()
    if not uid:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        holder = request.form.get("holder", "")
        card_type = request.form.get("type", "")
        phone = request.form.get("phone", "")
        comments = request.form.get("comments", "")

        template = f"""
        {{% extends "base.html" %}}
        {{% block title %}}Заявка на карту{{% endblock %}}
        {{% block content %}}
        <h2>Заявка на выпуск карты</h2>
        
        <div style="border:1px solid #0c0; background:#dfd; padding:10px;">
            Заявка принята для: {holder}
            <br>Статус: одобрено
            <br>Обработано: {{{{ now }}}}
        </div>
        
        <br>
        <a href="{{{{ url_for('main.apply_card') }}}}">Вернуться</a>
        {{% endblock %}}
        """
        
        return render_template_string(template, now=datetime.datetime.now())

    return render_template("apply_card.html")

@main_bp.route("/cards")
@login_required()
def cards():
    user_id = current_user_id()
    with get_db_session() as db:
        cards = db.query(Card).filter(Card.user_id == user_id).all()
        card_list = [
            {
                "type": c.card_type,
                "number": c.card_number,
                "holder": c.user.fullname or c.user.username,
                "cvv": c.cvv,
                "expiry": c.expiry_date.strftime("%m/%Y"),
                "balance": c.balance,
            }
            for c in cards
        ]
    return render_template("cards.html", cards=card_list)
