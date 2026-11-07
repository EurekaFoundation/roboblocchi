import json

import pytest

webview = pytest.importorskip("webview")
import main  # noqa: E402


def test_verifica_senza_finestra(capsys):
    main.verifica()
    assert "verifica superata" in capsys.readouterr().out


def test_api_mondi_e_sfide():
    api = main.Api()
    assert {m["id"] for m in api.elenco_mondi()} >= {"vuota", "linea"}
    stato = api.scegli_sfida("parete")
    assert stato["mondo"]["nome"] == "Fermati in tempo"
    json.dumps(stato)                                   # deve arrivare all'interfaccia
    assert api.scegli_sfida(None)["mondo"]["id"] == "vuota"
    api.imposta_mondo("linea")
    assert api.leggi_impostazioni()["mondo"] == "linea"


def test_intestazione_esportazione():
    assert "from roboblocchi import" in main.INTESTAZIONE_ESPORTAZIONE.format(versione="1")
