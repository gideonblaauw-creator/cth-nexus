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
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_API_KEY, {})
    if not uid:
        raise RuntimeError("Odoo authentication failed — check ODOO_USER and ODOO_PASSWORD (API key)")
    _uid_cache = uid
    log.info("Odoo authenticated as uid=%s", uid)
    return uid


def _execute(model: str, method: str, *args, **kwargs):
    uid = _get_uid()
    obj = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return obj.execute_kw(ODOO_DB, uid, ODOO_API_KEY, model, method, list(args), kwargs)


def _get_or_create_tag(name: str) -> int:
    existing = _execute("res.partner.category", "search_read",
                        [["name", "=", name]], fields=["id"], limit=1)
    if existing:
        return existing[0]["id"]
    return _execute("res.partner.category", "create", {"name": name})


PROGRAM_TAG_MAP = {
    "CLP": "CLP",
    "DPS": "DPS",
    "PDET": "PDET",
}


def _infer_program_tag(programs_str: str) -> int | None:
    if not programs_str:
        return None
    for key, tag_name in PROGRAM_TAG_MAP.items():
        if key.lower() in programs_str.lower():
            try:
                return _get_or_create_tag(tag_name)
            except Exception:
                log.warning("Could not create program tag %s", tag_name)
                return None
    return None


def upsert_mentor(data: dict) -> int:
    if not ODOO_URL:
        raise RuntimeError("ODOO_BASE_URL not configured")

    email = data["email"]
    log.info("Upserting mentor %s in Odoo", email)

    existing = _execute("res.partner", "search_read",
                        [["email", "=", email]], fields=["id"], limit=1)

    mentor_tag_id = _get_or_create_tag("Mentor")
    program_tag_id = _infer_program_tag(data.get("programs", ""))

    values = {
        "name": data.get("name", ""),
        "email": email,
        "phone": data.get("phone", ""),
        "function": data.get("role", ""),
        "company_name": data.get("company", ""),
        "website": data.get("linkedin", ""),
        "category_id": [(4, mentor_tag_id)],
    }
    if program_tag_id:
        values["category_id"].append((4, program_tag_id))

    if existing:
        partner_id = existing[0]["id"]
        _execute("res.partner", "write", [partner_id], values)
        log.info("Updated existing partner %s", partner_id)
    else:
        # Workaround: res.partner.create() is broken via XML-RPC in this
        # Odoo 18 instance (custom module strips @api.model_create_multi).
        # Use name_create (which has @api.model) then write the rest.
        result = _execute("res.partner", "name_create", data.get("name", email))
        partner_id = result[0]
        _execute("res.partner", "write", [partner_id], values)
        log.info("Created new partner %s via name_create+write", partner_id)

    try:
        _execute("mail.message", "create", {
            "model": "res.partner",
            "res_id": partner_id,
            "body": f"Mentor onboarding form submitted. Source: {data.get('source', 'webhook')}",
            "message_type": "comment",
            "subtype_xmlid": "mail.mt_note",
        })
    except Exception:
        log.warning("Could not create chatter message for partner %s", partner_id)

    return partner_id


