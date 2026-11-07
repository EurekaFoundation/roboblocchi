/* Interfaccia di RoboBlocchi: editor Blockly, robot virtuale, sfide, telecamera, impostazioni. */
(function () {
  'use strict';

  const gen = python.pythonGenerator;
  RoboBlocchi.registra(Blockly, gen, python.Order);
  // Nomi usati dal motore: Blockly non li userà per le variabili degli studenti
  gen.addReservedWords('robot,ia,dici,ascolta,attendi,evidenzia,controlla_stop');

  const $ = (sel) => document.querySelector(sel);
  const C = RoboBlocchi.COLORI;
  const numero = (n) => ({shadow: {type: 'math_number', fields: {NUM: n}}});
  const testo = (t) => ({shadow: {type: 'text', fields: {TEXT: t}}});
  const blocco = (type, inputs, fields) => ({kind: 'block', type, ...(inputs && {inputs}), ...(fields && {fields})});
  const categoria = (name, colour, contents) => ({kind: 'category', name, colour, contents});
  const standard = (name, style, contents) => ({kind: 'category', name, categorystyle: style, contents});

  // ---------- toolbox ----------
  const TOOLBOX_COMPLETA = {
    kind: 'categoryToolbox',
    contents: [
      categoria('Robot', C.robot, [
        blocco('robot_avanti', {CM: numero(20)}),
        blocco('robot_indietro', {CM: numero(20)}),
        blocco('robot_gira', {GRADI: numero(90)}),
        blocco('robot_ferma'),
        blocco('robot_attendi', {SECONDI: numero(1)}),
        blocco('robot_led'),
        blocco('robot_suona', {SECONDI: numero(0.5)}),
      ]),
      categoria('Sensori', C.sensori, [
        blocco('robot_distanza'),
        blocco('robot_linea'),
        blocco('robot_segui_linea', {SECONDI: numero(30)}),
        blocco('robot_evita', {SECONDI: numero(20)}),
      ]),
      categoria('Visione', C.visione, [
        blocco('ia_descrivi'),
        blocco('ia_vede', {OGGETTO: testo('una persona')}),
        blocco('ia_conta', {OGGETTO: testo('persone')}),
        blocco('ia_leggi'),
        blocco('ia_chiedi_foto', {DOMANDA: testo('Di che colore è l\'oggetto davanti a te?')}),
        blocco('robot_colore'),
      ]),
      categoria('Voce', C.voce, [
        blocco('ia_dici', {TESTO: testo('Ciao!')}),
        blocco('ia_ascolta', {SECONDI: numero(4)}),
      ]),
      categoria('Intelligenza artificiale', C.ia, [
        blocco('ia_chiedi', {DOMANDA: testo('Raccontami una curiosità sui robot')}),
        blocco('ia_perche'),
      ]),
      {kind: 'sep'},
      standard('Logica', 'logic_category', [
        blocco('controls_if'), blocco('logic_compare'), blocco('logic_operation'),
        blocco('logic_negate'), blocco('logic_boolean'),
      ]),
      standard('Cicli', 'loop_category', [
        blocco('controls_repeat_ext', {TIMES: numero(4)}),
        blocco('controls_whileUntil'),
        blocco('controls_for', {FROM: numero(1), TO: numero(10), BY: numero(1)}),
        blocco('controls_flow_statements'),
      ]),
      standard('Matematica', 'math_category', [
        blocco('math_number'), blocco('math_arithmetic'),
        blocco('math_random_int', {FROM: numero(1), TO: numero(100)}),
        blocco('math_number_property'),
      ]),
      standard('Testo', 'text_category', [
        blocco('text'), blocco('text_join'), blocco('text_length'), blocco('text_isEmpty'),
        blocco('text_indexOf'),
      ]),
      {kind: 'sep'},
      {kind: 'category', name: 'Variabili', categorystyle: 'variable_category', custom: 'VARIABLE'},
      {kind: 'category', name: 'Funzioni', categorystyle: 'procedure_category', custom: 'PROCEDURE'},
    ],
  };

  const TOOLBOX_SEMPLICE = {
    kind: 'categoryToolbox',
    contents: [
      categoria('Muoviti', C.robot, [
        blocco('robot_avanti', {CM: numero(20)}),
        blocco('robot_indietro', {CM: numero(20)}),
        blocco('robot_gira', {GRADI: numero(90)}),
        blocco('robot_attendi', {SECONDI: numero(1)}),
      ]),
      categoria('Luci e suoni', C.voce, [
        blocco('robot_led'),
        blocco('robot_suona', {SECONDI: numero(0.5)}),
        blocco('ia_dici', {TESTO: testo('Ciao!')}),
      ]),
      categoria('Guarda', C.visione, [
        blocco('ia_descrivi'),
        blocco('ia_vede', {OGGETTO: testo('una persona')}),
        blocco('robot_colore'),
      ]),
      standard('Ripeti e decidi', 'loop_category', [
        blocco('controls_repeat_ext', {TIMES: numero(4)}),
        blocco('controls_if'),
        blocco('logic_compare'),
        blocco('text'),
        blocco('math_number'),
      ]),
    ],
  };

  // ---------- programma di esempio ----------
  // Collega una sequenza di blocchi (ognuno è il "next" del precedente)
  function catena(...blocchi) {
    for (let i = blocchi.length - 2; i >= 0; i--) blocchi[i].next = {block: blocchi[i + 1]};
    return blocchi[0];
  }
  const ESEMPIO = {blocks: {languageVersion: 0, blocks: [Object.assign(catena(
    {type: 'robot_led', fields: {COLORE: 'verde'}},
    {type: 'ia_dici', inputs: {TESTO: testo('Ciao! Sono RoboBlocchi')}},
    {type: 'robot_avanti', inputs: {CM: numero(40)}},
    {type: 'ia_dici', inputs: {TESTO: {block: {type: 'ia_descrivi'}}}},
    {type: 'controls_if', inputs: {
      IF0: {block: {type: 'ia_vede', inputs: {OGGETTO: testo('una persona')}}},
      DO0: {block: catena(
        {type: 'ia_dici', inputs: {TESTO: testo('Ti ho visto!')}},
        {type: 'robot_suona', fields: {NOTA: 'do alto'}, inputs: {SECONDI: numero(0.5)}},
        {type: 'robot_gira', fields: {DIREZIONE: 'destra'}, inputs: {GRADI: numero(360)}},
      )},
    }},
  ), {x: 40, y: 40})]}};

  // ---------- editor ----------
  const ws = Blockly.inject('blockly', {
    toolbox: TOOLBOX_COMPLETA,
    renderer: 'zelos',
    media: 'vendor/blockly/media/',
    grid: {spacing: 24, length: 3, colour: '#e2e6ec', snap: true},
    zoom: {controls: true, wheel: true, startScale: 0.85},
    trashcan: true,
    move: {scrollbars: true, drag: true, wheel: false},
  });

  const memoria = {
    leggi(chiave, predefinito) { try { const v = localStorage.getItem(chiave); return v === null ? predefinito : JSON.parse(v); } catch (e) { return predefinito; } },
    scrivi(chiave, valore) { try { localStorage.setItem(chiave, JSON.stringify(valore)); } catch (e) { /* non essenziale */ } },
  };

  function caricaStato(stato) {
    ws.clear();
    Blockly.serialization.workspaces.load(stato, ws);
  }
  try { caricaStato(memoria.leggi('roboblocchi.bozza', null) || ESEMPIO); } catch (e) { caricaStato(ESEMPIO); }

  // ---------- generazione del codice ----------
  function genera(perEseguire) {
    // Per l'esecuzione aggiungiamo chiamate nascoste che evidenziano il blocco in
    // corso, permettono il passo-passo e di fermare anche i cicli infiniti.
    gen.STATEMENT_PREFIX = perEseguire ? 'evidenzia(%1)\n' : null;
    gen.INFINITE_LOOP_TRAP = perEseguire ? 'controlla_stop()\n' : null;
    try {
      return gen.workspaceToCode(ws);
    } finally {
      gen.STATEMENT_PREFIX = null;
      gen.INFINITE_LOOP_TRAP = null;
    }
  }

  const numeroBlocchi = () => ws.getAllBlocks(false).filter((b) => !b.isShadow()).length;

  function aggiornaCodice() {
    const codice = genera(false).trim();
    $('#codice').textContent = codice || '# trascina qui i blocchi per creare un programma';
  }

  ws.addChangeListener((evento) => {
    if (evento.isUiEvent) return;
    aggiornaCodice();
    memoria.scrivi('roboblocchi.bozza', Blockly.serialization.workspaces.save(ws));
  });
  aggiornaCodice();

  // ---------- console ----------
  function nuovaVoce(classe) {
    const voce = document.createElement('div');
    voce.className = 'voce ' + classe;
    $('#log').appendChild(voce);
    return voce;
  }
  function scorriConsole() { const log = $('#log'); log.scrollTop = log.scrollHeight; }

  window.aggiungiLog = function (messaggio, tipo) {
    nuovaVoce(tipo || 'info').textContent = messaggio;
    scorriConsole();
  };
  window.aggiungiFoto = function (dataUrl) {
    const img = document.createElement('img');
    img.src = dataUrl;
    img.alt = 'Foto analizzata';
    img.title = 'La foto su cui ha ragionato il robot (clic per ingrandire)';
    img.addEventListener('click', () => img.classList.toggle('grande'));
    img.addEventListener('load', scorriConsole);
    nuovaVoce('foto').appendChild(img);
  };
  $('#btn-pulisci').addEventListener('click', () => { $('#log').textContent = ''; });

  // ---------- suoni (robot virtuale) ----------
  let audio = null;
  window.suonaNota = function (frequenza, secondi) {
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      const osc = audio.createOscillator(), vol = audio.createGain(), t = audio.currentTime;
      osc.type = 'triangle';
      osc.frequency.value = frequenza;
      vol.gain.setValueAtTime(0.0001, t);
      vol.gain.exponentialRampToValueAtTime(0.25, t + 0.02);
      vol.gain.exponentialRampToValueAtTime(0.0001, t + Math.max(0.05, secondi));
      osc.connect(vol).connect(audio.destination);
      osc.start(t);
      osc.stop(t + secondi + 0.05);
    } catch (e) { /* audio non disponibile */ }
  };

  // ---------- collegamento con Python ----------
  // Fuori da pywebview (es. aprendo index.html nel browser) usiamo un'API finta
  // che permette solo di vedere l'interfaccia.
  const MONDO_ANTEPRIMA = {larghezza: 200, altezza: 150, partenza: [25, 75, 0], ostacoli: [[90, 45, 20, 60]],
    linea: [], obiettivo: [170, 75, 12]};
  const ANTEPRIMA = {
    async esegui() { aggiungiLog('Anteprima nel browser: avvia l\'app con "python app/main.py" per eseguire i programmi.', 'sistema'); setTimeout(esecuzioneFinita, 0); return true; },
    async passo() { return true; }, async continua() { return true; }, async ferma() { return true; },
    async leggi_impostazioni() { return {url_ollama: 'http://localhost:11434', modello: 'gemma3:4b', modalita_robot: 'simulato', indirizzo_robot: 'http://192.168.1.50:8000', indice_webcam: 0, voce_attiva: true, motore_voce: 'sistema', modello_piper: '', modello_whisper: 'base', interfaccia: 'completa', mondo: 'vuota'}; },
    async salva_impostazioni(d) { return Object.assign(await this.leggi_impostazioni(), d); },
    async verifica_ollama() { return {ok: false, messaggio: 'Disponibile solo nell\'app'}; },
    async prova_voce() { return {ok: false, messaggio: 'Disponibile solo nell\'app'}; },
    async stato_simulatore() { return {mondo: MONDO_ANTEPRIMA, robot: {x: 25, y: 75, angolo: 0, led: 'verde'}}; },
    async elenco_mondi() { return [{id: 'vuota', nome: 'Arena vuota'}]; },
    async imposta_mondo() { return this.stato_simulatore(); },
    async riposiziona() { return this.stato_simulatore(); },
    async elenco_sfide() { return [{id: 'ostacolo', livello: 2, titolo: 'Aggira l\'ostacolo', testo: 'Raggiungi la bandierina senza toccare l\'ostacolo grigio.', suggerimento: 'Gira, avanza, gira di nuovo…'}]; },
    async scegli_sfida() { return this.stato_simulatore(); },
    async anteprima() { return {ok: false, messaggio: 'Disponibile solo nell\'app'}; },
    async salva_progetto() { return null; }, async apri_progetto() { return null; }, async esporta_python() { return null; },
  };
  const api = () => (window.pywebview && window.pywebview.api) || ANTEPRIMA;

  // ---------- esecuzione ----------
  let inEsecuzione = false, modoPasso = false;

  function impostaInEsecuzione(attivo, passo) {
    inEsecuzione = attivo;
    modoPasso = attivo && !!passo;
    $('#btn-esegui').disabled = attivo && !modoPasso;   // in passo-passo, Esegui = "continua"
    $('#btn-esegui').textContent = modoPasso ? '▶ Continua' : '▶ Esegui';
    $('#btn-passo').disabled = attivo && !modoPasso;
    $('#btn-ferma').disabled = !attivo;
    $('#sel-mondo').disabled = attivo;
    $('#btn-riposiziona').disabled = attivo;
    if (!attivo) { ws.highlightBlock(null); window.inPausa(false); }
  }

  window.evidenziaBlocco = (id) => ws.highlightBlock(id || null);
  window.esecuzioneFinita = () => impostaInEsecuzione(false);
  window.inPausa = (attivo) => $('#btn-passo').classList.toggle('in-pausa', !!attivo);

  async function avvia(passo) {
    const codice = genera(true);
    if (!codice.trim()) { aggiungiLog('Il programma è vuoto: aggiungi qualche blocco.', 'sistema'); return; }
    if (sfidaCorrente) $('#sfida-esito').hidden = true;
    impostaInEsecuzione(true, passo);
    const avviato = await api().esegui(codice, {passo, sfida: sfidaCorrente && sfidaCorrente.id, num_blocchi: numeroBlocchi()});
    if (!avviato) impostaInEsecuzione(false);
  }

  $('#btn-esegui').addEventListener('click', () => {
    if (inEsecuzione && modoPasso) { impostaInEsecuzione(true, false); api().continua(); }
    else if (!inEsecuzione) avvia(false);
  });
  $('#btn-passo').addEventListener('click', () => (inEsecuzione ? api().passo() : avvia(true)));
  $('#btn-ferma').addEventListener('click', () => api().ferma());

  // ---------- schede del pannello laterale ----------
  let schedaAttiva = 'sim';
  document.querySelectorAll('.linguette button').forEach((b) => b.addEventListener('click', () => {
    schedaAttiva = b.dataset.scheda;
    document.querySelectorAll('.linguette button').forEach((x) => x.classList.toggle('attiva', x === b));
    document.querySelectorAll('.scheda').forEach((s) => s.classList.toggle('attiva', s.id === 'scheda-' + schedaAttiva));
    if (schedaAttiva === 'sim') RBSim.disegna();
    if (schedaAttiva === 'cam') aggiornaTelecamera();
  }));

  // ---------- robot virtuale ----------
  RBSim.imposta($('#canvas-sim'));
  window.simAggiorna = (stato) => RBSim.aggiorna(stato);
  const mostraSimulatore = (s) => RBSim.impostaMondo(s.mondo, s.robot);

  $('#sel-mondo').addEventListener('change', async (e) => {
    if (sfidaCorrente) esciSfida(false);
    mostraSimulatore(await api().imposta_mondo(e.target.value));
  });
  $('#btn-riposiziona').addEventListener('click', async () => mostraSimulatore(await api().riposiziona()));

  // ---------- sfide ----------
  let sfidaCorrente = null;
  const superate = new Set(memoria.leggi('roboblocchi.sfide_superate', []));

  $('#btn-sfide').addEventListener('click', async () => {
    const elenco = await api().elenco_sfide();
    const contenitore = $('#elenco-sfide');
    contenitore.textContent = '';
    for (const s of elenco) {
      const carta = document.createElement('button');
      carta.className = 'carta-sfida' + (superate.has(s.id) ? ' superata' : '');
      carta.innerHTML = '<strong></strong><span class="livello"></span><span class="testo"></span>';
      carta.querySelector('strong').textContent = s.titolo;
      carta.querySelector('.livello').textContent = '★'.repeat(s.livello) + '☆'.repeat(3 - s.livello);
      carta.querySelector('.testo').textContent = s.testo;
      carta.addEventListener('click', () => scegliSfida(s));
      contenitore.appendChild(carta);
    }
    $('#dlg-sfide').showModal();
  });
  $('#btn-chiudi-sfide').addEventListener('click', () => $('#dlg-sfide').close());

  async function scegliSfida(s) {
    $('#dlg-sfide').close();
    sfidaCorrente = s;
    $('#sfida-titolo').textContent = '🏁 ' + s.titolo;
    $('#sfida-testo').textContent = s.testo;
    $('#sfida-suggerimento').textContent = '💡 ' + s.suggerimento;
    $('#sfida-esito').hidden = true;
    $('#banner-sfida').hidden = false;
    mostraSimulatore(await api().scegli_sfida(s.id));
    aggiungiLog('Sfida: ' + s.titolo + ' — ' + s.testo, 'sistema');
  }

  async function esciSfida(ricarica = true) {
    sfidaCorrente = null;
    $('#banner-sfida').hidden = true;
    if (ricarica) mostraSimulatore(await api().scegli_sfida(null));
  }
  $('#btn-esci-sfida').addEventListener('click', () => esciSfida());

  window.esitoSfida = function (esito) {
    const el = $('#sfida-esito');
    el.hidden = false;
    el.className = 'esito ' + (esito.riuscita ? 'ok' : 'ko');
    el.textContent = (esito.riuscita ? '🎉 Sfida superata! ' : '✗ Non ancora: ') + esito.messaggio;
    aggiungiLog(el.textContent, esito.riuscita ? 'sistema' : 'errore');
    if (esito.riuscita && sfidaCorrente) {
      superate.add(sfidaCorrente.id);
      memoria.scrivi('roboblocchi.sfide_superate', [...superate]);
      suonaNota(523, 0.15); setTimeout(() => suonaNota(784, 0.3), 160);
    }
  };

  // ---------- telecamera ----------
  let richiestaCam = false;
  async function aggiornaTelecamera() {
    if (schedaAttiva !== 'cam' || richiestaCam || document.hidden) return;
    richiestaCam = true;
    try {
      const r = await api().anteprima();
      if (r.ok) { $('#img-cam').src = r.immagine; $('#stato-cam').textContent = ''; }
      else { $('#img-cam').removeAttribute('src'); $('#stato-cam').textContent = '📷 ' + r.messaggio; }
    } finally { richiestaCam = false; }
  }
  setInterval(aggiornaTelecamera, 400);

  // ---------- salva / apri / esporta ----------
  $('#btn-salva').addEventListener('click', async () => {
    const contenuto = JSON.stringify({formato: 'roboblocchi', versione: 1, blocchi: Blockly.serialization.workspaces.save(ws)}, null, 2);
    const nome = await api().salva_progetto(contenuto);
    if (nome) { $('#nome-progetto').textContent = nome; aggiungiLog('Progetto salvato: ' + nome, 'sistema'); }
  });
  $('#btn-apri').addEventListener('click', async () => {
    const file = await api().apri_progetto();
    if (!file) return;
    try {
      const dati = JSON.parse(file.contenuto);
      caricaStato(dati.blocchi || dati);
      $('#nome-progetto').textContent = file.nome;
      aggiungiLog('Progetto aperto: ' + file.nome, 'sistema');
    } catch (e) {
      aggiungiLog('Impossibile aprire il file: non è un progetto RoboBlocchi valido.', 'errore');
    }
  });
  $('#btn-esporta').addEventListener('click', async () => {
    const codice = genera(false);
    if (!codice.trim()) { aggiungiLog('Niente da esportare: il programma è vuoto.', 'sistema'); return; }
    const nome = await api().esporta_python(codice);
    if (nome) aggiungiLog('Programma Python esportato: ' + nome, 'sistema');
  });

  // ---------- impostazioni ----------
  const dlg = $('#dlg-impostazioni');
  const modulo = $('#modulo-impostazioni');

  function leggiModulo() {
    const d = Object.fromEntries(new FormData(modulo));
    d.indice_webcam = parseInt(d.indice_webcam, 10) || 0;
    d.voce_attiva = modulo.elements.voce_attiva.checked;
    return d;
  }

  function applica(imp) {
    $('#stato').textContent = (imp.modalita_robot === 'rete' ? `Robot: ${imp.indirizzo_robot}` : 'Robot virtuale')
      + ` · IA: ${imp.modello}` + (imp.voce_attiva ? ' · voce attiva' : '');
    const semplice = imp.interfaccia === 'semplice';
    if (document.body.classList.contains('semplice') !== semplice) {
      document.body.classList.toggle('semplice', semplice);
      ws.updateToolbox(semplice ? TOOLBOX_SEMPLICE : TOOLBOX_COMPLETA);
      ws.setScale(semplice ? 1.15 : 0.85);
    }
  }

  $('#btn-impostazioni').addEventListener('click', async () => {
    const imp = await api().leggi_impostazioni();
    for (const [k, v] of Object.entries(imp)) {
      const campo = modulo.elements[k];
      if (!campo) continue;
      if (campo.type === 'checkbox') campo.checked = !!v; else campo.value = v;
    }
    $('#esito-verifica').textContent = '';
    $('#esito-voce').textContent = '';
    dlg.showModal();
  });

  async function provaCon(pulsante, esito, metodo) {
    esito.className = 'esito-breve'; esito.textContent = 'Verifico…';
    pulsante.disabled = true;
    try {
      await api().salva_impostazioni(leggiModulo());
      const r = await api()[metodo]();
      esito.className = 'esito-breve ' + (r.ok ? 'ok' : 'ko');
      esito.textContent = r.messaggio;
      return r;
    } finally { pulsante.disabled = false; }
  }
  $('#btn-verifica').addEventListener('click', async () => {
    const r = await provaCon($('#btn-verifica'), $('#esito-verifica'), 'verifica_ollama');
    const lista = $('#lista-modelli');
    lista.textContent = '';
    for (const m of r.modelli || []) { const o = document.createElement('option'); o.value = m; lista.appendChild(o); }
  });
  $('#btn-prova-voce').addEventListener('click', () => provaCon($('#btn-prova-voce'), $('#esito-voce'), 'prova_voce'));

  dlg.addEventListener('close', async () => {
    if (dlg.returnValue === 'salva') applica(await api().salva_impostazioni(leggiModulo()));
  });

  // ---------- avvio ----------
  async function avvio() {
    const imp = await api().leggi_impostazioni();
    applica(imp);
    const selMondo = $('#sel-mondo');
    for (const m of await api().elenco_mondi()) {
      const o = document.createElement('option');
      o.value = m.id; o.textContent = '🗺️ ' + m.nome;
      selMondo.appendChild(o);
    }
    selMondo.value = imp.mondo || 'vuota';
    mostraSimulatore(await api().stato_simulatore());
    aggiungiLog('Pronto. Componi un programma con i blocchi e premi ▶ Esegui (o ⏭ Passo per andare un blocco alla volta).', 'sistema');
  }
  if (window.pywebview && window.pywebview.api) avvio();
  else {
    let avviato = false;
    const parti = () => { if (!avviato) { avviato = true; avvio(); } };
    window.addEventListener('pywebviewready', parti);
    // Se dopo un attimo pywebview non c'è, siamo in anteprima nel browser
    setTimeout(parti, 800);
  }
})();
