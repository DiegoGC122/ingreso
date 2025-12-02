import os
import sqlite3

RUTA_DB = "registro.db"

def conectar_sqlite():
    return sqlite3.connect(RUTA_DB, check_same_thread=False)

def crear_base_si_no_existe():
    if not os.path.exists(RUTA_DB):
        print("📁 Base de datos no encontrada. Creando nueva base...")
        crear_tablas()
    else:
        print("✅ Base de datos ya existe. No se requiere creación.")

def crear_tablas():
    conn = conectar_sqlite()
    cursor = conn.cursor()

    # 🔐 Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        )
    """)

    # 🕒 Tabla de ingresos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingreso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            supervisor TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            novedad TEXT,
            estado TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        )
    """)

    # 🚪 Tabla de salidas con columna 'nombre'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingreso_id INTEGER NOT NULL,
            hora_salida TEXT NOT NULL,
            nombre TEXT,
            FOREIGN KEY (ingreso_id) REFERENCES ingreso(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tablas creadas correctamente: usuario, ingreso, salida")

if __name__ == "__main__":
    crear_base_si_no_existe()