/**
 * Physics Engine
 * ==============
 * Projectile kinematics and timing calculations for the M2 ball launcher.
 */
export class PhysicsEngine {
  /**
   * @param {object} [opts]
   * @param {number} [opts.sy=0.036]           Vertical offset (m)
   * @param {number} [opts.launchAngleDeg=60]  Launch angle (degrees)
   * @param {number} [opts.g=9.81]             Gravitational acceleration (m/s²)
   * @param {number} [opts.armRadius=0.06]     Arm radius (m)
   * @param {number} [opts.armPivot=2.5]       Arm pivot distance (m)
   * @param {number} [opts.sxOffset=102]       Offset added to Sx for delay (mm)
   */
  constructor({
    sy           = 0.036,
    launchAngleDeg = 60.0,
    g            = 9.81,
    armRadius    = 0.06,
    armPivot     = 2.5,
    sxOffset     = 102,
  } = {}) {
    this.sy           = sy;
    this.launchAngleDeg = launchAngleDeg;
    this.g            = g;
    this.armRadius    = armRadius;
    this.armPivot     = armPivot;
    this.sxOffset     = sxOffset;
  }

  /**
   * Compute projectile flight time for a horizontal distance.
   * @param {number} sxM - Horizontal distance in metres.
   * @returns {number} Flight time in seconds.
   * @throws {Error} If target is unreachable.
   */
  computeFlightTime(sxM) {
    const angleRad  = this.launchAngleDeg * (Math.PI / 180);
    const innerTerm = (2 * (sxM * Math.tan(angleRad) - this.sy)) / this.g;

    if (innerTerm < 0) {
      throw new Error('Target unreachable (negative square root).');
    }
    return Math.sqrt(innerTerm);
  }

  /**
   * Compute the full delay-time pipeline.
   * @param {number} sxMm   - Landing distance in mm (raw input, before offset).
   * @param {number} rpm    - Motor speed in RPM.
   * @param {number} phiDeg - Phase angle in degrees.
   * @returns {{tFlight, tDelayRaw, tDelay, cycleAdded, omega, cConst, sxUsed}}
   * @throws {Error} On invalid physics.
   */
  computeDelayTime(sxMm, rpm, phiDeg) {
    const sxUsed = sxMm + this.sxOffset;   // apply offset
    const sxM    = sxUsed / 1000.0;

    const tFlight = this.computeFlightTime(sxM);
    const omega   = rpm * (Math.PI / 30);

    // Geometric constant c
    const denom = this.armPivot - sxM;
    const ratio = this.armRadius / denom;
    if (Math.abs(ratio) > 1) {
      throw new Error('Invalid arcsin domain for constant c.');
    }
    const cConst = Math.asin(ratio);

    const phiRad = phiDeg * (Math.PI / 180);

    // Raw delay
    let tDelay = ((2 * Math.PI - phiRad - cConst) / omega) - tFlight;
    if (tDelay < 0) tDelay += 2 * Math.PI / omega;

    const tDelayRaw = tDelay;
    let cycleAdded = false;

    if (tDelay < 0.1) {
      tDelay += 2 * Math.PI / omega;
      cycleAdded = true;
    }

    if (tDelay < 0.1) {
      throw new Error(
        `Delay (${tDelay.toFixed(2)}s) still < 0.1s after +2π/ω.`
      );
    }

    return { tFlight, tDelayRaw, tDelay, cycleAdded, omega, cConst, sxUsed };
  }
}
