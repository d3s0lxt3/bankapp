from flask import Blueprint, jsonify, request, session
from core.database import get_db_session
from core.models import AuditLog, User
from core.audit import record
from core.security import current_user_id

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _fake_balance_for_user(uid: int) -> float:
    base = 10000.0
    return base + ((uid * 137) % 5000)


def _fake_transactions_for_user(uid: int, count: int = 10):
    result = []
    for i in range(count):
        amount = ((i + 1) * 123.45) % 2000
        if i % 2 == 0:
            amount = -amount
            ttype = "debit"
            cp = "магазин.example"
        else:
            ttype = "credit"
            cp = "перечисление"
        result.append(
            {
                "id": i + 1,
                "date": None,
                "type": ttype,
                "amount": round(amount, 2),
                "status": "completed",
                "counterparty": cp,
                "comment": "",
            }
        )
    return result


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "bankline api"}), 200


@api_bp.route("/balance", methods=["GET"])
def balance():
    uid = current_user_id()
    if not uid:
        return jsonify({"error": "not_authenticated"}), 401
    bal = _fake_balance_for_user(int(uid))
    return jsonify({"balance": round(bal, 2)}), 200


@api_bp.route("/transactions", methods=["GET"])
def transactions():
    uid = current_user_id()
    if not uid:
        return jsonify({"error": "not_authenticated"}), 401
    txs = _fake_transactions_for_user(int(uid), count=12)
    return jsonify(txs), 200


@api_bp.route("/transfer", methods=["POST"])
def api_transfer():
    uid = current_user_id()
    if not uid:
        return jsonify({"error": "not_authenticated"}), 401
    body = request.get_json(silent=True) or {}
    amount = float(body.get("amount", 0))
    target = body.get("target", "")
    comment = body.get("comment", "")
    if amount <= 0 or not target:
        return jsonify({"error": "invalid_request"}), 400
    record(
        "tx_outgoing_api",
        source_ip=request.remote_addr,
        user=str(uid),
        details={"amount": amount, "counterparty": target, "comment": comment},
    )
    return jsonify({"status": "ok", "amount": amount, "target": target}), 201


@api_bp.route("/users", methods=["GET"])
def api_list_users():
    with get_db_session() as db:
        users = db.query(User).limit(50).all()
        out = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    record("api_users_list", source_ip=request.remote_addr, details={"count": len(out)})
    return jsonify(out), 200
