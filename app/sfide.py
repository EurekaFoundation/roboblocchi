"""Sfide guidate con verifica automatica (funzionano con il robot virtuale).

Ogni sfida indica il mondo da caricare, il testo per lo studente, un suggerimento
e una funzione `verifica(esito)` che restituisce (riuscita, messaggio).

`esito` contiene: sim (il Simulatore a fine programma), num_blocchi, detti (frasi dette).
"""

import math


def _vicino_partenza(sim, tolleranza=8):
    px, py, _ = sim.mondo["partenza"]
    return math.hypot(sim.x - px, sim.y - py) <= tolleranza


def _senza_urti(sim):
    return sim.urti == 0


def _v_viaggio(e):
    sim = e["sim"]
    if sim.in_obiettivo():
        return True, "Bandierina raggiunta!"
    return False, "Il robot non è arrivato sulla bandierina: misura meglio la distanza."


def _v_quadrato(e, max_blocchi=None):
    sim = e["sim"]
    if sim.percorso < 120:
        return False, "Il quadrato è troppo piccolo: fai lati di almeno 30 cm."
    if sim.rotazione < 340:
        return False, "Per fare un quadrato il robot deve girare quattro volte."
    if not _vicino_partenza(sim):
        return False, "Il robot non è tornato al punto di partenza."
    if max_blocchi and e["num_blocchi"] > max_blocchi:
        return False, f"Quadrato corretto, ma hai usato {e['num_blocchi']} blocchi: ne bastano {max_blocchi}!"
    return True, "Quadrato perfetto!"


def _v_ostacolo(e):
    sim = e["sim"]
    if not _senza_urti(sim):
        return False, f"Il robot ha urtato {sim.urti} volta/e. Prova a girare prima."
    if not sim.in_obiettivo():
        return False, "Nessun urto, ma il robot non è sulla bandierina."
    return True, "Ostacolo aggirato senza toccarlo!"


def _v_parete(e):
    sim = e["sim"]
    if not _senza_urti(sim):
        return False, "Il robot ha toccato la parete!"
    d = sim.distanza()
    if d >= 15:
        return False, f"Il robot si è fermato a {d:g} cm: deve arrivare a meno di 15 cm."
    return True, f"Fermo a {d:g} cm dalla parete, senza toccarla!"


def _v_linea(e):
    sim = e["sim"]
    if not _senza_urti(sim):
        return False, "Il robot è uscito di strada e ha urtato qualcosa."
    if not sim.in_obiettivo():
        return False, "Il robot non è arrivato alla fine della linea."
    return True, "Percorso completato seguendo la linea!"


def _v_saluto(e):
    sim = e["sim"]
    if not any("ciao" in str(d).lower() for d in e["detti"]):
        return False, "Il robot deve dire una frase che contiene «ciao»."
    if not sim.in_obiettivo():
        return False, "Il saluto c'è, ma il robot non è arrivato alla bandierina."
    return True, "Il robot ha salutato ed è arrivato!"


SFIDE = [
    {"id": "viaggio", "mondo": "sfida_viaggio", "livello": 1, "titolo": "Primo viaggio",
     "testo": "Porta il robot sulla bandierina verde.",
     "suggerimento": "Ogni quadretto della griglia è 10 cm.", "verifica": _v_viaggio},
    {"id": "quadrato", "mondo": "sfida_quadrato", "livello": 1, "titolo": "Il quadrato",
     "testo": "Fai percorrere al robot un quadrato e riportalo al punto di partenza.",
     "suggerimento": "Un quadrato ha 4 lati uguali e 4 angoli da 90°.", "verifica": _v_quadrato},
    {"id": "ciclo", "mondo": "sfida_quadrato", "livello": 2, "titolo": "Usa un ciclo",
     "testo": "Fai di nuovo il quadrato, ma usando al massimo 3 blocchi.",
     "suggerimento": "Cerca il blocco «ripeti» nella categoria Cicli.",
     "verifica": lambda e: _v_quadrato(e, max_blocchi=3)},
    {"id": "ostacolo", "mondo": "sfida_ostacolo", "livello": 2, "titolo": "Aggira l'ostacolo",
     "testo": "Raggiungi la bandierina senza toccare l'ostacolo grigio.",
     "suggerimento": "Gira, avanza, gira di nuovo…", "verifica": _v_ostacolo},
    {"id": "parete", "mondo": "sfida_parete", "livello": 3, "titolo": "Fermati in tempo",
     "testo": "Avvicinati alla parete e fermati a meno di 15 cm, senza toccarla.",
     "suggerimento": "Usa «ripeti finché» con il sensore di distanza.", "verifica": _v_parete},
    {"id": "linea", "mondo": "sfida_linea", "livello": 3, "titolo": "Segui la linea",
     "testo": "Arriva alla fine del percorso seguendo la linea nera.",
     "suggerimento": "C'è un blocco pronto in Sensori… ma riesci a farlo con i sensori di linea?",
     "verifica": _v_linea},
    {"id": "saluto", "mondo": "sfida_saluto", "livello": 1, "titolo": "Un saluto",
     "testo": "Fai dire «ciao» al robot e portalo sulla bandierina.",
     "suggerimento": "Il blocco «di'» è nella categoria Voce.", "verifica": _v_saluto},
]

_PER_ID = {s["id"]: s for s in SFIDE}


def ottieni(id_sfida):
    return _PER_ID.get(id_sfida)


def elenco():
    """Versione senza funzioni, da inviare all'interfaccia."""
    return [{k: v for k, v in s.items() if k != "verifica"} for s in sorted(SFIDE, key=lambda s: s["livello"])]


def verifica(id_sfida, esito):
    sfida = ottieni(id_sfida)
    if sfida is None:
        return None
    riuscita, messaggio = sfida["verifica"](esito)
    return {"riuscita": riuscita, "messaggio": messaggio, "titolo": sfida["titolo"]}
