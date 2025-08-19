import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from data import cargar_turnos, obtener_horario_asignado, guardar_registro
from config import REMITENTE, PASSWORD, SMTP_SERVIDOR, SMTP_PUERTO, CORREO_SUPERVISOR

# 📤 Enviar correo
def enviar_correo(destinatario, asunto, cuerpo):
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE
    msg['To'] = destinatario

    try:
        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PUERTO) as server:
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.sendmail(REMITENTE, destinatario, msg.as_string())
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")

# 🧠 Validación principal
def validar_registro(nombre, novedad, horario_df):
    hora_entrada_real = datetime.now().time()
    hora_entrada_asignada, hora_salida_asignada = obtener_horario_asignado(nombre)

    if not hora_entrada_asignada:
        st.warning("⚠️ No tienes turno asignado hoy.")
        return

    h1 = datetime.combine(datetime.today(), hora_entrada_asignada)
    h2 = datetime.combine(datetime.today(), hora_entrada_real)
    minutos_diferencia = (h2 - h1).total_seconds() / 60

    if minutos_diferencia > 5 and not novedad:
        estado = "Tarde"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"📅 Fecha: {datetime.today().date()}\n"
            f"🕒 Hora registrada (PC): {hora_entrada_real.strftime('%H:%M')}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"📌 Estado: Llegada tarde\n"
            f"📄 Observación: El analista llegó {int(minutos_diferencia)} minutos después de la hora asignada. No se registró ninguna novedad."
        )
        enviar_correo(CORREO_SUPERVISOR, "Alerta de llegada tarde", mensaje)
        st.warning("📧 Se ha enviado una alerta por tardanza.")

    elif novedad:
        estado = "Con novedad"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"📅 Fecha: {datetime.today().date()}\n"
            f"🕒 Hora registrada (PC): {hora_entrada_real.strftime('%H:%M')}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"📌 Estado: Con novedad\n"
            f"📄 Observación: El analista registró la siguiente novedad: \"{novedad}\".\n"
            f"No se considera tardanza por justificación."
        )
        enviar_correo(CORREO_SUPERVISOR, "Novedad registrada", mensaje)
        st.warning("📧 Se ha enviado una alerta por novedad.")

    else:
        estado = "OK"
        st.success("✅ Registro guardado correctamente. No se requiere alerta.")

    guardar_registro(nombre, hora_entrada_real, hora_salida_asignada, novedad, estado)

# 🖥️ Interfaz Streamlit
def main():
    st.title("📋 Registro de entrada de analistas")

    horario_df = cargar_turnos()
    if horario_df.empty:
        st.error("❌ No se pudo cargar el archivo de turnos.")
        return

    nombres = horario_df.iloc[:, 0].dropna().str.strip().unique()
    if not nombres.any():
        st.error("❌ No se encontraron nombres en el archivo.")
        return

    nombre = st.selectbox("Selecciona tu nombre", nombres)

    # Obtener hora asignada y hora actual
    hora_entrada_asignada, hora_salida_asignada = obtener_horario_asignado(nombre)
    hora_entrada_real = datetime.now().time()

    # Mostrar horarios
    st.markdown("### 🕒 Horarios")
    st.write(f"**Hora actual (PC):** {hora_entrada_real.strftime('%H:%M')}")

    if hora_entrada_asignada and hora_salida_asignada:
        st.write(f"**Hora asignada:** {hora_entrada_asignada.strftime('%H:%M')} - {hora_salida_asignada.strftime('%H:%M')}")
    else:
        st.warning("⚠️ No tienes turno asignado hoy.")
        return

    # Desplegable de novedades
    opciones_novedad = [
        "Sin novedad",
        "Cita médica",
        "Error con el usuario",
        "Error con el ingreso al edificio"
    ]
    novedad = st.selectbox("¿Tienes alguna novedad?", opciones_novedad)

    if st.button("Registrar entrada"):
        novedad_final = None if novedad == "Sin novedad" else novedad
        validar_registro(nombre.strip(), novedad_final, horario_df)

if __name__ == "__main__":
    main()
