"""Mondi (arene) del robot virtuale. Misure in centimetri, angoli in gradi.

Coordinate: x verso destra, y verso il basso; angolo 0 = verso destra,
angoli crescenti = rotazione oraria (cioè "gira a destra").
"""

import math

LARGHEZZA = 200
ALTEZZA = 150


def _arco(cx, cy, r, da, a, passi=12):
    return [(cx + r * math.cos(math.radians(da + (a - da) * i / passi)),
             cy + r * math.sin(math.radians(da + (a - da) * i / passi))) for i in range(passi + 1)]


def _percorso_linea():
    punti = [(15, 120), (100, 120)]
    punti += _arco(100, 90, 30, 90, 0)[1:]       # curva a sinistra verso l'alto
    punti += [(130, 50)]
    punti += _arco(160, 50, 30, 180, 270)[1:]    # curva a destra verso destra
    punti += [(188, 20)]
    return [(round(x, 1), round(y, 1)) for x, y in punti]


MONDI = {
    "vuota": {
        "nome": "Arena vuota",
        "partenza": [30, 75, 0],
        "ostacoli": [],
    },
    "ostacoli": {
        "nome": "Arena con ostacoli",
        "partenza": [25, 125, -90],
        "ostacoli": [[70, 0, 20, 70], [120, 80, 20, 70], [160, 30, 40, 15]],
    },
    "linea": {
        "nome": "Percorso con linea",
        "partenza": [20, 120, 0],
        "ostacoli": [],
        "linea": _percorso_linea(),
        "obiettivo": [186, 20, 11],
    },
    "labirinto": {
        "nome": "Piccolo labirinto",
        "partenza": [20, 20, 0],
        "ostacoli": [[0, 40, 140, 10], [60, 100, 140, 10], [170, 40, 10, 40]],
        "obiettivo": [25, 128, 12],
    },
    # --- mondi usati dalle sfide ---
    "sfida_viaggio": {
        "nome": "Primo viaggio", "partenza": [30, 75, 0], "ostacoli": [],
        "obiettivo": [150, 75, 12],
    },
    "sfida_quadrato": {
        "nome": "Il quadrato", "partenza": [80, 110, -90], "ostacoli": [],
        "obiettivo": [80, 110, 8],
    },
    "sfida_ostacolo": {
        "nome": "Aggira l'ostacolo", "partenza": [25, 75, 0],
        "ostacoli": [[90, 45, 20, 60]], "obiettivo": [170, 75, 12],
    },
    "sfida_parete": {
        "nome": "Fermati in tempo", "partenza": [20, 75, 0],
        "ostacoli": [[175, 0, 25, 150]],
    },
    "sfida_saluto": {
        "nome": "Un saluto", "partenza": [30, 120, -90], "ostacoli": [],
        "obiettivo": [30, 30, 12],
    },
}

MONDI["sfida_linea"] = dict(MONDI["linea"], nome="Segui la linea")

# Mondi mostrati nell'elenco per il gioco libero
MONDI_LIBERI = ["vuota", "ostacoli", "linea", "labirinto"]


def ottieni(nome):
    mondo = dict(MONDI.get(nome) or MONDI["vuota"])
    mondo.setdefault("ostacoli", [])
    mondo.setdefault("linea", [])
    mondo.setdefault("obiettivo", None)
    mondo["id"] = nome if nome in MONDI else "vuota"
    mondo["larghezza"] = LARGHEZZA
    mondo["altezza"] = ALTEZZA
    return mondo
