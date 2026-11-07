# Privacy: dove vanno i dati

*Una pagina pensata anche per dirigenti scolastici, DPO e famiglie.*

## In breve

**RoboBlocchi non invia nessun dato su Internet.** Immagini della webcam, voci registrate dal microfono,
programmi e impostazioni restano sul computer dell'utente o, al massimo, nella rete locale della scuola.
Non ci sono account, registrazioni, pubblicità, statistiche d'uso o servizi cloud.

## Cosa tratta l'app e dove

| Dato | Quando | Dove va | Conservato? |
|---|---|---|---|
| **Foto dalla webcam** | solo quando il programma usa un blocco di Visione, o con la scheda *Telecamera* aperta | al modello di IA su **Ollama**, che gira sullo stesso PC o su un PC della rete scolastica | No: restano in memoria per la durata del programma e compaiono nella console dell'app finché non la si pulisce |
| **Audio dal microfono** | solo durante il blocco *ascolta*, per i secondi indicati | trascritto **sul PC stesso** (Whisper) | No: l'audio viene scartato subito dopo la trascrizione |
| **Testi pronunciati** (blocco *di'*) | durante il programma | sintesi vocale **sul PC stesso** | No |
| **Programmi (blocchi)** | sempre | sul PC: bozza automatica dell'interfaccia e file `.robo` salvati dall'utente | Sì, finché l'utente non li elimina |
| **Impostazioni** | quando si salvano | file `impostazioni.json` nella cartella `.roboblocchi` dell'utente | Sì |
| **Avanzamento sfide** | quando una sfida viene superata | sul PC (memoria dell'interfaccia) | Sì |
| **Comandi al robot** | in modalità *robot vero* | al robot, nella **rete locale** | Dipende dal robot (il server di esempio non salva nulla) |

## Le uniche connessioni verso Internet

- **Primo utilizzo del blocco *ascolta***: il modello di riconoscimento vocale Whisper viene scaricato una
  volta sola. Non viene inviato nessun audio: si scarica solo il modello.
- **Scaricare i modelli di IA** con Ollama (`ollama pull …`) e le voci Piper è un'operazione che fa
  l'utente, separata dall'app.

Dopo questi download l'app funziona anche senza connessione.

## Consigli per l'uso a scuola

- **Ollama su un PC della scuola**: se un solo PC fa da "cervello" per la classe, le foto viaggiano nella
  rete locale fino a quel PC. Conviene che sia una rete scolastica protetta e che Ollama non sia
  raggiungibile dall'esterno.
- **Volti e immagini**: quando si usano i blocchi di Visione, la webcam può inquadrare studenti. Le foto non
  vengono salvate né inviate fuori, ma è buona pratica informare la classe, orientare la webcam verso il
  banco o gli oggetti e preferire attività su oggetti anziché persone.
- **Modelli di IA**: le risposte dei modelli possono essere sbagliate o imprecise. Il blocco *perché?*
  esiste proprio per discuterne con gli studenti.

## Per gli sviluppatori

Ogni contributo deve rispettare queste regole: **nessuna funzione può inviare dati fuori dalla rete
locale** né raccogliere statistiche d'uso. Se una nuova funzione richiede di scaricare qualcosa da Internet
(ad esempio un modello), deve essere esplicito, una tantum, e va documentato in questa pagina.

---

Questa pagina descrive il funzionamento del software, non costituisce consulenza legale. Ogni istituto
resta titolare del trattamento per l'uso che ne fa e valuta gli adempimenti previsti dal GDPR.
