"""Configurazione comune dei test: percorsi, impostazioni isolate, Ollama finto."""

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADICE, "app"))
sys.path.insert(0, os.path.join(RADICE, "robot_server"))


@pytest.fixture(autouse=True)
def impostazioni_isolate(tmp_path, monkeypatch):
    """Ogni test usa un file di impostazioni temporaneo, mai quello dell'utente."""
    import impostazioni
    monkeypatch.setattr(impostazioni, "CARTELLA", str(tmp_path))
    monkeypatch.setattr(impostazioni, "FILE", str(tmp_path / "impostazioni.json"))


@pytest.fixture
def esecutore_veloce(monkeypatch):
    """Esecutore con robot virtuale e pause istantanee (i test durano millisecondi)."""
    from esecutore import Esecutore
    from simulatore import Simulatore
    from visione import Telecamera

    monkeypatch.setattr(Esecutore, "_attendi", lambda self, secondi: self._controlla_stop())

    class Prova:
        def __init__(self):
            self.log, self.esiti, self.foto = [], [], []
            self.fatto = threading.Event()
            self.sim = Simulatore("vuota")
            self.esecutore = Esecutore(
                self.sim, Telecamera(0), lambda t, k="info": self.log.append((k, t)),
                fine=self.fatto.set, esito_sfida=self.esiti.append, mostra_foto=self.foto.append)
            self.impostazioni = {"url_ollama": "http://127.0.0.1:9", "modello": "finto",
                                 "modalita_robot": "simulato", "voce_attiva": False}

        def esegui(self, codice, mondo=None, timeout=20, **opzioni):
            if mondo:
                self.sim.carica(mondo)
            self.fatto.clear()
            self.esiti.clear()
            self.log.clear()
            assert self.esecutore.avvia(codice, self.impostazioni, opzioni)
            assert self.fatto.wait(timeout), "il programma non è terminato"
            return self.esiti[-1] if self.esiti else None

        def testi(self, tipo=None):
            return [t for k, t in self.log if tipo is None or k == tipo]

    return Prova()


class _OllamaFinto(BaseHTTPRequestHandler):
    risposte = []          # funzioni (contenuto_ultimo_messaggio) -> risposta o None
    richieste = []
    stato_http = 200

    def log_message(self, *_args):
        pass

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).richieste.append(corpo)
        if type(self).stato_http != 200:
            self.send_response(type(self).stato_http)
            self.end_headers()
            self.wfile.write(b'{"error":"model not found"}')
            return
        testo = corpo["messages"][-1]["content"]
        risposta = next((r for r in (f(testo) for f in type(self).risposte) if r is not None), "Risposta.")
        dati = json.dumps({"message": {"content": risposta}}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(dati)))
        self.end_headers()
        self.wfile.write(dati)


@pytest.fixture
def ollama_finto():
    """Server HTTP che imita l'API /api/chat di Ollama."""
    _OllamaFinto.risposte = []
    _OllamaFinto.richieste = []
    _OllamaFinto.stato_http = 200
    server = ThreadingHTTPServer(("127.0.0.1", 0), _OllamaFinto)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    _OllamaFinto.url = f"http://127.0.0.1:{server.server_address[1]}"
    yield _OllamaFinto
    server.shutdown()


@pytest.fixture
def foto_rossa():
    import cv2
    import numpy as np
    return cv2.imencode(".jpg", np.full((240, 320, 3), (40, 40, 220), np.uint8))[1].tobytes()
