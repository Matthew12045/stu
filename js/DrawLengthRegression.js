/**
 * Draw Length Regression
 * ======================
 * OLS linear regression in the natural direction (L → Sx),
 * with algebraic inversion to estimate L from Sx.
 */
export class DrawLengthRegression {
  /**
   * @param {number[]} [L]      - Draw lengths (mm).
   * @param {number[]} [sxMean] - Mean landing distances (mm).
   */
  constructor(
    L      = [105, 110, 115, 120, 125, 130],
    sxMean = [1548.07, 1657.67, 1783.74, 1946.85, 2067.23, 2199.73],
  ) {
    this.L      = L;
    this.sxMean = sxMean;
    this.n      = L.length;

    this.LMin  = Math.min(...L);
    this.LMax  = Math.max(...L);
    this.sxMin = Math.min(...sxMean);
    this.sxMax = Math.max(...sxMean);

    this._fit();
  }

  /**
   * Fit OLS linear regression:  Sx = a·L + b
   * @private
   */
  _fit() {
    const meanL  = this.L.reduce((s, v) => s + v, 0) / this.n;
    const meanSx = this.sxMean.reduce((s, v) => s + v, 0) / this.n;

    let ssxy = 0, ssxx = 0;
    for (let i = 0; i < this.n; i++) {
      ssxy += (this.L[i] - meanL) * (this.sxMean[i] - meanSx);
      ssxx += (this.L[i] - meanL) * (this.L[i] - meanL);
    }

    this.a = ssxy / ssxx;            // slope
    this.b = meanSx - this.a * meanL; // intercept

    // R²
    let ssTot = 0, ssRes = 0;
    for (let i = 0; i < this.n; i++) {
      const pred = this.a * this.L[i] + this.b;
      ssTot += (this.sxMean[i] - meanSx) ** 2;
      ssRes += (this.sxMean[i] - pred) ** 2;
    }
    this.r2 = 1 - ssRes / ssTot;
  }

  /**
   * Predict Sx from L (forward direction).
   * @param {number} L - Draw length in mm.
   * @returns {number} Predicted landing Sx in mm.
   */
  predictForward(L) {
    return this.a * L + this.b;
  }

  /**
   * Estimate L from Sx by inverting the linear fit.
   *   L = (Sx − b) / a
   * @param {number} Sx - Landing distance in mm.
   * @returns {number} Estimated draw length in mm.
   */
  invertLinear(Sx) {
    return (Sx - this.b) / this.a;
  }

  /**
   * Check whether Sx is within the calibrated range.
   * @param {number} Sx
   * @returns {boolean}
   */
  isInRange(Sx) {
    return Sx >= this.sxMin && Sx <= this.sxMax;
  }

  /**
   * Return formatted equation strings.
   * @returns {{forward: string, inverse: string}}
   */
  equationStrings() {
    const sign = this.b >= 0 ? '+' : '';
    return {
      forward: `Sx = ${this.a.toFixed(4)} · L ${sign}${this.b.toFixed(2)}`,
      inverse: `L = (Sx − ${this.b.toFixed(2)}) / ${this.a.toFixed(4)}`,
    };
  }
}
