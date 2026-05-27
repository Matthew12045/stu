# M2 Ball Launcher — Delay & Draw Length Calculator

A single-page web application for the **M2 Ball Launcher** project at **KMUTT**. Combines a **delay-time calculator** (NE555 timer) and a **draw-length regression estimator** into one tool, built with OOP principles using ES6 JavaScript modules.

## Features

- **Delay Calculator** — Enter landing distance (Sx), motor RPM, and phase angle (φ) to get the required NE555 dial settings (knob 1, knob 2, switch).
- **Draw Length Estimator** — Estimates the draw length (L) from landing distance (Sx) using OLS linear regression with algebraic inversion.
- **Shared Input** — One Sx input feeds both calculators. Delay uses Sx + 102 mm; regression uses raw Sx.
- **Live CSV Loading** — NE555 calibration data is loaded from `Example/ne555_full_dataset.csv` at runtime.

## How to Run

ES6 modules require a local web server. Start one with Python:

```bash
cd C:\Projects\m2_launcher
python -m http.server 8080
```

Then open **http://localhost:8080** in your browser.

## Project Structure

```
├── index.html                          HTML structure (no inline JS)
├── style.css                           Stylesheet (light theme)
├── js/
│   ├── main.js                         Entry point
│   ├── NE555TimerModel.js              CSV loading, regression, step lookup
│   ├── PhysicsEngine.js                Projectile kinematics, delay computation
│   ├── DrawLengthRegression.js         OLS linear fit, algebraic inversion
│   └── M2LauncherApp.js                Orchestrator, DOM rendering
├── Example/
│   ├── ne555_full_dataset.csv          NE555 calibration data
│   ├── delay.py                        Original Python reference
│   ├── regression.py                   Original Python reference
│   └── ne555_calculator.html           Original standalone HTML reference
└── project_context.md                  Full technical documentation
```

## OOP Architecture

| Class | File | Responsibility |
|-------|------|----------------|
| `NE555TimerModel` | `js/NE555TimerModel.js` | Load CSV, fit regression, step lookup, knob/switch decomposition |
| `PhysicsEngine` | `js/PhysicsEngine.js` | Flight time, delay time, Sx + 102 mm offset |
| `DrawLengthRegression` | `js/DrawLengthRegression.js` | OLS fit (L → Sx), algebraic inversion (Sx → L) |
| `M2LauncherApp` | `js/M2LauncherApp.js` | Composes all 3 classes, binds DOM events, renders output |

## Tech Stack

- **HTML5** — Semantic structure
- **Vanilla CSS** — Light theme (JetBrains Mono + DM Sans fonts)
- **ES6 JavaScript Modules** — `import` / `export` classes
- No frameworks, no build step, no dependencies
