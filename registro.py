import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import smtplib
from email.mime.text import MIMEText

from data import cargar_turnos, obtener_horario_asignado, guardar_registro, obtener_nombres_analistas
from config import REMITENTE, PASSWORD, SMTP_SERVIDOR, SMTP_PUERTO, CORREOS_SUPERVISORES

# 📤 Enviar correo a múltiples destinatarios
def enviar_correo(destinatarios, asunto, cuerpo):
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]

    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE
    msg["To"] = REMITENTE  # o un correo genérico como "notificaciones@empresa.com"
    msg["Bcc"] = ", ".join(destinatarios)


    try:
        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PUERTO) as server:
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.sendmail(REMITENTE, destinatarios, msg.as_string())
        st.info(f"📧 Correo enviado a: {', '.join(destinatarios)}")
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")

# 🧠 Validación principal
def validar_registro(nombre, novedad):
    hora_entrada_real = datetime.now(ZoneInfo("America/Bogota")).time()
    hora_entrada_asignada, hora_salida_asignada = obtener_horario_asignado(nombre)

    if not hora_entrada_asignada:
        st.warning("⚠️ No tienes turno asignado hoy.")
        return

    hoy = datetime.now(ZoneInfo("America/Bogota")).date()
    h1 = datetime.combine(hoy, hora_entrada_asignada)
    h2 = datetime.combine(hoy, hora_entrada_real)
    minutos_diferencia = (h2 - h1).total_seconds() / 60

    if minutos_diferencia > 5 and not novedad:
        estado = "Tarde"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"📅 Fecha: {hoy}\n"
            f"🕒 Hora registrada (PC - Colombia): {hora_entrada_real.strftime('%H:%M')}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"📌 Estado: Llegada tarde\n"
            f"📄 Observación: El analista llegó {int(minutos_diferencia)} minutos después de la hora asignada. No se registró ninguna novedad."
        )
        enviar_correo(CORREOS_SUPERVISORES, "Alerta de llegada tarde", mensaje)
        st.warning("📧 Se ha enviado una alerta por tardanza.")

    elif novedad:
        estado = "Con novedad"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"📅 Fecha: {hoy}\n"
            f"🕒 Hora registrada (PC - Colombia): {hora_entrada_real.strftime('%H:%M')}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"📌 Estado: Con novedad\n"
            f"📄 Observación: El analista registró la siguiente novedad: \"{novedad}\".\n"
            f"No se considera tardanza por justificación."
        )
        enviar_correo(CORREOS_SUPERVISORES, "Novedad registrada", mensaje)
        st.warning("📧 Se ha enviado una alerta por novedad.")

    else:
        estado = "OK"
        st.success("✅ Registro guardado correctamente. No se requiere alerta.")

    guardar_registro(nombre, hora_entrada_real, hora_salida_asignada, novedad, estado)

# 🖥️ Interfaz Streamlit
def main():
    st.title("📋 Registro de entrada de analistas")

    nombres = obtener_nombres_analistas()
    if not nombres:
        st.error("❌ No se encontraron nombres en el archivo.")
        return

    nombre = st.selectbox("Selecciona tu nombre", nombres)

    # Mostrar hora actual
    hora_actual = datetime.now(ZoneInfo("America/Bogota")).time()
    st.markdown("### 🕒 Horarios")
    st.write(f"**Hora actual (PC - Colombia):** {hora_actual.strftime('%H:%M')}")

    # Mostrar horario asignado automáticamente
    bloque_horario = st.empty()
    hora_entrada_asignada, hora_salida_asignada = obtener_horario_asignado(nombre)

    if hora_entrada_asignada and hora_salida_asignada:
        bloque_horario.success(f"🕓 Tu horario hoy es: **{hora_entrada_asignada.strftime('%H:%M')} - {hora_salida_asignada.strftime('%H:%M')}**")
    else:
        bloque_horario.warning("⚠️ No tienes turno asignado hoy.")
        return

    # Desplegable de novedades
    opciones_novedad = [
        "Sin novedad",
        "Cita médica",
        "Error con el usuario",
        "Error con el ingreso al edificio"
    ]
    novedad = st.selectbox("¿Tienes alguna novedad?", opciones_novedad)
    novedad_final = None if novedad == "Sin novedad" else novedad

    if st.button("Registrar entrada"):
        validar_registro(nombre.strip(), novedad_final)

if __name__ == "__main__":
    main()
