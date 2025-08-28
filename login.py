import streamlit as st
import sqlite3
import bcrypt
from config import conectar_sqlite

# 🔐 Validar login con SQLite
def validar_login(correo, password):
    conn = conectar_sqlite()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, contraseña_hash FROM usuarios WHERE correo = ?", (correo,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            nombre, password_hash = resultado
            if bcrypt.checkpw(password.encode(), password_hash.encode()):
                return nombre
    except Exception as e:
        st.error(f"❌ Error al validar credenciales: {e}")
    return None

# 🖥️ Interfaz de login (si se usa como módulo independiente)
def mostrar_login():
    st.title("🔐 Iniciar sesión")
    correo = st.text_input("Correo institucional").strip().lower()
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if not correo.endswith("@bbva.com") and not correo.endswith("@bbva.com.co"):
            st.error("❌ Solo se permite el correo institucional del banco.")
            return

        nombre = validar_login(correo, password)
        if nombre:
            st.session_state["usuario_autenticado"] = correo
            st.session_state["nombre_autenticado"] = nombre
            st.rerun()  # 🔁 Recarga limpia para mostrar el formulario
        else:
            st.error("❌ Credenciales incorrectas. Verifica tu correo y contraseña.")
