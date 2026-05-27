/**
 * NE555 Timer Model
 * =================
 * Loads NE555 calibration data from CSV, fits a linear regression,
 * and provides step lookup / decomposition methods.
 */
export class NE555TimerModel {
  /** Hardware constants */
  static THRESHOLD = 10.0;
  static MIN_STEP  = 0.1;
  static MAX_STEP  = 19.0;
  static STEP_INC  = 0.1;

  constructor() {
    this.slope     = null;
    this.intercept = null;
    this.recorded  = {};
    this.nRecorded = 0;
    this.ready     = false;
  }

  /**
   * Load and parse the NE555 dataset from a CSV file.
   * Tries multiple paths as fallback.
   * @param {...string} paths - CSV file paths to try in order.
   * @returns {Promise<void>}
   */
  async loadCSV(...paths) {
    let text = null;
    for (const path of paths) {
      try {
        const resp = await fetch(path);
        if (resp.ok) { text = await resp.text(); break; }
      } catch (_) { /* try next */ }
    }

    if (text) {
      this._parseCSV(text);
    } else {
      // Hardcoded fallback
      this.slope     = 0.990626;
      this.intercept = 0.115888;
      this.nRecorded = 0;
    }
    this.ready = true;
  }

  /**
   * Parse CSV text into recorded lookup and fit regression.
   * @param {string} text - Raw CSV content.
   * @private
   */
  _parseCSV(text) {
    const lines  = text.trim().split('\n');
    const header = lines[0].split(',');

    const iTarget = header.indexOf('target_time_s');
    const iMean   = header.indexOf('mean_s');
    const iStd    = header.indexOf('std_s');
    const iNread  = header.indexOf('n_readings');

    const cleanPoints = [];
    this.recorded  = {};
    this.nRecorded = 0;

    for (let i = 1; i < lines.length; i++) {
      const cols   = lines[i].split(',');
      const target = parseFloat(cols[iTarget]);
      const mean   = parseFloat(cols[iMean]);
      const std    = parseFloat(cols[iStd]);
      const nread  = cols[iNread].trim();

      if (nread !== 'PREDICTED') {
        this.recorded[target.toFixed(1)] = { mean, std };
        this.nRecorded++;
        if (std < 0.1) {
          cleanPoints.push({ x: target, y: mean });
        }
      }
    }

    this._fitRegression(cleanPoints);
  }

  /**
   * Fit a simple linear regression (y = slope*x + intercept).
   * @param {Array<{x:number, y:number}>} points
   * @private
   */
  _fitRegression(points) {
    if (points.length < 2) {
      this.slope = 0.990626;
      this.intercept = 0.115888;
      return;
    }

    const n  = points.length;
    const mx = points.reduce((s, p) => s + p.x, 0) / n;
    const my = points.reduce((s, p) => s + p.y, 0) / n;

    let sxy = 0, sxx = 0;
    for (const p of points) {
      sxy += (p.x - mx) * (p.y - my);
      sxx += (p.x - mx) * (p.x - mx);
    }

    this.slope     = Math.round((sxy / sxx) * 1e6) / 1e6;
    this.intercept = Math.round((my - this.slope * mx) * 1e6) / 1e6;
  }

  /**
   * Return the NE555 output time for a given dial step.
   * Prefers recorded measurement; falls back to regression.
   * @param {number} step - Dial step (0.1–19.0).
   * @returns {number} Output time in seconds.
   */
  ne555Output(step) {
    const rec = this.recorded[step.toFixed(1)];
    return rec ? rec.mean : (this.slope * step + this.intercept);
  }

  /**
   * Find the dial step whose NE555 output is closest to t_delay.
   * @param {number} tDelay - Target delay in seconds.
   * @returns {number} Best step value.
   */
  bestStep(tDelay) {
    let best = NE555TimerModel.MIN_STEP;
    let bestDiff = Infinity;

    for (let s = NE555TimerModel.MIN_STEP;
         s <= NE555TimerModel.MAX_STEP;
         s = Math.round((s + NE555TimerModel.STEP_INC) * 10) / 10) {
      const diff = Math.abs(this.ne555Output(s) - tDelay);
      if (diff < bestDiff) {
        bestDiff = diff;
        best = s;
      }
    }
    return best;
  }

  /**
   * Decompose a step into hardware knob/switch settings.
   * @param {number} step
   * @returns {{step, switchOn, effective, knob1, knob2, mean, std, isRecorded}}
   */
  decomposeStep(step) {
    const key      = step.toFixed(1);
    const rec      = this.recorded[key];
    const switchOn = step >= NE555TimerModel.THRESHOLD;
    const effective = switchOn
      ? Math.round((step - NE555TimerModel.THRESHOLD) * 10) / 10
      : step;
    const knob2 = Math.floor(effective);
    const knob1 = Math.round((effective - knob2) * 10);

    return {
      step:       Math.round(step * 10) / 10,
      switchOn,
      effective:  Math.round(effective * 10) / 10,
      knob1,
      knob2,
      mean:       rec ? rec.mean : +(this.slope * step + this.intercept).toFixed(6),
      std:        rec ? rec.std  : null,
      isRecorded: !!rec,
    };
  }
}
