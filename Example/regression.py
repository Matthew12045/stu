# â”€â”€ Cell 4: Interactive UI â€” full draw length analysis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display
mean_xbar_pooled = [1548.07, 1657.67, 1783.74, 1946.85, 2067.23, 2199.73]
mean_rbar_pooled = [1548.10, 1657.70, 1783.80, 1946.90, 2067.30, 2199.70]
sigmax_pooled = [15.67, 17.58, 42.59, 35.89, 43.36, 36.25]
# â”€â”€ Experimental data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
L       = np.array([105, 110, 115, 120, 125, 130])
Sx_mean = np.array([1548.07, 1657.67, 1783.74, 1946.85, 2067.23, 2199.73])
sigma_Sx = np.array([15.67, 17.58, 42.59, 35.89, 43.36, 36.25])

Sx_MIN, Sx_MAX = Sx_mean.min(), Sx_mean.max()
L_MIN,  L_MAX  = L.min(), L.max()

# â”€â”€ Fits â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Direct inverse: L = f(Sx)
p_lin_direct  = np.polyfit(Sx_mean, L, 1)
p_quad_direct = np.polyfit(Sx_mean, L, 2)

# Natural direction: Sx = f(L)
p_lin_nat  = np.polyfit(L, Sx_mean, 1)
p_quad_nat = np.polyfit(L, Sx_mean, 2)

a1, b1 = p_lin_nat
a2, b2, c2 = p_quad_nat

# â”€â”€ Inversion functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def invert_linear(Sx):
    return (Sx - b1) / a1

def invert_quadratic(Sx):
    Sx_arr = np.asarray(Sx, dtype=float)

    disc = b2**2 - 4 * a2 * (c2 - Sx_arr)
    disc = np.maximum(disc, 0)

    return (-b2 + np.sqrt(disc)) / (2 * a2)

# â”€â”€ Metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def metrics(L_true, L_pred):
    L_true = np.asarray(L_true)
    L_pred = np.asarray(L_pred)

    res = L_true - L_pred
    rmse = np.sqrt(np.mean(res**2))

    ss_tot = np.sum((L_true - L_true.mean())**2)
    r2 = 1 - (np.sum(res**2) / ss_tot) if ss_tot != 0 else float("nan")

    return rmse, r2

# â”€â”€ Theme colors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

def styled(desc, val, unit=""):
    return (
        f"<span style='color:{MUTED};font-size:12px'>{desc}: </span>"
        f"<span style='color:{WHITE};font-weight:600'>{val}</span>"
        f"<span style='color:{MUTED};font-size:11px'> {unit}</span>"
    )

# â”€â”€ CSS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

# â”€â”€ Title â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
title = widgets.HTML(f"""
<div style='background:{DARK};padding:18px 24px 10px;border-bottom:2px solid {BORDER}'>
  <div style='color:{CYAN};font-family:monospace;font-size:11px;letter-spacing:3px;
              margin-bottom:4px'>M2 BALL LAUNCHER</div>
  <div style='color:{WHITE};font-size:22px;font-weight:700;font-family:monospace'>
    Draw Length Estimator</div>
  <div style='color:{MUTED};font-size:12px;margin-top:4px'>
    OLS fit with algebraic inversion &nbsp;Â·&nbsp;
    n = {len(L)} draw lengths &nbsp;Â·&nbsp;
    range {int(L.min())}â€“{int(L.max())} mm</div>
</div>
""")

# â”€â”€ Method toggle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
model_toggle = widgets.ToggleButtons(
    options=[
        ("Direct inverse fit",   "direct"),
        ("OLS natural + invert", "natural"),
        ("Forward  L â†’ Sx",      "forward"),
    ],
    value="natural",
    style={"button_width": "220px", "description_width": "0px"},
    layout=widgets.Layout(margin="12px 0 0 0"),
)

# â”€â”€ Inverse input: Sx â†’ L â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Sx_input = widgets.BoundedFloatText(
    value=1601.2,
    min=500,
    max=3000,
    step=0.5,
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
    for v in Sx_mean
]

