import streamlit as st
import sqlite3
import bcrypt
from config import conectar_sqlite


# 🔐 Validar login con SQLite
def validar_login(correo, password):
    correo = correo.strip().lower()
    conn = conectar_sqlite()
    try:
        cursor = conn.cursor()
        # ✅ Consulta adaptada: solo id y contrasena (no existe 'nombre')
        cursor.execute("SELECT id, contrasena FROM usuario WHERE correo = ?", (correo,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            user_id, password_hash = resultado
            if password_hash and bcrypt.checkpw(password.encode(), password_hash.encode()):
                return user_id  # Retornamos el ID del usuario autenticado
    except Exception as e:
        st.error(f"❌ Error al validar credenciales: {e}")
    return None

# 🖥️ Interfaz de login
def mostrar_login():
    st.title("🔐 Iniciar sesión")
    correo = st.text_input("Correo BBVA").strip().lower()
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if not correo.endswith("@bbva.com") and not correo.endswith("@bbva.com.co"):
            st.error("❌ Solo se permite el correo BBVA.")
            return

        user_id = validar_login(correo, password)
        if user_id:
            # ✅ Guardamos el correo como 'nombre_autenticado' si no hay columna nombre
            st.session_state["usuario_autenticado"] = correo
            st.session_state["nombre_autenticado"] = correo  # o puedes usar el ID si prefieres
            st.success("✅ Inicio de sesión exitoso.")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas. Verifica tu correo y contraseña.")

if __name__ == "__main__":
    mostrar_login()
