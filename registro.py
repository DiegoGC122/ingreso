import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import smtplib
from email.mime.text import MIMEText

from data import cargar_turnos, obtener_horario_asignado, obtener_nombres_analistas
from config import (
    REMITENTE, PASSWORD, SMTP_SERVIDOR, SMTP_PUERTO,
    CORREOS_JEFES, conectar_mysql
)
from correo_analistas import CORREOS_ANALISTAS, normalizar, CORREOS_SUPERVISORES_INDIVIDUALES

# 🔍 Buscar correo por nombre
def buscar_correo(nombre_entrada):
    nombre_normalizado = normalizar(nombre_entrada)
    for nombre_diccionario, correo in CORREOS_ANALISTAS.items():
        if normalizar(nombre_diccionario) == nombre_normalizado:
            return correo
    return None

# 🛡️ Registrar intento sospechoso
def registrar_intento_sospechoso(nombre, correo_autenticado):
    with open("intentos_sospechosos.log", "a") as f:
        f.write(f"{datetime.now()} | Nombre seleccionado: {nombre} | Correo autenticado: {correo_autenticado}\n")

# 📧 Enviar correo de alerta
def enviar_correo_personalizado(nombre_analista, supervisor_seleccionado, asunto, cuerpo):
    correo_analista = buscar_correo(nombre_analista)
    correo_supervisor = CORREOS_SUPERVISORES_INDIVIDUALES.get(supervisor_seleccionado)

    if not correo_analista:
        st.warning(f"⚠️ No se encontró el correo del analista: {nombre_analista}")
        return
    if not correo_supervisor:
        st.warning(f"⚠️ No se encontró el correo del supervisor: {supervisor_seleccionado}")
        return

    destinatarios = [correo_analista, correo_supervisor] + CORREOS_JEFES

    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE
    msg['To'] = REMITENTE
    msg['Bcc'] = ", ".join(destinatarios)

    try:
        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PUERTO) as server:
            server.starttls()
            server.login(REMITENTE, PASSWORD)
            server.sendmail(REMITENTE, destinatarios, msg.as_string())
        st.success("📧 Correo enviado al analista, supervisor y jefes.")
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")

# ✅ Validar y registrar entrada
def validar_registro(nombre, supervisor, novedad, correo_autenticado, hora_salida_real):
    correo_esperado = buscar_correo(nombre)

    if normalizar(correo_autenticado) != normalizar(correo_esperado):
        registrar_intento_sospechoso(nombre, correo_autenticado)
        st.error("❌ El correo autenticado no coincide con el nombre seleccionado.")
        return

    if not correo_autenticado.endswith("@bbva.com") and not correo_autenticado.endswith("@bbva.com.co"):
        st.error("❌ Solo se permite el correo institucional del banco.")
        return

    hora_entrada_real = datetime.now(ZoneInfo("America/Bogota")).time()
    hora_entrada_asignada, hora_salida_asignada = obtener_horario_asignado(nombre)

    if not hora_entrada_asignada:
        st.warning("⚠️ No tienes turno asignado hoy.")
        return

    hoy = datetime.now(ZoneInfo("America/Bogota")).date()
    h1 = datetime.combine(hoy, hora_entrada_asignada)
    h2 = datetime.combine(hoy, hora_entrada_real)
    minutos_diferencia = (h2 - h1).total_seconds() / 60

    salida_real_str = hora_salida_real.strftime('%H:%M') if hora_salida_real else "No registrada"

    if minutos_diferencia > 5 and novedad in [None, "", "None"]:
        estado = "Tarde"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"👤 Supervisor a cargo: {supervisor}\n"
            f"📅 Fecha: {hoy}\n"
            f"🕒 Hora registrada (PC - Colombia): {hora_entrada_real.strftime('%H:%M')}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"🕕 Hora de salida real: {salida_real_str}\n"
            f"📌 Estado: Llegada tarde\n"
            f"📄 Observación: El analista llegó {int(minutos_diferencia)} minutos después de la hora asignada. No se registró ninguna novedad."
        )
        enviar_correo_personalizado(nombre, supervisor, "Alerta de llegada tarde", mensaje)
        st.warning("📧 Se ha enviado una alerta por tardanza.")

    elif novedad not in [None, "", "None"]:
        estado = "Con novedad"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"👤 Supervisor a cargo: {supervisor}\n"
            f"📅 Fecha: {hoy}\n"
            f"🕒 Hora registrada (PC - Colombia): {hora_entrada_real.strftime('%H:%M')}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"🕕 Hora de salida real: {salida_real_str}\n"
            f"📌 Estado: Con novedad\n"
            f"📄 Observación: El analista registró la siguiente novedad: \"{novedad}\".\n"
            f"No se considera tardanza por justificación."
        )
        enviar_correo_personalizado(nombre, supervisor, "Novedad registrada", mensaje)
        st.warning("📧 Se ha enviado una alerta por novedad.")

    else:
        estado = "OK"
        st.success("✅ Registro guardado correctamente. No se requiere alerta.")

    guardar_registro(nombre, hora_entrada_real, hora_salida_real, novedad, estado, supervisor)

# 🕒 Validar salida anticipada o desincronizada
def validar_salida_anticipada(hora_salida_real, hora_salida_asignada, novedad):
    hora_actual = datetime.now(ZoneInfo("America/Bogota")).time()
    diferencia = abs((datetime.combine(datetime.today(), hora_actual) - datetime.combine(datetime.today(), hora_salida_real)).total_seconds()) / 60

    if diferencia >= 1 and not novedad:
        alerta = (
            f"❌ La hora de salida registrada ({hora_salida_real.strftime('%H:%M')}) "
            f"no coincide con la hora actual del sistema ({hora_actual.strftime('%H:%M')}). "
            f"Diferencia de {int(diferencia)} minutos. Debes registrar una novedad para justificar."
        )
        return False, alerta
    return True, None

# 🗂️ Insertar login exitoso en base de datos
def insertar_login(nombre, correo):
    conn = conectar_mysql()
    cursor = conn.cursor()
    ahora = datetime.now(ZoneInfo("America/Bogota"))
    query = """
        INSERT INTO log_accesos (nombre, correo, fecha, hora, evento)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nombre, correo, ahora.date(), ahora.time(), "Login exitoso"))
    conn.commit()
    cursor.close()
    conn.close()

# 🗂️ Guardar registro de entrada en base de datos
def guardar_registro(nombre, hora_entrada, hora_salida, novedad, estado, supervisor):
    conn = conectar_mysql()
    cursor = conn.cursor()
    hoy = datetime.now(ZoneInfo("America/Bogota")).date()
    query = """
        INSERT INTO log_registros (nombre, supervisor, fecha, hora_entrada, hora_salida, novedad, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        nombre,
        supervisor,
        hoy,
        hora_entrada,
        hora_salida if hora_salida else None,
        novedad if novedad else "Sin novedad",
        estado
    ))
    conn.commit()
    cursor.close()
    conn.close()
