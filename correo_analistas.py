import pandas as pd
import unicodedata
from config import RUTA_TURNOS

SUPERVISORES = [
    "ANDREA CAROLINA TORRES NUÑEZ",
    "JOSE GUILLERMO LOZANO GUERRA",
    "JURANI ROSAS",
    "JHON HENRY MARIN SANTOFIMIO"
]
# ✅ Diccionario fijo: nombre completo → correo
CORREOS_ANALISTAS = {
    "EDGAR ALEJANDRO HERRERA SARMIENTO": "edgaralejandro.herrera.contractor@bbva.com",
    "FREDY ALEXANDER CALCETERO PARDO": "fredyalexander.calcetero.pard.contractor@bbva.com",
    "DAYANA ANDREA RAMIREZ BERNAL": "dayanaandrea.ramirez.contractor@bbva.com",
    "KAREN JULIANA CEPEDA GARCIA": "karenjuliana.cepeda.contractor@bbva.com",
    "XIOMARA CATHERIN SALGADO CUERVO": "xiomaracatherin.salgado.contractor@bbva.com",
    "ANA MARIA CAUSIL GARCIA": "anamaria.causil.contractor@bbva.com",
    "SARA SOFIA CASAS CHARCAS": "sarasofia.casas.contractor@bbva.com",
    "BRIAM ERNESTO NIETO HERNANDEZ": "briamernesto.nieto.contractor@bbva.com",
    "JUAN CAMILO ROSAS ALARCON": "juancamilo.rosas.contractor@bbva.com",
    "NICOLAS JOSE CABANZO SANTOS": "nicolasjose.cabanzo.contractor@bbva.com",
    "ANA MARIA SOLANO BRAVO": "anamaria.solano.contractor@bbva.com",
    "JUAN DAVID CHAPARRO VARGAS": "juandavid.chaparro.contractor@bbva.com",
    "OSWALDO FORERO PATIÑO": "oswaldo.forero.contractor@bbva.com",
    "HERNAN RICARDO BUSTAMANTE HERMIDA": "hernanricardo.bustamante.contractor@bbva.com",
    "PAOLA STEFANIA ARIAS PEÑA": "paolastefania.arias.contractor@bbva.com",
    "CARLOS DANIEL PATIÑO ALVAREZ": "carlosdaniel.patino.contractor@bbva.com",
    "JHOSNMAN ARLEY RODRIGUEZ ARIAS": "jhonsmanarley.rodriguez.contractor@bbva.com",
    "JUAN DAVID ORJUELA MORALES": "juandavid.orjuela.contractor@bbva.com",
    "KEILA DEL CARMEN BENAVIDEZ OLIVERA": "keiladelcarmen.benavides.contractor@bbva.com",
    "LOREN YIRETH INDABURO VARGAS": "lorenyireth.indaburo.contractor@bbva.com",
    "NATALIA CARRILLO HERNANDEZ": "natalia.carrillo.contractor@bbva.com",
    "DANIEL LOAIZA JIMENEZ": "daniel.loaiza.contractor@bbva.com",
    "JENNY ALEXANDRA ANTONIO ANTONIO": "jennyalexandra.antonio.contractor@bbva.com",
    "KELLY KATHERINE LOPEZ CHINGUAL": "kellykatherine.lopez.contractor@bbva.com",
    "PAOLA ANDREA BARRETO PATARROYO": "paolaandrea.barreto.contractor@bbva.com",
    "HEIDY ZULIEN ULLOA GARCES": "heidyzulien.ulloa.contractor@bbva.com",
    "JESSICA PAOLA MONTES CASALINS": "jessicapaola.montes.contractor@bbva.com",
    "FABER SEBASTIAN FÚQUENE HERNANDEZ": "fabersebatian.fuquene.contractor@bbva.com",
    "NICOLAS ALEJANDRO URRESTI GONZALEZ":"nicolasalejandro.urresti.contractor@bbva.com",
    "LUZ HELENA BARON MURILLO":"luzhelena.baron.contractor@bbva.com",
    "JEISSON ALEXANDER BOHORQUEZ":"jeissonalexander.bohorquez.contractor@bbva.com",
    "DIEGO ANDRES REYES RAMIREZ":"diegoandres.reyes.contractor@bbva.com",
    "PAULA ANDREA GARCES OSPINA":"paulaandrea.garces.contractor@bbva.com",
    "BRAYAN CAMILO ORTEGA NARVAEZ":"brayancamilo.ortega.contractor@bbva.com"



}

CORREOS_SUPERVISORES_INDIVIDUALES={

    "ANDREA CAROLINA TORRES NUÑEZ":"andreacarolina.torres.contractor@bbva.com",
    "JOSE GUILLERMO LOZANO GUERRA": "joseguillermo.lozano.contractor@bbva.com",
    "JURANI ROSAS":"jurani.rosas.contractor@bbva.com" ,


}



# ✅ Función para normalizar nombres
import unicodedata
import re

def normalizar(texto):
    if not isinstance(texto, str) or texto is None:
        return ""
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = texto.lower().strip()
    texto = re.sub(r'\s+', ' ', texto)  # reemplaza múltiples espacios por uno
    return texto

