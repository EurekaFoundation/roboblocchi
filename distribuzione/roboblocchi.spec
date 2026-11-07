# Configurazione PyInstaller di RoboBlocchi.
#
# Uso (dalla cartella principale del progetto):
#     pyinstaller distribuzione/roboblocchi.spec
# oppure, più semplice:
#     python distribuzione/costruisci.py
#
# Variante (variabile d'ambiente ROBOBLOCCHI_VARIANTE, la imposta costruisci.py):
#   completo -> include ascolto e voce Piper (faster-whisper, sounddevice, piper-tts),
#               che devono essere installati: pip install -r requirements-voce.txt
#   base     -> più leggera: ascolto e voce Piper esclusi (la voce di sistema funziona)

import importlib.util
import os
import sys

from PyInstaller.utils.hooks import collect_all

RADICE = os.path.dirname(SPECPATH)
APP = os.path.join(RADICE, "app")
sys.path.insert(0, APP)
from versione import VERSIONE  # noqa: E402

VARIANTE = os.environ.get("ROBOBLOCCHI_VARIANTE", "completo")
FACOLTATIVI = ("faster_whisper", "ctranslate2", "av", "piper", "onnxruntime", "sounddevice", "_sounddevice_data")

datas = [(os.path.join(APP, "ui"), "ui")]
binaries = []
hiddenimports = []
# pacchetti che a volte arrivano come dipendenze indirette ma non servono all'app
excludes = ["tkinter", "matplotlib", "IPython", "pytest", "pandas", "scipy", "torch"]

for pacchetto in FACOLTATIVI:
    if VARIANTE == "base":
        excludes.append(pacchetto)
    elif importlib.util.find_spec(pacchetto) is not None:
        d, b, h = collect_all(pacchetto)
        datas += d
        binaries += b
        hiddenimports += h

if sys.platform == "win32":
    icona = os.path.join(SPECPATH, "icona.ico")
elif sys.platform == "darwin":
    icona = os.path.join(SPECPATH, "icona.icns")
else:
    icona = None

a = Analysis(
    [os.path.join(APP, "main.py")],
    pathex=[APP],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + ["roboblocchi"],
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RoboBlocchi",
    console=False,
    icon=icona,
    upx=False,
)

coll = COLLECT(exe, a.binaries, a.datas, name="RoboBlocchi", upx=False)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="RoboBlocchi.app",
        icon=icona,
        bundle_identifier="org.roboblocchi.app",
        version=VERSIONE,
        info_plist={
            "CFBundleShortVersionString": VERSIONE,
            "NSHighResolutionCapable": True,
            # macOS chiede il permesso all'utente: senza queste frasi l'app verrebbe chiusa
            "NSCameraUsageDescription": "RoboBlocchi usa la webcam per mostrare all'IA cosa vede il robot.",
            "NSMicrophoneUsageDescription": "RoboBlocchi usa il microfono per il blocco «ascolta».",
        },
    )
