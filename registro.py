import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import sqlite3

from data import cargar_turnos, obtener_horario_asignado, obtener_nombres_analistas
from config import (
    REMITENTE, PASSWORD, SMTP_SERVIDOR, SMTP_PUERTO,
    CORREOS_JEFES, conectar_sqlite
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
def validar_registro(nombre, supervisor, novedad, correo_autenticado):
    correo_esperado = buscar_correo(nombre)

    if normalizar(correo_autenticado) != normalizar(correo_esperado):
        registrar_intento_sospechoso(nombre, correo_autenticado)
        st.error("❌ El correo autenticado no coincide con el nombre seleccionado.")
        return

    if not correo_autenticado.endswith("@bbva.com") and not correo_autenticado.endswith("@bbva.com.co"):
        st.error("❌ Solo se permite el correo institucional del banco.")
        return

    hora_entrada_real = datetime.now(ZoneInfo("America/Bogota")).time()
    hora_entrada_str = hora_entrada_real.strftime("%H:%M:%S")

    hora_entrada_asignada, _ = obtener_horario_asignado(nombre)
    if not hora_entrada_asignada:
        st.warning("⚠️ No tienes turno asignado hoy.")
        return

    hoy = datetime.now(ZoneInfo("America/Bogota")).date()
    h1 = datetime.combine(hoy, hora_entrada_asignada)
    h2 = datetime.combine(hoy, hora_entrada_real)
    minutos_diferencia = (h2 - h1).total_seconds() / 60

    estado = "OK"
    if minutos_diferencia > 5 and not novedad:
        estado = "Tarde"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"👤 Supervisor a cargo: {supervisor}\n"
            f"📅 Fecha: {hoy}\n"
            f"🕒 Hora registrada (PC - Colombia): {hora_entrada_str}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"📌 Estado: Llegada tarde\n"
            f"📄 Observación: El analista llegó {int(minutos_diferencia)} minutos después de la hora asignada. No se registró ninguna novedad."
        )
        enviar_correo_personalizado(nombre, supervisor, "Alerta de llegada tarde", mensaje)
        st.warning("📧 Se ha enviado una alerta por tardanza.")
    elif novedad:
        estado = "Con novedad"
        mensaje = (
            f"🧑 Analista: {nombre}\n"
            f"👤 Supervisor a cargo: {supervisor}\n"
            f"📅 Fecha: {hoy}\n"
            f"🕒 Hora registrada (PC - Colombia): {hora_entrada_str}\n"
            f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
            f"📌 Estado: Con novedad\n"
            f"📄 Observación: El analista registró la siguiente novedad: \"{novedad}\".\n"
            f"No se considera tardanza por justificación."
        )
        enviar_correo_personalizado(nombre, supervisor, "Novedad registrada", mensaje)
        st.warning("📧 Se ha enviado una alerta por novedad.")
    else:
        st.success("✅ Registro validado correctamente. No se requiere alerta.")

    resultado = guardar_registro(
        nombre.strip(),
        hora_entrada_str,
        None,
        novedad,
        estado,
        supervisor.strip()
    )

    if resultado == "registrado":
        st.info("📥 Registro insertado en la base de datos.")
    elif resultado == "error":
        st.error("❌ No se pudo guardar el registro. Verifica la conexión o la estructura de la base.")



# 🗂️ Insertar login exitoso en base de datos SQLite
def insertar_login(nombre, correo):
    conn = conectar_sqlite()
    cursor = conn.cursor()
    ahora = datetime.now(ZoneInfo("America/Bogota"))
    fecha_str = ahora.date().isoformat()
    hora_str = ahora.time().strftime("%H:%M:%S")

    query = """
        INSERT INTO log_accesos (nombre, correo, fecha, hora, evento)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (nombre, correo, fecha_str, hora_str, "Login exitoso"))
    conn.commit()
    cursor.close()
    conn.close()

# 🗂️ Guardar registro de entrada en base de datos SQLite
def guardar_registro(nombre, hora_entrada, hora_salida, novedad, estado, supervisor):
    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()
        hoy = datetime.now(ZoneInfo("America/Bogota")).date()

        query = """
            INSERT INTO log_registros (nombre, supervisor, fecha, hora_entrada, hora_salida, novedad, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            nombre.strip(),
            supervisor.strip(),
            hoy,
            hora_entrada.strip() if hora_entrada else None,
            hora_salida.strip() if hora_salida else None,
            novedad.strip() if novedad else "Sin novedad",
            estado.strip()
        ))

        conn.commit()
        return "registrado"
    except Exception as e:
        print(f"❌ Error al guardar el registro: {e}")
        return "error"
    finally:
        cursor.close()
        conn.close()


# 🚪 Verificar si el analista ya ingresó pero no ha registrado salida
def verificar_ingreso_pendiente(nombre):
    conn = conectar_sqlite()
    cursor = conn.cursor()

    fecha = datetime.now(ZoneInfo("America/Bogota")).date().isoformat()
    cursor.execute("""
        SELECT id FROM log_registros
        WHERE nombre = ? AND fecha = ? AND hora_salida IS NULL
        ORDER BY hora_entrada DESC LIMIT 1
    """, (nombre, fecha))
    resultado = cursor.fetchone()
    conn.close()
    return bool(resultado)

# 🚪 Registrar salida del analista
def registrar_salida(nombre):
    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()

        fecha = datetime.now(ZoneInfo("America/Bogota")).date().isoformat()
        hora_salida_obj = datetime.now(ZoneInfo("America/Bogota")).time()
        hora_salida_str = hora_salida_obj.strftime("%H:%M:%S")

        # Buscar ingreso pendiente (sin hora de salida)
        cursor.execute("""
            SELECT id FROM log_registros
            WHERE nombre = ? AND fecha = ? AND hora_salida IS NULL
            ORDER BY hora_entrada DESC LIMIT 1
        """, (nombre.strip(), fecha))
        resultado = cursor.fetchone()

        if resultado:
            registro_id = resultado[0]
            cursor.execute("""
                UPDATE log_registros
                SET hora_salida = ?
                WHERE id = ?
            """, (hora_salida_str, registro_id))
            conn.commit()
            return "registrado"
        else:
            return "sin_ingreso"
    except Exception as e:
        print(f"❌ Error al registrar salida: {e}")
        return "error"
    finally:
        conn.close()

# 📤 Exportar registros desde SQLite como Excel
def exportar_excel_desde_sqlite():
    conn = conectar_sqlite()
    query = "SELECT * FROM log_registros ORDER BY fecha DESC, hora_entrada DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


