import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from login import validar_login
from registro import (
    validar_registro,
    obtener_nombres_analistas,
    obtener_horario_asignado,
    validar_salida_anticipada,
    insertar_login
)
from correo_analistas import CORREOS_SUPERVISORES_INDIVIDUALES, normalizar
from verificacion import enviar_codigo_desde_gmail, generar_codigo_temporal

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
            insertar_login(nombre, correo)  # ✅ Registro de login exitoso
            codigo = generar_codigo_temporal()
            enviado = enviar_codigo_desde_gmail(correo, codigo)
            if enviado:
                st.session_state.update({
                    "correo_pendiente_verificacion": correo,
                    "nombre_pendiente_verificacion": nombre,
                    "codigo_temporal": codigo,
                    "codigo_generado_en": datetime.now(),
                    "fase_verificacion": "codigo"
                })
                st.rerun()
            else:
                st.error("❌ No se pudo enviar el código de verificación.")
        else:
            st.error("❌ Credenciales incorrectas.")

def mostrar_verificacion():
    st.title("🔐 Verificación por correo")
    st.info("Hemos enviado un código a tu correo institucional. Ingresa el código para continuar.")

    tiempo_generado = st.session_state.get("codigo_generado_en")
    if tiempo_generado and (datetime.now() - tiempo_generado).total_seconds() > 120:
        st.warning("⏳ El código ha expirado. Puedes reenviarlo para obtener uno nuevo.")

    codigo_ingresado = st.text_input("Código recibido")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Verificar"):
            if codigo_ingresado == st.session_state.get("codigo_temporal"):
                st.session_state.update({
                    "usuario_autenticado": st.session_state["correo_pendiente_verificacion"],
                    "nombre_autenticado": st.session_state["nombre_pendiente_verificacion"]
                })
                for key in ["fase_verificacion", "codigo_temporal", "codigo_generado_en", "correo_pendiente_verificacion", "nombre_pendiente_verificacion"]:
                    st.session_state.pop(key, None)
                st.rerun()
            else:
                st.error("❌ El código ingresado no es válido.")

    with col2:
        if st.button("🔄 Reenviar código"):
            nuevo_codigo = generar_codigo_temporal()
            correo = st.session_state.get("correo_pendiente_verificacion")
            enviado = enviar_codigo_desde_gmail(correo, nuevo_codigo)
            if enviado:
                st.session_state.update({
                    "codigo_temporal": nuevo_codigo,
                    "codigo_generado_en": datetime.now(),
                    "fase_verificacion": "codigo"
                })
                st.success("📤 Se ha enviado un nuevo código a tu correo.")
            else:
                st.error("❌ No se pudo reenviar el código. Intenta más tarde.")

def mostrar_registro():
    st.title("📋 Registro de entrada de analistas")

    correo_autenticado = st.session_state.get("usuario_autenticado")
    nombre_autenticado = st.session_state.get("nombre_autenticado")
    st.markdown(f"👤 Sesión activa: `{nombre_autenticado}` - `{correo_autenticado}`")

    nombres = obtener_nombres_analistas()
    nombre_seleccionado = st.selectbox("Selecciona tu nombre", nombres)

    if normalizar(nombre_seleccionado) != normalizar(nombre_autenticado):
        st.warning("⚠️ Recuerda seleccionar tu propio nombre.")
        return

    supervisor = st.selectbox("Selecciona tu supervisor", list(CORREOS_SUPERVISORES_INDIVIDUALES.keys()))
    hora_entrada_asignada, hora_salida_asignada = obtener_horario_asignado(nombre_seleccionado)

    if not hora_entrada_asignada or not hora_salida_asignada:
        st.error("❌ No tienes turno asignado hoy.")
        return

    st.success(f"🕓 Tu horario hoy es: {hora_entrada_asignada.strftime('%H:%M')} - {hora_salida_asignada.strftime('%H:%M')}")
    hora_actual = datetime.now(ZoneInfo("America/Bogota")).time()
    st.markdown(f"**Hora actual (PC - Colombia):** `{hora_actual.strftime('%H:%M')}`")

    novedad = st.selectbox("¿Tienes alguna novedad?", [
        "Sin novedad",
        "Cita médica",
        "Error con el usuario",
        "Error con el ingreso al edificio"
    ])
    novedad_final = None if novedad == "Sin novedad" else novedad

    hora_salida_real_str = st.text_input("Hora de salida real (formato HH:MM)", value="")
    hora_salida_real = None
    if hora_salida_real_str.strip():
        try:
            hora_salida_real = datetime.strptime(hora_salida_real_str.strip(), "%H:%M").time()
        except ValueError:
            st.error("❌ Formato incorrecto (HH:MM).")
            return

    if hora_salida_real:
        salida_valida, alerta = validar_salida_anticipada(hora_salida_real, hora_salida_asignada, novedad_final)
        if not salida_valida:
            st.error(alerta)
            return

    if st.button("Registrar entrada"):
        validar_registro(
            nombre_seleccionado.strip(),
            supervisor,
            novedad_final,
            correo_autenticado.strip(),
            hora_salida_real
        )
        st.success("✅ Registro exitoso.")

def mostrar_logout():
    st.sidebar.markdown("### 👤 Sesión activa")
    st.sidebar.info(f"{st.session_state['nombre_autenticado']}")
    if st.sidebar.button("🔓 Cerrar sesión"):
        for key in ["usuario_autenticado", "nombre_autenticado"]:
            st.session_state.pop(key, None)
        st.rerun()

def main():
    st.set_page_config(page_title="Ingreso BBVA", page_icon="🔐")
    if st.session_state.get("fase_verificacion") == "codigo":
        mostrar_verificacion()
    elif "usuario_autenticado" in st.session_state:
        mostrar_logout()
        mostrar_registro()
    else:
        mostrar_login()

if __name__ == "__main__":
    main()
