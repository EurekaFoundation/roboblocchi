"""Libreria per eseguire fuori dall'app i programmi esportati da RoboBlocchi.

    from roboblocchi import robot, ia, dici, ascolta, attendi

Usa le stesse impostazioni dell'app. In modalità "simulato" il robot virtuale
non viene disegnato: i suoi movimenti sono descritti nel terminale.
"""

from esecutore import Esecutore
from impostazioni import carica
from simulatore import Simulatore
from visione import Telecamera

_SIMBOLI = {"errore": "!", "sistema": "·"}


def _log(testo, tipo="info"):
    print(f"{_SIMBOLI.get(tipo, ' ')} {testo}", flush=True)


_imp = carica()
_esecutore = Esecutore(Simulatore(_imp.get("mondo", "vuota")), Telecamera(_imp.get("indice_webcam", 0)), _log)
_ambiente = _esecutore.crea_ambiente(_imp, detti=[])

robot = _ambiente["robot"]
ia = _ambiente["ia"]
dici = _ambiente["dici"]
ascolta = _ambiente["ascolta"]
attendi = _ambiente["attendi"]

__all__ = ["robot", "ia", "dici", "ascolta", "attendi"]
