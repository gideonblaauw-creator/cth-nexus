import logging
import os
from urllib.parse import quote, unquote

from flask import (
    jsonify,
    make_response,
    redirect,
    request,
    send_from_directory,
)

from api.nexus_auth import nexus_auth_bp
from api.nexus_auth import email as auth_email
from api.nexus_auth import store

log = logging.getLogger("cth-nexus-auth")

_purged = store.purge_users_outside_domain()
if _purged:
    log.info("Purged %s non-@%s user(s) from nexus auth DB", _purged, store.ALLOWED_EMAIL_DOMAIN)
for _probe in ("probe-gate@cleantechhub.net",):
    if store.delete_user_by_email(_probe):
        log.info("Removed probe account %s", _probe)

COOKIE_NAME = "nexus_dir_session"
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "nexus-auth")

STAFF_EMAILS = {
    e.strip().lower()
    for e in os.environ.get("NEXUS_AUTH_STAFF_EMAILS", "gideon.blaauw@cleantechhub.net").split(",")
    if e.strip()
}
STAFF_TOKEN = os.environ.get("NEXUS_AUTH_STAFF_TOKEN", os.environ.get("CTH_ADMIN_KEY", ""))


def _staff_email_required():
    return jsonify({"error": "staff_email_required"}), 403


def _safe_next_path(raw: str | None) -> str:
    path = unquote(raw or "").strip()
    if not path.startswith("/"):
        path = "/" + path if path else "/investors"
    if path.startswith("//") or path.startswith("/nexus-auth"):
        return "/investors"
    if path in ("/", "/index.html"):
        return "/investors"
    if path == "/funders.html":
        return "/p/funders"
    if path.startswith("/data/") or path.startswith("/assets/"):
        return "/investors" + path
    return path


def _cookie_kwargs():
    secure = os.environ.get("NEXUS_AUTH_COOKIE_SECURE", "1") == "1"
    return {
        "httponly": True,
        "secure": secure,
        "samesite": "Lax",
        "path": "/",
        "max_age": store.SESSION_TTL,
    }


def _set_session_cookie(response, token: str):
    response.set_cookie(COOKIE_NAME, token, **_cookie_kwargs())
    return response


def _clear_session_cookie(response):
    response.set_cookie(COOKIE_NAME, "", expires=0, path="/")
    return response


def _current_user():
    token = request.cookies.get(COOKIE_NAME)
    row = store.get_session(token)
    if not row:
        return None
    if not store.is_allowed_email(row["email"]):
        store.delete_session(token)
        return None
    return {"id": row["user_id"], "email": row["email"], "name": row["name"]}


def _staff_bearer_ok() -> bool:
    if not STAFF_TOKEN:
        return False
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {STAFF_TOKEN}"


def _is_json_request() -> bool:
    uri = request.headers.get("X-Forwarded-Uri") or request.args.get("uri") or request.path
    accept = request.headers.get("Accept", "")
    return uri.endswith(".json") or "application/json" in accept


def _ensure_user(email: str, name: str | None = None):
    if not store.is_allowed_email(email):
        raise ValueError("staff_email_required")
    user = store.get_user_by_email(email)
    if user:
        return user["id"]
    display = (name or email.split("@")[0]).strip()
    return store.create_user(email, display, password=None)


@nexus_auth_bp.route("/nexus-auth/")
def gate_page():
    nxt = _safe_next_path(request.args.get("next"))
    user = _current_user()
    if user:
        return redirect(nxt)
    return send_from_directory(STATIC_DIR, "gate.html")


@nexus_auth_bp.route("/nexus-auth/check", methods=["GET", "HEAD"])
def auth_check():
    if _current_user() or _staff_bearer_ok():
        return "", 200

    if _is_json_request():
        return jsonify({"error": "authentication_required"}), 401

    nxt = _safe_next_path(
        request.headers.get("X-Forwarded-Uri") or request.args.get("next")
    )
    return redirect(f"/nexus-auth/?next={quote(nxt)}"), 302


@nexus_auth_bp.route("/nexus-auth/api/register", methods=["POST"])
def api_register():
    return jsonify({"error": "registration_disabled"}), 403


@nexus_auth_bp.route("/nexus-auth/api/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True, silent=True) or {}
    email = store.normalize_email(data.get("email", ""))
    password = data.get("password") or ""

    if not store.is_allowed_email(email):
        return _staff_email_required()

    user = store.get_user_by_email(email)
    if not user or not store.verify_password(password, user["password_hash"]):
        return jsonify({"error": "invalid_credentials"}), 401

    token = store.create_session(user["id"])
    resp = make_response(jsonify({"ok": True, "email": user["email"], "name": user["name"]}))
    return _set_session_cookie(resp, token)


@nexus_auth_bp.route("/nexus-auth/api/magic-link", methods=["POST"])
def api_magic_link():
    data = request.get_json(force=True, silent=True) or {}
    email = store.normalize_email(data.get("email", ""))
    name = (data.get("name") or "").strip()
    nxt = _safe_next_path(data.get("next"))

    if not email:
        return jsonify({"error": "email_required"}), 400
    if not store.is_allowed_email(email):
        return _staff_email_required()

    user = store.get_user_by_email(email)
    if not user:
        _ensure_user(email, name or email.split("@")[0])

    token = store.create_magic_token(email, name or None)
    try:
        auth_email.send_magic_link(email, token, nxt)
    except Exception:
        log.exception("Magic link email failed for %s", email)
        return jsonify({"error": "email_send_failed"}), 503

    return jsonify({"ok": True, "message": "magic_link_sent"})


@nexus_auth_bp.route("/nexus-auth/verify/<token>")
def verify_magic(token):
    row = store.consume_magic_token(token)
    if not row:
        return redirect("/nexus-auth/?error=invalid_or_expired")
    if not store.is_allowed_email(row["email"]):
        return redirect("/nexus-auth/?error=staff_email_required")

    user_id = _ensure_user(row["email"], row["name"])
    session_token = store.create_session(user_id)
    nxt = _safe_next_path(request.args.get("next"))
    resp = make_response(redirect(nxt))
    return _set_session_cookie(resp, session_token)


@nexus_auth_bp.route("/nexus-auth/api/logout", methods=["POST"])
def api_logout():
    store.delete_session(request.cookies.get(COOKIE_NAME))
    resp = make_response(jsonify({"ok": True}))
    return _clear_session_cookie(resp)


@nexus_auth_bp.route("/nexus-auth/api/me", methods=["GET"])
def api_me():
    if _staff_bearer_ok():
        return jsonify({"ok": True, "staff": True})
    user = _current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401
    return jsonify({"ok": True, **user})
