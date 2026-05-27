/**
 * M2 Launcher App
 * ================
 * Orchestrator that composes NE555TimerModel, PhysicsEngine, and
 * DrawLengthRegression, then renders results to the DOM.
 */
import { NE555TimerModel }      from './NE555TimerModel.js';
import { PhysicsEngine }        from './PhysicsEngine.js';
import { DrawLengthRegression } from './DrawLengthRegression.js';

export class M2LauncherApp {
  constructor() {
    this.timer   = new NE555TimerModel();
    this.physics = new PhysicsEngine();
    this.reg     = new DrawLengthRegression();
  }

  /**
   * Initialise: load CSV data, wire up event listeners, run first calc.
   */
  async init() {
    await this.timer.loadCSV(
      'Example/ne555_full_dataset.csv',
      'ne555_full_dataset.csv',
    );
    this._updateSubtitle();
    this._bindInputs();
    this.update();
  }

  // ── Private: DOM wiring ──────────────────────────────────────

  /** Bind oninput on the three shared input fields. */
  _bindInputs() {
    for (const id of ['in-sx', 'in-rpm', 'in-phi']) {
      document.getElementById(id)
        .addEventListener('input', () => this.update());
    }
  }

  /** Update the subtitle bar with model info. */
  _updateSubtitle() {
    const el = document.getElementById('model-sub');
    if (!el) return;
    el.textContent =
      `${this.timer.nRecorded} recorded · ` +
      `regression: ${this.timer.slope} × t + ${this.timer.intercept}`;
  }

  // ── Public: master update ────────────────────────────────────

  /** Re-run both calculators from current input values. */
  update() {
    if (!this.timer.ready) return;
    this._runDelay();
    this._runRegression();
  }

  // ── Private: Delay Calculator ────────────────────────────────

  _runDelay() {
    const sxRaw  = document.getElementById('in-sx').value.trim();
    const rpmRaw = document.getElementById('in-rpm').value.trim();
    const phiRaw = document.getElementById('in-phi').value.trim();
    const err    = document.getElementById('nb-err');

    if (sxRaw === '' || rpmRaw === '' || phiRaw === '') {
      this._resetDelay(); return;
    }

    const sxMm   = parseFloat(sxRaw);
    const rpm    = parseFloat(rpmRaw);
    const phiDeg = parseFloat(phiRaw);

    if (isNaN(sxMm) || isNaN(rpm) || isNaN(phiDeg)) {
      this._resetDelay(false); return;
    }

    // Compute via PhysicsEngine (applies +102 mm offset internally)
    let result;
    try {
      result = this.physics.computeDelayTime(sxMm, rpm, phiDeg);
    } catch (e) {
      err.textContent = 'Error: ' + e.message;
      this._resetDelay(false);
      return;
    }

    err.textContent = '';

    const { tFlight, tDelayRaw, tDelay, cycleAdded, omega, sxUsed } = result;

    // Find best NE555 step and decompose
    const step   = this.timer.bestStep(tDelay);
    const decomp = this.timer.decomposeStep(step);
    const errorS = (decomp.mean - tDelay).toFixed(4);

    // ── Render knobs / switch / values ────────────────────────
    this._setText('nb-vt', step.toFixed(1));
    this._setText('nb-k1', decomp.knob1);
    this._setText('nb-d1', decomp.knob1);
    this._setArc('nb-a1', decomp.knob1);
    this._setText('nb-k2', decomp.knob2);
    this._setText('nb-d2', decomp.knob2);
    this._setArc('nb-a2', decomp.knob2);

    const sw = document.getElementById('nb-sw');
    const sv = document.getElementById('nb-sv');
    if (decomp.switchOn) {
      sw.classList.add('on');
      sv.textContent = 'ON'; sv.style.color = '#22c55e';
      this._setText('nb-sl', '10 s range');
    } else {
      sw.classList.remove('on');
      sv.textContent = 'OFF'; sv.style.color = '#6b7280';
      this._setText('nb-sl', '0–9.9 s');
    }

    // ── Formula breakdown ────────────────────────────────────
    const fm = document.getElementById('nb-fm');
    fm.classList.add('show');

    const hl = M2LauncherApp._hl, blu = M2LauncherApp._blu;
    const grn = M2LauncherApp._grn, prp = M2LauncherApp._prp;

    document.getElementById('nb-f0').innerHTML =
      `Sx<sub>delay</sub> = ${hl(sxUsed.toFixed(0) + ' mm')}` +
      ` (input ${sxMm.toFixed(0)} + ${this.physics.sxOffset})` +
      ` &nbsp;|&nbsp; T<sub>flight</sub> = ${hl(tFlight.toFixed(4) + ' s')}` +
      ` &nbsp;|&nbsp; T<sub>delay</sub> = ${prp(tDelayRaw.toFixed(4) + ' s')}` +
      (cycleAdded
        ? ` + ${blu((2 * Math.PI / omega).toFixed(4) + ' s')}` +
          ` (2&pi; added) &rarr; ${hl(tDelay.toFixed(4) + ' s')}`
        : '');

    document.getElementById('nb-f1').innerHTML = decomp.isRecorded
      ? `Best step = ${hl(step.toFixed(1) + ' s')} &rarr; NE555 = ` +
        `${grn(decomp.mean.toFixed(4) + ' s')} ${grn('(recorded)')}` +
        ` ± ${decomp.std.toFixed(4)} s &nbsp;|&nbsp; error = ${hl(errorS + ' s')}`
      : `Best step = ${hl(step.toFixed(1) + ' s')} &rarr; NE555 = ` +
        `${blu(this.timer.slope)} × ${hl(step.toFixed(1))} + ${blu(this.timer.intercept)}` +
        ` = ${blu(decomp.mean.toFixed(4) + ' s')} &nbsp;|&nbsp; error = ${hl(errorS + ' s')}`;

    document.getElementById('nb-f2').innerHTML = decomp.switchOn
      ? `switch = ${grn('ON')} &rarr; effective = ${hl(step.toFixed(1))} &minus; 10 = ${hl(decomp.effective.toFixed(1) + ' s')}`
      : `switch = ${hl('OFF')} &rarr; effective = ${hl(decomp.effective.toFixed(1) + ' s')}`;

    document.getElementById('nb-f3').innerHTML =
      `knob 2 = floor(${hl(decomp.effective.toFixed(1))}) = ${hl(decomp.knob2)}` +
      ` &nbsp;|&nbsp; knob 1 = round((${hl(decomp.effective.toFixed(1))}` +
      ` &minus; ${decomp.knob2}) &times; 10) = ${hl(decomp.knob1)}`;
  }