for btn, v in zip(quick_btns, Sx_mean):
    btn.style.button_color = PANEL

    def _mk(val):
        def _cb(_):
            Sx_input.value = val
        return _cb

    btn.on_click(_mk(v))

# â”€â”€ Forward input: L â†’ Sx â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
L_input = widgets.BoundedFloatText(
    value=100.0,
    min=50,
    max=200,
    step=0.5,
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
    for v in L
]

for btn, v in zip(L_quick_btns, L):
    btn.style.button_color = PANEL

    def _mkL(val):
        def _cb(_):
            L_input.value = val
        return _cb

    btn.on_click(_mkL(v))

# â”€â”€ Output areas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
input_box   = widgets.VBox([])
result_out  = widgets.Output()
metrics_out = widgets.Output()
plot_out    = widgets.Output()

section_header = widgets.HTML("")

def _section_html(mode):
    if mode == "forward":
        label = "FORWARD PREDICTION  Â·  L â†’ Sx"
        desc  = "Input draw length L â†’ predict landing Sx directly"
        col   = PURPLE
    else:
        label = "INVERSE PREDICTION  Â·  Sx â†’ L"
        desc  = "Input landing Sx â†’ estimate draw length L"
        col   = CYAN

    return (
        f"<div style='padding:12px 0 4px'>"
        f"<div style='color:{col};font-family:monospace;font-size:11px;"
        f"letter-spacing:3px;margin-bottom:6px'>{label}</div>"
        f"<div style='color:{MUTED};font-size:12px'>{desc}</div></div>"
    )

# â”€â”€ Metrics panel â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def render_metrics(mode):
    metrics_out.clear_output(wait=True)

    with metrics_out:
        if mode == "forward":
            sx_lin_rec  = np.polyval(p_lin_nat, L)
            sx_quad_rec = np.polyval(p_quad_nat, L)

            rmse_f1 = np.sqrt(np.mean((Sx_mean - sx_lin_rec)**2))
            rmse_f2 = np.sqrt(np.mean((Sx_mean - sx_quad_rec)**2))

            r2_f1 = 1 - np.sum((Sx_mean - sx_lin_rec)**2) / np.sum((Sx_mean - Sx_mean.mean())**2)
            r2_f2 = 1 - np.sum((Sx_mean - sx_quad_rec)**2) / np.sum((Sx_mean - Sx_mean.mean())**2)

            eq_lin = f"Sx = {a1:.6f}Â·L {'+' if b1 >= 0 else ''}{b1:.4f}"
            eq_quad = (
                f"Sx = {a2:.8f}Â·LÂ² "
                f"{'+' if b2 >= 0 else ''}{b2:.6f}Â·L "
                f"{'+' if c2 >= 0 else ''}{c2:.4f}"
            )

            rm1, rm2, r1, r2_ = rmse_f1, rmse_f2, r2_f1, r2_f2
            note, note_col = "OLS natural direction â€” L is error-free, Sx carries noise âœ“", GREEN

        elif mode == "direct":
            l_lin_rec  = np.polyval(p_lin_direct, Sx_mean)
            l_quad_rec = np.polyval(p_quad_direct, Sx_mean)

            rmse_d1, r2_d1 = metrics(L, l_lin_rec)
            rmse_d2, r2_d2 = metrics(L, l_quad_rec)

            eq_lin = (
                f"L = {p_lin_direct[0]:.6f}Â·Sx "
                f"{'+' if p_lin_direct[1] >= 0 else ''}{p_lin_direct[1]:.4f}"
            )
            eq_quad = (
                f"L = {p_quad_direct[0]:.8f}Â·SxÂ² "
                f"{'+' if p_quad_direct[1] >= 0 else ''}{p_quad_direct[1]:.6f}Â·Sx "
                f"{'+' if p_quad_direct[2] >= 0 else ''}{p_quad_direct[2]:.4f}"
            )

            rm1, rm2, r1, r2_ = rmse_d1, rmse_d2, r2_d1, r2_d2
            note, note_col = "Direct polyfit(Sx, L) â€” treats noisy Sx as error-free", ORANGE

        else:
            l_lin_rec  = invert_linear(Sx_mean)
            l_quad_rec = invert_quadratic(Sx_mean)

            rmse_n1, r2_n1 = metrics(L, l_lin_rec)
            rmse_n2, r2_n2 = metrics(L, l_quad_rec)

            eq_lin = (
                f"Sx = {a1:.6f}Â·L {'+' if b1 >= 0 else ''}{b1:.4f}  "
                f"â†’  L = (Sx âˆ’ {b1:.2f}) / {a1:.6f}"
            )
            eq_quad = (
                f"Sx = {a2:.8f}Â·LÂ² "
                f"{'+' if b2 >= 0 else ''}{b2:.6f}Â·L "
                f"{'+' if c2 >= 0 else ''}{c2:.4f}  â†’  quadratic formula"
            )

            rm1, rm2, r1, r2_ = rmse_n1, rmse_n2, r2_n1, r2_n2
            note, note_col = "OLS natural direction â€” L is error-free, Sx carries noise âœ“", GREEN

        display(widgets.HTML(f"""
<div style='background:{PANEL};border:1px solid {BORDER};border-radius:8px;
            padding:14px 18px;font-family:monospace;font-size:12px;margin:6px 0'>
  <div style='color:{CYAN};font-size:11px;letter-spacing:2px;margin-bottom:10px'>
    MODEL EQUATIONS</div>

  <div style='color:{MUTED};margin-bottom:3px'>Linear:</div>
  <div style='color:{WHITE};margin-bottom:10px;padding-left:12px'>{eq_lin}</div>

  <div style='color:{MUTED};margin-bottom:3px'>Quadratic:</div>
  <div style='color:{WHITE};padding-left:12px'>{eq_quad}</div>

  <hr style='border-color:{BORDER};margin:10px 0'>

  <div style='display:flex;gap:32px'>
    <div>{styled('Linear RMSE', f'{rm1:.4f}', 'mm')}</div>
    <div>{styled('Linear RÂ²',   f'{r1:.8f}')}</div>
    <div>{styled('Quad RMSE',   f'{rm2:.4f}', 'mm')}</div>
    <div>{styled('Quad RÂ²',     f'{r2_:.8f}')}</div>
  </div>

  <div style='margin-top:10px;color:{note_col};font-size:11px'>{note}</div>
</div>
"""))

