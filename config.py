
# config.py
import os
import json
import shutil
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------- Correo ----------------
try:
    import streamlit as st
    SMTP_USER = st.secrets["SMTP_USER"]
    SMTP_PASS = st.secrets["SMTP_PASS"]
    SMTP_SERVIDOR = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PUERTO = int(st.secrets.get("SMTP_PORT", 587))
    REMITENTE_EMAIL = st.secrets.get("REMITENTE_EMAIL", SMTP_USER)
except Exception:
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    SMTP_SERVIDOR = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PUERTO = int(os.getenv("SMTP_PORT", 587))
    REMITENTE_EMAIL = os.getenv("REMITENTE_EMAIL", SMTP_USER)

REMITENTE = REMITENTE_EMAIL
PASSWORD  = SMTP_PASS

# ---------------- Proyecto / Rutas base ----------------
# Carpeta del proyecto (donde está este config.py)
PROJECT_ROOT = Path(__file__).resolve().parent

# Archivos de Excel (pueden sobreescribirse por env o secrets)
def _get_path_from_env_or_secrets(key: str, default_filename: str) -> Path:
    """Resuelve rutas desde st.secrets o .env; si no, usa archivo en la raíz del proyecto."""
    # Prioriza st.secrets si estamos en Streamlit, luego variable de entorno
    try:
        import streamlit as st
        val = st.secrets.get(key, None)
        if val:
            return Path(val).expanduser().resolve()
    except Exception:
        pass
    env_val = os.getenv(key)
    if env_val:
        return Path(env_val).expanduser().resolve()
    return (PROJECT_ROOT / default_filename).resolve()

# Rutas públicas que usan otros módulos
RUTA_TURNOS     = _get_path_from_env_or_secrets("RUTA_TURNOS",     "turnos.xlsx")
RUTA_REGISTROS  = _get_path_from_env_or_secrets("RUTA_REGISTROS",  "registros.xlsx")

# ---------------- Base de datos (dual-modo) ----------------
REPO_DB = (PROJECT_ROOT / "registro.db").resolve()  # semilla versionada en el repo
TMP_DB  = Path("/tmp/registro.db")                  # sólo Streamlit Cloud

def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

def _resolve_db_path() -> Path:
    """
    Resolución de DB:
    - Si hay DB_PATH (env o secrets), úsalo.
    - Si estamos en Streamlit (Cloud/app), usa /tmp o st.secrets["DB_PATH"].
    - Si estamos local/script, usa registro.db del proyecto.
    """
    # Override explícito (útil en pruebas)
    env_db = os.getenv("DB_PATH")
    if env_db:
        return Path(env_db).expanduser().resolve()

    if _running_in_streamlit():
        try:
            import streamlit as st
            secrets_db = st.secrets.get("DB_PATH")
            if secrets_db:
                return Path(secrets_db).expanduser()
        except Exception:
            pass
        return TMP_DB

    # Local/scripts
    return REPO_DB

DB_PATH = _resolve_db_path()

def _ensure_tmp_has_seed_if_needed():
    """En Cloud: si DB apunta a /tmp y no existe, copia semilla desde el repo."""
    if str(DB_PATH).startswith("/tmp"):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not DB_PATH.exists() and REPO_DB.exists():
            shutil.copyfile(REPO_DB, DB_PATH)

def conectar_sqlite():
    """
    Conecta SIEMPRE a DB_PATH resuelto.
    - Cloud: /tmp/registro.db (copia semilla si falta).
    - Local/scripts: registro.db en la raíz del proyecto (misma que versionas).
    """
    _ensure_tmp_has_seed_if_needed()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    return conn

# Utilidades de depuración
def get_db_path() -> Path:
    return DB_PATH

def get_ruta_turnos() -> Path:
    return RUTA_TURNOS

def get_ruta_registros() -> Path:
    return RUTA_REGISTROS


# ---------------- Constantes de negocio (CORREOS_JEFES) ----------------
# Permitimos cargar desde st.secrets o variables de entorno usando JSON o CSV.
# Prioridad: st.secrets > env > por defecto (vacío)
def _load_correos_jefes():
    # 1) Intentar st.secrets
    try:
        import streamlit as st
        if "CORREOS_JEFES" in st.secrets:
            value = st.secrets["CORREOS_JEFES"]
            # Si viene como dict en secrets.toml, devolver solo las llaves (correos)
            if isinstance(value, dict):
                return list(value.keys())
            # Si viene como string (CSV o JSON), parsear
            if isinstance(value, str):
                parsed = _parse_correos_string(value)
                if parsed:
                    return list(parsed.keys())
    except Exception:
        pass

    # 2) Intentar variable de entorno
    env_val = os.getenv("CORREOS_JEFES", "").strip()
    if env_val:
        # Primero intentar JSON
        try:
            data = json.loads(env_val)
            if isinstance(data, dict):
                return list(data.keys())
        except Exception:
            # Si no es JSON, intentar CSV
            parsed = _parse_correos_string(env_val)
            if parsed:
                return list(parsed.keys())

    # 3) Por defecto vacío
    return []

def _parse_correos_string(raw: str):
    """
    Acepta formatos:
    - CSV: "correo1:Nombre 1, correo2:Nombre 2" (nombre opcional)
    - CSV simple: "correo1, correo2" (usa el correo como nombre)
    """
    raw = (raw or "").strip()
    if not raw:
        return {}
    result = {}
    # Separar por comas
    items = [x.strip() for x in raw.split(",") if x.strip()]
    for item in items:
        if ":" in item:
            correo, nombre = item.split(":", 1)
            correo = correo.strip()
            nombre = nombre.strip() or correo
        else:
            correo = item
            nombre = correo
        if correo:
            result[correo] = nombre
    return result

# Esta es la constante que otros módulos importan:
CORREOS_JEFES = _load_correos_jefes()
