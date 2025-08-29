import os
import sqlite3
from dotenv import load_dotenv

# 📦 Cargar variables desde .env
load_dotenv()

# 📤 Configuración de correo
REMITENTE = os.getenv("REMITENTE_EMAIL")  # ej: diegofgonzalez22@gmail.com
PASSWORD = os.getenv("SMTP_PASS")         # contraseña de aplicación
SMTP_SERVIDOR = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PUERTO = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", REMITENTE)  # por si usas SMTP_USER en login

# 📁 Rutas de archivos
RUTA_TURNOS = "turnos.xlsx"
RUTA_REGISTROS = "registros.xlsx"

# 📧 Correos de jefes que siempre deben recibir notificación
CORREOS_JEFES = [
    "jhonsebastian.chingate.contractor@bbva.com",
    "mariapaula.ramos.rodriguez.contractor@bbva.com",
    "sandraseneth.tibavizco.contractor@bbva.com",
    "diegofernando.gonzalez.contractor@bbva.com"
]

# 🔌 Conexión a SQLite (modo local o en Streamlit Cloud)
def conectar_sqlite():
    return sqlite3.connect("registro.db", check_same_thread=False)
