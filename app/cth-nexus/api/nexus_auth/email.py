import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.resend.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "noreply@cleantechhub.net")
NEXUS_URL = os.environ.get("HUMHUB_BASE_URL", "https://nexus.cleantechhub.net")

log = logging.getLogger("cth-nexus-auth.email")


def send_magic_link(email: str, token: str, next_path: str = "/investors"):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("smtp_not_configured")

    verify_url = f"{NEXUS_URL}/nexus-auth/verify/{token}?next={quote(next_path)}"
    subject = "CleantechHUB Nexus — enlace de acceso / access link"
    body = f"""Hola,

Usa este enlace para acceder al directorio de Inversores y Funders en Nexus (válido 20 min):

{verify_url}

---
Hello,

Use this link to access the Investors and Funders directory on Nexus (valid 20 min):

{verify_url}

CleantechHUB Nexus
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_FROM, email, msg.as_string())

    log.info("Magic link sent to %s", email)
