import streamlit as st
import sqlite3
import bcrypt
from config import conectar_sqlite

# 🔐 Validar login con SQLite
def validar_login(correo, password):
    conn = conectar_sqlite()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, contraseña_hash, rol FROM usuarios WHERE correo = ? AND activo = 1", (correo,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            nombre, password_hash, rol = resultado
            if password_hash and bcrypt.checkpw(password.encode(), password_hash.encode()):
                return nombre  # Si luego quieres usar el rol, puedes devolver {"nombre": nombre, "rol": rol}
    except Exception as e:
        st.error(f"❌ Error al validar credenciales: {e}")
    return None

# 🖥️ Interfaz de login (si se usa como módulo independiente)
def mostrar_login():
    st.title("🔐 Iniciar sesión")
    correo = st.text_input("Correo BBVA").strip().lower()
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if not correo.endswith("@bbva.com") and not correo.endswith("@bbva.com.co"):
            st.error("❌ Solo se permite el correo BBVA.")
            return

        nombre = validar_login(correo, password)
        if nombre:
            st.session_state["usuario_autenticado"] = correo
            st.session_state["nombre_autenticado"] = nombre
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas. Verifica tu correo y contraseña.")
