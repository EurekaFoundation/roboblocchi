"""Acquisizione di una foto dalla webcam del PC (usata in modalità simulata)."""

LARGHEZZA_MAX = 640  # immagini piccole = risposte più veloci dal modello


def scatta_foto(indice=0):
    """Restituisce una foto JPEG (bytes) dalla webcam indicata."""
    try:
        import cv2
    except ImportError as e:
        raise RuntimeError("OpenCV non è installato: esegui 'pip install opencv-python'") from e

    cam = cv2.VideoCapture(int(indice))
    try:
        if not cam.isOpened():
            raise RuntimeError(f"Impossibile aprire la webcam n. {indice}")
        # Le prime immagini sono spesso scure: ne scartiamo alcune
        for _ in range(5):
            cam.read()
        ok, frame = cam.read()
        if not ok:
            raise RuntimeError("La webcam non ha restituito nessuna immagine")
    finally:
        cam.release()

    altezza, larghezza = frame.shape[:2]
    if larghezza > LARGHEZZA_MAX:
        scala = LARGHEZZA_MAX / larghezza
        frame = cv2.resize(frame, (LARGHEZZA_MAX, int(altezza * scala)))

    ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        raise RuntimeError("Errore nella conversione della foto")
    return jpeg.tobytes()
