# Novità

Tutte le modifiche importanti del progetto sono elencate qui.
Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.1.0/) e le versioni seguono il
[versionamento semantico](https://semver.org/lang/it/).

## [Non ancora rilasciato]

### Aggiunto
- Installer per Windows (Inno Setup) e pacchetti per macOS e Linux, costruiti automaticamente a ogni
  versione, in due varianti: completa e base
- Icona dell'applicazione
- Test automatici (Python e blocchi) eseguiti su ogni modifica
- Controllo `--verifica` dell'app costruita, senza aprire finestre
- File per la comunità: guida per contribuire, codice di condotta, privacy, sicurezza, modelli per le issue

### Modificato
- OpenCV nella variante *headless* (più leggera, nessun conflitto con l'interfaccia su Linux)

## [0.2.0] - 2026-11-07

### Aggiunto
- Robot virtuale con mondi (arena, ostacoli, percorso con linea, labirinto), urti e traccia del percorso
- Sensori di distanza e di linea; comportamenti *segui la linea* ed *evita gli ostacoli*
- LED colorato e note musicali
- Blocchi di visione: *leggi il testo*, *quanti … vedo*, *colore davanti a me*
- Blocco *perché?*: l'IA spiega la sua ultima risposta
- Foto analizzate mostrate nella console e anteprima della telecamera
- Voce (di sistema o Piper) e ascolto con Whisper, offline
- Esecuzione passo-passo
- Esportazione del programma in Python
- Sette sfide guidate con verifica automatica
- Interfaccia semplice per i più piccoli

## [0.1.0] - 2026-11-07

### Aggiunto
- Prima versione: editor a blocchi in italiano, codice Python in tempo reale, robot simulato, collegamento
  a Ollama, server di esempio per il robot
