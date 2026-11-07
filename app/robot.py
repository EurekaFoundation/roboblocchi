"""Comandi del robot, uguali per il robot virtuale e per quello reale.

- RobotSimulato: muove il robot virtuale disegnato nell'app; le foto arrivano
  dalla webcam del PC.
- RobotRete: invia i comandi via HTTP al server sul robot (vedi robot_server/).

I comportamenti complessi (segui la linea, evita gli ostacoli, colore davanti)
sono scritti una sola volta in RobotBase usando i comandi semplici.
"""

import json
import random
import time
import urllib.parse
import urllib.request

import visione

DIREZIONI = ("destra", "sinistra")
LATI = ("sinistro", "destro")
COLORI_LED = ("rosso", "verde", "blu", "giallo", "bianco", "viola", "spento")
NOTE = {"do": 262, "re": 294, "mi": 330, "fa": 349, "sol": 392, "la": 440, "si": 494, "do alto": 523}


def _nessuno(*_args, **_kwargs):
    pass


class RobotBase:
    def __init__(self, log=None, controlla_stop=None, mostra_foto=None):
        self._log = log or _nessuno
        self._controlla = controlla_stop or _nessuno
        self._mostra_foto = mostra_foto or _nessuno

    # --- da implementare nelle sottoclassi ----------------------------------
    def _muovi(self, cm): raise NotImplementedError
    def _ruota(self, direzione, gradi): raise NotImplementedError
    def _ferma(self): raise NotImplementedError
    def _led(self, colore): raise NotImplementedError
    def _suona(self, frequenza, secondi): raise NotImplementedError
    def distanza(self): raise NotImplementedError
    def linea(self, lato): raise NotImplementedError
    def foto(self): raise NotImplementedError

    # --- comandi usati dai blocchi --------------------------------------------
    def avanti(self, cm):
        self._log(f"🤖 avanti di {cm:g} cm", "robot")
        self._muovi(cm)

    def indietro(self, cm):
        self._log(f"🤖 indietro di {cm:g} cm", "robot")
        self._muovi(-cm)

    def gira(self, direzione, gradi):
        if direzione not in DIREZIONI:
            raise ValueError(f"Direzione non valida: {direzione}")
        self._log(f"🤖 giro a {direzione} di {gradi:g}°", "robot")
        self._ruota(direzione, gradi)

    def ferma_motori(self):
        self._log("🤖 motori fermi", "robot")
        self._ferma()

    def accendi_led(self, colore):
        if colore not in COLORI_LED:
            raise ValueError(f"Colore LED non valido: {colore}")
        self._log(f"💡 LED {colore}", "robot")
        self._led(colore)

    def suona(self, nota, secondi=0.5):
        frequenza = NOTE.get(nota, 440)
        self._log(f"🎵 {nota}", "robot")
        self._suona(frequenza, float(secondi))

    def colore_davanti(self):
        """Colore prevalente al centro dell'immagine (calcolato, senza IA)."""
        jpeg = self.foto()
        self._mostra_foto(jpeg)
        colore = visione.colore_dominante(jpeg)
        self._log(f"🎨 colore al centro: {colore}", "ia")
        return colore

    # --- comportamenti ----------------------------------------------------------
    def segui_linea(self, secondi):
        """Segue la linea nera finché non finisce o scade il tempo."""
        self._log(f"〰️ seguo la linea (max {secondi:g} s)", "robot")
        fine = time.monotonic() + float(secondi)
        while time.monotonic() < fine:
            self._controlla()
            sx, dx = self.linea("sinistro"), self.linea("destro")
            if sx and dx:
                self._muovi(1.5)
            elif sx:
                self._ruota("sinistra", 6)
            elif dx:
                self._ruota("destra", 6)
            else:
                self._log("〰️ linea finita (o persa)", "robot")
                break
        self._ferma()

    def evita_ostacoli(self, secondi, distanza_minima=20):
        """Va avanti e gira quando trova un ostacolo, per il tempo indicato."""
        self._log(f"🧭 evito gli ostacoli per {secondi:g} s", "robot")
        fine = time.monotonic() + float(secondi)
        while time.monotonic() < fine:
            self._controlla()
            if self.distanza() < distanza_minima or self._muovi(2) is False:
                self._muovi(-3)   # dopo un urto laterale, prima indietreggia
                self._ruota(random.choice(DIREZIONI), 90)
        self._ferma()


class RobotSimulato(RobotBase):
    """Robot virtuale. `suono` riproduce una nota nell'interfaccia (se c'è)."""

    def __init__(self, simulatore, attendi, foto, suono=None, **kwargs):
        super().__init__(**kwargs)
        self.sim = simulatore
        self._attendi = attendi
        self._foto = foto
        self._suono = suono or _nessuno

    def _muovi(self, cm):
        if not self.sim.muovi(cm, self._attendi):
            self._log("💥 urto!", "errore")
            return False
        return True

    def _ruota(self, direzione, gradi):
        self.sim.ruota(gradi if direzione == "destra" else -gradi, self._attendi)

    def _ferma(self):
        pass

    def _led(self, colore):
        self.sim.imposta_led(colore)

    def _suona(self, frequenza, secondi):
        self._suono(frequenza, secondi)
        self._attendi(secondi)

    def distanza(self):
        self._controlla()
        return self.sim.distanza()

    def linea(self, lato):
        if lato not in LATI:
            raise ValueError(f"Lato non valido: {lato}")
        return self.sim.su_linea(lato)

    def foto(self):
        return self._foto()


class RobotRete(RobotBase):
    def __init__(self, indirizzo, timeout=10, **kwargs):
        super().__init__(**kwargs)
        self._base = indirizzo.rstrip("/")
        self._timeout = timeout

    def _chiama(self, percorso, **parametri):
        self._controlla()
        url = f"{self._base}/{percorso}"
        if parametri:
            url += "?" + urllib.parse.urlencode(parametri)
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as r:
                return r.read()
        except OSError as e:
            raise RuntimeError(f"Robot non raggiungibile su {self._base} ({e})") from e

    def _muovi(self, cm):
        if cm >= 0:
            self._chiama("avanti", cm=cm)
        else:
            self._chiama("indietro", cm=-cm)

    def _ruota(self, direzione, gradi):
        self._chiama("gira", direzione=direzione, gradi=gradi)

    def _ferma(self):
        self._chiama("ferma")

    def _led(self, colore):
        self._chiama("led", colore=colore)

    def _suona(self, frequenza, secondi):
        self._chiama("suona", frequenza=frequenza, secondi=secondi)

    def distanza(self):
        return float(json.loads(self._chiama("distanza"))["cm"])

    def linea(self, lato):
        if lato not in LATI:
            raise ValueError(f"Lato non valido: {lato}")
        return bool(json.loads(self._chiama("linea", lato=lato))["nero"])

    def foto(self):
        return self._chiama("foto")
