# Come contribuire a RoboBlocchi

Grazie per l'interesse! RoboBlocchi nasce per la scuola e cresce grazie a chi lo usa: **non serve essere
programmatori** per dare una mano.

Partecipando al progetto accetti il nostro [codice di condotta](CODE_OF_CONDUCT.md).

## Modi per contribuire

| Se sei… | Puoi… |
|---|---|
| **Docente** | provarlo in classe e raccontarci com'è andata, proporre o scrivere schede di attività, suggerire nuove sfide |
| **Studente** | segnalare cose poco chiare, proporre blocchi, correggere testi, scrivere codice (con la guida del tuo docente) |
| **Maker** | costruire il robot reale, documentare componenti e collegamenti, migliorare il server del robot |
| **Sviluppatore** | correggere bug, aggiungere blocchi, mondi e sfide, migliorare build e test |
| **Traduttore** | tradurre interfaccia e documentazione in altre lingue |

## Segnalare un problema o proporre un'idea

Apri una *issue* scegliendo il modello adatto: **Segnalazione di un problema**, **Proposta di una
funzione** oppure **Attività didattica**. Prima, dai un'occhiata alle issue già aperte: magari qualcuno
ha già segnalato la stessa cosa e puoi aggiungere un commento.

Per i problemi di sicurezza **non** aprire una issue pubblica: segui [SECURITY.md](SECURITY.md).

## Preparare l'ambiente di sviluppo

Servono Python 3.10+ e, per i test dei blocchi, Node.js 22+.

```bash
git clone <indirizzo del repository>
cd roboblocchi
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -r requirements-voce.txt   # facoltativo
npm install                            # solo per i test dei blocchi

python app/main.py --debug             # avvia l'app con gli strumenti di sviluppo
```

## Test

Prima di proporre una modifica, esegui i test:

```bash
python -m pytest        # Python: simulatore, sfide, esecuzione, IA (con Ollama finto), robot in rete…
npm test                # i blocchi generano il Python atteso
```

I test non richiedono webcam, microfono né Ollama: usano versioni finte. Vengono eseguiti
automaticamente su ogni *pull request*. Se aggiungi una funzione, aggiungi anche un test:
gli esempi in `tests/` mostrano come fare.

## Proporre una modifica (pull request)

1. Fai un *fork* del progetto e crea un ramo con un nome chiaro (`blocco-temperatura`, `correzione-urti`…)
2. Fai modifiche piccole e mirate: una pull request = un argomento
3. Esegui i test
4. Aggiorna la documentazione se serve (README, CHANGELOG nella sezione *Non ancora rilasciato*)
5. Apri la pull request compilando il modello

Va benissimo aprire una pull request in bozza per chiedere un parere prima di finire.

## Convenzioni

- **Lingua**: codice, commenti, messaggi e documentazione sono **in italiano**. È una scelta voluta:
  il progetto è pensato anche perché gli studenti possano leggerne il codice.
- **Python**: stile PEP 8, righe fino a ~110 caratteri, nomi chiari anche a scapito della brevità.
- **Messaggi per l'utente**: brevi, gentili e che dicano cosa fare ("Ollama non risponde: è avviato?").
- **Dipendenze**: aggiungerne una nuova è una decisione importante (pesa sull'installer e sulle scuole
  con PC datati). Parliamone prima in una issue.
- **Privacy**: nessuna funzione può inviare dati fuori dalla rete locale. Vedi [PRIVACY.md](PRIVACY.md).

## Guide rapide

- **Nuovo blocco**: `app/ui/blocchi.js` (aspetto e codice generato) → toolbox in `app/ui/app.js` →
  funzione Python in `app/robot.py`, `app/ia.py` o `app/esecutore.py` → test in `tests/generatori.test.js`
- **Nuovo mondo**: `app/mondi.py` (aggiungilo a `MONDI_LIBERI` per mostrarlo nell'elenco)
- **Nuova sfida**: un mondo in `app/mondi.py` + una voce in `SFIDE` di `app/sfide.py` con la funzione di
  verifica + due casi in `tests/test_sfide.py` (uno che la supera, uno che la fallisce)
- **Nuovo comando hardware**: anche in `robot_server/server.py` e in `RobotRete` (`app/robot.py`)

## Rilasciare una nuova versione (per i maintainer)

1. Aggiorna `VERSIONE` in `app/versione.py` e sposta le voci del CHANGELOG sotto il nuovo numero
2. Crea e pubblica il tag: `git tag v0.3.0 && git push origin v0.3.0`
3. La pipeline *Rilascio* costruisce installer e archivi per Windows, macOS e Linux e pubblica la release

## Licenza dei contributi

Contribuendo accetti che il tuo contributo sia distribuito con la stessa licenza del progetto
(**GNU GPL v3 o successiva**). Schede didattiche e documentazione sono benvenute anche con licenza
**CC BY-SA 4.0**, da indicare nel file.
