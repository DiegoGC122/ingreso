import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import unicodedata
from config import RUTA_TURNOS, RUTA_REGISTROS

# 🔤 Normalizar texto
def normalizar(texto):
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.strip().lower()

# 📥 Cargar archivo de turnos
def cargar_turnos():
    try:
        df = pd.read_excel(RUTA_TURNOS, header=None)

        # Convertir fechas a objetos datetime.date
        fechas = pd.to_datetime(df.iloc[1, 1:], dayfirst=True).dt.date.tolist()

        # Extraer horarios desde fila 2 en adelante
        horarios_raw = df.iloc[2:, :]
        horarios_raw = horarios_raw.dropna(subset=[0])  # Elimina filas sin nombre

        # Normalizar nombres
        horarios_raw[0] = horarios_raw[0].astype(str).apply(normalizar)

        # Construir DataFrame final
        horarios = horarios_raw.iloc[:, 1:]
        horarios.columns = fechas
        horarios.index = horarios_raw.iloc[:, 0].tolist()

        return horarios
    except Exception as e:
        print("❌ Error al leer el archivo de turnos:", e)
        return pd.DataFrame()

# import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import unicodedata
from config import RUTA_TURNOS, RUTA_REGISTROS

# 🔤 Normalizar texto
def normalizar(texto):
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.strip().lower()

# 📥 Cargar archivo de turnos
def cargar_turnos():
    try:
        df = pd.read_excel(RUTA_TURNOS, header=None)

        # Convertir fechas a objetos datetime.date
        fechas = pd.to_datetime(df.iloc[1, 1:], dayfirst=True).dt.date.tolist()
        print("📅 Fechas detectadas en el archivo:", fechas)

        # Extraer horarios desde fila 2 en adelante
        horarios_raw = df.iloc[2:, :]
        horarios_raw = horarios_raw.dropna(subset=[0])  # Elimina filas sin nombre

        # Normalizar nombres
        horarios_raw[0] = horarios_raw[0].astype(str).apply(normalizar)

        # Construir DataFrame final
        horarios = horarios_raw.iloc[:, 1:]
        horarios.columns = fechas
        horarios.index = horarios_raw.iloc[:, 0].tolist()
        print("📅 Columnas finales (tipos):", [(col, type(col)) for col in horarios.columns])


        print("👥 Nombres detectados:", horarios.index.tolist())
        return horarios
    except Exception as e:
        print("❌ Error al leer el archivo de turnos:", e)
        return pd.DataFrame()

# 📅 Obtener horario asignado para la fecha actual
def obtener_horario_asignado(nombre):
    horarios = cargar_turnos()
    if horarios.empty:
        return None, None

    fecha_actual = datetime.now(ZoneInfo("America/Bogota")).date()
    nombre_normalizado = normalizar(nombre)

    print(f"🔍 Buscando horario para: {nombre_normalizado}")
    print(f"📆 Fecha actual: {fecha_actual}")
    print(f"📆 Columnas disponibles: {horarios.columns.tolist()}")

    if nombre_normalizado not in horarios.index:
        print(f"❌ No se encontró al analista '{nombre}'.")
        return None, None

    if fecha_actual not in horarios.columns:
        print(f"❌ No se encontró la fecha '{fecha_actual}' en el archivo.")
        return None, None

    horario_str = horarios.loc[nombre_normalizado, fecha_actual]
    print(f"🕒 Horario bruto encontrado: {horario_str}")

    # Validar contenido
    if pd.isna(horario_str) or not isinstance(horario_str, str):
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
        hora_entrada = pd.to_datetime(entrada_str.strip()).time()
        hora_salida = pd.to_datetime(salida_str.strip()).time()
        print(f"✅ Horario procesado: {hora_entrada} - {hora_salida}")
        return hora_entrada, hora_salida
    except Exception as e:
        print(f"❌ Error al procesar el horario '{horario_str}':", e)
        return None, None



# 🗂️ Guardar registro
def guardar_registro(nombre, hora_entrada_real, hora_salida_real, novedad=None, estado="OK"):
    fecha_local = datetime.now(ZoneInfo("America/Bogota")).date()
    registro = {
        "nombre": nombre,
        "fecha": fecha_local,
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

# 📋 Obtener lista de nombres
def obtener_nombres_analistas():
    horarios = cargar_turnos()
    if horarios.empty:
        return []
    return horarios.index.tolist()