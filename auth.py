import bcrypt
from config import conectar_sqlite
from datetime import datetime

def validar_login(correo, contraseña):
    conn = conectar_sqlite()
    cursor = conn.cursor()

    cursor.execute("SELECT nombre, contraseña_hash, rol FROM usuarios WHERE correo = ? AND activo = 1", (correo,))
    resultado = cursor.fetchone()

    if resultado:
        nombre, hash_pw, rol = resultado
        if bcrypt.checkpw(contraseña.encode(), hash_pw.encode()):
            registrar_acceso(nombre, correo, "login exitoso")
            return {"nombre": nombre, "rol": rol}
    
    registrar_acceso("desconocido", correo, "login fallido")
    return None

def registrar_acceso(nombre, correo, evento):
    conn = conectar_sqlite()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
        INSERT INTO log_accesos (nombre, correo, fecha, hora, evento)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, correo, fecha, hora, evento))

    conn.commit()
    conn.close()
# Diccionario de correos para analistas