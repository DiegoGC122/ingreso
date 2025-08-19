import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
REMITENTE_EMAIL = os.getenv("REMITENTE_EMAIL")
SUPERVISOR_EMAIL = os.getenv("SUPERVISOR_EMAIL")

def enviar_correo(nombre, tipo_alerta, mensaje):
    asunto = f"[Alerta de ingreso] {tipo_alerta} - {nombre}"

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = REMITENTE_EMAIL
    msg["To"] = SUPERVISOR_EMAIL
    msg.set_content(
        f"""
🧑 Analista: {nombre}
📌 Tipo de alerta: {tipo_alerta}
🕒 Fecha: {os.getenv('FECHA_OVERRIDE') or 'Automática'}
📄 Detalle:
{mensaje}

Este correo fue generado automáticamente por el sistema de validación de asistencia.
"""
    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print("✅ Correo enviado correctamente.")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)
