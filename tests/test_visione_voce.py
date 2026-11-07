import os
import stat
import sys
import threading
import time

import pytest

import visione
from voce import Voce, _attendi_processo, _avvia


@pytest.mark.parametrize("hsv, nome", [((0, 200, 200), "rosso"), ((15, 200, 200), "arancione"),
                                       ((28, 200, 200), "giallo"), ((60, 200, 200), "verde"),
                                       ((110, 200, 200), "blu"), ((0, 10, 240), "bianco"),
                                       ((0, 10, 120), "grigio"), ((0, 0, 20), "nero")])
def test_nome_colore(hsv, nome):
    assert visione.nome_colore(*hsv) == nome


def test_colore_dominante(foto_rossa):
    assert visione.colore_dominante(foto_rossa) == "rosso"


@pytest.mark.skipif(sys.platform == "win32", reason="usa uno script shell finto")
def test_voce_di_sistema_linux(tmp_path, monkeypatch):
    registro = tmp_path / "detto.txt"
    finto = tmp_path / "espeak-ng"
    finto.write_text(f'#!/bin/sh\necho "$@" > "{registro}"\n')
    finto.chmod(finto.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    Voce("sistema").parla("Ciao a tutti")
    assert registro.read_text().strip() == "-v it Ciao a tutti"


def test_comando_windows_passa_il_testo_in_modo_sicuro(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    comando, via_ambiente = Voce("sistema").comando_sistema("l'albero \"grande\"")
    assert comando[0] == "powershell" and via_ambiente
    assert "albero" not in " ".join(comando)    # il testo non finisce nella riga di comando


def test_piper_senza_modello():
    with pytest.raises(RuntimeError, match="modello"):
        Voce("piper", "").parla("ciao")


@pytest.mark.skipif(sys.platform == "win32", reason="usa sleep")
def test_stop_interrompe_la_voce():
    stop = threading.Event()
    proc = _avvia(["sleep", "5"])
    threading.Timer(0.2, stop.set).start()
    inizio = time.monotonic()
    assert _attendi_processo(proc, stop) is False
    assert time.monotonic() - inizio < 2
