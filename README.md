# RoboBlocchi

**Robotica didattica a blocchi con intelligenza artificiale locale.**

RoboBlocchi è un'applicazione libera per la scuola: gli studenti programmano un robot con i blocchi
(come in Scratch) e possono usare un modello di intelligenza artificiale che **vede** attraverso la
telecamera, **ascolta**, **parla** e **risponde** alle domande. Tutto funziona **in locale**: immagini
e voci non escono mai dalla rete della scuola, nessun account, nessun servizio cloud.

> Stato: prototipo (v0.2). Cerchiamo docenti e sviluppatori che vogliano provarlo e contribuire:
> leggi [come contribuire](CONTRIBUTING.md).

## Scaricare

Dalla pagina **Releases** del progetto scarica il file per il tuo sistema:

- **Windows**: `RoboBlocchi-…-installer-windows.exe` — si installa anche senza diritti di amministratore
- **macOS**: `RoboBlocchi-…-macos.zip` — estrai e, al primo avvio, clic destro sull'app → *Apri*
- **Linux**: `RoboBlocchi-…-linux.tar.gz` — estrai e avvia `RoboBlocchi/RoboBlocchi`

Ogni file esiste in due varianti: **completa** (consigliata) e **base**, più leggera, senza il blocco
*ascolta* e la voce Piper. Poi installa Ollama e un modello (vedi *Requisiti*).

## Cosa sa fare

