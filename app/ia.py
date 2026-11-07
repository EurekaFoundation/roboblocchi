"""Collegamento al modello linguistico locale tramite Ollama (nessun dato esce dalla rete)."""

import base64
import json
import re
import urllib.error
import urllib.request

ISTRUZIONI = (
    "Sei l'intelligenza artificiale di un piccolo robot didattico usato a scuola. "
    "Rispondi sempre in italiano, in modo chiaro e breve (massimo due frasi)."
)

NUMERI_IN_LETTERE = {"zero": 0, "nessun": 0, "nessuna": 0, "uno": 1, "una": 1, "un": 1, "due": 2,
                     "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "sette": 7, "otto": 8,
                     "nove": 9, "dieci": 10}


def _nessuno(*_a, **_k):
    pass


class IA:
    def __init__(self, url_ollama, modello, foto, log=None, mostra_foto=None, timeout=120):
        self._url = url_ollama.rstrip("/")
        self._modello = modello
        self._foto = foto              # funzione che restituisce una foto JPEG (bytes)
        self._log = log or _nessuno
        self._mostra_foto = mostra_foto or _nessuno
        self._timeout = timeout
        self._ultimo_scambio = []      # ultima domanda e risposta, per il blocco "perché?"

    # ------------------------------------------------------------------ base
    def _scatta(self):
        jpeg = self._foto()
        self._mostra_foto(jpeg)
        return jpeg

    def _chat(self, domanda, immagine=None, storia=None):
        messaggio = {"role": "user", "content": domanda}
        if immagine is not None:
            messaggio["images"] = [base64.b64encode(immagine).decode("ascii")]
        messaggi = [{"role": "system", "content": ISTRUZIONI}] + (storia or []) + [messaggio]
        corpo = json.dumps({"model": self._modello, "stream": False, "messages": messaggi}).encode("utf-8")
        richiesta = urllib.request.Request(f"{self._url}/api/chat", data=corpo,
                                           headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(richiesta, timeout=self._timeout) as r:
                risposta = json.loads(r.read())
        except urllib.error.HTTPError as e:
            dettaglio = e.read().decode("utf-8", "replace")
            if e.code == 404:
                raise RuntimeError(f"Modello '{self._modello}' non trovato. "
                                   f"Scaricalo con: ollama pull {self._modello}") from e
            raise RuntimeError(f"Errore di Ollama ({e.code}): {dettaglio}") from e
        except OSError as e:
            raise RuntimeError(f"Ollama non risponde su {self._url}. È avviato? ({e})") from e
        testo = risposta["message"]["content"].strip()
        self._ultimo_scambio = [messaggio, {"role": "assistant", "content": testo}]
        return testo

    # ------------------------------------------------------------- visione
    def descrivi(self):
        self._log("👁️ guardo…", "ia")
        return self._chat("Descrivi in una o due frasi cosa vedi in questa immagine.", self._scatta())

    def vede(self, oggetto):
        self._log(f"👁️ cerco: {oggetto}", "ia")
        risposta = self._chat(f"Nell'immagine è presente questo: «{oggetto}»? "
                              "Rispondi solo con SI oppure NO.", self._scatta())
        return risposta.strip().upper().lstrip("«\"' ").startswith(("SI", "SÌ", "YES"))

    def chiedi_su_foto(self, domanda):
        self._log("👁️ guardo e penso…", "ia")
        return self._chat(str(domanda), self._scatta())

    def leggi_testo(self):
        self._log("👁️ leggo…", "ia")
        testo = self._chat("Trascrivi esattamente il testo scritto visibile nell'immagine, senza commenti. "
                           "Se non c'è nessun testo rispondi solo: NESSUN TESTO", self._scatta())
        return "" if testo.strip().upper().startswith("NESSUN TESTO") else testo

    def conta(self, oggetto):
        self._log(f"👁️ conto: {oggetto}", "ia")
        risposta = self._chat(f"Quanti elementi di questo tipo vedi nell'immagine: «{oggetto}»? "
                              "Rispondi solo con un numero (0 se non ce ne sono).", self._scatta())
        return interpreta_numero(risposta)

    # ------------------------------------------------------------------ testo
    def chiedi(self, domanda):
        self._log("💭 penso…", "ia")
        return self._chat(str(domanda))

    def perche(self):
        """Chiede al modello di spiegare la sua ultima risposta (stessa foto, stessa domanda)."""
        if not self._ultimo_scambio:
            return "Non ho ancora risposto a nessuna domanda."
        self._log("💭 spiego il mio ragionamento…", "ia")
        return self._chat("Perché hai risposto così? Spiega in modo semplice cosa hai notato o "
                          "su cosa ti sei basato, e se potresti esserti sbagliato.",
                          storia=self._ultimo_scambio)


def interpreta_numero(testo):
    trovato = re.search(r"-?\d+", testo)
    if trovato:
        return int(trovato.group())
    for parola in re.findall(r"[a-zàèéìòù]+", testo.lower()):
        if parola in NUMERI_IN_LETTERE:
            return NUMERI_IN_LETTERE[parola]
    return 0
