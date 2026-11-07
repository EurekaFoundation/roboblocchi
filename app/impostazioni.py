"""Impostazioni di RoboBlocchi, salvate in un file JSON nella cartella dell'utente."""

import json
import os

CARTELLA = os.path.join(os.path.expanduser("~"), ".roboblocchi")
FILE = os.path.join(CARTELLA, "impostazioni.json")

PREDEFINITE = {
    # Indirizzo del server Ollama (sullo stesso PC o su un PC della rete scolastica)
    "url_ollama": "http://localhost:11434",
    # Modello con capacità di visione (deve essere già scaricato: ollama pull <nome>)
    "modello": "gemma3:4b",
    # "simulato" = robot virtuale sullo schermo, foto dalla webcam del PC; "rete" = robot sulla rete locale
    "modalita_robot": "simulato",
    "indirizzo_robot": "http://192.168.1.50:8000",
    # Numero della webcam del PC (0 = prima webcam)
    "indice_webcam": 0,
    # Mondo del robot virtuale per il gioco libero
    "mondo": "vuota",
    # Voce: il blocco "di'" parla davvero
    "voce_attiva": True,
    "motore_voce": "sistema",      # "sistema" oppure "piper"
    "modello_piper": "",           # percorso del file .onnx (es. it_IT-paola-medium.onnx)
    # Ascolto: modello Whisper (tiny, base, small): più grande = più preciso ma più lento
    "modello_whisper": "base",
    # "completa" oppure "semplice" (meno blocchi, più grandi: per i più piccoli)
    "interfaccia": "completa",
}


def carica():
    dati = dict(PREDEFINITE)
    try:
        with open(FILE, encoding="utf-8") as f:
            dati.update(json.load(f))
    except (OSError, ValueError):
        pass
    return dati


def salva(nuove):
    dati = carica()
    dati.update({k: v for k, v in nuove.items() if k in PREDEFINITE})
    os.makedirs(CARTELLA, exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)
    return dati
