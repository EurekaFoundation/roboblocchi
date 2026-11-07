"""Costruisce RoboBlocchi per il sistema operativo in uso.

    python distribuzione/costruisci.py

    python distribuzione/costruisci.py --base     (versione leggera, senza ascolto e voce Piper)

Risultato nella cartella dist/ (con "-base" nel nome per la versione leggera):
  - Windows: RoboBlocchi-<versione>-installer-windows.exe  (serve Inno Setup 6.3+, comando iscc)
             e, in ogni caso, RoboBlocchi-<versione>-windows.zip
  - macOS:   RoboBlocchi-<versione>-macos.zip               (contiene RoboBlocchi.app)
  - Linux:   RoboBlocchi-<versione>-linux.tar.gz

Prima installa le dipendenze:  pip install -r requirements.txt pyinstaller
(e, per includere ascolto e voce Piper: pip install -r requirements-voce.txt)
"""

import os
import shutil
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
DIST = os.path.join(RADICE, "dist")
sys.path.insert(0, os.path.join(RADICE, "app"))
from versione import VERSIONE  # noqa: E402


def esegui(*comando):
    print("»", " ".join(comando), flush=True)
    subprocess.run(comando, check=True, cwd=RADICE)


def trova_iscc():
    trovato = shutil.which("iscc")
    if trovato:
        return trovato
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")):
        if base:
            percorso = os.path.join(base, "Inno Setup 6", "ISCC.exe")
            if os.path.isfile(percorso):
                return percorso
    return None


def main():
    base = "--base" in sys.argv
    if not base:
        try:
            import faster_whisper, piper, sounddevice  # noqa: F401,E401
        except Exception:  # noqa: BLE001
            print("! Mancano le dipendenze di voce/ascolto (pip install -r requirements-voce.txt):")
            print("  le funzioni mancanti non saranno incluse. Usa --base per una build leggera voluta.")
    os.environ["ROBOBLOCCHI_VARIANTE"] = "base" if base else "completo"

    if not os.path.isfile(os.path.join(QUI, "icona.ico")):
        esegui(sys.executable, os.path.join(QUI, "crea_icona.py"))

    esegui(sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
           "--distpath", DIST, "--workpath", os.path.join(RADICE, "build"),
           os.path.join(QUI, "roboblocchi.spec"))

    suffisso = "-base" if base else ""
    nome = f"RoboBlocchi-{VERSIONE}{suffisso}"
    prodotti = []
    if sys.platform == "win32":
        prodotti.append(shutil.make_archive(os.path.join(DIST, f"{nome}-windows"), "zip", DIST, "RoboBlocchi"))
        iscc = trova_iscc()
        if iscc:
            esegui(iscc, f"/DVersione={VERSIONE}", f"/DSuffisso={suffisso}", os.path.join(QUI, "roboblocchi.iss"))
            prodotti.append(os.path.join(DIST, f"{nome}-installer-windows.exe"))
        else:
            print("! Inno Setup non trovato: creato solo lo zip (installa Inno Setup 6.3+ per l'installer)")
    elif sys.platform == "darwin":
        archivio = os.path.join(DIST, f"{nome}-macos.zip")
        # ditto conserva permessi e attributi del pacchetto .app
        esegui("ditto", "-c", "-k", "--keepParent", os.path.join(DIST, "RoboBlocchi.app"), archivio)
        prodotti.append(archivio)
    else:
        prodotti.append(shutil.make_archive(os.path.join(DIST, f"{nome}-linux"), "gztar", DIST, "RoboBlocchi"))

    print("\nCreato:")
    for p in prodotti:
        print("  ", p)


if __name__ == "__main__":
    main()