**Programmazione**
- Editor a blocchi in italiano (basato su [Blockly](https://developers.google.com/blockly)), funziona offline
- Codice **Python** generato in tempo reale accanto ai blocchi, ed **esportabile** in un file `.py`
- **Esecuzione passo-passo**: un blocco alla volta, con il blocco in corso evidenziato
- Il pulsante **Ferma** interrompe anche i cicli infiniti
- **Interfaccia semplice** per i più piccoli: meno blocchi, più grandi

**Robot**
- **Robot virtuale** sullo schermo, con mondi diversi (arena, ostacoli, percorso con linea, labirinto):
  si può usare in classe anche senza nessun robot fisico
- Movimenti, LED colorato, note musicali
- Sensori: distanza dall'ostacolo, due sensori di linea
- Comportamenti pronti: *segui la linea*, *gira libero evitando gli ostacoli*
- **Robot vero** (es. Arduino UNO Q) comandato sulla rete locale con gli stessi blocchi

**Intelligenza artificiale**
- Visione: *cosa vedo*, *vedo …?*, *quanti … vedo*, *leggi il testo che vedo*, *guarda e rispondi a …*
- *Colore davanti a me*: calcolato senza IA (utile per confrontare i due approcci)
- **Perché?**: l'IA spiega su cosa si è basata per l'ultima risposta, ottimo spunto per parlare di errori
  e affidabilità dei modelli
- Ogni foto analizzata compare nella console: gli studenti vedono su cosa ha "ragionato" il robot
- Anteprima della telecamera nell'app

**Voce**
- Il blocco *di'* parla davvero (voce del sistema operativo oppure Piper, voce neurale)
- Il blocco *ascolta* trasforma in testo ciò che si dice al microfono (Whisper, offline)

**Sfide guidate** con verifica automatica: primo viaggio, il quadrato, usa un ciclo, aggira l'ostacolo,
fermati in tempo, segui la linea, un saluto. Le sfide superate restano segnate.

## Requisiti

- Python 3.10 o successivo
- [Ollama](https://ollama.com) con un modello che supporta le immagini, ad esempio:
  ```
  ollama pull gemma3:4b
  ```
  Ollama può girare sullo stesso PC o su un PC della scuola raggiungibile in rete
  (in quel caso va avviato in modo da accettare connessioni dalla rete locale; vedi la documentazione di Ollama).
- Per la voce di sistema su **Linux**: `sudo apt install espeak-ng` (su Windows e macOS è già presente;
  su Windows conviene installare la voce italiana dalle impostazioni di sistema, se manca)
- Per il blocco *ascolta* su **Linux**: `sudo apt install libportaudio2`
- Su **Windows** serve Microsoft Edge WebView2 Runtime, già presente in Windows 11 e nei Windows 10
  aggiornati (l'installer avvisa se manca)

## Installazione e avvio dal codice sorgente

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-voce.txt   # facoltativo: ascolto e voce Piper
python app/main.py
```

Su **Linux** pywebview ha bisogno di un motore grafico: il modo più semplice è
`pip install "pywebview[qt]"` (in alternativa i pacchetti GTK/WebKit della distribuzione).

Al primo avvio apri **⚙ Impostazioni**, controlla indirizzo di Ollama e modello e premi
**Verifica collegamento**; poi prova la voce con **Prova la voce**.

### Voce Piper (facoltativa)

Piper produce una voce molto più naturale. Dopo `pip install piper-tts`, scarica una voce italiana
(file `.onnx` più il suo `.onnx.json`, ad esempio *it_IT-paola-medium*) dalla raccolta di voci di Piper,
poi nelle impostazioni scegli *Piper* e indica il percorso del file `.onnx`.

### Ascolto

Il modello Whisper scelto nelle impostazioni (tiny, base o small) viene scaricato automaticamente al
primo utilizzo del blocco *ascolta*: serve la connessione a Internet solo quella volta.

Per un'anteprima veloce della sola interfaccia puoi anche aprire `app/ui/index.html` nel browser
(in questo caso i programmi non vengono eseguiti).

## Creare l'applicazione installabile

Di solito non serve: a ogni nuova versione (tag `v…`) la pipeline GitHub *Rilascio* costruisce e
pubblica da sola installer e archivi per Windows, macOS e Linux.

Per costruirla a mano sul proprio computer (sul sistema operativo di destinazione):

```bash
pip install -r requirements.txt -r requirements-voce.txt pyinstaller
python distribuzione/costruisci.py          # variante completa
python distribuzione/costruisci.py --base   # variante leggera
```

Il risultato è nella cartella `dist/`. Su Windows, se è installato
[Inno Setup](https://jrsoftware.org/isinfo.php) 6.3 o successivo, viene creato anche l'installer.
Per controllare l'app costruita senza aprire finestre: `RoboBlocchi --verifica`.

## Programmi esportati

Il pulsante **⬇ Esporta .py** salva il programma come file Python. Per eseguirlo fuori dall'app
copialo nella cartella `app/` e lancia `python nome_del_file.py`: usa la libreria `roboblocchi.py`
e le stesse impostazioni dell'app (il robot virtuale, in questo caso, descrive i movimenti nel terminale).

## Il robot

La cartella `robot_server/` contiene un piccolo server (solo libreria standard di Python, più OpenCV
per la telecamera) da eseguire sul robot:

```bash
python3 robot_server/server.py --porta 8000
```

Le funzioni di motori, sensori, LED e cicalino sono **segnaposto** da collegare all'hardware reale.
Nell'app imposta *Modalità: Robot vero sulla rete locale* e l'indirizzo del robot
(es. `http://192.168.1.50:8000`).

Il protocollo è volutamente semplice (richieste HTTP GET), così si può costruire il robot con
qualsiasi scheda in grado di eseguire Python: Arduino UNO Q, Raspberry Pi, ecc.

## Struttura del progetto

```
app/
  main.py          avvio dell'app e API verso l'interfaccia
  esecutore.py     esegue il codice generato (thread, stop, passo-passo, verifica sfide)
  robot.py         comandi del robot: virtuale e in rete, comportamenti (segui linea, evita ostacoli)
  simulatore.py    fisica del robot virtuale (movimenti, urti, sensori)
  mondi.py         arene del robot virtuale
  sfide.py         sfide guidate e loro verifica
  ia.py            collegamento a Ollama (visione, domande, "perché?")
  visione.py       webcam condivisa e riconoscimento del colore
  voce.py          sintesi vocale e ascolto
  impostazioni.py  impostazioni utente (~/.roboblocchi/impostazioni.json)
  roboblocchi.py   libreria per eseguire i programmi esportati
  ui/
    index.html, stile.css, app.js
    blocchi.js     definizione dei blocchi e codice Python generato
    simulatore.js  disegno del robot virtuale
    vendor/blockly Blockly (Apache 2.0), incluso per il funzionamento offline
robot_server/
  server.py        server da eseguire sul robot
tests/             test automatici (pytest e Node)
distribuzione/     icona, configurazione PyInstaller, installer Windows, script di build
.github/           pipeline di test e rilascio, modelli per issue e pull request
```

### Aggiungere un nuovo blocco

1. Definisci il blocco e il suo generatore Python in `app/ui/blocchi.js`
2. Aggiungilo alla toolbox in `app/ui/app.js` (completa e, se adatto, semplice)
3. Se richiede una nuova funzione, aggiungila in `app/robot.py` (in `RobotBase` se si può costruire
   con i comandi esistenti), in `app/ia.py` o in `app/esecutore.py`
4. Se coinvolge l'hardware, aggiungi il comando anche in `robot_server/server.py`

### Aggiungere una sfida

Aggiungi un mondo in `app/mondi.py` e una voce in `SFIDE` in `app/sfide.py` con la sua funzione di verifica.

## Prossimi passi

- [ ] Firma digitale degli installer (Windows e macOS)
- [ ] Robot di riferimento: distinta componenti, telaio stampabile in 3D, firmware per UNO Q
- [ ] Schede di attività per docenti (primaria, secondaria di primo e secondo grado)
- [ ] Telecamera "virtuale" che inquadra il mondo del robot simulato
- [ ] Editor di mondi e sfide per i docenti
- [ ] Traduzioni in altre lingue

## Contribuire

Segnalazioni, idee, schede didattiche e codice sono benvenuti. Non serve essere programmatori esperti:
anche provare l'app in classe e raccontare com'è andata è un contributo prezioso.

- [Come contribuire](CONTRIBUTING.md): ambiente di sviluppo, test, convenzioni
- [Codice di condotta](CODE_OF_CONDUCT.md)
- [Privacy](PRIVACY.md): dove vanno i dati (utile anche per dirigenti e DPO)
- [Sicurezza](SECURITY.md): come segnalare una vulnerabilità
- [Novità](CHANGELOG.md)

## Licenza

RoboBlocchi è software libero, distribuito con licenza **GNU GPL v3 o successiva** (vedi `LICENSE`).
Blockly è distribuito con licenza Apache 2.0 (vedi `app/ui/vendor/blockly/LICENSE`).
