"""
NE555 Timer Model
=================
Encapsulates the NE555 timer calibration data, linear regression model,
and dial-setting decomposition logic.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class NE555TimerModel:
    """Model for the NE555 timer circuit calibration.

    Loads recorded timing measurements from a CSV file, fits a linear
    regression (target_time → mean_output), and provides methods to
    query the best dial step for a desired delay.

    Attributes
    ----------
    slope : float
        Slope of the fitted linear regression.
    intercept : float
        Intercept of the fitted linear regression.
    r_squared : float
        Coefficient of determination (R²) of the fit.
    recorded_lookup : dict
        Mapping ``{"step_key": {"mean": float, "std": float}, ...}``
        built from non-predicted rows in the dataset.
    n_recorded : int
        Number of recorded (non-predicted) measurements.
    """

    # Hardware constants
    THRESHOLD = 10.0   # switch adds 10 s to effective range
    MIN_STEP  = 0.1
    MAX_STEP  = 19.0
    STEP_INC  = 0.1

    def __init__(self, csv_path: str | None = None):
        """Initialise the model from a CSV dataset.

        Parameters
        ----------
        csv_path : str or None
            Path to ``ne555_full_dataset.csv``.  When *None*, the
            bundled embedded data in ``_data.py`` is used.  If a path
            is given explicitly, it will be read from disk.
        """
        if csv_path is not None:
            self._df = pd.read_csv(csv_path)
        else:
            # Use the embedded CSV string (avoids OneDrive / cloud-
            # synced file issues where os.path.exists returns False).
            from . import _data
            from io import StringIO
            self._df = pd.read_csv(StringIO(_data.CSV_CONTENT))

        self._fit_model()
        self._build_lookup()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fit_model(self):
        """Fit a linear regression on recorded (non-predicted) data."""
        recorded = self._df[self._df["n_readings"] != "PREDICTED"].copy()
        self.n_recorded = len(recorded)

        # Filter outliers by std if available
        if "std_s" in recorded.columns:
            clean = recorded[recorded["std_s"] < 0.1].copy()
        else:
            clean = recorded.copy()

        X = clean["target_time_s"].values.reshape(-1, 1)
        y = clean["mean_s"].values

        model = LinearRegression().fit(X, y)

        self.slope     = round(float(model.coef_[0]), 6)
        self.intercept = round(float(model.intercept_), 6)
        self.r_squared = float(
            np.corrcoef(clean["target_time_s"].values, y)[0, 1] ** 2
        )

    def _build_lookup(self):
        """Build ``recorded_lookup`` dict from non-predicted rows."""
        recorded = self._df[self._df["n_readings"] != "PREDICTED"]
        self.recorded_lookup: dict[str, dict] = {}

        for _, row in recorded.iterrows():
            key = f"{round(row['target_time_s'], 1):.1f}"
            self.recorded_lookup[key] = {
                "mean": round(float(row["mean_s"]), 6),
                "std":  round(float(row.get("std_s", 0)), 6),
            }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ne555_output(self, step: float) -> float:
        """Return the predicted NE555 output time for a given dial step.

        Uses the recorded measurement if available; otherwise falls
        back to the linear-regression estimate.

        Parameters
        ----------
        step : float
            Dial step value (0.1 – 19.0).

        Returns
        -------
        float
            Predicted output time in seconds.
        """
        key = f"{step:.1f}"
        rec = self.recorded_lookup.get(key)
        if rec is not None:
            return rec["mean"]
        return self.slope * step + self.intercept

    def best_step(self, t_delay: float) -> float:
        """Find the dial step whose NE555 output is closest to *t_delay*.

        Scans every 0.1 s increment from 0.1 to 19.0.

        Parameters
        ----------
        t_delay : float
            Target delay time in seconds.

        Returns
        -------
        float
            Best dial-step value (0.1 – 19.0).
        """
        best, best_diff = self.MIN_STEP, float("inf")
        s = self.MIN_STEP
        while s <= self.MAX_STEP:
            diff = abs(self.ne555_output(s) - t_delay)
            if diff < best_diff:
                best_diff = diff
                best = s
            s = round(s + self.STEP_INC, 1)
        return best

    def decompose_step(self, step: float) -> dict:
        """Decompose a dial step into hardware knob/switch settings.

        Parameters
        ----------
        step : float
            Dial step value (0.1 – 19.0).

        Returns
        -------
        dict
            ``{"step", "switch_on", "effective", "knob1", "knob2",
              "ne555_mean", "ne555_std", "is_recorded"}``
        """
        key = f"{step:.1f}"
        rec = self.recorded_lookup.get(key)

        switch_on = step >= self.THRESHOLD
        effective = round(step - self.THRESHOLD, 1) if switch_on else step
        knob2     = int(effective)
        knob1     = round((effective - knob2) * 10)

        return {
            "step":        round(step, 1),
            "switch_on":   switch_on,
            "effective":   round(effective, 1),
            "knob1":       knob1,
            "knob2":       knob2,
            "ne555_mean":  rec["mean"] if rec else round(self.slope * step + self.intercept, 6),
            "ne555_std":   rec["std"] if rec else None,
            "is_recorded": rec is not None,
        }

    def to_json(self) -> str:
        """Serialise the recorded lookup to a JSON string (for HTML embed)."""
        return json.dumps(self.recorded_lookup)
