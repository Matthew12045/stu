"""
Physics Engine
==============
Projectile kinematics and timing calculations for the M2 Ball Launcher.
"""

import math


class PhysicsEngine:
    """Compute flight time and delay time for the M2 ball launcher.

    The launcher fires a projectile at a fixed angle.  This class
    computes the time-of-flight and the required NE555 trigger delay
    so that the ball lands at a specified horizontal distance.

    Parameters
    ----------
    sy : float
        Vertical offset of the landing surface (m).  Default ``0.036``.
    launch_angle_deg : float
        Launch angle in degrees.  Default ``60.0``.
    g : float
        Gravitational acceleration (m/s²).  Default ``9.81``.
    arm_radius : float
        Arm radius for arcsin constant (m).  Default ``0.06``.
    arm_pivot : float
        Arm pivot distance (m).  Default ``2.5``.
    """

    def __init__(
        self,
        sy: float = 0.036,
        launch_angle_deg: float = 60.0,
        g: float = 9.81,
        arm_radius: float = 0.06,
        arm_pivot: float = 2.5,
    ):
        self.sy = sy
        self.launch_angle_deg = launch_angle_deg
        self.g = g
        self.arm_radius = arm_radius
        self.arm_pivot = arm_pivot

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_flight_time(self, sx_m: float) -> float:
        """Compute the projectile flight time for a given horizontal distance.

        Parameters
        ----------
        sx_m : float
            Horizontal landing distance in **metres**.

        Returns
        -------
        float
            Flight time in seconds.

        Raises
        ------
        ValueError
            If the target is unreachable (negative discriminant).
        """
        angle_rad  = math.radians(self.launch_angle_deg)
        inner_term = (2 * (sx_m * math.tan(angle_rad) - self.sy)) / self.g

        if inner_term < 0:
            raise ValueError(
                "Target unreachable at this angle (negative square root)."
            )

        return math.sqrt(inner_term)

    def compute_delay_time(
        self,
        sx_mm: float,
        rpm: float,
        phi_deg: float,
    ) -> dict:
        """Compute the full delay-time pipeline.

        Parameters
        ----------
        sx_mm : float
            Horizontal landing distance in **millimetres**.
        rpm : float
            Motor speed in revolutions per minute.
        phi_deg : float
            Phase angle in degrees.

        Returns
        -------
        dict
            Keys: ``t_flight``, ``t_delay_raw``, ``t_delay``,
            ``cycle_added``, ``omega``, ``c_const``.

        Raises
        ------
        ValueError
            If inputs produce invalid physics (negative sqrt or
            arcsin domain error).
        """
        sx_m = sx_mm / 1000.0

        # Flight time
        t_flight = self.compute_flight_time(sx_m)

        # Angular velocity
        omega = rpm * (math.pi / 30.0)

        # Geometric constant c = arcsin(arm_radius / (arm_pivot − sx))
        denom = self.arm_pivot - sx_m
        ratio = self.arm_radius / denom
        if abs(ratio) > 1:
            raise ValueError(
                "Target Sx results in invalid arcsin domain for constant c."
            )
        c_const = math.asin(ratio)

        # Phase angle
        phi_rad = math.radians(phi_deg)

        # Raw delay
        t_delay = ((2 * math.pi - phi_rad - c_const) / omega) - t_flight
        if t_delay < 0:
            t_delay += 2 * math.pi / omega

        t_delay_raw = t_delay
        cycle_added = False

        # Ensure minimum 0.1 s (NE555 hardware limit)
        if t_delay < 0.1:
            t_delay += 2 * math.pi / omega
            cycle_added = True

        if t_delay < 0.1:
            raise ValueError(
                f"Calculated delay ({t_delay:.2f}s) is still below 0.1s "
                f"after adding one full cycle (2π/ω)."
            )

        return {
            "t_flight":    t_flight,
            "t_delay_raw": t_delay_raw,
            "t_delay":     t_delay,
            "cycle_added": cycle_added,
            "omega":       omega,
            "c_const":     c_const,
        }
