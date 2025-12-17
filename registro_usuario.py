import streamlit as st
import bcrypt
from config import conectar_mysql

def registrar_usuario(nombre, correo, password):
    if not correo.endswith("@bbva.com") and not correo.endswith("@bbva.com.co"):
        return "❌ Solo se permite el correo institucional."

    conn = conectar_mysql()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (%s, %s, %s)", (nombre, correo, hashed))
        conn.commit()
        return "✅ Usuario registrado correctamente."
    except Exception as e:
        return f"⚠️ Error al registrar: {e}"
    finally:
        conn.close()

def main():
    st.set_page_config(page_title="Registro de analistas", page_icon="📝")
    st.title("📝 Registro de nuevo analista")

    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo institucional").strip().lower()
    password = st.text_input("Contraseña", type="password")

    if st.button("Registrar"):
        mensaje = registrar_usuario(nombre, correo, password)
        st.info(mensaje)

if __name__ == "__main__":
    main()
