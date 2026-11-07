"""Esegue in un thread separato il codice Python generato dai blocchi.

Il codice generato può usare solo i nomi messi a disposizione qui:
robot, ia, dici, ascolta, attendi, più le funzioni interne evidenzia e
controlla_stop che Blockly inserisce per evidenziare i blocchi, fermare
il programma e permettere l'esecuzione passo-passo.
"""

import threading
import time
import traceback

import sfide
from ia import IA
from robot import RobotRete, RobotSimulato
from voce import Ascolto, Voce


class Interrotto(Exception):
    """Sollevata quando l'utente preme Ferma."""


def _nessuno(*_a, **_k):
    pass


class Esecutore:
    def __init__(self, simulatore, telecamera, log, evidenzia=None, fine=None,
                 mostra_foto=None, suono=None, esito_sfida=None, in_pausa=None):
        self.simulatore = simulatore
        self.telecamera = telecamera
        self._log = log
        self._evidenzia = evidenzia or _nessuno
        self._fine = fine or _nessuno
        self._mostra_foto = mostra_foto or _nessuno
        self._suono = suono or _nessuno
        self._esito_sfida = esito_sfida or _nessuno
        self._in_pausa = in_pausa or _nessuno
        self._stop = threading.Event()
        self._avanza = threading.Event()
        self._passo = False
        self._thread = None
        self._voce = None
        self._ascolto = None

    @property
    def in_esecuzione(self):
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------ controlli
    def avvia(self, codice, impostazioni, opzioni=None):
        if self.in_esecuzione:
            return False
        opzioni = opzioni or {}
        self._stop.clear()
        self._avanza.clear()
        self._passo = bool(opzioni.get("passo"))
        self._thread = threading.Thread(target=self._esegui, args=(codice, impostazioni, opzioni), daemon=True)
        self._thread.start()
        return True

    def ferma(self):
        self._stop.set()
        self._avanza.set()

    def passo(self):
        """Esegue il blocco successivo (in modalità passo-passo)."""
        self._passo = True
        self._avanza.set()

    def continua(self):
        """Esce dalla modalità passo-passo e prosegue normalmente."""
        self._passo = False
        self._avanza.set()

    # ----------------------------------------- funzioni a disposizione del programma
    def _controlla_stop(self):
        if self._stop.is_set():
            raise Interrotto()

    def _attendi(self, secondi):
        """Pausa che si interrompe subito se l'utente preme Ferma."""
        if self._stop.wait(max(0.0, float(secondi))):
            raise Interrotto()

    def _evidenzia_e_aspetta(self, id_blocco):
        self._controlla_stop()
        self._evidenzia(id_blocco)
        if self._passo:
            self._in_pausa(True)
            while not self._avanza.wait(0.1):
                pass
            self._avanza.clear()
            self._in_pausa(False)
            self._controlla_stop()

    def _prepara_voce(self, imp):
        motore, modello = imp.get("motore_voce", "sistema"), imp.get("modello_piper", "")
        if self._voce is None or (self._voce.motore, self._voce.modello_piper) != (motore, modello):
            self._voce = Voce(motore, modello, self._log)
        nome_whisper = imp.get("modello_whisper", "base")
        if self._ascolto is None or self._ascolto.nome_modello != nome_whisper:
            self._ascolto = Ascolto(nome_whisper, self._log)

    def crea_ambiente(self, imp, detti):
        log = self._log
        comuni = {"log": log, "controlla_stop": self._controlla_stop, "mostra_foto": self._mostra_foto}
        if imp.get("modalita_robot") == "rete":
            robot = RobotRete(imp["indirizzo_robot"], **comuni)
        else:
            self.telecamera.imposta_indice(imp.get("indice_webcam", 0))
            robot = RobotSimulato(self.simulatore, self._attendi, self.telecamera.foto, self._suono, **comuni)

        ia = IA(imp["url_ollama"], imp["modello"], robot.foto, log, self._mostra_foto)
        self._prepara_voce(imp)
        voce_attiva = imp.get("voce_attiva", True)

        def dici(*valori):
            self._controlla_stop()
            testo = " ".join(str(v) for v in valori)
            detti.append(testo)
            log(testo, "dici")
            if voce_attiva:
                try:
                    self._voce.parla(testo, self._stop)
                except RuntimeError as e:
                    log(f"🔇 {e}", "errore")
            self._controlla_stop()

        def ascolta(secondi=4):
            self._controlla_stop()
            testo = self._ascolto.ascolta(secondi, self._stop)
            self._controlla_stop()
            return testo

        return {
            "__name__": "__programma__",
            "robot": robot,
            "ia": ia,
            "dici": dici,
            "ascolta": ascolta,
            "print": dici,  # il blocco standard "stampa" scrive nella console e parla
            "attendi": self._attendi,
            "evidenzia": self._evidenzia_e_aspetta,
            "controlla_stop": self._controlla_stop,
        }

    # ------------------------------------------------------------ esecuzione
    def _esegui(self, codice, impostazioni, opzioni):
        robot = None
        completato = False
        detti = []
        simulato = impostazioni.get("modalita_robot") != "rete"
        try:
            if simulato:
                self.simulatore.reset()
            ambiente = self.crea_ambiente(impostazioni, detti)
            robot = ambiente["robot"]
            self._log("▶ Programma avviato" + (" (passo-passo)" if self._passo else ""), "sistema")
            inizio = time.monotonic()
            exec(compile(codice, "<programma>", "exec"), ambiente)
            completato = True
            self._log(f"✔ Programma terminato ({time.monotonic() - inizio:.1f} s)", "sistema")
        except Interrotto:
            self._log("■ Programma fermato", "sistema")
        except RuntimeError as e:
            self._log(f"⚠ {e}", "errore")
        except Exception as e:  # errori nel programma dello studente
            riga = ""
            for f in reversed(traceback.extract_tb(e.__traceback__)):
                if f.filename == "<programma>":
                    riga = f" (riga {f.lineno})"
                    break
            self._log(f"⚠ Errore nel programma{riga}: {type(e).__name__}: {e}", "errore")
        finally:
            if robot is not None and self._stop.is_set():
                try:
                    robot._ferma()
                except Exception:
                    pass
            self._evidenzia(None)
            self._in_pausa(False)

        id_sfida = opzioni.get("sfida")
        if completato and id_sfida:
            if simulato:
                esito = sfide.verifica(id_sfida, {"sim": self.simulatore, "detti": detti,
                                                 "num_blocchi": int(opzioni.get("num_blocchi") or 0)})
            else:
                esito = {"riuscita": False, "titolo": "", "messaggio":
                         "Le sfide si verificano con il robot virtuale (Impostazioni → Robot simulato)."}
            if esito:
                self._esito_sfida(esito)
        self._fine()
