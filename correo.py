import smtplib
from email.message import EmailMessage
from datetime import datetime
import streamlit as st

SMTP_SERVER = st.secrets["SMTP_SERVER"]
SMTP_PORT = int(st.secrets["SMTP_PORT"])
SMTP_USER = st.secrets["SMTP_USER"]
SMTP_PASS = st.secrets["SMTP_PASS"]
REMITENTE_EMAIL = st.secrets["REMITENTE_EMAIL"]
SUPERVISOR_EMAIL = st.secrets["SUPERVISOR_EMAIL"]
MI_CORREO = st.secrets["MI_CORREO"]

# Si quieres más destinatarios, agrégalos en secrets.toml como lista CORREOS_JEFES
CORREOS_JEFES = st.secrets.get("CORREOS_JEFES", [])

def enviar_correo(nombre, tipo_alerta, mensaje):
    asunto = f"[Alerta de ingreso] {tipo_alerta} - {nombre}"
    destinatarios = [SUPERVISOR_EMAIL] + CORREOS_JEFES

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = REMITENTE_EMAIL
    msg["To"] = SUPERVISOR_EMAIL
    msg["Bcc"] = ", ".join(destinatarios)

    msg.set_content(
        f"""
🧑 Analista: {nombre}
📌 Tipo de alerta: {tipo_alerta}
🕒 Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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
        st.success("📧 Correo enviado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")
