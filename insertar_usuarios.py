
import sqlite3
import bcrypt
from config import conectar_sqlite
from correo_analistas import CORREOS_ANALISTAS, normalizar

EQUIVALENCIAS = {
    "JULIAN DAVID CHAPARRO VARGAS": "JUAN DAVID CHAPARRO VARGAS",
    "ANA MILENA SOLANO BRAVO": "ANA MARIA SOLANO",
    "JURANI ROSAS": "JURANI ROSAS RODRIGUEZ",
    "JOSE GUILLERMO LOZANO GUERRA": "JOSE GUILLERMO LOZANO",
    "ANDREA CAROLINA TORRES NUÑEZ": "ANDREA CAROLINA TORRES"
}

CORREOS_MANUALES = {
    "ANDREA CAROLINA TORRES NUÑEZ": "andreacarolina.torres.contractor@bbva.com",
    "JOSE GUILLERMO LOZANO GUERRA": "joseguillermo.lozano.contractor@bbva.com",
    "JURANI ROSAS": "jurani.rosas.contractor@bbva.com",
    "ANA MILENA SOLANO BRAVO": "anamaria.solano.contractor@bbva.com",
    "JULIAN DAVID CHAPARRO VARGAS": "juandavid.chaparro.contractor@bbva.com"
}

CONTRASEÑAS = {
    "KAREN JULIANA CEPEDA GARCIA": "T033230",
    "ANDREA CAROLINA TORRES NUÑEZ": "T002964",
    "JOSE GUILLERMO LOZANO GUERRA": "T027384",
    "JURANI ROSAS": "T013829",
    "GERMAN LEONARDO ANAYA": "T033226",
    "NATALIA CARRILLO HERNANDEZ": "T047234",
    "FABER SEBASTIAN FÚQUENE HERNANDEZ": "T048326",
    "FREDY ALEXANDER CALCETERO PARDO": "T049147",
    "JULIAN DAVID CHAPARRO VARGAS": "T043557",
    "LOREN YIRETH INDABURO VARGAS": "T021664",
    "JUAN DAVID ORJUELA MORALES": "T044631",
    "DAYANA ANDREA RAMIREZ BERNAL": "T025146",
    "SARA SOFIA CASAS CHARCAS": "T044628",
    "KELLY KATHERINE LOPEZ CHINGUAL": "T013227",
    "DANIEL LOAIZA JIMENEZ": "T020154",
    "CARLOS DANIEL PATIÑO ALVAREZ": "T051146",
    "PAOLA ANDREA BARRETO PATARROYO": "T047232",
    "JENNY ALEXANDRA ANTONIO ANTONIO": "T020519",
    "KEILA DEL CARMEN BENAVIDEZ OLIVERA": "T043589",
    "NICOLAS JOSE CABANZO SANTOS": "T048316",
    "JUAN SEBASTIAN AGUDELO PUENTES": "T029048",
    "BRIAM ERNESTO NIETO HERNANDEZ": "T043576",
    "ANGIE CAROLINA NARANJO HERRERA": "T043590",
    "JHOSNMAN ARLEY RODRIGUEZ ARIAS": "T044622",
    "PAOLA STEFANIA ARIAS PEÑA": "T043594",
    "JAVIER EDUARDO CELIS GUZMAN": "T044623",
    "XIOMARA CATHERIN SALGADO CUERVO": "T033227",
    "JORGE ARTURO BERNAL MARIN": "T050732",
    "JUAN CAMILO ROSAS ALARCON": "T050687",
    "HERNAN RICARDO BUSTAMANTE HERMIDA": "T044305",
    "EDGAR ALEJANDRO HERRERA SARMIENTO": "T025168",
    "ANA MARIA CAUSIL GARCIA": "T044629",
    "HEIDY ZULIEN ULLOA GARCES": "T019168",
    "ANA MILENA SOLANO BRAVO": "T049200",
    "OSWALDO FORERO PATIÑO": "CE51874",
    "JESSICA PAOLA MONTES CASALINS": "T035580",
    "NICOLAS ALEJANDRO URRESTI GONZALEZ":"T059706",
    "LUZ HELENA BARON MURILLO":"CE70999",
    "JEISSON ALEXANDER BOHORQUEZ":"T060946",
    "DIEGO ANDRES REYES RAMIREZ":"T022010",
    "PAULA ANDREA GARCES OSPINA":"CE60413",
    "BRAYAN CAMILO ORTEGA NARVAEZ":"T033229"
}

