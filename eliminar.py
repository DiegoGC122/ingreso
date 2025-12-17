
import os

RUTA_DB = "registro.db"

def eliminar_base():
    if os.path.exists(RUTA_DB):
        os.remove(RUTA_DB)
        print(f"✅ Base de datos '{RUTA_DB}' eliminada correctamente.")
    else:
        print(f"⚠️ La base de datos '{RUTA_DB}' no existe en la ruta actual: {os.getcwd()}")

if __name__ == "__main__":
    eliminar_base()
