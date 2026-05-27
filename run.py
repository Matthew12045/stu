"""
M2 Ball Launcher — Entry Point
===============================

Run this script to launch the combined delay-time calculator
and draw-length regression tool in Jupyter Notebook.

Usage (in a Jupyter cell)::

    %run run.py

Or as a module::

    from m2_launcher import M2LauncherApp
    app = M2LauncherApp()
    app.display()
"""

from m2_launcher import M2LauncherApp


def main():
    """Create and display the M2 Launcher application."""
    app = M2LauncherApp()
    app.display()


if __name__ == "__main__":
    main()
