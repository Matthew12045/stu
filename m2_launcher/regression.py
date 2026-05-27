"""
Draw Length Regression
======================
OLS regression models (linear & quadratic) for the relationship
between draw length L and landing distance Sx.
"""

import numpy as np


class DrawLengthRegression:
    """Ordinary Least Squares regression for draw length ↔ landing distance.

    Fits both linear and quadratic polynomials in two directions:

    * **Natural** (L → Sx):  ``Sx = f(L)``   — treats L as error-free.
    * **Direct inverse** (Sx → L):  ``L = f(Sx)`` — convenience fit.

    Algebraic inversion of the natural fit gives the recommended
    Sx → L estimator.

    Parameters
    ----------
    L : array-like
        Draw lengths in mm.
    Sx_mean : array-like
        Mean landing distances in mm (one per draw length).
    sigma_Sx : array-like
        Standard deviations of landing distances in mm.
    """

    def __init__(
        self,
        L: list | np.ndarray | None = None,
        Sx_mean: list | np.ndarray | None = None,
        sigma_Sx: list | np.ndarray | None = None,
    ):
        # Defaults: M2 launcher calibration data
        if L is None:
            L        = [105, 110, 115, 120, 125, 130]
            Sx_mean  = [1548.07, 1657.67, 1783.74, 1946.85, 2067.23, 2199.73]
            sigma_Sx = [15.67, 17.58, 42.59, 35.89, 43.36, 36.25]

        self.L        = np.asarray(L, dtype=float)
        self.Sx_mean  = np.asarray(Sx_mean, dtype=float)
        self.sigma_Sx = np.asarray(sigma_Sx, dtype=float)

        # Ranges (for plotting / validation)
        self.L_min,  self.L_max  = float(self.L.min()),       float(self.L.max())
        self.Sx_min, self.Sx_max = float(self.Sx_mean.min()), float(self.Sx_mean.max())

        # Fit all models
        self._fit()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fit(self):
        """Compute all polynomial coefficients."""
        # Direct inverse: L = f(Sx)
        self.p_lin_direct  = np.polyfit(self.Sx_mean, self.L, 1)
        self.p_quad_direct = np.polyfit(self.Sx_mean, self.L, 2)

        # Natural direction: Sx = f(L)
        self.p_lin_nat  = np.polyfit(self.L, self.Sx_mean, 1)
        self.p_quad_nat = np.polyfit(self.L, self.Sx_mean, 2)

        # Unpack natural coefficients for inversion
        self._a1, self._b1             = self.p_lin_nat
        self._a2, self._b2, self._c2   = self.p_quad_nat

    # ------------------------------------------------------------------
    # Inversion (Sx → L via natural fit)
    # ------------------------------------------------------------------

    def invert_linear(self, Sx) -> np.ndarray | float:
        """Estimate L from Sx by inverting the linear natural fit.

        ``L = (Sx − b₁) / a₁``
        """
        Sx = np.asarray(Sx, dtype=float)
        return (Sx - self._b1) / self._a1

    def invert_quadratic(self, Sx) -> np.ndarray | float:
        """Estimate L from Sx by inverting the quadratic natural fit.

        Uses the positive root of the quadratic formula.
        """
        Sx = np.asarray(Sx, dtype=float)
        disc = self._b2 ** 2 - 4 * self._a2 * (self._c2 - Sx)
        disc = np.maximum(disc, 0)
        return (-self._b2 + np.sqrt(disc)) / (2 * self._a2)

    # ------------------------------------------------------------------
    # Forward prediction (L → Sx via natural fit)
    # ------------------------------------------------------------------

    def predict_forward_linear(self, L) -> np.ndarray | float:
        """Predict Sx from L using the linear natural fit."""
        return np.polyval(self.p_lin_nat, L)

    def predict_forward_quadratic(self, L) -> np.ndarray | float:
        """Predict Sx from L using the quadratic natural fit."""
        return np.polyval(self.p_quad_nat, L)

    # ------------------------------------------------------------------
    # Direct inverse prediction (Sx → L via direct fit)
    # ------------------------------------------------------------------

    def predict_direct_linear(self, Sx) -> np.ndarray | float:
        """Predict L from Sx using the direct inverse linear fit."""
        return np.polyval(self.p_lin_direct, Sx)

    def predict_direct_quadratic(self, Sx) -> np.ndarray | float:
        """Predict L from Sx using the direct inverse quadratic fit."""
        return np.polyval(self.p_quad_direct, Sx)

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    @staticmethod
    def metrics(y_true, y_pred) -> tuple[float, float]:
        """Compute RMSE and R² between true and predicted values.

        Parameters
        ----------
        y_true, y_pred : array-like
            True and predicted values.

        Returns
        -------
        (rmse, r2) : tuple[float, float]
        """
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)

        residuals = y_true - y_pred
        rmse = float(np.sqrt(np.mean(residuals ** 2)))

        ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
        r2 = 1 - float(np.sum(residuals ** 2)) / ss_tot if ss_tot != 0 else float("nan")

        return rmse, r2

    # ------------------------------------------------------------------
    # Equation strings (for display)
    # ------------------------------------------------------------------

    def equation_strings(self, mode: str) -> tuple[str, str]:
        """Return formatted equation strings for a given mode.

        Parameters
        ----------
        mode : str
            One of ``"direct"``, ``"natural"``, or ``"forward"``.

        Returns
        -------
        (eq_lin, eq_quad) : tuple[str, str]
        """
        if mode == "forward":
            eq_lin = (
                f"Sx = {self._a1:.6f}·L "
                f"{'+' if self._b1 >= 0 else ''}{self._b1:.4f}"
            )
            eq_quad = (
                f"Sx = {self._a2:.8f}·L² "
                f"{'+' if self._b2 >= 0 else ''}{self._b2:.6f}·L "
                f"{'+' if self._c2 >= 0 else ''}{self._c2:.4f}"
            )

        elif mode == "direct":
            eq_lin = (
                f"L = {self.p_lin_direct[0]:.6f}·Sx "
                f"{'+' if self.p_lin_direct[1] >= 0 else ''}"
                f"{self.p_lin_direct[1]:.4f}"
            )
            eq_quad = (
                f"L = {self.p_quad_direct[0]:.8f}·Sx² "
                f"{'+' if self.p_quad_direct[1] >= 0 else ''}"
                f"{self.p_quad_direct[1]:.6f}·Sx "
                f"{'+' if self.p_quad_direct[2] >= 0 else ''}"
                f"{self.p_quad_direct[2]:.4f}"
            )

        else:  # natural
            eq_lin = (
                f"Sx = {self._a1:.6f}·L "
                f"{'+' if self._b1 >= 0 else ''}{self._b1:.4f}  "
                f"→  L = (Sx − {self._b1:.2f}) / {self._a1:.6f}"
            )
            eq_quad = (
                f"Sx = {self._a2:.8f}·L² "
                f"{'+' if self._b2 >= 0 else ''}{self._b2:.6f}·L "
                f"{'+' if self._c2 >= 0 else ''}{self._c2:.4f}  "
                f"→  quadratic formula"
            )

        return eq_lin, eq_quad

    # ------------------------------------------------------------------
    # Convenience: compute all metrics for a given mode
    # ------------------------------------------------------------------

    def mode_metrics(self, mode: str) -> dict:
        """Return RMSE, R², equations, and a note for the given mode.

        Parameters
        ----------
        mode : str
            ``"direct"``, ``"natural"``, or ``"forward"``.

        Returns
        -------
        dict
            ``{"rmse_lin", "rmse_quad", "r2_lin", "r2_quad",
              "eq_lin", "eq_quad", "note", "note_color"}``
        """
        eq_lin, eq_quad = self.equation_strings(mode)

        if mode == "forward":
            sx_lin  = np.polyval(self.p_lin_nat, self.L)
            sx_quad = np.polyval(self.p_quad_nat, self.L)
            rmse_l = float(np.sqrt(np.mean((self.Sx_mean - sx_lin) ** 2)))
            rmse_q = float(np.sqrt(np.mean((self.Sx_mean - sx_quad) ** 2)))
            ss_tot = float(np.sum((self.Sx_mean - self.Sx_mean.mean()) ** 2))
            r2_l = 1 - float(np.sum((self.Sx_mean - sx_lin) ** 2)) / ss_tot
            r2_q = 1 - float(np.sum((self.Sx_mean - sx_quad) ** 2)) / ss_tot
            note = "OLS natural direction — L is error-free, Sx carries noise ✓"
            note_col = "#55efc4"

        elif mode == "direct":
            l_lin  = np.polyval(self.p_lin_direct, self.Sx_mean)
            l_quad = np.polyval(self.p_quad_direct, self.Sx_mean)
            rmse_l, r2_l = self.metrics(self.L, l_lin)
            rmse_q, r2_q = self.metrics(self.L, l_quad)
            note = "Direct polyfit(Sx, L) — treats noisy Sx as error-free"
            note_col = "#ff9f43"

        else:  # natural
            l_lin  = self.invert_linear(self.Sx_mean)
            l_quad = self.invert_quadratic(self.Sx_mean)
            rmse_l, r2_l = self.metrics(self.L, l_lin)
            rmse_q, r2_q = self.metrics(self.L, l_quad)
            note = "OLS natural direction — L is error-free, Sx carries noise ✓"
            note_col = "#55efc4"

        return {
            "rmse_lin":   rmse_l,
            "rmse_quad":  rmse_q,
            "r2_lin":     r2_l,
            "r2_quad":    r2_q,
            "eq_lin":     eq_lin,
            "eq_quad":    eq_quad,
            "note":       note,
            "note_color": note_col,
        }
