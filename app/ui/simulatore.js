/* Disegno del robot virtuale. La fisica è in Python (app/simulatore.py): qui si disegna soltanto. */
(function () {
  'use strict';

  const COLORI_LED = {rosso: '#e5484d', verde: '#30a46c', blu: '#3e63dd', giallo: '#f5d90a',
    bianco: '#ffffff', viola: '#8e4ec6', spento: null};
  const RAGGIO = 8;

  let canvas, ctx, mondo = null, robot = null, traccia = [], urtoFino = 0;

  function imposta(elementoCanvas) {
    canvas = elementoCanvas;
    ctx = canvas.getContext('2d');
    new ResizeObserver(disegna).observe(canvas.parentElement);
  }

  function impostaMondo(nuovoMondo, statoRobot) {
    mondo = nuovoMondo;
    traccia = [];
    aggiorna(statoRobot);
  }

  function aggiorna(stato) {
    if (!stato) return;
    if (stato.reset) traccia = [];
    robot = stato;
    const ultimo = traccia[traccia.length - 1];
    if (!ultimo || Math.hypot(ultimo[0] - stato.x, ultimo[1] - stato.y) > 0.8) traccia.push([stato.x, stato.y]);
    if (stato.urto) urtoFino = performance.now() + 400;
    disegna();
    if (stato.urto) setTimeout(disegna, 420);
  }

  function disegna() {
    if (!canvas || !mondo) return;
    const box = canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const scala = Math.min(box.width / mondo.larghezza, box.height / mondo.altezza);
    const w = mondo.larghezza * scala, h = mondo.altezza * scala;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr * scala, 0, 0, dpr * scala, 0, 0);

    // pavimento e griglia (10 cm)
    ctx.fillStyle = '#fbfaf6';
    ctx.fillRect(0, 0, mondo.larghezza, mondo.altezza);
    ctx.strokeStyle = '#ebe7dc';
    ctx.lineWidth = 0.3;
    ctx.beginPath();
    for (let x = 10; x < mondo.larghezza; x += 10) { ctx.moveTo(x, 0); ctx.lineTo(x, mondo.altezza); }
    for (let y = 10; y < mondo.altezza; y += 10) { ctx.moveTo(0, y); ctx.lineTo(mondo.larghezza, y); }
    ctx.stroke();

    // linea nera
    if (mondo.linea && mondo.linea.length > 1) {
      ctx.strokeStyle = '#222';
      ctx.lineWidth = 6;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.beginPath();
      mondo.linea.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
    }

    // obiettivo (bandierina)
    if (mondo.obiettivo) {
      const [ox, oy, r] = mondo.obiettivo;
      ctx.fillStyle = 'rgba(48, 164, 108, .18)';
      ctx.strokeStyle = '#30a46c';
      ctx.lineWidth = 0.8;
      ctx.setLineDash([2, 1.5]);
      ctx.beginPath(); ctx.arc(ox, oy, r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.setLineDash([]);
      ctx.strokeStyle = '#5b4a2f'; ctx.lineWidth = 0.8;
      ctx.beginPath(); ctx.moveTo(ox - 1, oy + 5); ctx.lineTo(ox - 1, oy - 7); ctx.stroke();
      ctx.fillStyle = '#30a46c';
      ctx.beginPath(); ctx.moveTo(ox - 1, oy - 7); ctx.lineTo(ox + 6, oy - 4.5); ctx.lineTo(ox - 1, oy - 2); ctx.fill();
    }

    // ostacoli
    for (const [x, y, ow, oh] of mondo.ostacoli) {
      ctx.fillStyle = '#9aa3ae';
      ctx.fillRect(x, y, ow, oh);
      ctx.strokeStyle = '#6f7883'; ctx.lineWidth = 0.6;
      ctx.strokeRect(x, y, ow, oh);
    }

    // partenza
    const [px, py] = mondo.partenza;
    ctx.strokeStyle = '#b8b2a3'; ctx.lineWidth = 0.6; ctx.setLineDash([1.5, 1.5]);
    ctx.beginPath(); ctx.arc(px, py, RAGGIO + 1.5, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);

    // traccia
    if (traccia.length > 1) {
      ctx.strokeStyle = 'rgba(62, 99, 221, .55)'; ctx.lineWidth = 0.8;
      ctx.beginPath();
      traccia.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
    }

    if (robot) disegnaRobot(robot);

    // bordo
    ctx.strokeStyle = '#4a5260'; ctx.lineWidth = 1.2;
    ctx.strokeRect(0.6, 0.6, mondo.larghezza - 1.2, mondo.altezza - 1.2);
  }

  function disegnaRobot(r) {
    ctx.save();
    ctx.translate(r.x, r.y);
    ctx.rotate(r.angolo * Math.PI / 180);
    const urto = performance.now() < urtoFino;
    // ruote
    ctx.fillStyle = '#2b2f36';
    ctx.fillRect(-4, -RAGGIO - 1, 8, 2.4);
    ctx.fillRect(-4, RAGGIO - 1.4, 8, 2.4);
    // corpo
    ctx.fillStyle = urto ? '#e5484d' : '#ffd166';
    ctx.strokeStyle = '#3a3f47'; ctx.lineWidth = 0.7;
    ctx.beginPath(); ctx.arc(0, 0, RAGGIO, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    // LED
    const led = COLORI_LED[r.led];
    if (led) {
      ctx.fillStyle = led;
      ctx.shadowColor = led; ctx.shadowBlur = 6;
      ctx.beginPath(); ctx.arc(-2.5, 0, 2.6, 0, Math.PI * 2); ctx.fill();
      ctx.shadowBlur = 0;
    }
    // "occhi" (telecamera) e sensori di linea
    ctx.fillStyle = '#1f3a5f';
    ctx.beginPath(); ctx.arc(5, -2.2, 1.1, 0, Math.PI * 2); ctx.arc(5, 2.2, 1.1, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#e5484d';
    ctx.beginPath(); ctx.arc(6, -2, 0.6, 0, Math.PI * 2); ctx.arc(6, 2, 0.6, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  window.RBSim = {imposta, impostaMondo, aggiorna, disegna};
})();
