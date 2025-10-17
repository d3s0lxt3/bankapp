from flask import Blueprint, render_template, request, abort, redirect, url_for
from core.database import get_db_session
from core.models import AuditLog, User
from core.audit import record

admin_bp = Blueprint("admin", __name__, template_folder="../templates")


def require_admin():
    return True


@admin_bp.route("/", methods=["GET"])
def panel():
    if not require_admin():
        abort(403)
    with get_db_session() as db:
        audits = db.query(AuditLog).order_by(AuditLog.ts.desc()).limit(200).all()
    return render_template("admin_panel.html", audits=audits)


@admin_bp.route("/search", methods=["POST"])
def search():
    if not require_admin():
        abort(403)
    q = request.form.get("q", "").strip()
    with get_db_session() as db:
        audits = (
            db.query(AuditLog)
            .filter(AuditLog.event.ilike(f"%{q}%"))
            .order_by(AuditLog.ts.desc())
            .limit(200)
            .all()
        )
    return render_template("admin_panel.html", audits=audits)


@admin_bp.route("/rebuild_index")
def rebuild_index():
    if not require_admin():
        abort(403)
    record(
        "admin_rebuild_index",
        source_ip=request.remote_addr,
        user="admin",
        details={"action": "rebuild_index"},
    )
    return redirect(url_for("admin.panel"))
