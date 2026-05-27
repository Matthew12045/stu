"""
m2_launcher — M2 Ball Launcher OOP Package
===========================================

Combines NE555 delay-time calculation, projectile physics, and
draw-length OLS regression into a single interactive application.

Quick start::

    from m2_launcher import M2LauncherApp
    app = M2LauncherApp()
    app.display()

Individual components are also importable::

    from m2_launcher import NE555TimerModel, PhysicsEngine, DrawLengthRegression
"""

from .timer_model import NE555TimerModel
from .physics import PhysicsEngine
from .regression import DrawLengthRegression
from .app import M2LauncherApp

__all__ = [
    "NE555TimerModel",
    "PhysicsEngine",
    "DrawLengthRegression",
    "M2LauncherApp",
]
