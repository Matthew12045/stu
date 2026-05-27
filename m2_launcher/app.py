"""
M2 Launcher Application — Standalone (matplotlib only)
=======================================================
No Jupyter / ipywidgets dependency.  Uses matplotlib.widgets
for interactive sliders, buttons, and text boxes.

Run with:  ``python run.py``
"""

import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
from matplotlib.patches import Arc, FancyBboxPatch, Circle, Wedge
import matplotlib.patches as mpatches

from .timer_model import NE555TimerModel
from .physics import PhysicsEngine
from .regression import DrawLengthRegression


# ── Theme colours ─────────────────────────────────────────────────────
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
BLUE   = "#3b82f6"
AMBER  = "#f59e0b"


class M2LauncherApp:
    """Combined M2 Ball Launcher application (standalone matplotlib).

    Brings together:
    * :class:`NE555TimerModel` – timer calibration and dial mapping
    * :class:`PhysicsEngine` – projectile kinematics
    * :class:`DrawLengthRegression` – OLS regression (3 modes)

    Call :meth:`run` to launch the interactive matplotlib windows.
    """

    def __init__(self, csv_path: str | None = None):
        self.timer   = NE555TimerModel(csv_path)
        self.physics = PhysicsEngine()
        self.reg     = DrawLengthRegression()

    # ==================================================================
    #  PUBLIC
    # ==================================================================

    def run(self):
        """Launch both windows and enter the matplotlib event loop."""
        self._build_delay_window()
        self._build_regression_window()
        plt.show()

    def display(self):
        """Alias for run() — backward compatibility."""
        self.run()

    # ==================================================================
    #  WINDOW 1 — DELAY CALCULATOR
    # ==================================================================

    def _build_delay_window(self):
        """Create the delay-calculator figure with sliders."""
        fig = plt.figure("Delay & Timer Calculator", figsize=(10, 7.5))
        fig.patch.set_facecolor(DARK)

        # ── Header ────────────────────────────────────────────────────
        fig.text(0.05, 0.95, "DELAY & TIMER CALCULATOR", fontsize=16,
                 fontweight="bold", color=CYAN, fontfamily="monospace",
                 va="top")
        fig.text(0.05, 0.91,
                 f"{self.timer.n_recorded} recorded · "
                 f"regression: {self.timer.slope}×t + {self.timer.intercept} · "
                 f"R²={self.timer.r_squared:.4f}",
                 fontsize=9, color=MUTED, fontfamily="monospace", va="top")

        # ── Sliders ───────────────────────────────────────────────────
        ax_sx  = fig.add_axes([0.15, 0.82, 0.70, 0.03])
        ax_rpm = fig.add_axes([0.15, 0.77, 0.70, 0.03])
        ax_phi = fig.add_axes([0.15, 0.72, 0.70, 0.03])

        for ax in (ax_sx, ax_rpm, ax_phi):
            ax.set_facecolor(PANEL)

        s_sx  = Slider(ax_sx,  "Sx (mm)",  100, 2400, valinit=2292,
                       valstep=1, color=CYAN)
        s_rpm = Slider(ax_rpm, "RPM",      1, 30, valinit=9,
                       valstep=0.5, color=PINK)
        s_phi = Slider(ax_phi, "φ (deg)",  0, 360, valinit=270,
                       valstep=1, color=PURPLE)

        for s in (s_sx, s_rpm, s_phi):
            s.label.set_color(MUTED)
            s.label.set_fontfamily("monospace")
            s.valtext.set_color(WHITE)
            s.valtext.set_fontfamily("monospace")

        # ── Dial gauges (knob1, knob2 arcs) ───────────────────────────
        ax_k1 = fig.add_axes([0.10, 0.28, 0.20, 0.30], aspect="equal")
        ax_k2 = fig.add_axes([0.40, 0.28, 0.20, 0.30], aspect="equal")
        ax_sw = fig.add_axes([0.70, 0.28, 0.20, 0.30], aspect="equal")

        for ax in (ax_k1, ax_k2, ax_sw):
            ax.set_facecolor(DARK)
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)

        # Draw background arcs
        bg_arc_kw = dict(fill=False, linewidth=6, edgecolor=BORDER)
        ax_k1.add_patch(Arc((0, 0), 2, 2, angle=0, theta1=-225, theta2=45, **bg_arc_kw))
        ax_k2.add_patch(Arc((0, 0), 2, 2, angle=0, theta1=-225, theta2=45, **bg_arc_kw))

        # Foreground arcs (will be redrawn)
        self._k1_arc = None
        self._k2_arc = None

        # Labels
        ax_k1.set_title("KNOB 1", fontsize=9, color=MUTED, fontfamily="monospace", pad=4)
        ax_k2.set_title("KNOB 2", fontsize=9, color=MUTED, fontfamily="monospace", pad=4)
        ax_sw.set_title("SWITCH", fontsize=9, color=MUTED, fontfamily="monospace", pad=4)

        # Text objects
        self._k1_txt = ax_k1.text(0, 0, "–", ha="center", va="center",
                                   fontsize=28, fontweight="bold", color=BLUE,
                                   fontfamily="monospace")
        self._k1_sub = ax_k1.text(0, -1.2, "pos 0–9", ha="center", va="center",
                                   fontsize=8, color=MUTED, fontfamily="monospace")
        self._k2_txt = ax_k2.text(0, 0, "–", ha="center", va="center",
                                   fontsize=28, fontweight="bold", color=AMBER,
                                   fontfamily="monospace")
        self._k2_sub = ax_k2.text(0, -1.2, "pos 0–9", ha="center", va="center",
                                   fontsize=8, color=MUTED, fontfamily="monospace")
        self._sw_txt = ax_sw.text(0, 0.1, "–", ha="center", va="center",
                                   fontsize=22, fontweight="bold", color=MUTED,
                                   fontfamily="monospace")
        self._sw_sub = ax_sw.text(0, -0.6, "–", ha="center", va="center",
                                   fontsize=9, color=MUTED, fontfamily="monospace")

        # ── Result text ───────────────────────────────────────────────
        self._delay_title = fig.text(
            0.50, 0.66, "", ha="center", va="top",
            fontsize=13, fontweight="bold", color=PURPLE, fontfamily="monospace")
        self._delay_info = fig.text(
            0.50, 0.62, "", ha="center", va="top",
            fontsize=9, color=WHITE, fontfamily="monospace")

        # ── Formula / details ─────────────────────────────────────────
        self._detail_lines = []
        for i in range(4):
            t = fig.text(0.05, 0.22 - i * 0.04, "", fontsize=8,
                         color=MUTED, fontfamily="monospace", va="top")
            self._detail_lines.append(t)

        self._err_text = fig.text(
            0.50, 0.25, "", ha="center", va="top",
            fontsize=10, fontweight="bold", color="#ef4444", fontfamily="monospace")

        # Store refs
        self._delay_fig = fig
        self._ax_k1 = ax_k1
        self._ax_k2 = ax_k2
        self._ax_sw = ax_sw

        # ── Connect sliders ───────────────────────────────────────────
        def update(_=None):
            self._update_delay(s_sx.val, s_rpm.val, s_phi.val)

        s_sx.on_changed(update)
        s_rpm.on_changed(update)
        s_phi.on_changed(update)

        update()  # initial draw

    def _draw_knob_arc(self, ax, pos, color, old_arc_attr):
        """Draw a coloured arc for a knob position (0–9)."""
        old = getattr(self, old_arc_attr, None)
        if old is not None:
            old.remove()
        frac = pos / 9.0
        theta_span = 270 * frac
        arc = Arc((0, 0), 2, 2, angle=0, theta1=45,
                  theta2=45 + theta_span,
                  linewidth=6, edgecolor=color, fill=False)
        ax.add_patch(arc)
        setattr(self, old_arc_attr, arc)

    def _update_delay(self, sx_mm, rpm, phi_deg):
        """Recompute and redraw the delay calculator display."""
        # Clear errors
        self._err_text.set_text("")

        try:
            result = self.physics.compute_delay_time(sx_mm, rpm, phi_deg)
        except ValueError as e:
            self._err_text.set_text(str(e))
            self._delay_title.set_text("")
            self._delay_info.set_text("")
            self._k1_txt.set_text("–")
            self._k2_txt.set_text("–")
            self._sw_txt.set_text("–")
            self._sw_sub.set_text("–")
            for ln in self._detail_lines:
                ln.set_text("")
            self._delay_fig.canvas.draw_idle()
            return

        t_delay = result["t_delay"]
        t_flight = result["t_flight"]
        cycle_added = result["cycle_added"]

        # Find best NE555 step
        step = self.timer.best_step(t_delay)
        decomp = self.timer.decompose_step(step)

        knob1     = decomp["knob1"]
        knob2     = decomp["knob2"]
        switch_on = decomp["switch_on"]
        ne555_mean = decomp["ne555_mean"]
        ne555_std  = decomp["ne555_std"]
        is_rec     = decomp["is_recorded"]
        error      = ne555_mean - t_delay

        # Update title
        self._delay_title.set_text(f"Target Delay: {step:.1f} s")

        info_parts = [f"T_flight={t_flight:.4f}s  |  T_delay={t_delay:.4f}s"]
        if cycle_added:
            info_parts.append("(+2π/ω cycle added)")
        self._delay_info.set_text("  ".join(info_parts))

        # Update knobs
        self._k1_txt.set_text(str(knob1))
        self._k2_txt.set_text(str(knob2))
        self._draw_knob_arc(self._ax_k1, knob1, BLUE, "_k1_arc")
        self._draw_knob_arc(self._ax_k2, knob2, AMBER, "_k2_arc")

        # Update switch
        if switch_on:
            self._sw_txt.set_text("ON")
            self._sw_txt.set_color(GREEN)
            self._sw_sub.set_text("10 s range")
        else:
            self._sw_txt.set_text("OFF")
            self._sw_txt.set_color(MUTED)
            self._sw_sub.set_text("0–9.9 s")

        # Update detail lines
        src = "RECORDED" if is_rec else "REGRESSION"
        std_str = f" ± {ne555_std:.4f}" if ne555_std else ""
        lines = [
            f"NE555 output = {ne555_mean:.4f}s ({src}){std_str}  |  error = {error:.4f}s",
            f"switch={'ON' if switch_on else 'OFF'}  →  effective = {decomp['effective']:.1f}s",
            f"knob2 = floor({decomp['effective']:.1f}) = {knob2}  |  "
            f"knob1 = round(({decomp['effective']:.1f} - {knob2}) × 10) = {knob1}",
            f"ω = {result['omega']:.4f} rad/s  |  c = {result['c_const']:.6f} rad",
        ]
        for i, ln in enumerate(self._detail_lines):
            ln.set_text(lines[i] if i < len(lines) else "")

        self._delay_fig.canvas.draw_idle()

    # ==================================================================
    #  WINDOW 2 — DRAW LENGTH REGRESSION
    # ==================================================================

    def _build_regression_window(self):
        """Create the regression figure with interactive controls."""
        reg = self.reg

        fig, axes = plt.subplots(1, 2, figsize=(13, 6), num="Draw Length Regression")
        fig.patch.set_facecolor(DARK)
        fig.subplots_adjust(left=0.08, right=0.96, bottom=0.30, top=0.88, wspace=0.30)

        # Title
        fig.text(0.50, 0.96, "DRAW LENGTH ESTIMATOR", ha="center",
                 fontsize=16, fontweight="bold", color=CYAN, fontfamily="monospace")
        fig.text(0.50, 0.92,
                 f"OLS fit with algebraic inversion  ·  n={len(reg.L)} draw lengths  ·  "
                 f"range {int(reg.L_min)}–{int(reg.L_max)} mm",
                 ha="center", fontsize=9, color=MUTED, fontfamily="monospace")

        # ── Radio buttons for mode ────────────────────────────────────
        ax_radio = fig.add_axes([0.02, 0.02, 0.22, 0.18], facecolor=PANEL)
        ax_radio.set_title("METHOD", fontsize=9, color=MUTED,
                           fontfamily="monospace", pad=6)
        radio = RadioButtons(ax_radio,
                             ("Natural + Invert", "Direct Inverse", "Forward L→Sx"),
                             active=0)
        for lbl in radio.labels:
            lbl.set_fontsize(9)
            lbl.set_color(WHITE)
            lbl.set_fontfamily("monospace")

        # ── Slider for Sx input ───────────────────────────────────────
        ax_sx_slider = fig.add_axes([0.35, 0.10, 0.55, 0.03], facecolor=PANEL)
        s_sx = Slider(ax_sx_slider, "Sx (mm)", reg.Sx_min - 100, reg.Sx_max + 200,
                      valinit=1800, valstep=1, color=CYAN)
        s_sx.label.set_color(MUTED)
        s_sx.label.set_fontfamily("monospace")
        s_sx.valtext.set_color(WHITE)
        s_sx.valtext.set_fontfamily("monospace")

        # ── Slider for L input (used in forward mode) ─────────────────
        ax_L_slider = fig.add_axes([0.35, 0.05, 0.55, 0.03], facecolor=PANEL)
        s_L = Slider(ax_L_slider, "L (mm)", reg.L_min - 10, reg.L_max + 15,
                     valinit=115, valstep=0.5, color=PURPLE)
        s_L.label.set_color(MUTED)
        s_L.label.set_fontfamily("monospace")
        s_L.valtext.set_color(WHITE)
        s_L.valtext.set_fontfamily("monospace")

        # ── Metrics text ──────────────────────────────────────────────
        self._reg_metrics_text = fig.text(
            0.35, 0.22, "", fontsize=8, color=WHITE, fontfamily="monospace",
            va="top")

        # Store refs
        self._reg_fig = fig
        self._reg_axes = axes
        self._reg_radio = radio
        self._reg_mode_map = {
            "Natural + Invert": "natural",
            "Direct Inverse":   "direct",
            "Forward L→Sx":     "forward",
        }

        # ── Draw function ─────────────────────────────────────────────
        def update(_=None):
            mode_label = radio.value_selected
            mode = self._reg_mode_map[mode_label]
            self._draw_regression(axes, mode, s_sx.val, s_L.val)
            fig.canvas.draw_idle()

        radio.on_clicked(update)
        s_sx.on_changed(update)
        s_L.on_changed(update)

        update()  # initial draw

    def _draw_regression(self, axes, mode, sx_val, L_val):
        """Redraw the regression plots for the given mode and input value."""
        reg = self.reg
        ax1, ax2 = axes

        for ax in axes:
            ax.clear()
            ax.set_facecolor(PANEL)
            ax.tick_params(colors=MUTED, labelsize=8)
            ax.xaxis.label.set_color(MUTED)
            ax.yaxis.label.set_color(MUTED)
            ax.title.set_color(WHITE)
            for sp in ax.spines.values():
                sp.set_color(BORDER)

        L_pad  = 0.08 * (reg.L_max - reg.L_min)
        Sx_pad = 0.08 * (reg.Sx_max - reg.Sx_min)

        L_fine  = np.linspace(reg.L_min - L_pad,  reg.L_max + L_pad,  500)
        Sx_fine = np.linspace(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad, 600)

        m = reg.mode_metrics(mode)

        if mode == "direct":
            l_fine_lin  = np.polyval(reg.p_lin_direct, Sx_fine)
            l_fine_quad = np.polyval(reg.p_quad_direct, Sx_fine)
            l_rec_lin   = np.polyval(reg.p_lin_direct, reg.Sx_mean)
            l_rec_quad  = np.polyval(reg.p_quad_direct, reg.Sx_mean)

            ax1.errorbar(reg.Sx_mean, reg.L, xerr=2*reg.sigma_Sx, fmt="o",
                         color=CYAN, ecolor=CYAN+"55", capsize=3, zorder=5, label="Data (±2σ)")
            ax1.plot(Sx_fine, l_fine_lin, color=PINK, linewidth=1.8, label="Linear")
            ax1.plot(Sx_fine, l_fine_quad, color=GREEN, linewidth=1.8, linestyle="--", label="Quadratic")
            ax1.axvline(sx_val, color=ORANGE, linewidth=1.2, linestyle=":", alpha=0.9,
                        label=f"Sx={sx_val:.0f}")
            ax1.set_xlabel("Landing Sx (mm)"); ax1.set_ylabel("Draw Length L (mm)")
            ax1.set_title("L = f(Sx)  —  Direct inverse fit", fontsize=10)
            ax1.set_xlim(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad)
            ax1.set_ylim(reg.L_min - L_pad, reg.L_max + L_pad)

            l_lin  = float(np.polyval(reg.p_lin_direct, sx_val))
            l_quad = float(np.polyval(reg.p_quad_direct, sx_val))

            ax2.plot(reg.L, reg.L - l_rec_lin, "o-", color=PINK, linewidth=1.5,
                     label=f"Linear  RMSE={m['rmse_lin']:.4f}")
            ax2.plot(reg.L, reg.L - l_rec_quad, "s--", color=GREEN, linewidth=1.5,
                     label=f"Quad  RMSE={m['rmse_quad']:.4f}")
            ax2.axhline(0, color=MUTED, linewidth=0.8)
            ax2.set_xlabel("True L (mm)"); ax2.set_ylabel("Residual (mm)")
            ax2.set_title("Residuals", fontsize=10)
            ax2.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)

            pred_str = (f"Sx={sx_val:.0f} mm  →  L_lin={l_lin:.3f}  |  "
                        f"L_quad={l_quad:.3f}  |  Δ={abs(l_lin-l_quad):.3f} mm")

        elif mode == "natural":
            l_inv_lin   = reg.invert_linear(Sx_fine)
            l_inv_quad  = reg.invert_quadratic(Sx_fine)
            l_rec_lin   = reg.invert_linear(reg.Sx_mean)
            l_rec_quad  = reg.invert_quadratic(reg.Sx_mean)

            ax1.errorbar(reg.Sx_mean, reg.L, xerr=2*reg.sigma_Sx, fmt="o",
                         color=CYAN, ecolor=CYAN+"55", capsize=3, zorder=5, label="Data (±2σ)")
            ax1.plot(Sx_fine, l_inv_lin, color=PINK, linewidth=1.8, label="Linear (inverted)")
            ax1.plot(Sx_fine, l_inv_quad, color=GREEN, linewidth=1.8, linestyle="--", label="Quad (inverted)")
            ax1.axvline(sx_val, color=ORANGE, linewidth=1.2, linestyle=":", alpha=0.9,
                        label=f"Sx={sx_val:.0f}")
            ax1.set_xlabel("Landing Sx (mm)"); ax1.set_ylabel("Draw Length L (mm)")
            ax1.set_title("L = f⁻¹(Sx)  —  OLS natural + inversion", fontsize=10)
            ax1.set_xlim(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad)
            ax1.set_ylim(reg.L_min - L_pad, reg.L_max + L_pad)

            l_lin  = float(reg.invert_linear(sx_val))
            l_quad = float(reg.invert_quadratic(sx_val))

            ax2.plot(reg.L, reg.L - l_rec_lin, "o-", color=PINK, linewidth=1.5,
                     label=f"Linear  RMSE={m['rmse_lin']:.4f}")
            ax2.plot(reg.L, reg.L - l_rec_quad, "s--", color=GREEN, linewidth=1.5,
                     label=f"Quad  RMSE={m['rmse_quad']:.4f}")
            ax2.axhline(0, color=MUTED, linewidth=0.8)
            ax2.set_xlabel("True L (mm)"); ax2.set_ylabel("Residual (mm)")
            ax2.set_title("Residuals", fontsize=10)
            ax2.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)

            pred_str = (f"Sx={sx_val:.0f} mm  →  L_lin={l_lin:.3f}  |  "
                        f"L_quad={l_quad:.3f}  |  Δ={abs(l_lin-l_quad):.3f} mm")

        else:  # forward
            sx_lin_fine  = np.polyval(reg.p_lin_nat, L_fine)
            sx_quad_fine = np.polyval(reg.p_quad_nat, L_fine)
            sx_lin_rec   = np.polyval(reg.p_lin_nat, reg.L)
            sx_quad_rec  = np.polyval(reg.p_quad_nat, reg.L)

            ax1.errorbar(reg.L, reg.Sx_mean, yerr=2*reg.sigma_Sx, fmt="o",
                         color=CYAN, ecolor=CYAN+"55", capsize=3, zorder=5, label="Data (±2σ)")
            ax1.plot(L_fine, sx_lin_fine, color=PINK, linewidth=1.8, label="Linear")
            ax1.plot(L_fine, sx_quad_fine, color=GREEN, linewidth=1.8, linestyle="--", label="Quadratic")
            ax1.axvline(L_val, color=PURPLE, linewidth=1.2, linestyle=":", alpha=0.9,
                        label=f"L={L_val:.0f}")
            ax1.set_xlabel("Draw Length L (mm)"); ax1.set_ylabel("Landing Sx (mm)")
            ax1.set_title("Sx = f(L)  —  Forward (no inversion)", fontsize=10)
            ax1.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)
            ax1.set_ylim(reg.Sx_min - Sx_pad, reg.Sx_max + Sx_pad)

            sx_lin  = float(np.polyval(reg.p_lin_nat, L_val))
            sx_quad = float(np.polyval(reg.p_quad_nat, L_val))

            rmse_lin  = float(np.sqrt(np.mean((reg.Sx_mean - sx_lin_rec)**2)))
            rmse_quad = float(np.sqrt(np.mean((reg.Sx_mean - sx_quad_rec)**2)))

            ax2.plot(reg.L, reg.Sx_mean - sx_lin_rec, "o-", color=PINK, linewidth=1.5,
                     label=f"Linear  RMSE={rmse_lin:.2f}")
            ax2.plot(reg.L, reg.Sx_mean - sx_quad_rec, "s--", color=GREEN, linewidth=1.5,
                     label=f"Quad  RMSE={rmse_quad:.2f}")
            ax2.axhline(0, color=MUTED, linewidth=0.8)
            ax2.set_xlabel("True L (mm)"); ax2.set_ylabel("Residual (mm)")
            ax2.set_title("Residuals", fontsize=10)
            ax2.set_xlim(reg.L_min - L_pad, reg.L_max + L_pad)

            pred_str = (f"L={L_val:.0f} mm  →  Sx_lin={sx_lin:.2f}  |  "
                        f"Sx_quad={sx_quad:.2f}  |  Δ={abs(sx_lin-sx_quad):.2f} mm")

        # Common formatting
        for ax in axes:
            ax.legend(fontsize=8, facecolor=DARK, labelcolor=WHITE, framealpha=0.8)
            ax.grid(alpha=0.15, color=BORDER)

        # Update metrics text
        metrics_str = (
            f"{pred_str}\n"
            f"Linear: {m['eq_lin']}\n"
            f"Quad:   {m['eq_quad']}\n"
            f"R²_lin={m['r2_lin']:.8f}  |  R²_quad={m['r2_quad']:.8f}"
        )
        self._reg_metrics_text.set_text(metrics_str)
