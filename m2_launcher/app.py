"""
M2 Launcher Application
========================
Orchestrator that combines the NE555 timer, physics engine, and
draw-length regression into a single tabbed Jupyter widget.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, HTML

from .timer_model import NE555TimerModel
from .physics import PhysicsEngine
from .regression import DrawLengthRegression


# ── Theme colours (dark theme for regression tab) ─────────────────────
DARK   = "#0f1117"
PANEL  = "#1c1f2e"
BORDER = "#2e3250"
CYAN   = "#00d4ff"
PINK   = "#ff6b9d"
GREEN  = "#55efc4"
ORANGE = "#ff9f43"
MUTED  = "#8892b0"
WHITE  = "#e6e6f0"
PURPLE = "#c792ea"


def _styled(desc: str, val: str, unit: str = "") -> str:
    """Return an HTML snippet for a labelled metric value."""
    return (
        f"<span style='color:{MUTED};font-size:12px'>{desc}: </span>"
        f"<span style='color:{WHITE};font-weight:600'>{val}</span>"
        f"<span style='color:{MUTED};font-size:11px'> {unit}</span>"
    )


class M2LauncherApp:
    """Combined M2 Ball Launcher application.

    Brings together:

    * :class:`NE555TimerModel` – timer calibration and dial mapping
    * :class:`PhysicsEngine` – projectile kinematics
    * :class:`DrawLengthRegression` – OLS regression (3 modes)

    Call :meth:`display` in a Jupyter cell to render the full UI.

    Parameters
    ----------
    csv_path : str or None
        Path to the NE555 dataset CSV.  ``None`` uses the bundled file.
    """

    def __init__(self, csv_path: str | None = None):
        self.timer   = NE555TimerModel(csv_path)
        self.physics = PhysicsEngine()
        self.reg     = DrawLengthRegression()

    # ==================================================================
    #  PUBLIC
    # ==================================================================

    def display(self):
        """Render the full tabbed UI in a Jupyter notebook."""
        tab = widgets.Tab()
        tab.children = [
            self._build_delay_tab(),
            self._build_regression_tab(),
        ]
        tab.set_title(0, "⏱  Delay Calculator")
        tab.set_title(1, "📐  Draw Length Regression")
        display(tab)

    # ==================================================================
    #  TAB 1 — DELAY CALCULATOR  (identical HTML widget)
    # ==================================================================

    def _build_delay_tab(self) -> widgets.VBox:
        """Build the delay-time calculator tab (HTML widget)."""
        html_content = self._generate_delay_html()
        html_widget = widgets.HTML(value=html_content)
        return widgets.VBox(
            [html_widget],
            layout=widgets.Layout(padding="0px"),
        )

    def _generate_delay_html(self) -> str:
        """Generate the full HTML/CSS/JS for the delay calculator widget.

        This reproduces the exact same display as the original
        ``delay.py`` / ``ne555_calculator.html``.
        """
        SLOPE         = self.timer.slope
        INTERCEPT     = self.timer.intercept
        r2            = self.timer.r_squared
        n_recorded    = self.timer.n_recorded
        recorded_json = self.timer.to_json()

        return f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=DM+Sans:wght@400;500&display=swap');

  .ne555-wrap {{
    font-family: 'DM Sans', sans-serif;
    background: #ffffff;
    border-radius: 14px;
    padding: 2rem;
    max-width: 640px;
    margin: 0 auto;
    position: relative;
    border: 1px solid rgba(0,0,0,0.1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  }}
  .ne555-wrap * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  .n-chip {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b7280;
    border: 1px solid rgba(0,0,0,0.15);
    border-radius: 4px;
    padding: 3px 8px;
    margin-bottom: 10px;
  }}
  .n-h1 {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
  }}
  .n-h1 span {{ color: #3b82f6; }}
  .n-sub {{
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 1.5rem;
  }}

  .n-inputs {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 1rem;
  }}
  .n-input-col {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .n-input-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #8b5cf6;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .n-input {{
    background: #f9fafb;
    border: 1px solid rgba(0,0,0,0.15);
    border-radius: 8px;
    color: #111827;
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 700;
    padding: 10px 12px;
    outline: none;
    width: 100%;
    -moz-appearance: textfield;
    transition: border-color 0.2s, background 0.2s;
  }}
  .n-input::-webkit-outer-spin-button,
  .n-input::-webkit-inner-spin-button {{ -webkit-appearance: none; }}
  .n-input:focus {{ border-color: #3b82f6; background: #ffffff; }}
  .n-input::placeholder {{ color: #9ca3af; font-weight: 400; }}

  .n-err {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #ef4444;
    min-height: 16px;
    margin-bottom: 1rem;
  }}

  .n-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 1rem;
  }}
  .n-card {{
    background: #f9fafb;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    padding: 12px 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
  }}
  .n-clabel {{
    font-size: 9px;
    font-family: 'JetBrains Mono', monospace;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    text-align: center;
  }}
  .n-icon {{
    height: 62px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 4px;
  }}
  .n-cval {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: #4b5563;
    transition: color 0.2s;
  }}
  .n-cval.purple {{ color: #8b5cf6; }}
  .n-cval.blue   {{ color: #3b82f6; }}
  .n-cval.amber  {{ color: #f59e0b; }}
  .n-cval.green  {{ color: #22c55e; }}
  .n-csub {{
    font-size: 8px;
    font-family: 'JetBrains Mono', monospace;
    color: #6b7280;
    text-align: center;
    line-height: 1.4;
  }}

  .n-sw-track {{
    width: 42px; height: 22px;
    border-radius: 11px;
    background: #e5e7eb;
    border: 1px solid rgba(0,0,0,0.15);
    display: flex; align-items: center;
    padding: 0 3px;
    transition: background 0.3s, border-color 0.3s;
  }}
  .n-sw-track.on {{ background: rgba(34,197,94,0.2); border-color: rgba(34,197,94,0.4); }}
  .n-sw-dot {{
    width: 16px; height: 16px;
    border-radius: 50%;
    background: #9ca3af;
    transition: transform 0.3s, background 0.3s;
  }}
  .n-sw-track.on .n-sw-dot {{ transform: translateX(20px); background: #22c55e; }}

  .n-formula {{
    background: #f9fafb;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    padding: 12px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    line-height: 2;
    color: #4b5563;
    display: none;
    margin-bottom: 1rem;
  }}
  .n-formula.show {{ display: block; }}
  .n-formula .hl  {{ color: #111827; font-weight: 700; }}
  .n-formula .blu {{ color: #3b82f6; }}
  .n-formula .grn {{ color: #22c55e; }}
  .n-formula .prp {{ color: #8b5cf6; }}

  .n-footer {{
    font-size: 10px;
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
  }}
</style>

<div class="ne555-wrap">
  <div class="n-chip">Integrated Tool</div>
  <div class="n-h1">Delay &amp; Timer <span>Calculator</span></div>
  <div class="n-sub">
    {n_recorded} recorded measurements &middot;
    regression: {SLOPE} &times; t + {INTERCEPT} &middot;
    R&sup2; = {r2:.4f}
  </div>

  <div class="n-inputs">
    <div class="n-input-col">
      <div class="n-input-label">Sx (mm)</div>
      <input class="n-input" type="number" id="in-sx" placeholder="e.g. 2292" oninput="run_pipeline()" />
    </div>
    <div class="n-input-col">
      <div class="n-input-label">Motor (RPM)</div>
      <input class="n-input" type="number" id="in-rpm" placeholder="e.g. 9" oninput="run_pipeline()" />
    </div>
    <div class="n-input-col">
      <div class="n-input-label">Phi (deg)</div>
      <input class="n-input" type="number" id="in-phi" placeholder="e.g. 270" oninput="run_pipeline()" />
    </div>
  </div>

  <div class="n-err" id="nb-err"></div>

  <div class="n-grid">
    <div class="n-card">
      <div class="n-clabel">Target Delay</div>
      <div class="n-icon">
        <svg width="26" height="26" fill="none" stroke="#8b5cf6" stroke-width="1.5" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>
        </svg>
      </div>
      <div class="n-cval purple" id="nb-vt">&ndash;</div>
      <div class="n-csub">seconds</div>
    </div>

    <div class="n-card">
      <div class="n-clabel">Knob 1</div>
      <div class="n-icon">
        <svg width="62" height="62" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="30" fill="none" stroke="#e5e7eb" stroke-width="8"
            stroke-linecap="round" stroke-dasharray="163 24" stroke-dashoffset="-12"/>
          <circle cx="40" cy="40" r="30" fill="none" stroke="#3b82f6" stroke-width="8"
            stroke-linecap="round" id="nb-a1" stroke-dasharray="0 187" stroke-dashoffset="-12"/>
          <text x="40" y="45" text-anchor="middle" font-size="20" font-weight="700"
            font-family="JetBrains Mono,monospace" fill="#3b82f6" id="nb-d1">&ndash;</text>
        </svg>
      </div>
      <div class="n-cval blue" id="nb-k1">&ndash;</div>
      <div class="n-csub">pos 0&ndash;9</div>
    </div>

    <div class="n-card">
      <div class="n-clabel">Knob 2</div>
      <div class="n-icon">
        <svg width="62" height="62" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="30" fill="none" stroke="#e5e7eb" stroke-width="8"
            stroke-linecap="round" stroke-dasharray="163 24" stroke-dashoffset="-12"/>
          <circle cx="40" cy="40" r="30" fill="none" stroke="#f59e0b" stroke-width="8"
            stroke-linecap="round" id="nb-a2" stroke-dasharray="0 187" stroke-dashoffset="-12"/>
          <text x="40" y="45" text-anchor="middle" font-size="20" font-weight="700"
            font-family="JetBrains Mono,monospace" fill="#f59e0b" id="nb-d2">&ndash;</text>
        </svg>
      </div>
      <div class="n-cval amber" id="nb-k2">&ndash;</div>
      <div class="n-csub">pos 0&ndash;9</div>
    </div>

    <div class="n-card">
      <div class="n-clabel">Switch</div>
      <div class="n-icon">
        <div class="n-sw-track" id="nb-sw"><div class="n-sw-dot"></div></div>
      </div>
      <div class="n-cval" id="nb-sv">&ndash;</div>
      <div class="n-csub" id="nb-sl">&ndash;</div>
    </div>
  </div>

  <div class="n-formula" id="nb-fm">
    <div id="nb-f0"></div>
    <div id="nb-f1"></div>
    <div id="nb-f2"></div>
    <div id="nb-f3"></div>
    <div id="nb-f4"></div>
  </div>

  <div class="n-footer">
    Limit: 0.1 s min &nbsp;&middot;&nbsp;
    <span style="color:#22c55e">&#9632;</span> recorded &nbsp;
    <span style="color:#3b82f6">&#9632;</span> regression
  </div>
</div>

<script>
(function() {{
  const SLOPE     = {SLOPE};
  const INTERCEPT = {INTERCEPT};
  const THRESHOLD = 10.0;
  const ARC       = 163;
  const RECORDED  = {recorded_json};

  function ne555_output(step) {{
    const key = step.toFixed(1);
    return RECORDED[key] ? RECORDED[key].mean : (SLOPE * step + INTERCEPT);
  }}

  function best_step(t_delay) {{
    let bestStep = 0.1;
    let bestDiff = Infinity;
    for (let s = 0.1; s <= 19.0; s = Math.round((s + 0.1) * 10) / 10) {{
      const diff = Math.abs(ne555_output(s) - t_delay);
      if (diff < bestDiff) {{
        bestDiff = diff;
        bestStep = s;
      }}
    }}
    return bestStep;
  }}

  function arc(id, pos) {{
    const f = (pos / 9) * ARC;
    document.getElementById(id).setAttribute('stroke-dasharray', f + ' ' + (187 - f));
  }}
  function hl(t)  {{ return '<span class="hl">'  + t + '</span>'; }}
  function blu(t) {{ return '<span class="blu">' + t + '</span>'; }}
  function grn(t) {{ return '<span class="grn">' + t + '</span>'; }}
  function prp(t) {{ return '<span class="prp">' + t + '</span>'; }}

  window.run_pipeline = function() {{
    const sx_raw  = document.getElementById('in-sx').value.trim();
    const rpm_raw = document.getElementById('in-rpm').value.trim();
    const phi_raw = document.getElementById('in-phi').value.trim();
    const err     = document.getElementById('nb-err');

    if (sx_raw === '' || rpm_raw === '' || phi_raw === '') {{
      nb_reset();
      return;
    }}

    const sx_mm   = parseFloat(sx_raw);
    const rpm     = parseFloat(rpm_raw);
    const phi_deg = parseFloat(phi_raw);

    if (isNaN(sx_mm) || isNaN(rpm) || isNaN(phi_deg)) {{
      nb_reset(false);
      return;
    }}

    const sx           = sx_mm / 1000.0;
    const sy           = 0.036;
    const launch_angle = 60.0;
    const g            = 9.81;

    const angle_rad  = launch_angle * (Math.PI / 180);
    const inner_term = (2 * (sx * Math.tan(angle_rad) - sy)) / g;

    if (inner_term < 0) {{
      err.textContent = 'Error: Target unreachable at this angle (negative square root).';
      nb_reset(false);
      return;
    }}

    const denom = 2.5 - sx;
    const ratio = 0.06 / denom;
    if (Math.abs(ratio) > 1) {{
      err.textContent = 'Error: Target Sx results in invalid arcsin domain for constant c.';
      nb_reset(false);
      return;
    }}

    const t_flight = Math.sqrt(inner_term);
    const omega    = rpm * (Math.PI / 30);
    const c        = Math.asin(ratio);
    const phi_rad  = phi_deg * (Math.PI / 180);

    let t_delay = (((2 * Math.PI) - phi_rad - c) / omega) - t_flight;
    if (t_delay < 0) {{
      t_delay += (2 * Math.PI / omega);
    }}

    const t_delay_raw = t_delay;

    if (t_delay < 0.1) {{
      t_delay += (2 * Math.PI / omega);
    }}

    if (t_delay < 0.1) {{
      err.textContent = `Calculated delay (${{t_delay.toFixed(2)}}s) is still below 0.1s after adding 2\u03c0.`;
      nb_reset(false);
      return;
    }}

    err.textContent = '';

    const step   = best_step(t_delay);
    const key    = step.toFixed(1);
    const rec    = RECORDED[key];
    const mean   = rec ? rec.mean : +(SLOPE * step + INTERCEPT).toFixed(6);
    const std    = rec ? rec.std  : null;
    const isRec  = !!rec;
    const error  = (mean - t_delay).toFixed(4);

    const swOn  = step >= THRESHOLD;
    const tEff  = swOn ? +(step - THRESHOLD).toFixed(1) : step;
    const knob2 = Math.floor(tEff);
    const knob1 = Math.round((tEff - knob2) * 10);

    document.getElementById('nb-vt').textContent = step.toFixed(1);

    document.getElementById('nb-k1').textContent = knob1;
    document.getElementById('nb-d1').textContent = knob1;
    arc('nb-a1', knob1);

    document.getElementById('nb-k2').textContent = knob2;
    document.getElementById('nb-d2').textContent = knob2;
    arc('nb-a2', knob2);

    const sw = document.getElementById('nb-sw');
    const sv = document.getElementById('nb-sv');
    if (swOn) {{
      sw.classList.add('on');
      sv.textContent   = 'ON';
      sv.style.color   = '#22c55e';
      document.getElementById('nb-sl').textContent = '10 s range';
    }} else {{
      sw.classList.remove('on');
      sv.textContent   = 'OFF';
      sv.style.color   = '#6b7280';
      document.getElementById('nb-sl').textContent = '0\u20139.9 s';
    }}

    const fm = document.getElementById('nb-fm');
    fm.classList.add('show');

    const cycleAdded = t_delay_raw < 0.1;
    document.getElementById('nb-f0').innerHTML =
      'T<sub>flight</sub> = ' + hl(t_flight.toFixed(4) + ' s') + ' &nbsp;|&nbsp; ' +
      'T<sub>delay</sub> = ' + prp(t_delay_raw.toFixed(4) + ' s') +
      (cycleAdded
        ? ' + ' + blu((2 * Math.PI / omega).toFixed(4) + ' s') +
          ' (2&pi; added) &rarr; ' + hl(t_delay.toFixed(4) + ' s')
        : '');

    document.getElementById('nb-f1').innerHTML = isRec
      ? 'Best step = ' + hl(step.toFixed(1) + ' s') + '  &rarr;  NE555 output = ' +
        grn(mean.toFixed(4) + ' s') + ' ' + grn('(recorded)') +
        ' \u00b1 ' + std.toFixed(4) + ' s std' +
        '  &nbsp;|&nbsp;  error = ' + hl(error + ' s')
      : 'Best step = ' + hl(step.toFixed(1) + ' s') + '  &rarr;  NE555 output = ' +
        blu(SLOPE) + ' \u00d7 ' + hl(step.toFixed(1)) + ' + ' + blu(INTERCEPT) +
        ' = ' + blu(mean.toFixed(4) + ' s') +
        '  &nbsp;|&nbsp;  error = ' + hl(error + ' s');

    document.getElementById('nb-f2').innerHTML =
      'switch = ' + (swOn
        ? grn('ON') + '   &rarr; effective = ' + hl(step.toFixed(1)) + ' &minus; 10 = ' + hl(tEff.toFixed(1)) + ' s'
        : hl('OFF') + '  &rarr; effective = ' + hl(tEff.toFixed(1)) + ' s');

    document.getElementById('nb-f3').innerHTML =
      'knob 2 = floor(' + hl(tEff.toFixed(1)) + ') = ' + hl(knob2) +
      ' &nbsp;|&nbsp; knob 1 = round((' + hl(tEff.toFixed(1)) +
      ' &minus; ' + knob2 + ') &times; 10) = ' + hl(knob1);
  }};

  window.nb_reset = function(clearErr = true) {{
    ['nb-vt','nb-k1','nb-k2'].forEach(id => document.getElementById(id).textContent = '\u2013');
    ['nb-d1','nb-d2'].forEach(id => document.getElementById(id).textContent = '\u2013');
    ['nb-a1','nb-a2'].forEach(id => arc(id, 0));
    document.getElementById('nb-sv').textContent  = '\u2013';
    document.getElementById('nb-sv').style.color  = '#6b7280';
    document.getElementById('nb-sl').textContent  = '\u2013';
    document.getElementById('nb-sw').classList.remove('on');
    document.getElementById('nb-fm').classList.remove('show');
    if (clearErr) document.getElementById('nb-err').textContent = '';
  }};
}})();
</script>
"""

    # ==================================================================
    #  TAB 2 — DRAW LENGTH REGRESSION
    # ==================================================================

    def _build_regression_tab(self) -> widgets.VBox:
        """Build the interactive draw-length regression tab."""
        reg = self.reg

        # ── Custom CSS ────────────────────────────────────────────────
        custom_css = widgets.HTML(f"""
<style>
    .m2-dark-ui {{ background-color: {DARK} !important; }}
    .m2-dark-ui .widget-html,
    .m2-dark-ui .widget-html-content,
    .m2-dark-ui .widget-vbox,
    .m2-dark-ui .widget-hbox,
    .m2-dark-ui .widget-label {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    .m2-dark-ui .widget-label {{ color: {MUTED} !important; }}
    .m2-dark-ui input[type="number"] {{
        background-color: {PANEL} !important;
        color: {WHITE} !important;
        border: 1px solid {BORDER} !important;
    }}
    .m2-dark-ui .widget-button {{
        background-color: {PANEL} !important;
        color: {WHITE} !important;
        border: 1px solid {BORDER} !important;
    }}
    .widget-toggle-button.mod-active {{
        background-color: {CYAN} !important;
        color: {DARK} !important;
        box-shadow: 0 0 10px {CYAN} !important;
        border-color: {CYAN} !important;
        font-weight: bold !important;
    }}
    .widget-toggle-button {{
        background-color: {PANEL} !important;
        color: {MUTED} !important;
        border: 1px solid {BORDER} !important;
    }}
</style>
""")

        # ── Title ─────────────────────────────────────────────────────
        title = widgets.HTML(f"""
<div style='background:{DARK};padding:18px 24px 10px;border-bottom:2px solid {BORDER}'>
  <div style='color:{CYAN};font-family:monospace;font-size:11px;letter-spacing:3px;
              margin-bottom:4px'>M2 BALL LAUNCHER</div>
  <div style='color:{WHITE};font-size:22px;font-weight:700;font-family:monospace'>
    Draw Length Estimator</div>
  <div style='color:{MUTED};font-size:12px;margin-top:4px'>
    OLS fit with algebraic inversion &nbsp;&middot;&nbsp;
    n = {len(reg.L)} draw lengths &nbsp;&middot;&nbsp;
    range {int(reg.L_min)}\u2013{int(reg.L_max)} mm</div>
</div>
""")

        # ── Method toggle ─────────────────────────────────────────────
        model_toggle = widgets.ToggleButtons(
            options=[
                ("Direct inverse fit",    "direct"),
                ("OLS natural + invert",  "natural"),
                ("Forward  L → Sx",       "forward"),
            ],
            value="natural",
            style={"button_width": "220px", "description_width": "0px"},
            layout=widgets.Layout(margin="12px 0 0 0"),
        )

        # ── Inverse input: Sx → L ────────────────────────────────────
        Sx_input = widgets.BoundedFloatText(
            value=1601.2, min=500, max=3000, step=0.5,
            description="Sx (mm):",
            style={"description_width": "60px"},
            layout=widgets.Layout(width="200px"),
        )

        quick_label = widgets.HTML(
            f"<span style='color:{MUTED};font-size:12px;line-height:32px'>Quick pick: </span>"
        )
        quick_btns = [
            widgets.Button(
                description=f"{int(v)}",
                layout=widgets.Layout(width="72px", height="30px"),
            )
            for v in reg.Sx_mean
        ]
        for btn, v in zip(quick_btns, reg.Sx_mean):
            btn.style.button_color = PANEL
            def _mk(val):
                def _cb(_): Sx_input.value = val
                return _cb
            btn.on_click(_mk(v))

        # ── Forward input: L → Sx ────────────────────────────────────
        L_input = widgets.BoundedFloatText(
            value=100.0, min=50, max=200, step=0.5,
            description="L (mm):",
            style={"description_width": "60px"},
            layout=widgets.Layout(width="200px"),
        )

        L_quick_label = widgets.HTML(
            f"<span style='color:{MUTED};font-size:12px;line-height:32px'>Quick pick: </span>"
        )
        L_quick_btns = [
            widgets.Button(
                description=f"{int(v)}",
                layout=widgets.Layout(width="56px", height="30px"),
            )
            for v in reg.L
        ]
        for btn, v in zip(L_quick_btns, reg.L):
            btn.style.button_color = PANEL
            def _mkL(val):
                def _cb(_): L_input.value = val
                return _cb
            btn.on_click(_mkL(v))

        # ── Output areas ──────────────────────────────────────────────
        input_box    = widgets.VBox([])
        result_out   = widgets.Output()
        metrics_out  = widgets.Output()
        plot_out     = widgets.Output()

        section_header = widgets.HTML("")

        quick_row   = widgets.HBox(
            [quick_label] + quick_btns,
            layout=widgets.Layout(margin="6px 0 0 0", flex_wrap="wrap"),
        )
        L_quick_row = widgets.HBox(
            [L_quick_label] + L_quick_btns,
            layout=widgets.Layout(margin="6px 0 0 0", flex_wrap="wrap"),
        )
        inv_input_box = widgets.VBox([Sx_input, quick_row])
        fwd_input_box = widgets.VBox([L_input, L_quick_row])

        method_label = widgets.HTML(
            f"<div style='color:{MUTED};font-size:11px;letter-spacing:2px;"
            f"margin:8px 0 6px'>METHOD</div>"
        )
        input_label = widgets.HTML(
            f"<div style='color:{MUTED};font-size:11px;letter-spacing:2px;"
            f"margin:12px 0 6px'>INPUT</div>"
        )

        controls = widgets.VBox([
            section_header, method_label, model_toggle, input_label, input_box,
        ])

        # ── Section header builder ────────────────────────────────────
        def _section_html(mode):
            if mode == "forward":
                label = "FORWARD PREDICTION  ·  L → Sx"
                desc  = "Input draw length L → predict landing Sx directly"
                col   = PURPLE
            else:
                label = "INVERSE PREDICTION  ·  Sx → L"
                desc  = "Input landing Sx → estimate draw length L"
                col   = CYAN
            return (
                f"<div style='padding:12px 0 4px'>"
                f"<div style='color:{col};font-family:monospace;font-size:11px;"
                f"letter-spacing:3px;margin-bottom:6px'>{label}</div>"
                f"<div style='color:{MUTED};font-size:12px'>{desc}</div></div>"
            )

        # ── Metrics renderer ─────────────────────────────────────────
        def render_metrics(mode):
            metrics_out.clear_output(wait=True)
            m = reg.mode_metrics(mode)
            with metrics_out:
                display(widgets.HTML(f"""
<div style='background:{PANEL};border:1px solid {BORDER};border-radius:8px;
            padding:14px 18px;font-family:monospace;font-size:12px;margin:6px 0'>
  <div style='color:{CYAN};font-size:11px;letter-spacing:2px;margin-bottom:10px'>
    MODEL EQUATIONS</div>

  <div style='color:{MUTED};margin-bottom:3px'>Linear:</div>
  <div style='color:{WHITE};margin-bottom:10px;padding-left:12px'>{m['eq_lin']}</div>

  <div style='color:{MUTED};margin-bottom:3px'>Quadratic:</div>
  <div style='color:{WHITE};padding-left:12px'>{m['eq_quad']}</div>

  <hr style='border-color:{BORDER};margin:10px 0'>

  <div style='display:flex;gap:32px'>
    <div>{_styled('Linear RMSE', f"{m['rmse_lin']:.4f}", 'mm')}</div>
    <div>{_styled('Linear R\u00b2',   f"{m['r2_lin']:.8f}")}</div>
    <div>{_styled('Quad RMSE',   f"{m['rmse_quad']:.4f}", 'mm')}</div>
    <div>{_styled('Quad R\u00b2',     f"{m['r2_quad']:.8f}")}</div>
  </div>

  <div style='margin-top:10px;color:{m['note_color']};font-size:11px'>{m['note']}</div>
</div>
"""))

        # ── Result card renderer ──────────────────────────────────────
        def render_result(mode):
            result_out.clear_output(wait=True)
            with result_out:
                if mode == "forward":
                    Lv = L_input.value
                    sx_lin  = reg.predict_forward_linear(Lv)
                    sx_quad = reg.predict_forward_quadratic(Lv)
                    delta = abs(sx_lin - sx_quad)
                    idx = int(np.argmin(np.abs(reg.L - Lv)))

                    warn = (
                        f"<div style='color:{ORANGE};margin-top:8px;font-size:11px'>"
                        f"⚠️ Outside calibrated range [{int(reg.L_min)}, {int(reg.L_max)}] mm — "
                        f"extrapolation only</div>"
                        if Lv < reg.L_min or Lv > reg.L_max else ""
                    )
                    agree = GREEN if delta < 10 else ORANGE if delta < 30 else PINK
                    header_col, header_lbl = PURPLE, "PREDICTION  ·  L → Sx  (forward, no inversion)"
                    input_lbl, input_val = "L =", f"{Lv:.2f}"
                    val_lin, val_quad = f"{sx_lin:.2f}", f"{sx_quad:.2f}"
                    unit_lin = unit_quad = "mm landing"
                    extra = (
                        f"<div style='border-left:1px solid {BORDER};padding-left:28px'>"
                        f"<div style='color:{MUTED};font-size:11px;margin-bottom:4px'>"
                        f"NEAREST CALIBRATION POINT</div>"
                        f"<div style='color:{CYAN};font-size:16px;font-weight:700'>"
                        f"L={int(reg.L[idx])} mm → {reg.Sx_mean[idx]:.2f} mm</div>"
                        f"<div style='color:{MUTED};font-size:11px'>"
                        f"σ = {reg.sigma_Sx[idx]:.2f} mm"
                        f" &nbsp;(±2σ = {2*reg.sigma_Sx[idx]:.2f} mm)</div></div>"
                    )
                    delta_fmt = f"{delta:.2f}"

                else:
                    Sx = Sx_input.value
                    if mode == "direct":
                        l_lin  = reg.predict_direct_linear(Sx)
                        l_quad = reg.predict_direct_quadratic(Sx)
                    else:
                        l_lin  = reg.invert_linear(Sx)
                        l_quad = reg.invert_quadratic(Sx)

                    delta = abs(l_lin - l_quad)
                    warn = (
                        f"<div style='color:{ORANGE};margin-top:8px;font-size:11px'>"
                        f"⚠️ Outside calibrated range [{reg.Sx_min:.1f}, {reg.Sx_max:.1f}] mm — "
                        f"extrapolation only</div>"
                        if Sx < reg.Sx_min or Sx > reg.Sx_max else ""
                    )
                    agree = GREEN if delta < 0.5 else ORANGE if delta < 1.5 else PINK
                    header_col, header_lbl = CYAN, "PREDICTION  ·  Sx → L"
                    input_lbl, input_val = "Sx =", f"{Sx:.2f}"
                    val_lin, val_quad = f"{float(l_lin):.3f}", f"{float(l_quad):.3f}"
                    unit_lin = unit_quad = "mm draw length"
                    extra, delta_fmt = "", f"{delta:.3f}"

                display(widgets.HTML(f"""
<div style='background:{PANEL};border:1px solid {BORDER};border-radius:8px;
            padding:14px 18px;font-family:monospace;font-size:13px;margin:6px 0'>
  <div style='color:{header_col};font-size:11px;letter-spacing:2px;margin-bottom:10px'>
    {header_lbl}</div>

  <div style='display:flex;gap:12px;align-items:baseline;margin-bottom:8px'>
    <span style='color:{MUTED}'>{input_lbl}</span>
    <span style='color:{WHITE};font-size:20px;font-weight:700'>{input_val}</span>
    <span style='color:{MUTED}'>mm</span>
  </div>

  <div style='display:flex;gap:40px;margin-top:10px'>
    <div>
      <div style='color:{MUTED};font-size:11px;margin-bottom:4px'>LINEAR</div>
      <div style='color:{PINK};font-size:22px;font-weight:700'>{val_lin}</div>
      <div style='color:{MUTED};font-size:11px'>{unit_lin}</div>
    </div>
    <div>
      <div style='color:{MUTED};font-size:11px;margin-bottom:4px'>QUADRATIC</div>
      <div style='color:{GREEN};font-size:22px;font-weight:700'>{val_quad}</div>
      <div style='color:{MUTED};font-size:11px'>{unit_quad}</div>
    </div>
    <div>
      <div style='color:{MUTED};font-size:11px;margin-bottom:4px'>Δ MODELS</div>
      <div style='color:{agree};font-size:22px;font-weight:700'>{delta_fmt}</div>
      <div style='color:{MUTED};font-size:11px'>mm difference</div>
    </div>
    {extra}
  </div>
  {warn}
</div>
"""))

        # ── Plot renderer ─────────────────────────────────────────────
        def render_plot(mode):
            plot_out.clear_output(wait=True)
            with plot_out:
                L_pad  = 0.08 * (reg.L_max - reg.L_min)
                Sx_pad = 0.08 * (reg.Sx_max - reg.Sx_min)

                L_fine  = np.linspace(reg.L_min - L_pad,  reg.L_max + L_pad,  500)
                Sx_fine = np.linspace(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad, 600)

                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), facecolor=DARK)
                for ax in (ax1, ax2):
                    ax.set_facecolor(PANEL)
                    ax.tick_params(colors=MUTED, labelsize=8)
                    ax.xaxis.label.set_color(MUTED)
                    ax.yaxis.label.set_color(MUTED)
                    ax.title.set_color(WHITE)
                    for sp in ax.spines.values():
                        sp.set_color(BORDER)

                if mode == "direct":
                    l_fine_lin  = np.polyval(reg.p_lin_direct, Sx_fine)
                    l_fine_quad = np.polyval(reg.p_quad_direct, Sx_fine)
                    l_rec_lin   = np.polyval(reg.p_lin_direct, reg.Sx_mean)
                    l_rec_quad  = np.polyval(reg.p_quad_direct, reg.Sx_mean)

                    ax1.errorbar(reg.Sx_mean, reg.L, xerr=2*reg.sigma_Sx, fmt="o",
                                 color=CYAN, ecolor=CYAN+"55", capsize=3, zorder=5, label="Data (±2σ)")
                    ax1.plot(Sx_fine, l_fine_lin, color=PINK, linewidth=1.8, label="Linear")
                    ax1.plot(Sx_fine, l_fine_quad, color=GREEN, linewidth=1.8, linestyle="--", label="Quadratic")

                    ax1.axvline(Sx_input.value, color=ORANGE, linewidth=1.2, linestyle=":", alpha=0.9,
                                label=f"Sx={Sx_input.value:.0f} mm")
                    ax1.axhline(np.polyval(reg.p_lin_direct, Sx_input.value), color=PINK, linewidth=0.8, linestyle=":", alpha=0.7)
                    ax1.axhline(np.polyval(reg.p_quad_direct, Sx_input.value), color=GREEN, linewidth=0.8, linestyle=":", alpha=0.7)

                    ax1.set_xlabel("Landing Sx (mm)"); ax1.set_ylabel("Draw Length L (mm)")
                    ax1.set_title("L = f(Sx)  —  Direct inverse fit")
                    ax1.set_xlim(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad)
                    ax1.set_ylim(reg.L_min - L_pad, reg.L_max + L_pad)
                    ax1.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
                    ax1.grid(alpha=0.15, color=BORDER)

                    ax2.plot(reg.L, reg.L - l_rec_lin, "o-", color=PINK, linewidth=1.5,
                             label=f"Linear  RMSE={reg.metrics(reg.L, l_rec_lin)[0]:.4f} mm")
                    ax2.plot(reg.L, reg.L - l_rec_quad, "s--", color=GREEN, linewidth=1.5,
                             label=f"Quad    RMSE={reg.metrics(reg.L, l_rec_quad)[0]:.4f} mm")
                    ax2.axhline(0, color=MUTED, linewidth=0.8)
                    ax2.set_xlabel("True L (mm)"); ax2.set_ylabel("Residual  L − L\u0302  (mm)")
                    ax2.set_title("Residuals  —  Direct inverse")
                    ax2.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)
                    ax2.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
                    ax2.grid(alpha=0.15, color=BORDER)

                elif mode == "natural":
                    l_rec_lin   = reg.invert_linear(reg.Sx_mean)
                    l_rec_quad  = reg.invert_quadratic(reg.Sx_mean)
                    l_inv_lin   = reg.invert_linear(Sx_fine)
                    l_inv_quad  = reg.invert_quadratic(Sx_fine)

                    ax1.errorbar(reg.Sx_mean, reg.L, xerr=2*reg.sigma_Sx, fmt="o",
                                 color=CYAN, ecolor=CYAN+"55", capsize=3, zorder=5, label="Data (±2σ)")
                    ax1.plot(Sx_fine, l_inv_lin, color=PINK, linewidth=1.8, label="Linear  (inverted)")
                    ax1.plot(Sx_fine, l_inv_quad, color=GREEN, linewidth=1.8, linestyle="--", label="Quadratic  (inverted)")

                    ax1.axvline(Sx_input.value, color=ORANGE, linewidth=1.2, linestyle=":", alpha=0.9,
                                label=f"Sx={Sx_input.value:.0f} mm")
                    ax1.axhline(float(reg.invert_linear(Sx_input.value)), color=PINK, linewidth=0.8, linestyle=":", alpha=0.7)
                    ax1.axhline(float(reg.invert_quadratic(Sx_input.value)), color=GREEN, linewidth=0.8, linestyle=":", alpha=0.7)

                    ax1.set_xlabel("Landing Sx (mm)"); ax1.set_ylabel("Draw Length L (mm)")
                    ax1.set_title("L = f\u207b\u00b9(Sx)  —  OLS natural + inversion")
                    ax1.set_xlim(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad)
                    ax1.set_ylim(reg.L_min - L_pad, reg.L_max + L_pad)
                    ax1.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
                    ax1.grid(alpha=0.15, color=BORDER)

                    ax2.plot(reg.L, reg.L - l_rec_lin, "o-", color=PINK, linewidth=1.5,
                             label=f"Linear  RMSE={reg.metrics(reg.L, l_rec_lin)[0]:.4f} mm")
                    ax2.plot(reg.L, reg.L - l_rec_quad, "s--", color=GREEN, linewidth=1.5,
                             label=f"Quad    RMSE={reg.metrics(reg.L, l_rec_quad)[0]:.4f} mm")
                    ax2.axhline(0, color=MUTED, linewidth=0.8)
                    ax2.set_xlabel("True L (mm)"); ax2.set_ylabel("Residual  L − L\u0302  (mm)")
                    ax2.set_title("Residuals  —  OLS natural + inversion")
                    ax2.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)
                    ax2.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
                    ax2.grid(alpha=0.15, color=BORDER)

                else:  # forward
                    sx_lin_fine  = np.polyval(reg.p_lin_nat, L_fine)
                    sx_quad_fine = np.polyval(reg.p_quad_nat, L_fine)
                    sx_lin_rec   = np.polyval(reg.p_lin_nat, reg.L)
                    sx_quad_rec  = np.polyval(reg.p_quad_nat, reg.L)

                    ax1.errorbar(reg.L, reg.Sx_mean, yerr=2*reg.sigma_Sx, fmt="o",
                                 color=CYAN, ecolor=CYAN+"55", capsize=3, zorder=5, label="Data (±2σ)")
                    ax1.plot(L_fine, sx_lin_fine, color=PINK, linewidth=1.8, label="Linear")
                    ax1.plot(L_fine, sx_quad_fine, color=GREEN, linewidth=1.8, linestyle="--", label="Quadratic")

                    ax1.axvline(L_input.value, color=PURPLE, linewidth=1.2, linestyle=":", alpha=0.9,
                                label=f"L={L_input.value:.0f} mm")
                    ax1.axhline(np.polyval(reg.p_lin_nat, L_input.value), color=PINK, linewidth=0.8, linestyle=":", alpha=0.7)
                    ax1.axhline(np.polyval(reg.p_quad_nat, L_input.value), color=GREEN, linewidth=0.8, linestyle=":", alpha=0.7)

                    ax1.set_xlabel("Draw Length L (mm)"); ax1.set_ylabel("Landing Sx (mm)")
                    ax1.set_title("Sx = f(L)  —  Forward  (no inversion)")
                    ax1.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)
                    ax1.set_ylim(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad)
                    ax1.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
                    ax1.grid(alpha=0.15, color=BORDER)

                    rmse_lin  = float(np.sqrt(np.mean((reg.Sx_mean - sx_lin_rec)**2)))
                    rmse_quad = float(np.sqrt(np.mean((reg.Sx_mean - sx_quad_rec)**2)))

                    ax2.plot(reg.L, reg.Sx_mean - sx_lin_rec, "o-", color=PINK, linewidth=1.5,
                             label=f"Linear  RMSE={rmse_lin:.2f} mm")
                    ax2.plot(reg.L, reg.Sx_mean - sx_quad_rec, "s--", color=GREEN, linewidth=1.5,
                             label=f"Quad    RMSE={rmse_quad:.2f} mm")
                    ax2.axhline(0, color=MUTED, linewidth=0.8)
                    ax2.set_xlabel("True L (mm)"); ax2.set_ylabel("Residual  Sx − Sx\u0302  (mm)")
                    ax2.set_title("Residuals  —  Forward Sx")
                    ax2.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)
                    ax2.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
                    ax2.grid(alpha=0.15, color=BORDER)

                plt.tight_layout()
                plt.show()
                plt.close(fig)

        # ── Master refresh ────────────────────────────────────────────
        def refresh(_=None):
            mode = model_toggle.value
            section_header.value = _section_html(mode)

            if mode == "forward":
                controls.children = (
                    section_header, method_label, model_toggle,
                    input_label, fwd_input_box,
                )
            else:
                controls.children = (
                    section_header, method_label, model_toggle,
                    input_label, inv_input_box,
                )

            render_metrics(mode)
            render_result(mode)
            render_plot(mode)

        model_toggle.observe(refresh, names="value")
        Sx_input.observe(refresh, names="value")
        L_input.observe(refresh, names="value")

        refresh()

        # ── Assemble ──────────────────────────────────────────────────
        main_ui = widgets.VBox(
            [custom_css, title, controls, metrics_out, result_out, plot_out],
            layout=widgets.Layout(
                background_color=DARK,
                border=f"1px solid {BORDER}",
                border_radius="10px",
                overflow="hidden",
                padding="0 0 16px 0",
                width="1240px",
            ),
        )
        main_ui.add_class("m2-dark-ui")
        return main_ui