def _ensure_usuario_nombre(conn: sqlite3.Connection):
    """Asegura que la tabla 'usuario' tenga columna 'nombre' (por si faltara)."""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(usuario)").fetchall()]
    if "nombre" not in cols:
        conn.execute("ALTER TABLE usuario ADD COLUMN nombre TEXT;")
        conn.commit()

def insertar_usuarios():
    conn = conectar_sqlite()
    cursor = conn.cursor()

    # Garantiza columna 'nombre' para evitar fallos si la DB no la tiene aún
    _ensure_usuario_nombre(conn)

    insertados, actualizados, sin_correo = 0, 0, 0

    for nombre, password in CONTRASEÑAS.items():
        # Aplica equivalencias si hay variaciones del nombre
        nombre_corregido = EQUIVALENCIAS.get(nombre, nombre)

        # Busca el correo en mapeos disponibles
        correo = (
            CORREOS_ANALISTAS.get(nombre_corregido)
            or CORREOS_MANUALES.get(nombre)
            or CORREOS_MANUALES.get(nombre_corregido)
        )
        if not correo:
            print(f"❌ No se encontró correo para: {nombre} (corregido: {nombre_corregido})")
            sin_correo += 1
            continue

        correo_norm = (correo or "").strip().lower()
        nombre_norm = normalizar(nombre_corregido)  # o nombre_corregido.strip()

        # Genera hash de la contraseña
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        try:
            # UPSERT: si existe, actualiza; si no, inserta
            row = cursor.execute("SELECT id FROM usuario WHERE correo = ?", (correo_norm,)).fetchone()
            if row:
                cursor.execute(
                    "UPDATE usuario SET contrasena = ?, nombre = ? WHERE id = ?",
                    (hashed, nombre_norm, row[0])
                )
                actualizados += 1
                print(f"🔄 Usuario actualizado: {nombre_norm} ({correo_norm})")
            else:
                cursor.execute(
                    "INSERT INTO usuario (correo, contrasena, nombre) VALUES (?, ?, ?)",
                    (correo_norm, hashed, nombre_norm)
                )
                insertados += 1
                print(f"✅ Usuario insertado: {nombre_norm} ({correo_norm})")

            conn.commit()
        except Exception as e:
            print(f"⚠️ Error con {nombre}: {e}")

    # 🔐 Admin (tu usuario)
    correo_admin = "diegofernando.gonzalez.contractor@bbva.com"
    nombre_admin = "Diego Gonzalez"
    password_admin = "Admin123"
    hashed_admin = bcrypt.hashpw(password_admin.encode(), bcrypt.gensalt()).decode()
    correo_admin_norm = correo_admin.strip().lower()

    try:
        row = cursor.execute("SELECT id FROM usuario WHERE correo = ?", (correo_admin_norm,)).fetchone()
        if row:
            cursor.execute(
                "UPDATE usuario SET contrasena = ?, nombre = ? WHERE id = ?",
                (hashed_admin, nombre_admin, row[0])
            )
            actualizados += 1
            print(f"🔄 Usuario administrativo actualizado: {correo_admin_norm}")
        else:
            cursor.execute(
                "INSERT INTO usuario (correo, contrasena, nombre) VALUES (?, ?, ?)",
                (correo_admin_norm, hashed_admin, nombre_admin)
            )
            insertados += 1
            print(f"✅ Usuario administrativo insertado: {correo_admin_norm}")
        conn.commit()
    except Exception as e:
        print(f"⚠️ Error al insertar/actualizar tu usuario: {e}")

    # 🧮 Resumen y muestra
    total = cursor.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]
    print(f"\n🧮 Resumen → insertados={insertados}, actualizados={actualizados}, sin_correo={sin_correo}")
    print(f"👥 Total usuarios en DB: {total}")
    muestra = cursor.execute("SELECT id, correo, nombre FROM usuario ORDER BY id LIMIT 10").fetchall()
    print("🔎 Muestra de usuarios:")
    for r in muestra:
        print("   ", r)

    conn.close()

if __name__ == "__main__":
    insertar_usuarios()
