import sqlite3

def crear_tablas():
    conn = sqlite3.connect("registro.db")
    cursor = conn.cursor()

    # 🔐 Tabla de usuarios (correo + contraseña)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        )
    """)

    # 🕒 Tabla de ingresos (registro de entrada)
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

    # 🚪 Tabla de salidas (registro de salida)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingreso_id INTEGER NOT NULL,
            hora_salida TEXT NOT NULL,
            FOREIGN KEY (ingreso_id) REFERENCES ingreso(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tablas creadas correctamente: usuario, ingreso, salida")

if __name__ == "__main__":
    crear_tablas()
