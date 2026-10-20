from flask import Blueprint

mentoring_bp = Blueprint(
    "mentoring",
    __name__,
    static_folder="../../static/mentoring",
    static_url_path="/mentoring/static",
)

from api.mentoring import routes  # noqa: E402, F401
