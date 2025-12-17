
import sqlite3

RUTA_DB = "registro.db"

def mostrar_estructura_y_datos():
    conn = sqlite3.connect(RUTA_DB)
    cur = conn.cursor()

    try:
        # 1. Listar todas las tablas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [t[0] for t in cur.fetchall()]
        if not tablas:
            print("⚠️ No hay tablas en la base de datos.")
            return

        print("📋 Tablas encontradas:", tablas)

        # 2. Mostrar estructura y datos de cada tabla
        for tabla in tablas:
            print(f"\n🔍 Tabla: {tabla}")
            
            # Estructura (columnas)
            cur.execute(f"PRAGMA table_info({tabla});")
            columnas = cur.fetchall()
            print("   ➤ Estructura:")
            for col in columnas:
                print(f"      - {col[1]} ({col[2]}) NOT NULL={bool(col[3])}")

            # Datos (primeros 10 registros)
            cur.execute(f"SELECT * FROM {tabla} LIMIT 10;")
            filas = cur.fetchall()
            if filas:
                print("   ➤ Datos (primeros 10):")
                for fila in filas:
                    print(f"      {fila}")
            else:
                print("   ➤ Sin datos en esta tabla.")

    except Exception as e:
        print(f"❌ Error al consultar la base: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    mostrar_estructura_y_datos()
