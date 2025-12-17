
# scripts/seed_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("registro.db")

SCHEMA_SQL = """
-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correo TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL,
    nombre TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_correo ON usuario (correo);

-- Registros de ingreso
CREATE TABLE IF NOT EXISTS ingreso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    supervisor TEXT NOT NULL,
    fecha TEXT NOT NULL,         -- yyyy-mm-dd
    hora_entrada TEXT NOT NULL,  -- HH:MM
    novedad TEXT,
    estado TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Registros de salida
CREATE TABLE IF NOT EXISTS salida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingreso_id INTEGER NOT NULL,
    fecha_salida TEXT,           -- yyyy-mm-dd
    hora_salida TEXT NOT NULL,   -- HH:MM
    nombre TEXT,
    FOREIGN KEY (ingreso_id) REFERENCES ingreso(id)
);
"""

def main():
    # Crea la DB si no existe y asegura el esquema si ya existe
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()

        # Diagnóstico rápido (opcional)
        tablas = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("✅ Tablas presentes:", tablas)
        print("🧩 usuario:", conn.execute("PRAGMA table_info(usuario)").fetchall())
        print("🧩 ingreso:", conn.execute("PRAGMA table_info(ingreso)").fetchall())
        print("🧩 salida:", conn.execute("PRAGMA table_info(salida)").fetchall())

        print(f"\n🎉 Esquema asegurado en: {DB_PATH.resolve()}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
