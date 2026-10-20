import os
import hmac
import hashlib
import logging

from flask import Flask, request, jsonify
from api.handlers import odoo, humhub, moodle, email_sender
from api.mentoring import mentoring_bp
from api.nexus_auth import nexus_auth_bp

app = Flask(__name__)
app.register_blueprint(mentoring_bp)
app.register_blueprint(nexus_auth_bp)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("cth-mentor-api")


def verify_signature(payload_bytes, sig_header):
    if not WEBHOOK_SECRET:
        return True
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header or "")


@app.route("/mentor-api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/mentor-api/onboard", methods=["POST"])
def onboard():
    raw = request.get_data()
    sig = request.headers.get("X-CTH-Signature", "")
    if not verify_signature(raw, sig):
        return jsonify({"error": "invalid_signature"}), 403

    data = request.get_json(force=True)
    log.info("Onboard request for %s", data.get("email", "unknown"))

    if data.get("habeas_data", "").lower() not in ("acepto", "yes", "si", "sí"):
        return jsonify({"error": "habeas_data_not_accepted"}), 400

    results = {}
    errors = []

    # 1. Odoo upsert
    try:
        partner_id = odoo.upsert_mentor(data)
        results["odoo_partner_id"] = partner_id
    except Exception as e:
        log.exception("Odoo failed")
        errors.append({"step": "odoo", "error": str(e)})

    # 2. HumHub profile
    try:
        hh = humhub.create_or_update_user(data)
        results["humhub_user_id"] = hh["user_id"]
        results["nexus_username"] = hh["username"]
        results["nexus_temp_password"] = hh["temp_password"]
    except Exception as e:
        log.exception("HumHub failed")
        errors.append({"step": "humhub", "error": str(e)})

    # 3. Moodle enrollment
    try:
        moodle_id = moodle.create_and_enroll(data, results.get("nexus_username"))
        results["moodle_user_id"] = moodle_id
    except Exception as e:
        log.exception("Moodle failed")
        errors.append({"step": "moodle", "error": str(e)})

    # 4. Welcome email (only if HumHub succeeded)
    if "nexus_username" in results:
        try:
            email_sender.send_welcome(data, results)
            results["email_sent"] = True
        except Exception as e:
            log.exception("Email failed")
            errors.append({"step": "email", "error": str(e)})

    status_code = 200 if not errors else 207
    return jsonify({"results": results, "errors": errors}), status_code


@app.route("/mentor-api/claim", methods=["POST"])
def claim():
    return onboard()
