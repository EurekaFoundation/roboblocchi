"""Genera le icone dell'app (PNG, ICO per Windows, ICNS per macOS) con Pillow.

    python distribuzione/crea_icona.py
"""
import os

from PIL import Image, ImageDraw

LATO = 1024
BLU, GIALLO = (31, 58, 95, 255), (255, 209, 102, 255)
CARTELLA = os.path.dirname(os.path.abspath(__file__))


def disegna(lato=LATO):
    s = lato / 32  # il disegno originale è su una griglia 32x32 (come il logo nell'app)
    img = Image.new("RGBA", (lato, lato), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, lato - 1, lato - 1], radius=7 * s, fill=BLU)
    d.rounded_rectangle([5 * s, 11 * s, 27 * s, 26 * s], radius=4.5 * s, fill=GIALLO)   # testa
    d.rectangle([15.2 * s, 5.5 * s, 16.8 * s, 11 * s], fill=GIALLO)                     # antenna
    d.ellipse([13.6 * s, 3.2 * s, 18.4 * s, 8 * s], fill=GIALLO)
    for cx in (11.5, 20.5):                                                              # occhi
        d.ellipse([(cx - 2.8) * s, 15.7 * s, (cx + 2.8) * s, 21.3 * s], fill=BLU)
    return img


if __name__ == "__main__":
    grande = disegna()
    grande.resize((512, 512), Image.LANCZOS).save(os.path.join(CARTELLA, "icona.png"))
    grande.save(os.path.join(CARTELLA, "icona.ico"),
                sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    grande.save(os.path.join(CARTELLA, "icona.icns"))
    print("Icone create in", CARTELLA)
