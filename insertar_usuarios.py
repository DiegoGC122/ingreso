import bcrypt
from config import conectar_sqlite
from correo_analistas import CORREOS_ANALISTAS

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
    "JEISSON ALEXANDER BOHORQUEZ":"T060946"
}

def insertar_usuarios():
    conn = conectar_sqlite()
    cursor = conn.cursor()

    for nombre, password in CONTRASEÑAS.items():
        nombre_corregido = EQUIVALENCIAS.get(nombre, nombre)
        correo = CORREOS_ANALISTAS.get(nombre_corregido) or CORREOS_MANUALES.get(nombre)

        if not correo:
            print(f"❌ No se encontró correo para: {nombre} (corregido: {nombre_corregido})")
            continue

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        try:
            cursor.execute(
                "INSERT INTO usuario (correo, contrasena) VALUES (?, ?)",
                (correo, hashed)
            )
            conn.commit()
            print(f"✅ Usuario insertado: {nombre}")
        except Exception as e:
            print(f"⚠️ Error con {nombre}: {e}")

    # 🔐 Insertar tu usuario administrativo
    correo_admin = "diegofernando.gonzalez.contractor@bbva.com"
    password_admin = "Admin123"
    hashed_admin = bcrypt.hashpw(password_admin.encode(), bcrypt.gensalt()).decode()

    try:
        cursor.execute(
            "INSERT INTO usuario (correo, contrasena) VALUES (?, ?)",
            (correo_admin, hashed_admin)
        )
        conn.commit()
        print(f"✅ Usuario administrativo insertado: {correo_admin}")
    except Exception as e:
        print(f"⚠️ Error al insertar tu usuario: {e}")

    conn.close()

if __name__ == "__main__":
    insertar_usuarios()