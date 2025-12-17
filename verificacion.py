import random
import smtplib
import socket
from email.mime.text import MIMEText
from config import SMTP_USER, SMTP_PASS, SMTP_SERVIDOR, SMTP_PUERTO, REMITENTE_EMAIL

def generar_codigo_temporal():
    return str(random.randint(100000, 999999))

def enviar_codigo_desde_gmail(correo_destino, codigo):
    asunto = "🔐 Código de verificación BBVA"
    cuerpo = f"""Hola,

Tu código de acceso es: {codigo}

Este código es válido por 2 minutos. No compartas este mensaje.

Atentamente,
Sistema de Registro BBVA
"""

    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE_EMAIL
    msg['To'] = correo_destino

    try:
        # 🔍 Diagnóstico de conexión
        print("📤 Conectando a servidor SMTP:", SMTP_SERVIDOR, SMTP_PUERTO)
        print("🔍 Resolviendo IP:", socket.gethostbyname(SMTP_SERVIDOR))

        server = smtplib.SMTP(SMTP_SERVIDOR, SMTP_PUERTO)
        banner = server.ehlo()[1].decode()
        print("📡 Banner del servidor SMTP:", banner)

        server.starttls()
        server.ehlo()

        print("🔐 Autenticando con:", SMTP_USER)
        server.login(SMTP_USER, SMTP_PASS)

        server.sendmail(REMITENTE_EMAIL, [correo_destino], msg.as_string())
        server.quit()
        print("✅ Código enviado correctamente a:", correo_destino)
        return True

    except Exception as e:
        import traceback
        print("❌ Error al enviar el código:", repr(e))
        traceback.print_exc()
        return False