# â”€â”€ Result card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def render_result(mode):
    result_out.clear_output(wait=True)

    with result_out:
        if mode == "forward":
            Lv = L_input.value

            sx_lin  = np.polyval(p_lin_nat, Lv)
            sx_quad = np.polyval(p_quad_nat, Lv)

            delta = abs(sx_lin - sx_quad)
            idx = int(np.argmin(np.abs(L - Lv)))

            warn = (
                f"<div style='color:{ORANGE};margin-top:8px;font-size:11px'>"
                f"âš ï¸ Outside calibrated range [{int(L_MIN)}, {int(L_MAX)}] mm â€” "
                f"extrapolation only</div>"
                if Lv < L_MIN or Lv > L_MAX else ""
            )

            agree = GREEN if delta < 10 else ORANGE if delta < 30 else PINK

            header_col = PURPLE
            header_lbl = "PREDICTION  Â·  L â†’ Sx  (forward, no inversion)"
            input_lbl  = "L ="
            input_val  = f"{Lv:.2f}"

            val_lin  = f"{sx_lin:.2f}"
            val_quad = f"{sx_quad:.2f}"

            unit_lin = unit_quad = "mm landing"

            extra = (
                f"<div style='border-left:1px solid {BORDER};padding-left:28px'>"
                f"<div style='color:{MUTED};font-size:11px;margin-bottom:4px'>"
                f"NEAREST CALIBRATION POINT</div>"
                f"<div style='color:{CYAN};font-size:16px;font-weight:700'>"
                f"L={int(L[idx])} mm â†’ {Sx_mean[idx]:.2f} mm</div>"
                f"<div style='color:{MUTED};font-size:11px'>"
                f"Ïƒ = {sigma_Sx[idx]:.2f} mm"
                f" &nbsp;(Â±2Ïƒ = {2 * sigma_Sx[idx]:.2f} mm)</div></div>"
            )

            delta_fmt = f"{delta:.2f}"

        else:
            Sx = Sx_input.value

            if mode == "direct":
                l_lin  = np.polyval(p_lin_direct, Sx)
                l_quad = np.polyval(p_quad_direct, Sx)
            else:
                l_lin  = invert_linear(Sx)
                l_quad = invert_quadratic(Sx)

            delta = abs(l_lin - l_quad)

            warn = (
                f"<div style='color:{ORANGE};margin-top:8px;font-size:11px'>"
                f"âš ï¸ Outside calibrated range [{Sx_MIN:.1f}, {Sx_MAX:.1f}] mm â€” "
                f"extrapolation only</div>"
                if Sx < Sx_MIN or Sx > Sx_MAX else ""
            )

            agree = GREEN if delta < 0.5 else ORANGE if delta < 1.5 else PINK

            header_col = CYAN
            header_lbl = "PREDICTION  Â·  Sx â†’ L"
            input_lbl  = "Sx ="
            input_val  = f"{Sx:.2f}"

            val_lin  = f"{l_lin:.3f}"
            val_quad = f"{l_quad:.3f}"

            unit_lin = unit_quad = "mm draw length"
            extra = ""
            delta_fmt = f"{delta:.3f}"

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
      <div style='color:{MUTED};font-size:11px;margin-bottom:4px'>Î” MODELS</div>
      <div style='color:{agree};font-size:22px;font-weight:700'>{delta_fmt}</div>
      <div style='color:{MUTED};font-size:11px'>mm difference</div>
    </div>

    {extra}
  </div>

  {warn}
