import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from io import BytesIO

from login import validar_login
from registro import (
    validar_registro,
    obtener_nombres_analistas,
    obtener_horario_asignado,
    registrar_salida,
    verificar_ingreso_pendiente,
    exportar_excel_desde_sqlite
)
from correo_analistas import CORREOS_SUPERVISORES_INDIVIDUALES, normalizar
from verificacion import enviar_codigo_desde_gmail, generar_codigo_temporal

# 🔐 Pantalla de login
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

# 📧 Verificación por código
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
            codigo_guardado = st.session_state.get("codigo_temporal", "").strip()
            if codigo_ingresado.strip() == codigo_guardado:
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

# 📋 Registro de ingreso
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

    if st.button("Registrar entrada"):
        if hora_actual > hora_entrada_asignada:
            mensaje_puntualidad = "✉️ Se ha enviado correo por llegada tarde."
        else:
            mensaje_puntualidad = "🕓 Llegada puntual o anticipada."

        validar_registro(
            nombre_seleccionado.strip(),
            supervisor,
            novedad_final,
            correo_autenticado.strip()
        )

        st.success("✅ Registro exitoso.")
        st.info(mensaje_puntualidad)

# 🚪 Registro de salida
def mostrar_salida():
    st.title("🚪 Registro de salida")

    nombre_autenticado = st.session_state.get("nombre_autenticado")
    correo_autenticado = st.session_state.get("usuario_autenticado")
    st.markdown(f"👤 Sesión activa: `{nombre_autenticado}` - `{correo_autenticado}`")

    _, hora_salida_asignada = obtener_horario_asignado(nombre_autenticado)
    if not hora_salida_asignada:
        st.error("❌ No tienes turno asignado hoy.")
        return

    st.success(f"🕓 Tu hora de salida asignada es: `{hora_salida_asignada.strftime('%H:%M')}`")
    hora_actual = datetime.now(ZoneInfo("America/Bogota")).time()
    st.markdown(f"**Hora actual (PC - Colombia):** `{hora_actual.strftime('%H:%M')}`")

    hora_salida_real_str = st.text_input("Hora de salida real (formato HH:MM)", value="")
    if st.button("Registrar salida"):
        try:
            hora_salida_real = datetime.strptime(hora_salida_real_str.strip(), "%H:%M").time()
        except ValueError:
            st.error("❌ Formato incorrecto. Usa HH:MM.")
            return

        hoy = datetime.now(ZoneInfo("America/Bogota")).date()
        hora_actual_dt = datetime.combine(hoy, hora_actual)
        hora_salida_real_dt = datetime.combine(hoy, hora_salida_real)
        hora_asignada_dt = datetime.combine(hoy, hora_salida_asignada)

        hora_minima_permitida = hora_asignada_dt - timedelta(minutes=2)

        if hora_salida_real_dt < hora_minima_permitida:
            st.error(
                f"❌ La hora ingresada ({hora_salida_real.strftime('%H:%M')}) es demasiado anticipada. "
                f"Solo se permite registrar salida desde las {hora_minima_permitida.strftime('%H:%M')} en adelante."
            )
            return

        resultado = registrar_salida(correo_autenticado)
        if resultado == "registrado":
            st.success("✅ Salida registrada correctamente.")
        elif resultado == "ya_registrado":
            st.warning("⚠️ Ya se había registrado una salida para hoy.")
        elif resultado == "sin_ingreso":
            st.warning("⚠️ No se encontró un ingreso pendiente para hoy.")
        else:
            st.error("❌ Error al registrar salida.")

# 🔓 Cierre de sesión
def mostrar_logout():
    st.sidebar.markdown("### 👤 Sesión activa")
    st.sidebar.info(f"{st.session_state.get('nombre_autenticado', 'Desconocido')}")
    if st.sidebar.button("🔓 Cerrar sesión"):
        for key in list(st.session_state.keys()):
            if key.startswith("usuario_") or key.startswith("nombre_") or key.startswith("fase_") or key.startswith("codigo_") or key == "redirigir_a_salida":
                st.session_state.pop(key, None)
        st.rerun()

# 🚀 Punto de entrada
# 🚀 Punto de entrada
def main():
    st.set_page_config(page_title="Ingreso BBVA", page_icon="🔐")

    # 🔐 Verificación por código
    if st.session_state.get("fase_verificacion") == "codigo":
        mostrar_verificacion()
        return

    # ✅ Usuario autenticado
    if st.session_state.get("usuario_autenticado") and st.session_state.get("nombre_autenticado"):
        mostrar_logout()

        # 🔁 Redirección forzada a salida
        if st.session_state.get("redirigir_a_salida"):
            st.session_state.pop("redirigir_a_salida")
            mostrar_salida()
            return

        # 🔁 Si ya ingresó y no ha salido, mostrar salida directamente
        if verificar_ingreso_pendiente(st.session_state["usuario_autenticado"]):
            mostrar_salida()
            return

        # 🗂️ Interfaz principal con pestañas
        tab1, tab2, tab3 = st.tabs(["📋 Registro de ingreso", "🚪 Registro de salida", "📊 Reportes"])

        with tab1:
            mostrar_registro()
        with tab2:
            mostrar_salida()
        with tab3:
            st.header("📊 Reportes de asistencia")

            df = exportar_excel_desde_sqlite()

            if not df.empty:
                buffer = BytesIO()
                df.to_excel(buffer, index=False)
                buffer.seek(0)
                st.download_button(
                    label="📥 Descargar registros en Excel",
                    data=buffer,
                    file_name="registros.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("📁 No hay registros disponibles para exportar.")
        return

    # 🔐 Usuario no autenticado
    mostrar_login()
if __name__ == "__main__":
    main()