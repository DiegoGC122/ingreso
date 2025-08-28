import sqlite3

conn = sqlite3.connect("registro.db")
cursor = conn.cursor()

# Tabla de usuarios
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT UNIQUE,
    contraseña_hash TEXT,
    rol TEXT DEFAULT 'analista',
    activo BOOLEAN DEFAULT 1
)
""")

# Tabla de accesos
cursor.execute("""
CREATE TABLE IF NOT EXISTS log_accesos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT,
    fecha TEXT,
    hora TEXT,
    evento TEXT
)
""")

# Tabla de registros
cursor.execute("""
CREATE TABLE IF NOT EXISTS log_registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    supervisor TEXT,
    fecha TEXT,
    hora_entrada TEXT,
    hora_salida TEXT,
    novedad TEXT,
    estado TEXT
)
""")

conn.commit()
conn.close()
print("✅ Base de datos SQLite creada correctamente.")
