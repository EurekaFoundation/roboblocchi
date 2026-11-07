"""Fisica semplificata del robot virtuale (nessuna dipendenza grafica).

Il disegno avviene nell'interfaccia: il simulatore invia lo stato tramite la
funzione `disegna`, se presente. Senza interfaccia funziona comunque (test,
programmi esportati).
"""

import math

import mondi

RAGGIO = 8            # il robot è un cerchio di 8 cm di raggio
VELOCITA = 25         # cm/s
VELOCITA_ROT = 180    # gradi/s
FPS = 25
SENSORE_AVANTI = 6    # i sensori di linea sono 6 cm davanti al centro...
SENSORE_LATO = 2      # ...e 2 cm a sinistra/destra
LARGHEZZA_LINEA = 6
PORTATA_DISTANZA = 300


def _distanza_segmento(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    lung2 = dx * dx + dy * dy
    t = 0.0 if lung2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / lung2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


class Simulatore:
    def __init__(self, nome_mondo="vuota", disegna=None):
        self._disegna = disegna
        self.carica(nome_mondo)

    # ------------------------------------------------------------------ stato
    def carica(self, nome_mondo):
        self.mondo = mondi.ottieni(nome_mondo)
        self.reset()

    def reset(self):
        self.x, self.y, self.angolo = (float(v) for v in self.mondo["partenza"])
        self.led = "spento"
        self.urti = 0
        self.percorso = 0.0
        self.rotazione = 0.0
        self._invia(reset=True)

    def stato(self):
        return {"x": round(self.x, 2), "y": round(self.y, 2), "angolo": round(self.angolo % 360, 1),
                "led": self.led, "urti": self.urti, "percorso": round(self.percorso, 1),
                "rotazione": round(self.rotazione, 1)}

    def _invia(self, **extra):
        if self._disegna is not None:
            self._disegna(dict(self.stato(), **extra))

    # ------------------------------------------------------------ collisioni
    def _libero(self, x, y, margine=RAGGIO):
        m = self.mondo
        if x < margine or y < margine or x > m["larghezza"] - margine or y > m["altezza"] - margine:
            return False
        for ox, oy, ow, oh in m["ostacoli"]:
            vx = min(max(x, ox), ox + ow)
            vy = min(max(y, oy), oy + oh)
            if math.hypot(x - vx, y - vy) < margine:
                return False
        return True

    # -------------------------------------------------------------- movimenti
    def muovi(self, cm, attendi):
        """Muove il robot di `cm` (negativo = indietro). Restituisce False se urta."""
        passo = min(VELOCITA / FPS, 1.0)   # passi piccoli: il robot non "salta" gli ostacoli
        segno = 1 if cm >= 0 else -1
        rimanente = abs(cm)
        rad = math.radians(self.angolo)
        while rimanente > 1e-9:
            d = min(passo, rimanente)
            nx = self.x + segno * d * math.cos(rad)
            ny = self.y + segno * d * math.sin(rad)
            if not self._libero(nx, ny):
                self.urti += 1
                self._invia(urto=True)
                return False
            self.x, self.y = nx, ny
            self.percorso += d
            rimanente -= d
            attendi(d / VELOCITA)
            self._invia()
        return True

    def ruota(self, gradi, attendi):
        """Ruota sul posto: gradi positivi = destra (senso orario)."""
        passo = VELOCITA_ROT / FPS
        segno = 1 if gradi >= 0 else -1
        rimanente = abs(gradi)
        while rimanente > 1e-9:
            d = min(passo, rimanente)
            self.angolo += segno * d
            self.rotazione += d
            rimanente -= d
            attendi(d / VELOCITA_ROT)
            self._invia()
        self.angolo %= 360

    def imposta_led(self, colore):
        self.led = colore
        self._invia()

    # ---------------------------------------------------------------- sensori
    def distanza(self):
        """Distanza (cm) dal bordo anteriore del robot al primo ostacolo davanti."""
        rad = math.radians(self.angolo)
        d = 0.0
        while d < PORTATA_DISTANZA:
            px = self.x + (RAGGIO + d) * math.cos(rad)
            py = self.y + (RAGGIO + d) * math.sin(rad)
            if not self._libero(px, py, margine=0.01):
                return round(d, 1)
            d += 0.5
        return float(PORTATA_DISTANZA)

    def posizione_sensore(self, lato):
        rad = math.radians(self.angolo)
        laterale = -SENSORE_LATO if lato == "sinistro" else SENSORE_LATO
        # vettore "destra" del robot = (cos(a+90), sin(a+90))
        return (self.x + SENSORE_AVANTI * math.cos(rad) - laterale * math.sin(rad),
                self.y + SENSORE_AVANTI * math.sin(rad) + laterale * math.cos(rad))

    def su_linea(self, lato):
        punti = self.mondo["linea"]
        if len(punti) < 2:
            return False
        px, py = self.posizione_sensore(lato)
        return any(_distanza_segmento(px, py, *punti[i], *punti[i + 1]) <= LARGHEZZA_LINEA / 2
                   for i in range(len(punti) - 1))

    def in_obiettivo(self):
        ob = self.mondo.get("obiettivo")
        return bool(ob) and math.hypot(self.x - ob[0], self.y - ob[1]) <= ob[2]
