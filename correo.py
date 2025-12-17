import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


import streamlit as st

SMTP_SERVER = st.secrets["SMTP_SERVER"]
SMTP_PORT = int(st.secrets["SMTP_PORT"])
SMTP_USER = st.secrets["SMTP_USER"]
SMTP_PASS = st.secrets["SMTP_PASS"]
REMITENTE_EMAIL = st.secrets["REMITENTE_EMAIL"]
SUPERVISOR_EMAIL = st.secrets["SUPERVISOR_EMAIL"]


def enviar_correo(nombre, tipo_alerta, mensaje):
    asunto = f"[Alerta de ingreso] {tipo_alerta} - {nombre}"
    
    destinatarios = [supervisor_email] + CORREOS_JEFES

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = REMITENTE_EMAIL
    msg["To"] = REMITENTE_EMAIL  # solo se muestra el remitente
    msg["Bcc"] = ", ".join(destinatarios)  # supervisores ocultos

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
            server.sendmail(REMITENTE_EMAIL, destinatarios, msg.as_string())
        print("✅ Correo enviado correctamente.")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)


