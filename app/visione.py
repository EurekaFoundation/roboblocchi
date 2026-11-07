"""Telecamera del PC (condivisa tra anteprima e programma) e analisi semplici delle immagini."""

import threading
import time

LARGHEZZA_MAX = 640       # immagini piccole = risposte più veloci dal modello
RILASCIO_DOPO_S = 4       # la webcam si spegne dopo qualche secondo di inutilizzo


def _cv2():
    try:
        import cv2
        return cv2
    except ImportError as e:
        raise RuntimeError("OpenCV non è installato: esegui 'pip install opencv-python'") from e


class Telecamera:
    """Una sola webcam aperta per tutta l'app, usata da anteprima e blocchi."""

    def __init__(self, indice=0):
        self.indice = int(indice)
        self._cam = None
        self._lock = threading.Lock()
        self._ultimo_uso = 0.0
        threading.Thread(target=self._sorveglia, daemon=True).start()

    def imposta_indice(self, indice):
        indice = int(indice)
        if indice != self.indice:
            with self._lock:
                self._chiudi()
                self.indice = indice

    def foto(self):
        cv2 = _cv2()
        with self._lock:
            self._ultimo_uso = time.monotonic()
            if self._cam is None:
                self._cam = cv2.VideoCapture(self.indice)
                if not self._cam.isOpened():
                    self._chiudi()
                    raise RuntimeError(f"Impossibile aprire la webcam n. {self.indice}")
                for _ in range(5):        # le prime immagini sono spesso scure
                    self._cam.read()
            self._cam.grab()              # scarta l'immagine rimasta nel buffer
            ok, frame = self._cam.read()
            if not ok:
                self._chiudi()
                raise RuntimeError("La webcam non ha restituito nessuna immagine")
        return codifica_jpeg(frame)

    def _chiudi(self):
        if self._cam is not None:
            self._cam.release()
            self._cam = None

    def _sorveglia(self):
        while True:
            time.sleep(1)
            with self._lock:
                if self._cam is not None and time.monotonic() - self._ultimo_uso > RILASCIO_DOPO_S:
                    self._chiudi()


def codifica_jpeg(frame):
    cv2 = _cv2()
    altezza, larghezza = frame.shape[:2]
    if larghezza > LARGHEZZA_MAX:
        frame = cv2.resize(frame, (LARGHEZZA_MAX, int(altezza * LARGHEZZA_MAX / larghezza)))
    ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        raise RuntimeError("Errore nella conversione della foto")
    return jpeg.tobytes()


def colore_dominante(jpeg):
    """Nome (in italiano) del colore prevalente nella zona centrale dell'immagine."""
    cv2 = _cv2()
    import numpy as np

    img = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("Foto non valida")
    h, w = img.shape[:2]
    centro = img[int(h * .35):int(h * .65), int(w * .35):int(w * .65)]
    hsv = cv2.cvtColor(centro, cv2.COLOR_BGR2HSV).reshape(-1, 3).astype(int)
    tinta, saturazione, luminosita = (int(np.median(hsv[:, i])) for i in range(3))
    return nome_colore(tinta, saturazione, luminosita)


def nome_colore(h, s, v):
    """h in 0-179, s e v in 0-255 (scala OpenCV)."""
    if v < 50:
        return "nero"
    if s < 45:
        return "bianco" if v > 190 else "grigio"
    for limite, nome in ((8, "rosso"), (20, "arancione"), (34, "giallo"), (85, "verde"),
                         (100, "azzurro"), (130, "blu"), (150, "viola"), (170, "rosa")):
        if h < limite:
            return nome
    return "rosso"