  _resetDelay(clearErr = true) {
    for (const id of ['nb-vt', 'nb-k1', 'nb-k2']) this._setText(id, '–');
    for (const id of ['nb-d1', 'nb-d2']) this._setText(id, '–');
    this._setArc('nb-a1', 0);
    this._setArc('nb-a2', 0);
    document.getElementById('nb-sv').textContent = '–';
    document.getElementById('nb-sv').style.color = '#6b7280';
    this._setText('nb-sl', '–');
    document.getElementById('nb-sw').classList.remove('on');
    document.getElementById('nb-fm').classList.remove('show');
    if (clearErr) document.getElementById('nb-err').textContent = '';
  }

  // ── Private: Draw Length Regression ──────────────────────────

  _runRegression() {
    const sxRaw = document.getElementById('in-sx').value.trim();
    const elL   = document.getElementById('reg-L');
    const elSx  = document.getElementById('reg-Sx');
    const elEq  = document.getElementById('reg-eq');
    const elW   = document.getElementById('reg-warn');

    if (sxRaw === '') {
      elL.textContent  = '–';
      elSx.textContent = '–';
      elEq.textContent = 'Enter Sx above to see the regression result.';
      elW.textContent  = '';
      return;
    }

    const Sx = parseFloat(sxRaw);
    if (isNaN(Sx)) return;

    const Lest = this.reg.invertLinear(Sx);
    const eqs  = this.reg.equationStrings();

    const hl = M2LauncherApp._hl, prp = M2LauncherApp._prp;

    elL.textContent  = Lest.toFixed(2);
    elSx.textContent = Sx.toFixed(0);

    elEq.innerHTML =
      `<div style="margin-bottom:6px">` +
      `<span class="prp">Natural fit (L → Sx):</span> ${eqs.forward}</div>` +
      `<div style="margin-bottom:6px">` +
      `<span class="prp">Inverted (Sx → L):</span> ${eqs.inverse}` +
      ` = ${hl(Lest.toFixed(2) + ' mm')}</div>` +
      `<div style="color:#6b7280;font-size:10px">` +
      `R² = ${this.reg.r2.toFixed(8)} &nbsp;|&nbsp; ` +
      `Calibration: L ∈ [${this.reg.LMin}, ${this.reg.LMax}] mm</div>`;

    elW.textContent = this.reg.isInRange(Sx)
      ? ''
      : `⚠️ Outside calibrated range [${this.reg.sxMin.toFixed(0)}, ` +
        `${this.reg.sxMax.toFixed(0)}] mm — extrapolation`;
  }

  // ── Private: DOM helpers ─────────────────────────────────────

  _setText(id, val) {
    document.getElementById(id).textContent = val;
  }

  /** Set SVG arc dasharray for a knob position 0–9. */
  _setArc(id, pos) {
    const ARC = 163;
    const f = (pos / 9) * ARC;
    document.getElementById(id)
      .setAttribute('stroke-dasharray', f + ' ' + (187 - f));
  }

  // ── Static HTML helpers ──────────────────────────────────────

  static _hl(t)  { return `<span class="hl">${t}</span>`; }
  static _blu(t) { return `<span class="blu">${t}</span>`; }
  static _grn(t) { return `<span class="grn">${t}</span>`; }
  static _prp(t) { return `<span class="prp">${t}</span>`; }
}
