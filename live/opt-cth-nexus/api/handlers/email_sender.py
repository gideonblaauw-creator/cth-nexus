import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")  # Auth username (e.g. "resend" for Resend)
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "")  # From address (must be verified domain)
MOODLE_COURSE_URL = os.environ.get("MOODLE_MENTOR_COURSE_URL", "")
MOODLE_COURSE_NAME = os.environ.get("MOODLE_MENTOR_COURSE_NAME", "Mentor Onboarding")
NEXUS_URL = os.environ.get("HUMHUB_BASE_URL", "https://nexus.cleantechhub.net")

log = logging.getLogger("cth-mentor-api.email")

WELCOME_SUBJECT = "Bienvenido/a a la comunidad CTH - Tu perfil en Nexus esta listo"

WELCOME_BODY = """\
Hola {first_name},

Que alegria tenerte en nuestra comunidad de mentores!

Tu perfil ya esta activo en Nexus: {nexus_url}

ACCESO A NEXUS
Usuario: {nexus_username}
Contrasena temporal: {temp_password}

Al ingresar por primera vez, te pediremos que cambies tu contrasena.

CURSO DE INDUCCION
Plataforma: {moodle_course_url}
Curso: {moodle_course_name}
(Usa el mismo usuario y contrasena de Nexus)

Que sigue?
1. Ingresa a Nexus y completa tu perfil
2. Revisa el curso de induccion
3. Unete al espacio Mentors para conocer a tus colegas

Con carino,
Gideon Blaauw
CleantechHUB
"""


def send_welcome(data: dict, results: dict):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("SMTP not configured (SMTP_USER / SMTP_PASS)")

    first_name = data.get("name", "").split()[0] if data.get("name") else "Mentor"
    body = WELCOME_BODY.format(
        first_name=first_name,
        nexus_url=NEXUS_URL,
        nexus_username=results.get("nexus_username", ""),
        temp_password=results.get("nexus_temp_password", ""),
        moodle_course_url=MOODLE_COURSE_URL or "(pendiente)",
        moodle_course_name=MOODLE_COURSE_NAME,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = WELCOME_SUBJECT
    from_addr = SMTP_FROM or SMTP_USER
    msg["From"] = from_addr
    msg["To"] = data["email"]
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(from_addr, data["email"], msg.as_string())

    log.info("Welcome email sent to %s", data["email"])
