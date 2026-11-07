import threading
import time

from esecutore import Esecutore
from simulatore import Simulatore
from visione import Telecamera


def test_programma_semplice(esecutore_veloce):
    esecutore_veloce.esegui("robot.accendi_led('verde')\ndici('ciao', 3)\nprint('ok')\n")
    assert esecutore_veloce.testi("dici") == ["ciao 3", "ok"]
    assert esecutore_veloce.sim.led == "verde"
    assert esecutore_veloce.testi("sistema")[-1].startswith("✔")


def test_errore_con_numero_di_riga(esecutore_veloce):
    esecutore_veloce.esegui("x = 1\ny = x / 0\n")
    errore = esecutore_veloce.testi("errore")[0]
    assert "riga 2" in errore and "ZeroDivisionError" in errore


def test_valori_non_validi_danno_un_errore_chiaro(esecutore_veloce):
    esecutore_veloce.esegui("robot.gira('su', 90)\n")
    assert "Direzione non valida" in esecutore_veloce.testi("errore")[0]


def _esecutore_reale():
    """Esecutore con pause vere, per i test di stop e passo-passo."""
    log, fatto, pause = [], threading.Event(), []
    e = Esecutore(Simulatore("vuota"), Telecamera(0), lambda t, k="info": log.append((k, t)),
                  fine=fatto.set, in_pausa=pause.append)
    imp = {"url_ollama": "http://127.0.0.1:9", "modello": "x", "modalita_robot": "simulato", "voce_attiva": False}
    return e, imp, log, fatto, pause


def test_ferma_interrompe_un_ciclo_infinito():
    e, imp, log, fatto, _ = _esecutore_reale()
    e.avvia("while True:\n  controlla_stop()\n  robot.avanti(1)\n", imp)
    time.sleep(0.3)
    e.ferma()
    assert fatto.wait(2)
    assert ("sistema", "■ Programma fermato") in log


def test_passo_passo():
    e, imp, _log, fatto, pause = _esecutore_reale()
    sim = e.simulatore
    codice = "evidenzia('a')\nrobot.avanti(5)\nevidenzia('b')\nrobot.avanti(5)\n"
    e.avvia(codice, imp, {"passo": True})
    time.sleep(0.2)
    assert pause[-1] is True and sim.x == 30         # fermo sul primo blocco
    e.passo()
    time.sleep(0.6)
    assert round(sim.x) == 35 and pause[-1] is True  # eseguito un blocco, in pausa sul secondo
    e.continua()
    assert fatto.wait(2)
    assert round(sim.x) == 40


def test_ferma_durante_la_pausa():
    e, imp, log, fatto, _ = _esecutore_reale()
    e.avvia("evidenzia('a')\nrobot.avanti(5)\n", imp, {"passo": True})
    time.sleep(0.2)
    e.ferma()
    assert fatto.wait(2)
    assert e.simulatore.x == 30


def test_non_parte_due_volte():
    e, imp, _log, fatto, _ = _esecutore_reale()
    assert e.avvia("attendi(0.3)\n", imp)
    assert not e.avvia("attendi(0.3)\n", imp)
    assert fatto.wait(2)


def test_comportamenti(esecutore_veloce):
    esecutore_veloce.esegui("robot.evita_ostacoli(0.5)\n", mondo="ostacoli")
    assert esecutore_veloce.sim.percorso > 0
    esecutore_veloce.esegui("robot.segui_linea(30)\n", mondo="linea")
    assert esecutore_veloce.sim.in_obiettivo() and esecutore_veloce.sim.urti == 0


def test_colore_davanti(esecutore_veloce, foto_rossa, monkeypatch):
    import visione
    monkeypatch.setattr(visione.Telecamera, "foto", lambda self: foto_rossa)
    esecutore_veloce.esegui("dici(robot.colore_davanti())\n")
    assert esecutore_veloce.testi("dici") == ["rosso"]
    assert esecutore_veloce.foto == [foto_rossa]


def test_ascolta(esecutore_veloce, monkeypatch):
    import voce
    monkeypatch.setattr(voce.Ascolto, "ascolta", lambda self, secondi, stop=None: "vai avanti")
    esecutore_veloce.esegui("if ascolta(2) == 'vai avanti':\n  robot.avanti(10)\n")
    assert round(esecutore_veloce.sim.x) == 40
