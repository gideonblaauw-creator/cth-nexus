"""
Odoo 18 handler — uses XML-RPC for API key authentication.
API keys authenticate via xmlrpc/2/common and execute via xmlrpc/2/object.
"""
import os
import logging
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_BASE_URL", "")
ODOO_DB = os.environ.get("ODOO_DB", "")
ODOO_USER = os.environ.get("ODOO_USER", "")
ODOO_API_KEY = os.environ.get("ODOO_PASSWORD", "")  # API key used as password

log = logging.getLogger("cth-mentor-api.odoo")

_uid_cache = None


def _get_uid() -> int:
    global _uid_cache
    if _uid_cache:
        return _uid_cache
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USER, OODOO_API_KEY, {})
    if not uid:
        raise RuntimeError("Odoo authentication failed — check ODOO_USER and ODOO_PASSWORD (API key)")
    _uid_cache = uid
    log.info("Odoo authenticated as uid=%s", uid)
    return uid


def _execute(model: str, method: str, *args, **kwargs):
    uid = _get_uid()
    obj = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return obj.execute_kw(ODOO_DB, uid, OODOO_API_KEY, model, method, list(args), kwargs)
