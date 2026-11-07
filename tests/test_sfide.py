import pytest

import sfide

QUADRATO = "for i in range(4):\n  robot.avanti(40)\n  robot.gira('destra', 90)\n"
AGGIRA = ("robot.gira('sinistra', 90)\nrobot.avanti(40)\nrobot.gira('destra', 90)\n"
          "robot.avanti(145)\nrobot.gira('destra', 90)\nrobot.avanti(40)\n")

CASI = [
    ("viaggio", "robot.avanti(120)\n", {}, True),
    ("viaggio", "robot.avanti(60)\n", {}, False),
    ("quadrato", QUADRATO, {}, True),
    ("quadrato", "robot.avanti(40)\n", {}, False),
    ("ciclo", QUADRATO, {"num_blocchi": 3}, True),
    ("ciclo", QUADRATO, {"num_blocchi": 9}, False),
    ("ostacolo", AGGIRA, {}, True),
    ("ostacolo", "robot.avanti(150)\n", {}, False),
    ("parete", "while not robot.distanza() < 10:\n  robot.avanti(1)\n", {}, True),
    ("parete", "robot.avanti(200)\n", {}, False),
    ("linea", "robot.segui_linea(30)\n", {}, True),
    ("linea", "robot.avanti(50)\n", {}, False),
    ("saluto", "dici('Ciao a tutti')\nrobot.avanti(90)\n", {}, True),
    ("saluto", "robot.avanti(90)\n", {}, False),
]


@pytest.mark.parametrize("id_sfida, codice, opzioni, attesa", CASI)
def test_verifica_sfide(esecutore_veloce, id_sfida, codice, opzioni, attesa):
    sfida = sfide.ottieni(id_sfida)
    esito = esecutore_veloce.esegui(codice, mondo=sfida["mondo"], sfida=id_sfida, **opzioni)
    assert esito["riuscita"] is attesa, esito["messaggio"]


def test_elenco_sfide_serializzabile():
    import json
    elenco = sfide.elenco()
    assert len(elenco) == len(sfide.SFIDE)
    json.dumps(elenco)
    assert all("verifica" not in s for s in elenco)


def test_ogni_sfida_ha_un_mondo_valido():
    import mondi
    for s in sfide.SFIDE:
        assert s["mondo"] in mondi.MONDI, s["id"]


def test_sfida_non_verificata_se_il_programma_ha_un_errore(esecutore_veloce):
    esito = esecutore_veloce.esegui("1/0\n", mondo="sfida_viaggio", sfida="viaggio")
    assert esito is None
