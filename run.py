"""
M2 Ball Launcher — Entry Point
===============================

Run this script to launch the combined delay-time calculator
and draw-length regression tool.

Usage::

    python run.py
"""

from m2_launcher import M2LauncherApp


def main():
    """Create and display the M2 Launcher application."""
    app = M2LauncherApp()
    app.run()


if __name__ == "__main__":
    main()
