"""RoboBlocchi — robotica didattica a blocchi con intelligenza artificiale locale.

Avvio:  python app/main.py      (aggiungi --debug per gli strumenti di sviluppo,
                                  --verifica per un controllo senza finestra)
"""

import base64
import json
import os
import sys
import urllib.request

import webview

import mondi
import sfide
from esecutore import Esecutore
from impostazioni import carica, salva
from robot import RobotRete
from simulatore import Simulatore
from versione import VERSIONE
from visione import Telecamera

NOME_APP = "RoboBlocchi"

INTESTAZIONE_ESPORTAZIONE = '''\
# Programma creato con RoboBlocchi {versione}
#
# Per eseguirlo fuori dall'app, copia questo file nella cartella "app" di RoboBlocchi
# e lancia:  python nome_del_file.py
# Il robot (virtuale o in rete) e il modello di IA sono quelli scelti nelle impostazioni.

from roboblocchi import robot, ia, dici, ascolta, attendi

'''


def percorso_risorsa(relativo):
    """Funziona sia dal codice sorgente sia dall'eseguibile creato con PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relativo)


def _tipo_dialogo(nome):
    # pywebview >= 5 usa webview.FileDialog; le versioni precedenti le costanti *_DIALOG
    if hasattr(webview, "FileDialog"):
        return getattr(webview.FileDialog, nome)
    return getattr(webview, f"{nome}_DIALOG")


def _data_url(jpeg):
    return "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")


class Api:
    """Metodi richiamabili dall'interfaccia con window.pywebview.api.<metodo>().

    Gli attributi che iniziano con "_" non vengono esposti all'interfaccia.
    """

    def __init__(self):
        self._finestra = None
        imp = carica()
        self._telecamera = Telecamera(imp.get("indice_webcam", 0))
        self._simulatore = Simulatore(imp.get("mondo", "vuota"), disegna=self._disegna)
        self._esecutore = Esecutore(
            self._simulatore, self._telecamera, self._log,
            evidenzia=lambda id_blocco: self._js("evidenziaBlocco", id_blocco),
            fine=lambda: self._js("esecuzioneFinita"),
            mostra_foto=lambda jpeg: self._js("aggiungiFoto", _data_url(jpeg)),
            suono=lambda frequenza, secondi: self._js("suonaNota", frequenza, secondi),
            esito_sfida=lambda esito: self._js("esitoSfida", esito),
            in_pausa=lambda attivo: self._js("inPausa", attivo),
        )

    # --- chiamate verso l'interfaccia ---------------------------------------
    def _js(self, funzione, *argomenti):
        if self._finestra is None:
            return
        args = ", ".join(json.dumps(a, ensure_ascii=False) for a in argomenti)
        codice = f"window.{funzione} && window.{funzione}({args})"
        # run_js (pywebview >= 5) non aspetta il risultato: più veloce per le animazioni
        if hasattr(self._finestra, "run_js"):
            self._finestra.run_js(codice)
        else:
            self._finestra.evaluate_js(codice)

    def _log(self, testo, tipo="info"):
        self._js("aggiungiLog", str(testo), tipo)

    def _disegna(self, stato):
        self._js("simAggiorna", stato)

    # --- informazioni e impostazioni ----------------------------------------
    def info(self):
        return {"nome": NOME_APP, "versione": VERSIONE}

    def leggi_impostazioni(self):
        return carica()

    def salva_impostazioni(self, dati):
        imp = salva(dati)
        self._telecamera.imposta_indice(imp.get("indice_webcam", 0))
        return imp

    def verifica_ollama(self):
        """Controlla che Ollama risponda e che il modello scelto sia installato."""
        imp = carica()
        try:
            with urllib.request.urlopen(imp["url_ollama"].rstrip("/") + "/api/tags", timeout=5) as r:
                modelli = [m["name"] for m in json.loads(r.read()).get("models", [])]
        except OSError:
            return {"ok": False, "messaggio": f"Ollama non risponde su {imp['url_ollama']}"}
        nome = imp["modello"]
        if not any(m == nome or m == f"{nome}:latest" for m in modelli):
            return {"ok": False, "messaggio": f"Modello '{nome}' non installato (ollama pull {nome})",
                    "modelli": modelli}
        return {"ok": True, "messaggio": f"Ollama pronto con il modello {nome}", "modelli": modelli}

    def prova_voce(self):
        from voce import Voce
        imp = carica()
        try:
            Voce(imp.get("motore_voce", "sistema"), imp.get("modello_piper", "")).parla(
                "Ciao! Sono RoboBlocchi.")
            return {"ok": True, "messaggio": "Voce funzionante"}
        except Exception as e:  # noqa: BLE001 - messaggio mostrato all'utente
            return {"ok": False, "messaggio": str(e)}

    # --- esecuzione ---------------------------------------------------------
    def esegui(self, codice, opzioni=None):
        return self._esecutore.avvia(codice, carica(), opzioni or {})

    def passo(self):
        self._esecutore.passo()
        return True

    def continua(self):
        self._esecutore.continua()
        return True

    def ferma(self):
        self._esecutore.ferma()
        return True

    # --- robot virtuale e sfide ---------------------------------------------
    def stato_simulatore(self):
        return {"mondo": self._simulatore.mondo, "robot": self._simulatore.stato()}

    def elenco_mondi(self):
        return [{"id": i, "nome": mondi.MONDI[i]["nome"]} for i in mondi.MONDI_LIBERI]

    def imposta_mondo(self, id_mondo):
        if not self._esecutore.in_esecuzione:
            if id_mondo in mondi.MONDI_LIBERI:
                salva({"mondo": id_mondo})
            self._simulatore.carica(id_mondo)
        return self.stato_simulatore()

    def riposiziona(self):
        if not self._esecutore.in_esecuzione:
            self._simulatore.reset()
        return self.stato_simulatore()

    def elenco_sfide(self):
        return sfide.elenco()

    def scegli_sfida(self, id_sfida):
        """Carica il mondo della sfida (o torna al gioco libero con id_sfida = None)."""
        sfida = sfide.ottieni(id_sfida) if id_sfida else None
        self.imposta_mondo(sfida["mondo"] if sfida else carica().get("mondo", "vuota"))
        return self.stato_simulatore()

    # --- telecamera ---------------------------------------------------------
    def anteprima(self):
        imp = carica()
        try:
            if imp.get("modalita_robot") == "rete":
                jpeg = RobotRete(imp["indirizzo_robot"], timeout=3).foto()
            else:
                jpeg = self._telecamera.foto()
            return {"ok": True, "immagine": _data_url(jpeg)}
        except Exception as e:  # noqa: BLE001 - messaggio mostrato all'utente
            return {"ok": False, "messaggio": str(e)}

    # --- file ----------------------------------------------------------------
    def _salva_file(self, nome, tipi, contenuto):
        percorso = self._finestra.create_file_dialog(_tipo_dialogo("SAVE"), save_filename=nome, file_types=tipi)
        if not percorso:
            return None
        if isinstance(percorso, (list, tuple)):
            percorso = percorso[0]
        with open(percorso, "w", encoding="utf-8") as f:
            f.write(contenuto)
        return os.path.basename(percorso)

    def salva_progetto(self, contenuto):
        return self._salva_file("progetto.robo", ("Progetti RoboBlocchi (*.robo)",), contenuto)

    def apri_progetto(self):
        percorsi = self._finestra.create_file_dialog(
            _tipo_dialogo("OPEN"), file_types=("Progetti RoboBlocchi (*.robo)", "Tutti i file (*.*)"))
        if not percorsi:
            return None
        with open(percorsi[0], encoding="utf-8") as f:
            return {"nome": os.path.basename(percorsi[0]), "contenuto": f.read()}

    def esporta_python(self, codice):
        nome = "programma.py"
        testo = INTESTAZIONE_ESPORTAZIONE.format(versione=VERSIONE) + codice
        return self._salva_file(nome, ("Programmi Python (*.py)",), testo)


def verifica():
    """Controllo rapido senza finestra (usato dopo la build): python main.py --verifica"""
    pagina = percorso_risorsa(os.path.join("ui", "index.html"))
    assert os.path.isfile(pagina), f"Interfaccia mancante: {pagina}"
    assert os.path.isfile(percorso_risorsa(os.path.join("ui", "vendor", "blockly", "blockly_compressed.js")))
    api = Api()
    assert len(api.elenco_sfide()) > 0 and api.stato_simulatore()["mondo"]
    import importlib
    for facoltativo in ("faster_whisper", "sounddevice", "piper"):
        try:
            importlib.import_module(facoltativo)
            print(f"  {facoltativo}: incluso")
        except Exception as e:  # noqa: BLE001
            print(f"  {facoltativo}: assente ({type(e).__name__})")
    print(f"{NOME_APP} {VERSIONE}: verifica superata")


def main():
    if "--verifica" in sys.argv:
        try:
            verifica()
        except Exception as e:  # noqa: BLE001 - nessuna finestra di errore: serve un codice di uscita
            print(f"Verifica non superata: {type(e).__name__}: {e}")
            sys.exit(1)
        return
    api = Api()
    finestra = webview.create_window(
        NOME_APP,
        url=percorso_risorsa(os.path.join("ui", "index.html")),
        js_api=api,
        width=1360,
        height=860,
        min_size=(1000, 640),
    )
    api._finestra = finestra
    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
