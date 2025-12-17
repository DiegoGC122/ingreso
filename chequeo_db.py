
# scripts/check_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("registro.db")

def main():
    if not DB_PATH.exists():
        print(f"❌ No se encontró {DB_PATH}. Ejecuta primero el script de creación.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        # Mostrar todas las tablas
        tablas = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("📋 Tablas en la base de datos:", tablas)

        # Mostrar datos de cada tabla (máximo 10 filas por tabla)
        for tabla in tablas:
            print(f"\n🔍 Contenido de la tabla '{tabla}':")
            rows = conn.execute(f"SELECT * FROM {tabla} LIMIT 10").fetchall()
            if rows:
                # Mostrar encabezados
                columnas = [desc[0] for desc in conn.execute(f"PRAGMA table_info({tabla})").fetchall()]
                print("Columnas:", columnas)
                for row in rows:
                    print(row)
            else:
                print("⚠️ No hay datos en esta tabla.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
