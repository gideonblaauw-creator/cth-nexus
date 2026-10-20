import os
import logging

import requests

MOODLE_URL = os.environ.get("MOODLE_BASE_URL", "")
MOODLE_TOKEN = os.environ.get("MOODLE_WS_TOKEN", "")
COURSE_ID = int(os.environ.get("MOODLE_MENTOR_COURSE_ID", "0"))
STUDENT_ROLE = 5

log = logging.getLogger("cth-mentor-api.moodle")


def _call(function: str, params: dict) -> dict:
    params.update({
        "wstoken": MOODLE_TOKEN,
        "wsfunction": function,
        "moodlewsrestformat": "json",
    })
    r = requests.post(f"{MOODLE_URL}/webservice/rest/server.php", data=params, timeout=15)
    r.raise_for_status()
    result = r.json()
    if isinstance(result, dict) and result.get("exception"):
        raise RuntimeError(f"Moodle error: {result.get('message')}")
    return result


def _get_user_by_email(email: str) -> int | None:
    result = _call("core_user_get_users", {
        "criteria[0][key]": "email",
        "criteria[0][value]": email,
    })
    users = result.get("users", [])
    return users[0]["id"] if users else None


def create_and_enroll(data: dict, username: str | None = None) -> int:
    if not MOODLE_URL or not MOODLE_TOKEN:
        raise RuntimeError("Moodle not configured (MOODLE_BASE_URL / MOODLE_WS_TOKEN)")

    email = data["email"]
    user_id = _get_user_by_email(email)

    if not user_id:
        name_parts = data.get("name", "").split(None, 1)
        result = _call("core_user_create_users", {
            "users[0][username]": username or email.split("@")[0],
            "users[0][password]": "ChangeMe123!",
            "users[0][firstname]": name_parts[0] if name_parts else "",
            "users[0][lastname]": name_parts[1] if len(name_parts) > 1 else "",
            "users[0][email]": email,
            "users[0][auth]": "manual",
        })
        user_id = result[0]["id"]
        log.info("Created Moodle user %s (id=%s)", username, user_id)

    if COURSE_ID:
        _call("enrol_manual_enrol_users", {
            "enrolments[0][roleid]": STUDENT_ROLE,
            "enrolments[0][userid]": user_id,
            "enrolments[0][courseid]": COURSE_ID,
        })
        log.info("Enrolled user %s in course %s", user_id, COURSE_ID)

    return user_id
