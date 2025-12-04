
# init_db.py
from config import conectar_sqlite

def crear_base_si_no_existe():
    """Crea tablas base si no existen y aplica migraciones mínimas."""
    import sqlite3

    try:
        with conectar_sqlite() as conn:
            cur = conn.cursor()

            # —— Tablas base ——
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correo TEXT UNIQUE NOT NULL,
                    contrasena TEXT NOT NULL
                    -- 'nombre' se agrega por migración si falta
                )
            """)

            cur.execute("""
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
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS salida (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingreso_id INTEGER NOT NULL,
                    hora_salida TEXT NOT NULL,   -- HH:MM
                    nombre TEXT,
                    FOREIGN KEY (ingreso_id) REFERENCES ingreso(id)
                )
            """)

            # —— Migraciones mínimas para alinear con tu código ——
            _migrar_agregar_columna_si_falta(conn, "usuario", "nombre", "TEXT")       # tu SELECT usa usuario.nombre
            _migrar_agregar_columna_si_falta(conn, "salida", "fecha_salida", "TEXT")  # tu reporte usa salida.fecha_salida

            # Índice útil
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_correo ON usuario (correo)")

            conn.commit()

    except sqlite3.OperationalError as e:
        # Deja registro en logs
        raise
    except Exception as e:
        # Deja registro en logs
        raise

def _migrar_agregar_columna_si_falta(conn, tabla, columna, tipo):
    cur = conn.execute(f"PRAGMA table_info({tabla});")
    cols = [r[1] for r in cur.fetchall()]  # r[1] = nombre de columna
    if columna not in cols:
        conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo};")
