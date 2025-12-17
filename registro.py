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

    # Buscar en analistas
    for nombre_diccionario, correo in CORREOS_ANALISTAS.items():
        if normalizar(nombre_diccionario) == nombre_normalizado:
            return correo

    # Buscar en supervisores
    for nombre_diccionario, correo in CORREOS_SUPERVISORES_INDIVIDUALES.items():
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

    # Obtener todos los correos de supervisores desde la lista
    correos_supervisores = list(CORREOS_SUPERVISORES_INDIVIDUALES.values())

    if not correo_analista:
        st.warning(f"⚠️ No se encontró el correo del analista: {nombre_analista}")
        return
    if not correos_supervisores:
        st.warning("⚠️ La lista de supervisores está vacía.")
        return

    destinatarios = [correo_analista] + correos_supervisores + CORREOS_JEFES

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
        st.success("📧 Correo enviado al analista, todos los supervisores y jefes.")
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")

# ✅ Validar y registrar entrada
from correo_analistas import normalizar
def validar_registro(nombre, supervisor, novedad, correo_autenticado):
    usuario_id = obtener_usuario_id(correo_autenticado)
    if not usuario_id:
        st.error("❌ Usuario no encontrado en la base de datos.")
        return

    conn = conectar_sqlite()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuario WHERE correo = ?", (correo_autenticado,))
    resultado = cursor.fetchall()
    conn.close()    

    if resultado:
        nombre_registrado = normalizar(resultado[0])
        nombre_ingresado = normalizar(nombre)

        if nombre_ingresado != nombre_registrado:
            registrar_intento_sospechoso(nombre, correo_autenticado)
            st.warning("⚠️ El nombre seleccionado no coincide con el registrado para tu correo. Se registrará con trazabilidad.")
    else:
        st.error("❌ No se encontró el nombre vinculado a tu correo en la base de datos.")
        return

    ahora = datetime.now(ZoneInfo("America/Bogota"))
    hora_entrada_real = ahora.time()
    hora_entrada_str = hora_entrada_real.strftime("%H:%M:%S")
    fecha_actual = ahora.date()

    hora_entrada_asignada, _ = obtener_horario_asignado(nombre)
    estado = "OK"

    if not hora_entrada_asignada:
        st.warning("⚠️ No tienes turno asignado hoy.")
        estado = "Sin turno"
    else:
        minutos_diferencia = (
            datetime.combine(fecha_actual, hora_entrada_real) -
            datetime.combine(fecha_actual, hora_entrada_asignada)
        ).total_seconds() / 60

        if minutos_diferencia > 5 and not novedad:
            estado = "Tarde"
            mensaje = (
                f"🧑 Analista: {nombre}\n"
                f"👤 Supervisor: {supervisor}\n"
                f"📅 Fecha: {fecha_actual}\n"
                f"🕒 Hora registrada: {hora_entrada_str}\n"
                f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
                f"📌 Estado: Llegada tarde\n"
                f"📄 Observación: Llegó {int(minutos_diferencia)} minutos tarde sin novedad."
            )
            enviar_correo_personalizado(nombre, supervisor, "Alerta de llegada tarde", mensaje)
            st.warning("📧 Se ha enviado una alerta por tardanza.")
        elif novedad:
            estado = "Con novedad"
            mensaje = (
                f"🧑 Analista: {nombre}\n"
                f"👤 Supervisor: {supervisor}\n"
                f"📅 Fecha: {fecha_actual}\n"
                f"🕒 Hora registrada: {hora_entrada_str}\n"
                f"🕓 Hora asignada: {hora_entrada_asignada.strftime('%H:%M')}\n"
                f"📌 Estado: Con novedad\n"
                f"📄 Observación: Novedad registrada: \"{novedad}\"."
            )
            enviar_correo_personalizado(nombre, supervisor, "Novedad registrada", mensaje)
            st.warning("📧 Se ha enviado una alerta por novedad.")
        else:
            st.success("✅ Registro validado correctamente. No se requiere alerta.")

    resultado = guardar_registro(usuario_id, nombre, supervisor, hora_entrada_str, novedad, estado)

    if resultado == "registrado":
        st.info("📥 Registro insertado en la base de datos.")
    else:
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
def guardar_registro(usuario_id, nombre, supervisor, hora_entrada, novedad, estado):
    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()
        fecha = datetime.now(ZoneInfo("America/Bogota")).date().isoformat()

        cursor.execute("""
            INSERT INTO ingreso (usuario_id, nombre, supervisor, fecha, hora_entrada, novedad, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            usuario_id,
            nombre.strip(),
            supervisor.strip(),
            fecha,
            hora_entrada.strip(),
            novedad.strip() if novedad else "Sin novedad",
            estado.strip()
        ))

        conn.commit()
        return "registrado"
    except Exception as e:
        print(f"❌ Error al guardar ingreso: {e}")
        return "error"
    finally:
        conn.close()


# 🚪 Verificar si el analista ya ingresó pero no ha registrado salida
def verificar_ingreso_pendiente(correo_autenticado):
    conn = conectar_sqlite()
    cursor = conn.cursor()
    fecha = datetime.now(ZoneInfo("America/Bogota")).date().isoformat()

    cursor.execute("""
        SELECT i.id
        FROM ingreso i
        JOIN usuario u ON i.usuario_id = u.id
        LEFT JOIN salida s ON s.ingreso_id = i.id
        WHERE u.correo = ? AND i.fecha = ? AND s.id IS NULL
        ORDER BY i.hora_entrada DESC
    """, (correo_autenticado.strip().lower(), fecha))

    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None


# 🚪 Registrar salida del analista
def registrar_salida(correo_autenticado, nombre_manual=None):
    try:
        if not correo_autenticado or not isinstance(correo_autenticado, str):
            print("❌ Correo autenticado inválido.")
            return "error"

        conn = conectar_sqlite()
        cursor = conn.cursor()

        # Obtener fecha y hora actual del computador
        fecha = datetime.now(ZoneInfo("America/Bogota")).date().isoformat()
        hora_salida_str = datetime.now(ZoneInfo("America/Bogota")).time().strftime("%H:%M:%S")

        # Verificar si la columna 'nombre' existe en la tabla salida
        cursor.execute("PRAGMA table_info(salida)")
        columnas_salida = [col[1] for col in cursor.fetchall()]
        tiene_columna_nombre = "nombre" in columnas_salida
        tiene_columna_fecha = "fecha_salida" in columnas_salida

        # Buscar ingreso pendiente para ese correo en la fecha actual
        cursor.execute("""
            SELECT i.id, i.nombre
            FROM ingreso i
            JOIN usuario u ON i.usuario_id = u.id
            LEFT JOIN salida s ON s.ingreso_id = i.id
            WHERE u.correo = ? AND i.fecha = ? AND s.id IS NULL
            ORDER BY i.hora_entrada DESC
        """, (correo_autenticado.strip().lower(), fecha))

        ingreso = cursor.fetchone()

        if ingreso:
            ingreso_id, nombre = ingreso
        else:
            ingreso_id = None
            nombre = nombre_manual or st.session_state.get("nombre_autenticado", "Sin ingreso")

        # Construir el INSERT dinámicamente según columnas disponibles
        if tiene_columna_nombre and tiene_columna_fecha:
            cursor.execute("""
                INSERT INTO salida (ingreso_id, fecha_salida, hora_salida, nombre)
                VALUES (?, ?, ?, ?)
            """, (ingreso_id, fecha, hora_salida_str, nombre.strip()))
        elif tiene_columna_fecha:
            cursor.execute("""
                INSERT INTO salida (ingreso_id, fecha_salida, hora_salida)
                VALUES (?, ?, ?)
            """, (ingreso_id, fecha, hora_salida_str))
        else:
            cursor.execute("""
                INSERT INTO salida (ingreso_id, hora_salida)
                VALUES (?, ?)
            """, (ingreso_id, hora_salida_str))

        conn.commit()
        conn.close()

        print(f"✅ Salida registrada (ingreso_id: {ingreso_id}, nombre: {nombre}, hora: {hora_salida_str})")
        return "registrado"

    except Exception as e:
        print(f"❌ Error al registrar salida: {e}")
        return "error"
    finally:
        conn.close()



# 📤 Exportar registros desde SQLite como Excel
def exportar_excel_desde_sqlite():
    conn = conectar_sqlite()
    query = """
    SELECT 
        u.correo,
        i.nombre,
        i.supervisor,
        i.fecha AS fecha_ingreso,
        i.hora_entrada,
        s.fecha_salida,
        s.hora_salida,
        i.novedad,
        i.estado
    FROM ingreso i
    JOIN usuario u ON i.usuario_id = u.id
    LEFT JOIN salida s ON s.ingreso_id = i.id
    ORDER BY i.fecha DESC, i.hora_entrada DESC
"""
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df



def obtener_usuario_id(correo_autenticado):
    conn = conectar_sqlite()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuario WHERE correo = ?", (correo_autenticado.strip().lower(),))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None
