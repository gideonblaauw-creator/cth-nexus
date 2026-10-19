import os
import hmac
import hashlib
import logging

from flask import jsonify, send_from_directory, request

from api.mentoring import mentoring_bp
from api.mentoring.models import MODULES
from api.mentoring import bookstack_service
from api.handlers import odoo, humhub, email_sender

log = logging.getLogger("cth-mentor-api.mentoring")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "mentoring")
ADMIN_KEY = os.environ.get("CTH_ADMIN_KEY", "")


@mentoring_bp.route("/mentoring/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@mentoring_bp.route("/mentoring/api/startups")
def api_startups():
    country = request.args.get("country")
    module = request.args.get("module", type=int)

    startups = bookstack_service.get_selected_startups()
    result = [s.to_dict() for s in startups]

    if country and country != "all":
        result = [s for s in result if s["country"] == country]
    if module:
        result = [s for s in result if module in s["needs_mentor"]]

    return jsonify(result)


@mentoring_bp.route("/mentoring/api/startups/<int:page_id>")
def api_startup_detail(page_id):
    startup = bookstack_service.get_startup_detail(page_id)
    if not startup:
        return jsonify({"error": "not_found"}), 404
    return jsonify(startup.to_dict())


@mentoring_bp.route("/mentoring/api/modules")
def api_modules():
    return jsonify(MODULES)


@mentoring_bp.route("/mentoring/api/modules/<int:number>/homework")
def api_homework(number):
    if number < 1 or number > 8:
        return jsonify({"error": "invalid_module"}), 400
    hw = bookstack_service.get_homework(number)
    if not hw:
        return jsonify({"error": "not_available", "message": "Workbook content coming soon"}), 404
    return jsonify(hw)


@mentoring_bp.route("/mentoring/api/mentors")
def api_mentors():
    return jsonify([])


# ── Registration ─────────────────────────────────────────

@mentoring_bp.route("/mentoring/api/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True)

    required = ["name", "email", "company", "modules"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400

    if not data.get("consent"):
        return jsonify({"error": "consent_required"}), 400

    modules = data.get("modules", [])
    if not isinstance(modules, list) or not modules:
        return jsonify({"error": "at_least_one_module_required"}), 400
    for m in modules:
        if not isinstance(m, int) or m < 1 or m > 8:
            return jsonify({"error": "invalid_module", "value": m}), 400

    reg_data = {
        "name": data["name"].strip(),
        "email": data["email"].strip().lower(),
        "company": data["company"].strip(),
        "role": data.get("role", "").strip(),
        "phone": data.get("whatsapp", "").strip(),
        "whatsapp": data.get("whatsapp", "").strip(),
        "whatsapp_consent": bool(data.get("whatsapp") and data.get("consent")),
        "modules": modules,
        "availability": data.get("availability", ""),
        "linkedin": data.get("linkedin", ""),
        "source": "mentoring-platform",
    }

    results = {}
    errors = []

    try:
        partner_id = odoo.upsert_clp26_mentor(reg_data)
        results["odoo_partner_id"] = partner_id
    except Exception as e:
        log.exception("Odoo registration failed for %s", reg_data["email"])
        errors.append({"step": "odoo", "error": str(e)})

    try:
        hh_data = {
            "name": reg_data["name"],
            "email": reg_data["email"],
            "role": reg_data.get("role", ""),
            "phone": reg_data.get("whatsapp", ""),
            "linkedin": reg_data.get("linkedin", ""),
            "bio": f"CLP26 Mentor | {reg_data['company']}",
        }
        hh = humhub.create_or_update_user(hh_data)
        results["humhub_user_id"] = hh["user_id"]
        results["nexus_username"] = hh["username"]
    except Exception as e:
        log.exception("HumHub registration failed for %s", reg_data["email"])
        errors.append({"step": "humhub", "error": str(e)})

    status_code = 201 if not errors else 207
    return jsonify({
        "status": "pending_approval",
        "message": "Tu registro fue recibido y está pendiente de aprobación por el hub manager.",
        "results": results,
        "errors": errors,
    }), status_code


# ── Admin approval ───────────────────────────────────────

def _check_admin():
    if not ADMIN_KEY:
        return False
    key = request.headers.get("X-CTH-Admin-Key", "")
    return hmac.compare_digest(key, ADMIN_KEY)


@mentoring_bp.route("/mentoring/admin/")
def admin_index():
    return send_from_directory(STATIC_DIR, "admin.html")


@mentoring_bp.route("/mentoring/api/admin/pending")
def api_admin_pending():
    if not _check_admin():
        return jsonify({"error": "unauthorized"}), 401
    try:
        pending = odoo.get_pending_clp26_mentors()
        return jsonify(pending)
    except Exception as e:
        log.exception("Failed to fetch pending mentors")
        return jsonify({"error": str(e)}), 500


@mentoring_bp.route("/mentoring/api/admin/approve/<int:partner_id>", methods=["POST"])
def api_admin_approve(partner_id):
    if not _check_admin():
        return jsonify({"error": "unauthorized"}), 401
    try:
        odoo.approve_clp26_mentor(partner_id)
        return jsonify({"status": "approved", "partner_id": partner_id})
    except Exception as e:
        log.exception("Failed to approve partner %s", partner_id)
        return jsonify({"error": str(e)}), 500


@mentoring_bp.route("/mentoring/api/admin/reject/<int:partner_id>", methods=["POST"])
def api_admin_reject(partner_id):
    if not _check_admin():
        return jsonify({"error": "unauthorized"}), 401
    try:
        odoo.reject_clp26_mentor(partner_id)
        return jsonify({"status": "rejected", "partner_id": partner_id})
    except Exception as e:
        log.exception("Failed to reject partner %s", partner_id)
        return jsonify({"error": str(e)}), 500
