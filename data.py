import pandas as pd
from datetime import datetime
import unicodedata
from config import RUTA_TURNOS, RUTA_REGISTROS

# 🔤 Normalizar texto (elimina tildes, espacios, mayúsculas)
def normalizar(texto):
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.strip().lower()

# 📥 Cargar archivo de turnos y normalizar columnas
def cargar_turnos():
    try:
        df = pd.read_excel(RUTA_TURNOS)
        df.columns = [normalizar(col) for col in df.columns]
        return df
    except Exception as e:
        print("❌ Error al leer el archivo:", e)
        return pd.DataFrame()

# 📅 Obtener horario asignado para el día actual
def obtener_horario_asignado(nombre):
    df = cargar_turnos()
    if df.empty:
        return None, None

    # Traducir día actual al formato de columna
    dia_actual = datetime.today().strftime("%A").lower()
    dias_traducidos = {
        "monday": "lunes",
        "tuesday": "martes",
        "wednesday": "miercoles",
        "thursday": "jueves",
        "friday": "viernes",
        "saturday": "sabado",
        "sunday": "domingo"
    }
    dia_columna = dias_traducidos.get(dia_actual)

    if dia_columna not in df.columns:
        print(f"❌ No se encontró la columna para el día '{dia_columna}'.")
        return None, None

    # Buscar por nombre en la primera columna
    df_filtrado = df[df.iloc[:, 0].astype(str).str.strip().str.lower() == nombre.strip().lower()]
    if df_filtrado.empty:
        print(f"❌ No se encontró al analista '{nombre}'.")
        return None, None

    horario_str = df_filtrado.iloc[0][dia_columna]

    # Validar que el horario sea procesable
    if pd.isna(horario_str):
        print(f"⚠️ El analista '{nombre}' no tiene turno asignado hoy.")
        return None, None

    if not isinstance(horario_str, str):
        print(f"⚠️ El analista '{nombre}' no tiene turno asignado hoy.")
        return None, None

    horario_str = horario_str.strip().lower()
    if horario_str in ["vacaciones", "libre", "descanso", "no aplica", ""]:
        print(f"⚠️ El analista '{nombre}' no tiene horario asignado hoy ({horario_str}).")
        return None, None

    if "-" not in horario_str or len(horario_str.split("-")) != 2:
        print(f"⚠️ El valor '{horario_str}' no es un horario válido para '{nombre}'.")
        return None, None

    try:
        entrada_str, salida_str = horario_str.split("-")
        hora_entrada = pd.to_datetime(entrada_str.strip(), format="%H:%M").time()
        hora_salida = pd.to_datetime(salida_str.strip(), format="%H:%M").time()
        return hora_entrada, hora_salida
    except Exception as e:
        print(f"❌ Error al procesar el horario '{horario_str}':", e)
        return None, None

# 🗂️ Guardar registro en archivo de auditoría
def guardar_registro(nombre, hora_entrada_real, hora_salida_real, novedad=None, estado="OK"):
    registro = {
        "nombre": nombre,
        "fecha": datetime.today().date(),
        "hora_entrada": hora_entrada_real.strftime("%H:%M"),
        "hora_salida": hora_salida_real.strftime("%H:%M") if hora_salida_real else "",
        "novedad": novedad if novedad else "Sin novedad",
        "estado": estado
    }

    try:
        df_nuevo = pd.DataFrame([registro])
        try:
            df_existente = pd.read_excel(RUTA_REGISTROS)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        except FileNotFoundError:
            df_final = df_nuevo

        df_final.to_excel(RUTA_REGISTROS, index=False)
        print("✅ Registro guardado correctamente.")
    except Exception as e:
        print("❌ Error al guardar el registro:", e)

# 📋 Obtener lista de nombres desde el archivo de turnos
def obtener_nombres_analistas():
    df = cargar_turnos()
    if df.empty:
        return []

    nombres = df.iloc[:, 0].dropna().astype(str).str.strip().unique().tolist()
    return nombres
