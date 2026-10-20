from flask import Blueprint

nexus_auth_bp = Blueprint(
    "nexus_auth",
    __name__,
    static_folder="../../static/nexus-auth",
    static_url_path="/nexus-auth/static",
)

from api.nexus_auth import routes  # noqa: E402, F401
