import os
import sqlite3
import secrets
import time
from contextlib import contextmanager

import bcrypt

DB_PATH = os.environ.get(
    "NEXUS_AUTH_DB",
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "nexus_auth.db"),
)

SESSION_TTL = int(os.environ.get("NEXUS_AUTH_SESSION_DAYS", "30")) * 86400
MAGIC_TTL = int(os.environ.get("NEXUS_AUTH_MAGIC_MINUTES", "20")) * 60
_DB_READY = False


def _ensure_db():
    global _DB_READY
    if _DB_READY:
        return
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            name TEXT NOT NULL,
            password_hash TEXT,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS magic_tokens (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL COLLATE NOCASE,
            name TEXT,
            expires_at INTEGER NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()
    _DB_READY = True


@contextmanager
def _connect():
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


ALLOWED_EMAIL_DOMAIN = os.environ.get(
    "NEXUS_AUTH_ALLOWED_DOMAIN", "cleantechhub.net"
).strip().lower().lstrip("@")


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def is_allowed_email(email: str) -> bool:
    email = normalize_email(email)
    if not email or "@" not in email:
        return False
    return email.rsplit("@", 1)[-1] == ALLOWED_EMAIL_DOMAIN


def delete_user_by_email(email: str) -> bool:
    email = normalize_email(email)
    with _connect() as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            return False
        user_id = row["id"]
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM magic_tokens WHERE email = ?", (email,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return True


def purge_users_outside_domain(domain: str | None = None) -> int:
    domain = (domain or ALLOWED_EMAIL_DOMAIN).strip().lower().lstrip("@")
    suffix = "@" + domain
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, email FROM users WHERE LOWER(email) NOT LIKE ?",
            (f"%{suffix}",),
        ).fetchall()
        if not rows:
            return 0
        ids = [row["id"] for row in rows]
        placeholders = ",".join("?" * len(ids))
        conn.execute(
            f"DELETE FROM sessions WHERE user_id IN ({placeholders})", ids
        )
        for row in rows:
            conn.execute(
                "DELETE FROM magic_tokens WHERE email = ?", (row["email"],)
            )
        conn.execute(
            f"DELETE FROM users WHERE id IN ({placeholders})", ids
        )
        return len(rows)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def get_user_by_email(email: str):
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (normalize_email(email),)
        ).fetchone()


def get_user_by_id(user_id: int):
    with _connect() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(email: str, name: str, password: str | None = None):
    email = normalize_email(email)
    name = (name or "").strip()
    if not email or not name:
        raise ValueError("email_and_name_required")
    pw_hash = hash_password(password) if password else None
    now = int(time.time())
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO users (email, name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email, name, pw_hash, now),
        )
        return cur.lastrowid


def set_password(user_id: int, password: str):
    pw_hash = hash_password(password)
    with _connect() as conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (pw_hash, user_id),
        )


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + SESSION_TTL
    with _connect() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires_at),
        )
    return token


def get_session(token: str | None):
    if not token:
        return None
    now = int(time.time())
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT s.token, s.expires_at, u.id AS user_id, u.email, u.name
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?
            """,
            (token, now),
        ).fetchone()
        return row


def delete_session(token: str | None):
    if not token:
        return
    with _connect() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def create_magic_token(email: str, name: str | None = None) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + MAGIC_TTL
    with _connect() as conn:
        conn.execute("DELETE FROM magic_tokens WHERE email = ?", (normalize_email(email),))
        conn.execute(
            "INSERT INTO magic_tokens (token, email, name, expires_at) VALUES (?, ?, ?, ?)",
            (token, normalize_email(email), (name or "").strip() or None, expires_at),
        )
    return token


def consume_magic_token(token: str):
    now = int(time.time())
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM magic_tokens WHERE token = ? AND expires_at > ?",
            (token, now),
        ).fetchone()
        if not row:
            return None
        conn.execute("DELETE FROM magic_tokens WHERE token = ?", (token,))
        return row