def upsert_clp26_mentor(data: dict) -> int:
    if not ODOO_URL:
        raise RuntimeError("ODOO_BASE_URL not configured")

    email = data["email"]
    log.info("Upserting CLP26 mentor %s in Odoo", email)

    existing = _execute("res.partner", "search_read",
                        [["email", "=", email]], fields=["id"], limit=1)

    mentor_tag_id = _get_or_create_tag("Mentor")
    clp26_tag_id = _get_or_create_tag("CLP26 Mentor")
    pending_tag_id = _get_or_create_tag("CLP26-Pending")

    module_tags = []
    for mod_num in data.get("modules", []):
        tag_id = _get_or_create_tag(f"CLP26-M{mod_num}")
        module_tags.append((4, tag_id))

    category_ids = [(4, mentor_tag_id), (4, clp26_tag_id), (4, pending_tag_id)] + module_tags

    if data.get("whatsapp_consent"):
        wa_tag_id = _get_or_create_tag("WhatsApp-OK")
        category_ids.append((4, wa_tag_id))

    modules_str = ", ".join(str(m) for m in data.get("modules", []))

    values = {
        "name": data.get("name", ""),
        "email": email,
        "phone": data.get("phone", ""),
        "mobile": data.get("whatsapp", "") or data.get("phone", ""),
        "function": data.get("role", ""),
        "company_name": data.get("company", ""),
        "website": data.get("linkedin", ""),
        "comment": f"CLP26 Mentor | Modules: {modules_str} | Availability: {data.get('availability', '')}",
        "category_id": category_ids,
    }

    if existing:
        partner_id = existing[0]["id"]
        _execute("res.partner", "write", [partner_id], values)
        log.info("Updated existing CLP26 mentor partner %s", partner_id)
    else:
        result = _execute("res.partner", "name_create", data.get("name", email))
        partner_id = result[0]
        _execute("res.partner", "write", [partner_id], values)
        log.info("Created new CLP26 mentor partner %s via name_create+write", partner_id)

    try:
        _execute("mail.message", "create", {
            "model": "res.partner",
            "res_id": partner_id,
            "body": (
                f"CLP26 Mentor registration via mentoring platform.<br/>"
                f"Modules: {modules_str}<br/>"
                f"Availability: {data.get('availability', 'N/A')}<br/>"
                f"WhatsApp consent: {'Yes' if data.get('whatsapp_consent') else 'No'}<br/>"
                f"Source: {data.get('source', 'mentoring-platform')}"
            ),
            "message_type": "comment",
            "subtype_xmlid": "mail.mt_note",
        })
    except Exception:
        log.warning("Could not create chatter message for partner %s", partner_id)

    return partner_id


def get_pending_clp26_mentors():
    if not ODOO_URL:
        return []
    pending_tag = _execute("res.partner.category", "search_read",
                           [["name", "=", "CLP26-Pending"]], fields=["id"], limit=1)
    if not pending_tag:
        return []
    tag_id = pending_tag[0]["id"]
    partners = _execute("res.partner", "search_read",
                        [["category_id", "in", [tag_id]]],
                        fields=["id", "name", "email", "phone", "mobile",
                                "company_name", "function", "comment",
                                "category_id", "create_date"])
    return partners


def approve_clp26_mentor(partner_id: int) -> bool:
    if not ODOO_URL:
        raise RuntimeError("ODOO_BASE_URL not configured")

    pending_tag = _execute("res.partner.category", "search_read",
                           [["name", "=", "CLP26-Pending"]], fields=["id"], limit=1)
    approved_tag_id = _get_or_create_tag("CLP26-Approved")

    category_updates = [(4, approved_tag_id)]
    if pending_tag:
        category_updates.append((3, pending_tag[0]["id"]))

    _execute("res.partner", "write", [partner_id], {
        "category_id": category_updates,
    })

    try:
        _execute("mail.message", "create", {
            "model": "res.partner",
            "res_id": partner_id,
            "body": "CLP26 Mentor approved by hub manager.",
            "message_type": "comment",
            "subtype_xmlid": "mail.mt_note",
        })
    except Exception:
        log.warning("Could not log approval for partner %s", partner_id)

    log.info("Approved CLP26 mentor partner %s", partner_id)
    return True


def reject_clp26_mentor(partner_id: int) -> bool:
    if not ODOO_URL:
        raise RuntimeError("ODOO_BASE_URL not configured")

    pending_tag = _execute("res.partner.category", "search_read",
                           [["name", "=", "CLP26-Pending"]], fields=["id"], limit=1)
    rejected_tag_id = _get_or_create_tag("CLP26-Rejected")

    category_updates = [(4, rejected_tag_id)]
    if pending_tag:
        category_updates.append((3, pending_tag[0]["id"]))

    _execute("res.partner", "write", [partner_id], {
        "category_id": category_updates,
    })
    log.info("Rejected CLP26 mentor partner %s", partner_id)
    return True
