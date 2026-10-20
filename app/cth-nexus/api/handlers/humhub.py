"""
HumHub handler — direct database approach.
The REST API module has broken route registration in the Docker container,
so we create users directly in MariaDB (exposed at HUMHUB_DB_HOST:HUMHUB_DB_PORT).
"""
import os
import uuid
import secrets
import string
import unicodedata
import logging
from datetime import datetime

import pymysql

HUMHUB_DB_HOST = os.environ.get("HUMHUB_DB_HOST", "127.0.0.1")
HUMHUB_DB_PORT = int(os.environ.get("HUMHUB_DB_PORT", "3307"))
HUMHUB_DB_NAME = os.environ.get("HUMHUB_DB_NAME", "humhub")
HUMHUB_DB_USER = os.environ.get("HUMHUB_DB_USER", "humhub")
HUMHUB_DB_PASS = os.environ.get("HUMHUB_DB_PASS", "")
SPACE_ID = int(os.environ.get("HUMHUB_MENTORS_SPACE_ID", "0"))

log = logging.getLogger("cth-mentor-api.humhub")


def _connect():
    return pymysql.connect(
        host=HUMHUB_DB_HOST,
        port=HUMHUB_DB_PORT,
        user=HUMHUB_DB_USER,
        password=HUMHUB_DB_PASS,
        database=HUMHUB_DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def _gen_password(length=12):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def _hash_password(plain: str) -> str:
    import bcrypt
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    parts = name.lower().split()
    if len(parts) > 1:
        return f"{parts[0]}.{parts[-1]}"
    return parts[0] if parts else "user"


def _split_name(full_name: str):
    parts = full_name.strip().split(None, 1)
    firstname = parts[0] if parts else ""
    lastname = parts[1] if len(parts) > 1 else ""
    return firstname, lastname


def _unique_username(conn, base: str) -> str:
    username = base
    with conn.cursor() as cur:
        for i in range(2, 100):
            cur.execute("SELECT id FROM user WHERE username = %s", (username,))
            if not cur.fetchone():
                return username
            username = f"{base}{i}"
    raise RuntimeError("Could not generate unique username")


def create_or_update_user(data: dict) -> dict:
    if not HUMHUB_DB_PASS:
        raise RuntimeError("HumHub DB not configured (HUMHUB_DB_PASS)")

    email = data["email"].lower()
    conn = _connect()
    try:
        with conn.cursor() as cur:
            # Check if user exists by email
            cur.execute("SELECT id, username, contentcontainer_id FROM user WHERE email = %s", (email,))
            existing = cur.fetchone()

        temp_password = _gen_password()
        firstname, lastname = _split_name(data.get("name", ""))

        if existing:
            user_id = existing["id"]
            username = existing["username"]
            log.info("Updating existing HumHub user %s (id=%s)", username, user_id)

            with conn.cursor() as cur:
                # Update profile
                cur.execute("""
                    UPDATE profile SET
                        firstname = %s, lastname = %s, title = %s,
                        url_linkedin = %s, about = %s, mobile = %s
                    WHERE user_id = %s
                """, (firstname, lastname, data.get("role", ""),
                      data.get("linkedin", ""), data.get("bio", ""),
                      data.get("phone", ""), user_id))

                # Update password
                pw_hash = _hash_password(temp_password)
                cur.execute("""
                    UPDATE user_password SET password = %s, algorithm = 'bcrypt'
                    WHERE user_id = %s
                """, (pw_hash, user_id))

                # Activate user if not active
                cur.execute("UPDATE user SET status = 1 WHERE id = %s", (user_id,))

            conn.commit()
        else:
            base_username = _slugify(data.get("name", email.split("@")[0]))
            username = _unique_username(conn, base_username)
            log.info("Creating new HumHub user %s", username)

            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            user_guid = str(uuid.uuid4())
            container_guid = str(uuid.uuid4())

            with conn.cursor() as cur:
                # 1. Create contentcontainer
                cur.execute("""
                    INSERT INTO contentcontainer (guid, class, pk, owner_user_id)
                    VALUES (%s, 'humhub\\\\modules\\\\user\\\\models\\\\User', 0, NULL)
                """, (container_guid,))
                container_id = cur.lastrowid

                # 2. Create user
                cur.execute("""
                    INSERT INTO user (guid, status, username, email, auth_mode,
                                     language, created_at, updated_at,
                                     visibility, contentcontainer_id)
                    VALUES (%s, 1, %s, %s, 'local', 'es', %s, %s, 1, %s)
                """, (user_guid, username, email, now, now, container_id))
                user_id = cur.lastrowid

                # Update contentcontainer pk to point to user
                cur.execute("UPDATE contentcontainer SET pk = %s, owner_user_id = %s WHERE id = %s",
                            (user_id, user_id, container_id))

                # 3. Create profile
                cur.execute("""
                    INSERT INTO profile (user_id, firstname, lastname, title,
                                        url_linkedin, about, mobile)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, firstname, lastname, data.get("role", ""),
                      data.get("linkedin", ""), data.get("bio", ""),
                      data.get("phone", "")))

                # 4. Create password
                pw_hash = _hash_password(temp_password)
                cur.execute("""
                    INSERT INTO user_password (user_id, algorithm, password, created_at)
                    VALUES (%s, 'bcrypt', %s, %s)
                """, (user_id, pw_hash, now))

            conn.commit()

        # 5. Add to Mentors space if configured
        if SPACE_ID:
            _add_to_space(conn, user_id, SPACE_ID)

        return {"user_id": user_id, "username": username, "temp_password": temp_password}

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _add_to_space(conn, user_id: int, space_id: int):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM space_membership WHERE space_id = %s AND user_id = %s",
            (space_id, user_id))
        if cur.fetchone():
            return  # already a member

        cur.execute("""
            INSERT INTO space_membership (space_id, user_id, status, group_id,
                                          show_at_dashboard, created_at, updated_at)
            VALUES (%s, %s, 3, 'member', 1, %s, %s)
        """, (space_id, user_id, now, now))
    conn.commit()
