import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import os

def integrated_calculator(csv_filename="ne555_full_dataset.csv"):
    """Reads the CSV, processes the data, and renders the integrated widget."""
    
    # 1. Load data & fit regression
    if not os.path.exists(csv_filename):
        print(f"Error: Could not find '{csv_filename}' in the current directory.")
        return
        
    df = pd.read_csv(csv_filename)
    
    recorded_df = df[df["n_readings"] != "PREDICTED"].copy()
    
    if "std_s" in recorded_df.columns:
        clean_df = recorded_df[recorded_df["std_s"] < 0.1].copy()
    else:
        clean_df = recorded_df.copy()

    X = clean_df["target_time_s"].values.reshape(-1, 1)
    y = clean_df["mean_s"].values
    model = LinearRegression().fit(X, y)
    
    SLOPE     = round(model.coef_[0], 6)
    INTERCEPT = round(model.intercept_, 6)
    r2        = np.corrcoef(clean_df["target_time_s"].values, y)[0, 1] ** 2

    # 2. Build recorded lookup dict
    RECORDED = {}
    for _, row in recorded_df.iterrows():
        key = f"{round(row['target_time_s'], 1):.1f}"
        RECORDED[key] = {
            "mean": round(row["mean_s"], 6),
            "std":  round(row.get("std_s", 0), 6),
        }

    recorded_json = json.dumps(RECORDED)
    
    # 3. Generate the Widget HTML/CSS/JS (Light Theme)
    html = f"""
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
    {len(recorded_df)} recorded measurements &middot;
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

  // Returns the NE555 predicted output time for a given dial step.
  // Prefers a recorded measurement; falls back to linear regression.
  function ne555_output(step) {{
    const key = step.toFixed(1);
    return RECORDED[key] ? RECORDED[key].mean : (SLOPE * step + INTERCEPT);
  }}

  // Scan every 0.1-s increment and return the step whose NE555
  // output is closest to the physics-derived target delay.
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

    // --- Physics / Kinematics Logic ---
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
      err.textContent = `Calculated delay (${{t_delay.toFixed(2)}}s) is still below 0.1s after adding 2π.`;
      nb_reset(false);
      return;
    }}

    err.textContent = '';

    // --- NE555 Step Selection (closest-output search) ---
    // Pick the dial step whose actual NE555 output is nearest to t_delay,
    // rather than simply rounding t_delay to the nearest 0.1 s.
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

    // --- Render ---
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
      document.getElementById('nb-sl').textContent = '0–9.9 s';
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

    // Show how we picked the step: best NE555 output vs raw t_delay
    document.getElementById('nb-f1').innerHTML = isRec
      ? 'Best step = ' + hl(step.toFixed(1) + ' s') + '  &rarr;  NE555 output = ' +
        grn(mean.toFixed(4) + ' s') + ' ' + grn('(recorded)') +
        ' ± ' + std.toFixed(4) + ' s std' +
        '  &nbsp;|&nbsp;  error = ' + hl(error + ' s')
      : 'Best step = ' + hl(step.toFixed(1) + ' s') + '  &rarr;  NE555 output = ' +
        blu(SLOPE) + ' × ' + hl(step.toFixed(1)) + ' + ' + blu(INTERCEPT) +
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
    ['nb-vt','nb-k1','nb-k2'].forEach(id => document.getElementById(id).textContent = '–');
    ['nb-d1','nb-d2'].forEach(id => document.getElementById(id).textContent = '–');
    ['nb-a1','nb-a2'].forEach(id => arc(id, 0));
    document.getElementById('nb-sv').textContent  = '–';
    document.getElementById('nb-sv').style.color  = '#6b7280';
    document.getElementById('nb-sl').textContent  = '–';
    document.getElementById('nb-sw').classList.remove('on');
    document.getElementById('nb-fm').classList.remove('show');
    if (clearErr) document.getElementById('nb-err').textContent = '';
  }};
}})();
</script>
"""
    
    # 4. Display or Export
    try:
        get_ipython()
        from IPython.display import display, HTML
        display(HTML(html))
    except NameError:
        import webbrowser
        output_file = "ne555_calculator.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>NE555 Calculator</title>\n"
                    "<style>body{background:#f3f4f6; display:flex; justify-content:center; padding:2rem;}</style>\n"
                    "</head>\n<body>\n")
            f.write(html)
            f.write("\n</body>\n</html>")
        print(f"Widget successfully generated: {output_file}")
        webbrowser.open('file://' + os.path.realpath(output_file))

integrated_calculator()