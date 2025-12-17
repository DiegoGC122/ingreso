# ingreso/alertas.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuración
SUPERVISOR_EMAIL = "supervisor@empresa.com"
REMITENTE_EMAIL = "registro@empresa.com"
SMTP_SERVER = "smtp.empresa.com"
SMTP_PORT = 587
SMTP_USER = "registro@empresa.com"
SMTP_PASS = "tu_contraseña_segura"

def enviar_alerta(nombre, mensaje):
    fecha = datetime.today().strftime("%d/%m/%Y")
    asunto = f"Alerta de ingreso - {nombre} ({fecha})"

    # Cuerpo del correo en HTML
    cuerpo_html = f"""
    <html>
        <body>
            <h3>🔔 Alerta de ingreso</h3>
            <p><strong>Analista:</strong> {nombre}</p>
            <p><strong>Fecha:</strong> {fecha}</p>
            <p><strong>Detalle:</strong> {mensaje}</p>
        </body>
    </html>
    """

    # Construcción del mensaje
    msg = MIMEMultipart()
    msg["From"] = REMITENTE_EMAIL
    msg["To"] = SUPERVISOR_EMAIL
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo_html, "html"))

    # Envío
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")
