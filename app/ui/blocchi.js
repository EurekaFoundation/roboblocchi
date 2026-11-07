/*
 * Blocchi personalizzati di RoboBlocchi e relativo codice Python generato.
 *
 * Per aggiungere un blocco:
 *   1. definiscilo in DEFINIZIONI (vedi https://developers.google.com/blockly/guides/create-custom-blocks/define-blocks)
 *   2. scrivi il generatore in GENERATORI (cosa diventa in Python)
 *   3. aggiungilo alla toolbox in app.js
 *   4. se serve, implementa la funzione Python in app/robot.py, app/ia.py o app/esecutore.py
 */
(function () {
  'use strict';

  const COLORI = {robot: 200, sensori: 165, visione: 290, voce: 330, ia: 255};

  const opzioni = (...valori) => valori.map((v) => [v, v]);

  // Scorciatoie per definire i blocchi
  const comando = (type, colore, message0, args0, tooltip) =>
    ({type, message0, args0, inputsInline: true, previousStatement: null, nextStatement: null, colour: colore, tooltip});
  const valore = (type, colore, output, message0, args0, tooltip) =>
    ({type, message0, args0, inputsInline: true, output, colour: colore, tooltip});
  const numero = (name) => ({type: 'input_value', name, check: 'Number'});
  const testo = (name) => ({type: 'input_value', name, check: 'String'});

  const DEFINIZIONI = [
    // ---------- Robot ----------
    comando('robot_avanti', COLORI.robot, 'vai avanti di %1 cm', [numero('CM')], 'Il robot avanza della distanza indicata'),
    comando('robot_indietro', COLORI.robot, 'vai indietro di %1 cm', [numero('CM')], 'Il robot arretra della distanza indicata'),
    comando('robot_gira', COLORI.robot, 'gira a %1 di %2 gradi',
      [{type: 'field_dropdown', name: 'DIREZIONE', options: opzioni('destra', 'sinistra')}, numero('GRADI')],
      'Il robot ruota su se stesso'),
    comando('robot_ferma', COLORI.robot, 'ferma i motori', [], 'Spegne i motori'),
    comando('robot_attendi', COLORI.robot, 'attendi %1 secondi', [numero('SECONDI')], 'Pausa'),
    comando('robot_led', COLORI.robot, '💡 LED %1',
      [{type: 'field_dropdown', name: 'COLORE', options: opzioni('rosso', 'verde', 'blu', 'giallo', 'bianco', 'viola', 'spento')}],
      'Accende il LED del robot del colore scelto'),
    comando('robot_suona', COLORI.robot, '🎵 suona %1 per %2 secondi',
      [{type: 'field_dropdown', name: 'NOTA', options: opzioni('do', 're', 'mi', 'fa', 'sol', 'la', 'si', 'do alto')}, numero('SECONDI')],
      'Suona una nota con il cicalino'),

    // ---------- Sensori ----------
    valore('robot_distanza', COLORI.sensori, 'Number', 'distanza dall\'ostacolo (cm)', [], 'Valore letto dal sensore di distanza'),
    valore('robot_linea', COLORI.sensori, 'Boolean', 'sensore linea %1 vede nero',
      [{type: 'field_dropdown', name: 'LATO', options: opzioni('sinistro', 'destro')}],
      'Vero se il sensore di linea è sopra la linea nera'),
    comando('robot_segui_linea', COLORI.sensori, 'segui la linea per %1 secondi', [numero('SECONDI')],
      'Segue la linea nera finché non finisce o scade il tempo'),
    comando('robot_evita', COLORI.sensori, 'gira libero evitando gli ostacoli per %1 secondi', [numero('SECONDI')],
      'Va avanti e cambia direzione quando incontra un ostacolo'),

    // ---------- Visione ----------
    valore('ia_descrivi', COLORI.visione, 'String', '👁️ cosa vedo', [], 'Scatta una foto e l\'IA descrive cosa c\'è davanti al robot'),
    valore('ia_vede', COLORI.visione, 'Boolean', '👁️ vedo %1 ?', [testo('OGGETTO')], 'Vero se l\'IA riconosce l\'oggetto nella foto'),
    valore('ia_chiedi_foto', COLORI.visione, 'String', '👁️ guarda e rispondi a %1', [testo('DOMANDA')], 'Domanda all\'IA sulla foto'),
    valore('ia_leggi', COLORI.visione, 'String', '👁️ leggi il testo che vedo', [], 'L\'IA legge le scritte nella foto (cartelli, fogli…)'),
    valore('ia_conta', COLORI.visione, 'Number', '👁️ quanti %1 vedo', [testo('OGGETTO')], 'L\'IA conta gli oggetti nella foto'),
    valore('robot_colore', COLORI.visione, 'String', '🎨 colore davanti a me', [],
      'Colore prevalente al centro dell\'immagine (calcolato senza IA)'),

    // ---------- Voce ----------
    comando('ia_dici', COLORI.voce, '🔊 di\' %1', [{type: 'input_value', name: 'TESTO'}], 'Il robot pronuncia il messaggio e lo scrive in console'),
    valore('ia_ascolta', COLORI.voce, 'String', '👂 ascolta per %1 secondi', [numero('SECONDI')], 'Restituisce le parole sentite dal microfono'),

    // ---------- Intelligenza artificiale ----------
    valore('ia_chiedi', COLORI.ia, 'String', '💭 risposta dell\'IA a %1', [testo('DOMANDA')], 'Fa una domanda all\'IA (senza foto)'),
    valore('ia_perche', COLORI.ia, 'String', '💭 perché? (spiega l\'ultima risposta)', [],
      'L\'IA spiega su cosa si è basata per l\'ultima risposta. Può sbagliare!'),
  ];

  const GENERATORI = {
    robot_avanti: (b, g) => `robot.avanti(${v(b, g, 'CM', '0')})\n`,
    robot_indietro: (b, g) => `robot.indietro(${v(b, g, 'CM', '0')})\n`,
    robot_gira: (b, g) => `robot.gira('${b.getFieldValue('DIREZIONE')}', ${v(b, g, 'GRADI', '0')})\n`,
    robot_ferma: () => 'robot.ferma_motori()\n',
    robot_attendi: (b, g) => `attendi(${v(b, g, 'SECONDI', '0')})\n`,
    robot_led: (b) => `robot.accendi_led('${b.getFieldValue('COLORE')}')\n`,
    robot_suona: (b, g) => `robot.suona('${b.getFieldValue('NOTA')}', ${v(b, g, 'SECONDI', '0.5')})\n`,

    robot_distanza: (b, g) => ['robot.distanza()', g.ORDINE.FUNCTION_CALL],
    robot_linea: (b, g) => [`robot.linea('${b.getFieldValue('LATO')}')`, g.ORDINE.FUNCTION_CALL],
    robot_segui_linea: (b, g) => `robot.segui_linea(${v(b, g, 'SECONDI', '10')})\n`,
    robot_evita: (b, g) => `robot.evita_ostacoli(${v(b, g, 'SECONDI', '10')})\n`,

    ia_descrivi: (b, g) => ['ia.descrivi()', g.ORDINE.FUNCTION_CALL],
    ia_vede: (b, g) => [`ia.vede(${v(b, g, 'OGGETTO', "''")})`, g.ORDINE.FUNCTION_CALL],
    ia_chiedi_foto: (b, g) => [`ia.chiedi_su_foto(${v(b, g, 'DOMANDA', "''")})`, g.ORDINE.FUNCTION_CALL],
    ia_leggi: (b, g) => ['ia.leggi_testo()', g.ORDINE.FUNCTION_CALL],
    ia_conta: (b, g) => [`ia.conta(${v(b, g, 'OGGETTO', "''")})`, g.ORDINE.FUNCTION_CALL],
    robot_colore: (b, g) => ['robot.colore_davanti()', g.ORDINE.FUNCTION_CALL],

    ia_dici: (b, g) => `dici(${v(b, g, 'TESTO', "''")})\n`,
    ia_ascolta: (b, g) => [`ascolta(${v(b, g, 'SECONDI', '4')})`, g.ORDINE.FUNCTION_CALL],

    ia_chiedi: (b, g) => [`ia.chiedi(${v(b, g, 'DOMANDA', "''")})`, g.ORDINE.FUNCTION_CALL],
    ia_perche: (b, g) => ['ia.perche()', g.ORDINE.FUNCTION_CALL],
  };

  function v(blocco, gen, nome, predefinito) {
    return gen.valueToCode(blocco, nome, gen.ORDINE.NONE) || predefinito;
  }

  /** Registra blocchi e generatori. Funziona nel browser e (per i test) in Node.js. */
  function registra(Blockly, generatore, Ordine) {
    Blockly.common.defineBlocksWithJsonArray(DEFINIZIONI);
    generatore.ORDINE = Ordine;
    for (const [tipo, fn] of Object.entries(GENERATORI)) {
      generatore.forBlock[tipo] = (blocco, gen) => fn(blocco, gen);
    }
  }

  const esporta = {registra, COLORI};
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = esporta;
  } else {
    window.RoboBlocchi = esporta;
  }
})();
