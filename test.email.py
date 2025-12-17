import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Cargar variables del entorno
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
REMITENTE_EMAIL = os.getenv("REMITENTE_EMAIL")
SUPERVISOR_EMAIL = os.getenv("SUPERVISOR_EMAIL")

# 2. Crear el mensaje
msg = EmailMessage()
msg["Subject"] = "🔔 Prueba de notificación automática"
msg["From"] = REMITENTE_EMAIL
msg["To"] = SUPERVISOR_EMAIL
msg.set_content(
    "Este es un correo de prueba enviado desde el sistema de validación de asistencia.\n\n"
    "Si lo recibes correctamente, la configuración SMTP está lista para usarse."
)

# 3. Enviar el correo
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print("✅ Correo de prueba enviado correctamente.")
except Exception as e:
    print("❌ Error al enviar el correo:", e)
