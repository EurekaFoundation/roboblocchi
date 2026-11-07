"""Voce del robot (sintesi vocale) e ascolto (riconoscimento vocale), entrambi offline.

Sintesi vocale:
- motore "sistema": usa la voce già presente nel sistema operativo
    Windows -> System.Speech (PowerShell), macOS -> say, Linux -> espeak-ng / espeak / spd-say
- motore "piper": voce neurale Piper (pip install piper-tts + un modello .onnx italiano)

Ascolto: faster-whisper + sounddevice (pip install faster-whisper sounddevice).
Il modello Whisper viene scaricato automaticamente al primo uso.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import threading
import wave

FREQUENZA_ASCOLTO = 16000


def _nessuno(*_a, **_k):
    pass


def _attendi_processo(proc, stop):
    """Aspetta la fine del processo; se viene premuto Ferma lo chiude."""
    while proc.poll() is None:
        if stop is not None and stop.wait(0.05):
            proc.kill()
            proc.wait()
            return False
    return True


def _avvia(comando, env=None):
    opzioni = {}
    if sys.platform == "win32":
        opzioni["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    return subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            env=env, **opzioni)


# =============================================================== sintesi vocale

_PS_SINTESI = (
    "Add-Type -AssemblyName System.Speech;"
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
    "$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like 'it*' } | Select-Object -First 1;"
    "if ($v) { $s.SelectVoice($v.VoiceInfo.Name) };"
    "$s.Speak($env:ROBOBLOCCHI_TESTO)"
)


class Voce:
    def __init__(self, motore="sistema", modello_piper="", log=None):
        self.motore = motore
        self.modello_piper = modello_piper
        self._log = log or _nessuno
        self._voce_piper = None
        self._voce_mac = None

    def parla(self, testo, stop=None):
        testo = str(testo).strip()
        if not testo:
            return
        if self.motore == "piper":
            self._parla_piper(testo, stop)
        else:
            self._parla_sistema(testo, stop)

    # ---------------------------------------------------------------- sistema
    def comando_sistema(self, testo):
        if sys.platform == "win32":
            return ["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_SINTESI], True
        if sys.platform == "darwin":
            voce = self._voce_italiana_mac()
            return (["say", "-v", voce, testo] if voce else ["say", testo]), False
        for programma, args in (("espeak-ng", ["-v", "it"]), ("espeak", ["-v", "it"]),
                                ("spd-say", ["-l", "it", "-w"])):
            if shutil.which(programma):
                return [programma, *args, testo], False
        raise RuntimeError("Nessuna voce di sistema trovata: installa espeak-ng "
                           "(es. sudo apt install espeak-ng) oppure usa il motore Piper")

    def _voce_italiana_mac(self):
        if self._voce_mac is None:
            self._voce_mac = ""
            try:
                elenco = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, timeout=10).stdout
                for riga in elenco.splitlines():
                    if "it_IT" in riga:
                        self._voce_mac = riga.split("  ")[0].strip()
                        break
            except (OSError, subprocess.SubprocessError):
                pass
        return self._voce_mac

    def _parla_sistema(self, testo, stop):
        comando, via_ambiente = self.comando_sistema(testo)
        env = None
        if via_ambiente:  # il testo passa da una variabile d'ambiente: niente problemi di virgolette
            env = dict(os.environ, ROBOBLOCCHI_TESTO=testo)
        _attendi_processo(_avvia(comando, env), stop)

    # ------------------------------------------------------------------ piper
    def _parla_piper(self, testo, stop):
        if not self.modello_piper or not os.path.isfile(self.modello_piper):
            raise RuntimeError("Per la voce Piper indica nelle impostazioni il file del modello (.onnx)")
        try:
            from piper import PiperVoice
        except ImportError as e:
            raise RuntimeError("Piper non è installato: esegui 'pip install piper-tts'") from e
        if self._voce_piper is None:
            self._log("🔊 carico la voce Piper…", "sistema")
            self._voce_piper = PiperVoice.load(self.modello_piper)

        fd, percorso = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            with wave.open(percorso, "wb") as wav:
                if hasattr(self._voce_piper, "synthesize_wav"):   # piper-tts >= 1.3
                    self._voce_piper.synthesize_wav(testo, wav)
                else:                                             # versioni precedenti
                    self._voce_piper.synthesize(testo, wav)
            riproduci_wav(percorso, stop)
        finally:
            try:
                os.remove(percorso)
            except OSError:
                pass


def riproduci_wav(percorso, stop=None):
    if sys.platform == "win32":
        import winsound
        with wave.open(percorso) as w:
            durata = w.getnframes() / float(w.getframerate())
        winsound.PlaySound(percorso, winsound.SND_FILENAME | winsound.SND_ASYNC)
        if stop is not None and stop.wait(durata):
            winsound.PlaySound(None, 0)
        elif stop is None:
            threading.Event().wait(durata)
        return
    if sys.platform == "darwin":
        comando = ["afplay", percorso]
    else:
        programma = next((p for p in ("pw-play", "paplay", "aplay") if shutil.which(p)), None)
        if programma is None:
            raise RuntimeError("Nessun programma per riprodurre l'audio (installa alsa-utils)")
        comando = [programma, percorso]
    _attendi_processo(_avvia(comando), stop)


# ===================================================================== ascolto

class Ascolto:
    def __init__(self, modello="base", log=None):
        self.nome_modello = modello
        self._log = log or _nessuno
        self._modello = None

    def _carica(self):
        if self._modello is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as e:
                raise RuntimeError("Per ascoltare installa: pip install faster-whisper sounddevice") from e
            self._log(f"👂 preparo il riconoscimento vocale (modello {self.nome_modello})…", "sistema")
            self._modello = WhisperModel(self.nome_modello, device="cpu", compute_type="int8")
        return self._modello

    def registra(self, secondi, stop=None):
        try:
            import sounddevice as sd
        except (ImportError, OSError) as e:
            raise RuntimeError("Per ascoltare installa: pip install sounddevice") from e
        campioni = int(float(secondi) * FREQUENZA_ASCOLTO)
        audio = sd.rec(campioni, samplerate=FREQUENZA_ASCOLTO, channels=1, dtype="float32")
        if stop is not None and stop.wait(float(secondi)):
            sd.stop()
            return None
        sd.wait()
        return audio.reshape(-1)

    def ascolta(self, secondi, stop=None):
        modello = self._carica()
        self._log(f"👂 ascolto per {secondi:g} secondi…", "ia")
        audio = self.registra(secondi, stop)
        if audio is None:
            return ""
        segmenti, _info = modello.transcribe(audio, language="it", vad_filter=True)
        testo = " ".join(s.text.strip() for s in segmenti).strip()
        self._log(f"👂 ho sentito: «{testo}»" if testo else "👂 non ho sentito niente", "ia")
        return testo
