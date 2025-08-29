# verificacion.py

import random
import smtplib
from email.mime.text import MIMEText
from config import REMITENTE, PASSWORD, SMTP_SERVIDOR, SMTP_PUERTO

def generar_codigo_temporal():
    return str(random.randint(100000, 999999))

def enviar_codigo_desde_gmail(correo_destino, codigo):
    asunto = "🔐 Código de verificación BBVA"
    cuerpo = f"""
Hola,

Tu código de acceso es: {codigo}

Este código es válido por 2 minutos. No compartas este mensaje.

Atentamente,
Sistema de Registro BBVA
"""

    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE
    msg['To'] = correo_destino

    try:
        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PUERTO) as server:
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.sendmail(REMITENTE, [correo_destino], msg.as_string())
        return True
    except Exception as e:
        import traceback
        print("❌ Error al enviar el código:", repr(e))
        traceback.print_exc()
        return False
