import threading
from http.server import ThreadingHTTPServer

import pytest

import server as server_robot
from robot import RobotRete


@pytest.fixture
def robot_in_rete(monkeypatch):
    comandi = []
    monkeypatch.setattr(server_robot, "motori_avanti", lambda cm: comandi.append(("avanti", cm)))
    monkeypatch.setattr(server_robot, "motori_indietro", lambda cm: comandi.append(("indietro", cm)))
    monkeypatch.setattr(server_robot, "motori_gira", lambda d, g: comandi.append(("gira", d, g)))
    monkeypatch.setattr(server_robot, "imposta_led", lambda c: comandi.append(("led", c)))
    monkeypatch.setattr(server_robot, "sensore_linea_nero", lambda lato: lato == "destro")
    monkeypatch.setattr(server_robot, "leggi_distanza_cm", lambda: 42.5)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server_robot.Gestore)
    srv.RequestHandlerClass.log_message = lambda *a: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield RobotRete(f"http://127.0.0.1:{srv.server_address[1]}"), comandi
    srv.shutdown()


def test_comandi_arrivano_al_robot(robot_in_rete):
    robot, comandi = robot_in_rete
    robot.avanti(10)
    robot.indietro(5)
    robot.gira("sinistra", 45)
    robot.accendi_led("blu")
    assert comandi == [("avanti", 10.0), ("indietro", 5.0), ("gira", "sinistra", 45.0), ("led", "blu")]


def test_sensori_dal_robot(robot_in_rete):
    robot, _ = robot_in_rete
    assert robot.distanza() == 42.5
    assert robot.linea("destro") and not robot.linea("sinistro")


def test_robot_irraggiungibile():
    with pytest.raises(RuntimeError, match="non raggiungibile"):
        RobotRete("http://127.0.0.1:9", timeout=1).avanti(10)
