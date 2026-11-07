// Test dei blocchi: ogni blocco ha un generatore e produce il Python atteso.
// Esecuzione: npm test   (richiede: npm install)
const test = require('node:test');
const assert = require('node:assert');
const Blockly = require('blockly');
const {pythonGenerator, Order} = require('blockly/python');
const RoboBlocchi = require('../app/ui/blocchi.js');

RoboBlocchi.registra(Blockly, pythonGenerator, Order);

const numero = (n) => ({shadow: {type: 'math_number', fields: {NUM: n}}});
const testo = (t) => ({shadow: {type: 'text', fields: {TEXT: t}}});

function genera(blocco) {
  const ws = new Blockly.Workspace();
  Blockly.serialization.workspaces.load({blocks: {languageVersion: 0, blocks: [blocco]}}, ws);
  return pythonGenerator.workspaceToCode(ws).trim();
}

const nostri = Object.keys(Blockly.Blocks).filter((t) => t.startsWith('robot_') || t.startsWith('ia_'));

test('ogni blocco personalizzato ha un generatore Python', () => {
  assert.ok(nostri.length >= 20);
  for (const tipo of nostri) assert.ok(pythonGenerator.forBlock[tipo], `manca il generatore di ${tipo}`);
});

const CASI = [
  [{type: 'robot_avanti', inputs: {CM: numero(20)}}, 'robot.avanti(20)'],
  [{type: 'robot_gira', fields: {DIREZIONE: 'sinistra'}, inputs: {GRADI: numero(90)}}, "robot.gira('sinistra', 90)"],
  [{type: 'robot_led', fields: {COLORE: 'blu'}}, "robot.accendi_led('blu')"],
  [{type: 'robot_suona', fields: {NOTA: 'do alto'}, inputs: {SECONDI: numero(0.5)}}, "robot.suona('do alto', 0.5)"],
  [{type: 'robot_segui_linea', inputs: {SECONDI: numero(30)}}, 'robot.segui_linea(30)'],
  [{type: 'robot_evita', inputs: {SECONDI: numero(5)}}, 'robot.evita_ostacoli(5)'],
  [{type: 'ia_dici', inputs: {TESTO: {block: {type: 'ia_descrivi'}}}}, 'dici(ia.descrivi())'],
  [{type: 'ia_dici', inputs: {TESTO: {block: {type: 'ia_conta', inputs: {OGGETTO: testo('mele')}}}}}, "dici(ia.conta('mele'))"],
  [{type: 'ia_dici', inputs: {TESTO: {block: {type: 'ia_ascolta', inputs: {SECONDI: numero(3)}}}}}, 'dici(ascolta(3))'],
  [{type: 'ia_dici', inputs: {TESTO: {block: {type: 'ia_perche'}}}}, 'dici(ia.perche())'],
  [{type: 'controls_if', inputs: {IF0: {block: {type: 'robot_linea', fields: {LATO: 'destro'}}},
    DO0: {block: {type: 'robot_ferma'}}}}, "if robot.linea('destro'):\n  robot.ferma_motori()"],
  [{type: 'ia_dici'}, "dici('')"],   // ingresso vuoto: valore predefinito, niente errore
];

for (const [blocco, atteso] of CASI) {
  test(`genera: ${atteso.split('\n')[0]}`, () => assert.strictEqual(genera(blocco), atteso));
}

test('evidenziazione e stop vengono inseriti per l\'esecuzione', () => {
  pythonGenerator.STATEMENT_PREFIX = 'evidenzia(%1)\n';
  pythonGenerator.INFINITE_LOOP_TRAP = 'controlla_stop()\n';
  try {
    const codice = genera({type: 'controls_whileUntil', fields: {MODE: 'WHILE'},
      inputs: {BOOL: {block: {type: 'logic_boolean', fields: {BOOL: 'TRUE'}}},
        DO: {block: {type: 'robot_avanti', inputs: {CM: numero(1)}}}}});
    assert.match(codice, /^evidenzia\('.+'\)\nwhile True:\n  controlla_stop\(\)\n  evidenzia/);
  } finally {
    pythonGenerator.STATEMENT_PREFIX = null;
    pythonGenerator.INFINITE_LOOP_TRAP = null;
  }
});
