"""Server da eseguire sul robot (es. sulla parte Linux di Arduino UNO Q).

Riceve i comandi dall'app RoboBlocchi sulla rete locale:
    GET /avanti?cm=20       GET /indietro?cm=20
    GET /gira?direzione=destra&gradi=90
    GET /ferma              GET /distanza  -> {"cm": 42.0}
    GET /linea?lato=sinistro -> {"nero": true}
    GET /led?colore=rosso   (rosso, verde, blu, giallo, bianco, viola, spento)
    GET /suona?frequenza=440&secondi=0.5
    GET /foto               -> immagine JPEG dalla telecamera del robot

Avvio:  python3 server.py --porta 8000

Le funzioni nella sezione HARDWARE sono segnaposto: vanno collegate ai motori
e al sensore. Su Arduino UNO Q i motori sono comandati dal microcontrollore,
a cui la parte Linux invia i comandi (vedi la documentazione di Arduino App Lab).
Solo la libreria standard è obbligatoria; OpenCV serve per /foto.
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# ============================== HARDWARE ======================================
# TODO: sostituire con i comandi reali verso i motori e i sensori.


def motori_avanti(cm):
    print(f"[motori] avanti {cm} cm")


def motori_indietro(cm):
    print(f"[motori] indietro {cm} cm")


def motori_gira(direzione, gradi):
    print(f"[motori] gira a {direzione} di {gradi} gradi")


def motori_ferma():
    print("[motori] stop")


def leggi_distanza_cm():
    return 100.0  # valore finto finché non c'è il sensore


def sensore_linea_nero(lato):
    return False  # TODO: leggere il sensore IR "sinistro" o "destro"


def imposta_led(colore):
    print(f"[led] {colore}")


def suona(frequenza, secondi):
    print(f"[cicalino] {frequenza} Hz per {secondi} s")


def scatta_foto(indice=0):
    import cv2

    cam = cv2.VideoCapture(indice)
    try:
        for _ in range(5):
            cam.read()
        ok, frame = cam.read()
        if not ok:
            raise RuntimeError("telecamera non disponibile")
        h, w = frame.shape[:2]
        if w > 640:
            frame = cv2.resize(frame, (640, int(h * 640 / w)))
        return cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])[1].tobytes()
    finally:
        cam.release()

# ==============================================================================


class Gestore(BaseHTTPRequestHandler):
    def _rispondi(self, codice, corpo, tipo="application/json"):
        if isinstance(corpo, (dict, list)):
            corpo = json.dumps(corpo).encode("utf-8")
        self.send_response(codice)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        url = urlparse(self.path)
        p = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/avanti":
                motori_avanti(float(p.get("cm", 0)))
            elif url.path == "/indietro":
                motori_indietro(float(p.get("cm", 0)))
            elif url.path == "/gira":
                direzione = p.get("direzione", "destra")
                if direzione not in ("destra", "sinistra"):
                    return self._rispondi(400, {"errore": "direzione non valida"})
                motori_gira(direzione, float(p.get("gradi", 0)))
            elif url.path == "/ferma":
                motori_ferma()
            elif url.path == "/distanza":
                return self._rispondi(200, {"cm": leggi_distanza_cm()})
            elif url.path == "/linea":
                lato = p.get("lato", "sinistro")
                if lato not in ("sinistro", "destro"):
                    return self._rispondi(400, {"errore": "lato non valido"})
                return self._rispondi(200, {"nero": bool(sensore_linea_nero(lato))})
            elif url.path == "/led":
                imposta_led(p.get("colore", "spento"))
            elif url.path == "/suona":
                suona(float(p.get("frequenza", 440)), float(p.get("secondi", 0.5)))
            elif url.path == "/foto":
                return self._rispondi(200, scatta_foto(), "image/jpeg")
            else:
                return self._rispondi(404, {"errore": "comando sconosciuto"})
        except Exception as e:  # noqa: BLE001 - l'errore viene restituito all'app
            return self._rispondi(500, {"errore": str(e)})
        self._rispondi(200, {"ok": True})


def main():
    parser = argparse.ArgumentParser(description="Server robot per RoboBlocchi")
    parser.add_argument("--porta", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("0.0.0.0", args.porta), Gestore)
    print(f"Robot in ascolto sulla porta {args.porta}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        motori_ferma()


if __name__ == "__main__":
    main()