</div>
"""))

# â”€â”€ Plot renderer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def render_plot(mode):
    plot_out.clear_output(wait=True)

    with plot_out:
        # Corrected fine intervals with padding.
        # These are only for smooth plotting, not for changing the fitted model.
        L_pad  = 0.08 * (L_MAX - L_MIN)
        Sx_pad = 0.08 * (Sx_MAX - Sx_MIN)

        L_fine  = np.linspace(L_MIN  - L_pad,  L_MAX  + L_pad,  500)
        Sx_fine = np.linspace(Sx_MIN - Sx_pad, Sx_MAX + Sx_pad, 600)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), facecolor=DARK)

        for ax in (ax1, ax2):
            ax.set_facecolor(PANEL)
            ax.tick_params(colors=MUTED, labelsize=8)
            ax.xaxis.label.set_color(MUTED)
            ax.yaxis.label.set_color(MUTED)
            ax.title.set_color(WHITE)

            for sp in ax.spines.values():
                sp.set_color(BORDER)

        # â”€â”€ Mode A: Direct inverse fit, L = f(Sx) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if mode == "direct":
            l_fine_lin  = np.polyval(p_lin_direct, Sx_fine)
            l_fine_quad = np.polyval(p_quad_direct, Sx_fine)

            l_rec_lin  = np.polyval(p_lin_direct, Sx_mean)
            l_rec_quad = np.polyval(p_quad_direct, Sx_mean)

            ax1.errorbar(
                Sx_mean,
                L,
                xerr=2 * sigma_Sx,
                fmt="o",
                color=CYAN,
                ecolor=CYAN + "55",
                capsize=3,
                zorder=5,
                label="Data (Â±2Ïƒ)",
            )

            ax1.plot(Sx_fine, l_fine_lin, color=PINK, linewidth=1.8, label="Linear")
            ax1.plot(Sx_fine, l_fine_quad, color=GREEN, linewidth=1.8,
                     linestyle="--", label="Quadratic")

            l_at_Sx_lin  = np.polyval(p_lin_direct, Sx_input.value)
            l_at_Sx_quad = np.polyval(p_quad_direct, Sx_input.value)

            ax1.axvline(Sx_input.value, color=ORANGE, linewidth=1.2,
                        linestyle=":", alpha=0.9, label=f"Sx={Sx_input.value:.0f} mm")
            ax1.axhline(l_at_Sx_lin, color=PINK, linewidth=0.8,
                        linestyle=":", alpha=0.7)
            ax1.axhline(l_at_Sx_quad, color=GREEN, linewidth=0.8,
                        linestyle=":", alpha=0.7)

            ax1.set_xlabel("Landing Sx (mm)")
            ax1.set_ylabel("Draw Length L (mm)")
            ax1.set_title("L = f(Sx)  â€”  Direct inverse fit")
            ax1.set_xlim(Sx_MIN - Sx_pad, Sx_MAX + Sx_pad)
            ax1.set_ylim(L_MIN - L_pad, L_MAX + L_pad)
            ax1.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
            ax1.grid(alpha=0.15, color=BORDER)

            ax2.plot(L, L - l_rec_lin, "o-", color=PINK, linewidth=1.5,
                     label=f"Linear  RMSE={metrics(L, l_rec_lin)[0]:.4f} mm")
            ax2.plot(L, L - l_rec_quad, "s--", color=GREEN, linewidth=1.5,
                     label=f"Quad    RMSE={metrics(L, l_rec_quad)[0]:.4f} mm")

            ax2.axhline(0, color=MUTED, linewidth=0.8)
            ax2.set_xlabel("True L (mm)")
            ax2.set_ylabel("Residual  L âˆ’ LÌ‚  (mm)")
            ax2.set_title("Residuals  â€”  Direct inverse")
            ax2.set_xlim(L_MIN - L_pad, L_MAX + L_pad)
            ax2.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
            ax2.grid(alpha=0.15, color=BORDER)

        # â”€â”€ Mode B: Natural fit + algebraic inversion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        elif mode == "natural":
            l_rec_lin  = invert_linear(Sx_mean)
            l_rec_quad = invert_quadratic(Sx_mean)

            l_inv_lin  = invert_linear(Sx_fine)
            l_inv_quad = invert_quadratic(Sx_fine)

            ax1.errorbar(
                Sx_mean,
                L,
                xerr=2 * sigma_Sx,
                fmt="o",
                color=CYAN,
                ecolor=CYAN + "55",
                capsize=3,
                zorder=5,
                label="Data (Â±2Ïƒ)",
            )

            ax1.plot(Sx_fine, l_inv_lin, color=PINK, linewidth=1.8,
                     label="Linear  (inverted)")
            ax1.plot(Sx_fine, l_inv_quad, color=GREEN, linewidth=1.8,
                     linestyle="--", label="Quadratic  (inverted)")

            l_at_Sx_lin  = invert_linear(Sx_input.value)
            l_at_Sx_quad = invert_quadratic(Sx_input.value)

            ax1.axvline(Sx_input.value, color=ORANGE, linewidth=1.2,
                        linestyle=":", alpha=0.9, label=f"Sx={Sx_input.value:.0f} mm")
            ax1.axhline(l_at_Sx_lin, color=PINK, linewidth=0.8,
                        linestyle=":", alpha=0.7)
            ax1.axhline(l_at_Sx_quad, color=GREEN, linewidth=0.8,
                        linestyle=":", alpha=0.7)

            ax1.set_xlabel("Landing Sx (mm)")
            ax1.set_ylabel("Draw Length L (mm)")
            ax1.set_title("L = fâ»Â¹(Sx)  â€”  OLS natural + inversion")
            ax1.set_xlim(Sx_MIN - Sx_pad, Sx_MAX + Sx_pad)
            ax1.set_ylim(L_MIN - L_pad, L_MAX + L_pad)
            ax1.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
            ax1.grid(alpha=0.15, color=BORDER)

            ax2.plot(L, L - l_rec_lin, "o-", color=PINK, linewidth=1.5,
                     label=f"Linear  RMSE={metrics(L, l_rec_lin)[0]:.4f} mm")
            ax2.plot(L, L - l_rec_quad, "s--", color=GREEN, linewidth=1.5,
                     label=f"Quad    RMSE={metrics(L, l_rec_quad)[0]:.4f} mm")

            ax2.axhline(0, color=MUTED, linewidth=0.8)
            ax2.set_xlabel("True L (mm)")
            ax2.set_ylabel("Residual  L âˆ’ LÌ‚  (mm)")
            ax2.set_title("Residuals  â€”  OLS natural + inversion")
            ax2.set_xlim(L_MIN - L_pad, L_MAX + L_pad)
            ax2.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
            ax2.grid(alpha=0.15, color=BORDER)

        # â”€â”€ Mode C: Forward prediction, Sx = f(L) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        else:
            sx_lin_fine  = np.polyval(p_lin_nat, L_fine)
            sx_quad_fine = np.polyval(p_quad_nat, L_fine)

            sx_lin_rec  = np.polyval(p_lin_nat, L)
            sx_quad_rec = np.polyval(p_quad_nat, L)

            ax1.errorbar(
                L,
                Sx_mean,
                yerr=2 * sigma_Sx,
                fmt="o",
                color=CYAN,
                ecolor=CYAN + "55",
                capsize=3,
                zorder=5,
                label="Data (Â±2Ïƒ)",
            )

            ax1.plot(L_fine, sx_lin_fine, color=PINK, linewidth=1.8, label="Linear")
            ax1.plot(L_fine, sx_quad_fine, color=GREEN, linewidth=1.8,
                     linestyle="--", label="Quadratic")

            sx_lin_pt  = np.polyval(p_lin_nat, L_input.value)
            sx_quad_pt = np.polyval(p_quad_nat, L_input.value)

            ax1.axvline(L_input.value, color=PURPLE, linewidth=1.2,
                        linestyle=":", alpha=0.9, label=f"L={L_input.value:.0f} mm")
            ax1.axhline(sx_lin_pt, color=PINK, linewidth=0.8,
                        linestyle=":", alpha=0.7)
            ax1.axhline(sx_quad_pt, color=GREEN, linewidth=0.8,
                        linestyle=":", alpha=0.7)

            ax1.set_xlabel("Draw Length L (mm)")
            ax1.set_ylabel("Landing Sx (mm)")
            ax1.set_title("Sx = f(L)  â€”  Forward  (no inversion)")
            ax1.set_xlim(L_MIN - L_pad, L_MAX + L_pad)
            ax1.set_ylim(Sx_MIN - Sx_pad, Sx_MAX + Sx_pad)
            ax1.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
            ax1.grid(alpha=0.15, color=BORDER)

            rmse_lin  = np.sqrt(np.mean((Sx_mean - sx_lin_rec)**2))
            rmse_quad = np.sqrt(np.mean((Sx_mean - sx_quad_rec)**2))

            ax2.plot(L, Sx_mean - sx_lin_rec, "o-", color=PINK, linewidth=1.5,
                     label=f"Linear  RMSE={rmse_lin:.2f} mm")
            ax2.plot(L, Sx_mean - sx_quad_rec, "s--", color=GREEN, linewidth=1.5,
                     label=f"Quad    RMSE={rmse_quad:.2f} mm")

            ax2.axhline(0, color=MUTED, linewidth=0.8)
            ax2.set_xlabel("True L (mm)")
            ax2.set_ylabel("Residual  Sx âˆ’ SxÌ‚  (mm)")
            ax2.set_title("Residuals  â€”  Forward Sx")
            ax2.set_xlim(L_MIN - L_pad, L_MAX + L_pad)
            ax2.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
            ax2.grid(alpha=0.15, color=BORDER)

        plt.tight_layout()
        plt.savefig(
            "/tmp/dl_plot.png",
            dpi=130,
            bbox_inches="tight",
            facecolor=DARK,
        )
        plt.show()
        plt.close(fig)

# â”€â”€ Layout helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
quick_row = widgets.HBox(
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
    section_header,
    method_label,
    model_toggle,
    input_label,
    input_box,
])

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

# â”€â”€ Master refresh â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def refresh(_=None):
    mode = model_toggle.value

    section_header.value = _section_html(mode)

    if mode == "forward":
        controls.children = (
            section_header,
            method_label,
            model_toggle,
            input_label,
            fwd_input_box,
        )
    else:
        controls.children = (
            section_header,
            method_label,
            model_toggle,
            input_label,
            inv_input_box,
        )

    render_metrics(mode)
    render_result(mode)
    render_plot(mode)

model_toggle.observe(refresh, names="value")
Sx_input.observe(refresh, names="value")
L_input.observe(refresh, names="value")

refresh()
display(main_ui)