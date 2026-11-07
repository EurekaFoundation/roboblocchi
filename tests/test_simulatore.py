import math

import pytest

import simulatore as modulo
from simulatore import Simulatore

subito = lambda _secondi: None  # noqa: E731


def test_avanti_e_gira():
    sim = Simulatore("vuota")          # partenza (30, 75) verso destra
    assert sim.muovi(50, subito)
    assert (round(sim.x), round(sim.y)) == (80, 75)
    sim.ruota(90, subito)               # destra = senso orario = verso il basso
    sim.muovi(20, subito)
    assert (round(sim.x), round(sim.y)) == (80, 95)
    assert sim.percorso == pytest.approx(70)
    assert sim.rotazione == pytest.approx(90)


def test_urto_ferma_il_robot_e_non_attraversa_gli_ostacoli(monkeypatch):
    monkeypatch.setattr(modulo, "VELOCITA", 5000)   # anche a velocità altissima…
    sim = Simulatore("sfida_ostacolo")              # ostacolo da x=90 a x=110
    assert not sim.muovi(150, subito)
    assert sim.urti == 1
    assert sim.x < 90 - modulo.RAGGIO + 1           # …il robot si ferma prima dell'ostacolo


def test_sensore_distanza():
    sim = Simulatore("sfida_parete")                # parete a x=175, robot a x=20 con raggio 8
    assert sim.distanza() == pytest.approx(175 - 20 - modulo.RAGGIO, abs=0.5)
    sim.ruota(180, subito)                          # verso il bordo sinistro del mondo
    assert sim.distanza() == pytest.approx(20 - modulo.RAGGIO, abs=0.5)


def test_sensori_di_linea():
    sim = Simulatore("linea")
    assert sim.su_linea("sinistro") and sim.su_linea("destro")
    sim.y -= 4                                      # robot spostato verso l'alto: la linea è a destra
    assert sim.su_linea("destro") and not sim.su_linea("sinistro")
    assert not Simulatore("vuota").su_linea("sinistro")


def test_reset_riporta_alla_partenza():
    sim = Simulatore("vuota")
    sim.muovi(30, subito)
    sim.imposta_led("rosso")
    sim.reset()
    assert (sim.x, sim.y, sim.led, sim.urti, sim.percorso) == (30, 75, "spento", 0, 0)


def test_disegno_riceve_lo_stato():
    stati = []
    sim = Simulatore("vuota", disegna=stati.append)
    sim.muovi(5, subito)
    assert stati[0].get("reset") and len(stati) > 2
    assert math.isclose(stati[-1]["x"], 35)


def test_mondo_sconosciuto_usa_arena_vuota():
    assert Simulatore("non-esiste").mondo["id"] == "vuota"
