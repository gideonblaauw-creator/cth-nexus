import hashlib
import json
import uuid

from app.database import get_provenance_db


def append_ledger(event_type: str, actor_did: str, details: dict, subject_did: str = None) -> str:
    entry_id = str(uuid.uuid4())
    with get_provenance_db() as conn:
        prev = conn.execute(
            "SELECT entry_hash FROM governance_ledger ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        prev_hash = prev["entry_hash"] if prev else "GENESIS"

        detail_str = json.dumps(details, sort_keys=True)
        raw = f"{entry_id}{event_type}{actor_did}{detail_str}{prev_hash}"
        entry_hash = hashlib.sha256(raw.encode()).hexdigest()

        conn.execute(
            """INSERT INTO governance_ledger
               (id, event_type, actor_did, subject_did, details, prev_hash, entry_hash)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (entry_id, event_type, actor_did, subject_did, detail_str, prev_hash, entry_hash),
        )
        conn.commit()
    return entry_hash
