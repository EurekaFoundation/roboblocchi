# Sicurezza

## Segnalare una vulnerabilità

Se trovi un problema di sicurezza **non aprire una issue pubblica**. Segnalalo in privato:

- dalla scheda **Security → Report a vulnerability** del repository, se attiva, oppure
- per email a **eureka.foundationn@proton.me**

Indica come riprodurre il problema e quali versioni sono coinvolte. Ti risponderemo appena possibile e ti
terremo aggiornato fino alla correzione. Se vuoi, ti ringrazieremo pubblicamente nelle note di rilascio.

## Versioni supportate

Le correzioni di sicurezza vengono pubblicate sull'ultima versione rilasciata.

## Cose da sapere sul funzionamento

- I programmi creati con i blocchi vengono eseguiti come codice Python sul computer dell'utente, con i
  suoi stessi permessi. Questo è normale per un ambiente di programmazione, ma significa che un file
  `.robo` di provenienza sconosciuta va trattato come un qualsiasi programma scaricato.
- Il server di esempio del robot (`robot_server/server.py`) accetta comandi da chiunque sia nella stessa
  rete e non ha autenticazione: va usato solo in reti locali fidate.
- Ollama, se configurato per accettare connessioni dalla rete, non deve essere raggiungibile da Internet.
