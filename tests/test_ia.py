import pytest

from ia import IA, interpreta_numero


@pytest.fixture
def ia(ollama_finto, foto_rossa):
    mostrate = []
    oggetto = IA(ollama_finto.url, "modello-finto", lambda: foto_rossa, mostra_foto=mostrate.append)
    oggetto.mostrate = mostrate
    return oggetto


def test_descrivi_invia_la_foto(ia, ollama_finto):
    ollama_finto.risposte = [lambda t: "Vedo un quadrato rosso." if "Descrivi" in t else None]
    assert ia.descrivi() == "Vedo un quadrato rosso."
    richiesta = ollama_finto.richieste[-1]
    assert richiesta["model"] == "modello-finto" and "images" in richiesta["messages"][-1]
    assert len(ia.mostrate) == 1


@pytest.mark.parametrize("risposta, attesa", [("SI", True), ("Sì, c'è.", True), ("«Si»", True),
                                              ("NO", False), ("Non lo so", False)])
def test_vede(ia, ollama_finto, risposta, attesa):
    ollama_finto.risposte = [lambda t: risposta]
    assert ia.vede("una mela") is attesa


def test_conta_e_leggi(ia, ollama_finto):
    ollama_finto.risposte = [lambda t: "Ne vedo tre." if "Quanti" in t else None,
                             lambda t: "NESSUN TESTO" if "Trascrivi" in t else None]
    assert ia.conta("mele") == 3
    assert ia.leggi_testo() == ""


def test_perche_usa_la_domanda_precedente(ia, ollama_finto):
    assert ia.perche().startswith("Non ho ancora")
    ia.descrivi()
    ia.perche()
    messaggi = ollama_finto.richieste[-1]["messages"]
    assert [m["role"] for m in messaggi] == ["system", "user", "assistant", "user"]
    assert "images" in messaggi[1]


def test_modello_mancante(ia, ollama_finto):
    ollama_finto.stato_http = 404
    with pytest.raises(RuntimeError, match="ollama pull modello-finto"):
        ia.chiedi("ciao")


def test_ollama_spento():
    with pytest.raises(RuntimeError, match="Ollama non risponde"):
        IA("http://127.0.0.1:9", "m", lambda: b"").chiedi("ciao")


@pytest.mark.parametrize("testo, numero", [("3", 3), ("Ci sono 12 sedie", 12), ("due", 2),
                                           ("nessuna", 0), ("boh", 0)])
def test_interpreta_numero(testo, numero):
    assert interpreta_numero(testo) == numero
