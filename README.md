# 🔬 Open ThermoKinetics

> Open-source desktop toolkit for solid-state reaction kinetics analysis

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

**Open ThermoKinetics** is a free alternative to proprietary thermokinetic software. It analyzes thermal analysis data (TGA, DSC) and determines the full kinetic *"triplet"* — activation energy, pre-exponential factor, and reaction model — for each reaction stage.

---

## ✨ Features

- **Model-Free (Isoconversional) Methods** — Friedman, Kissinger, OFW, KAS, Starink, Vyazovkin (AIC)
- **Model-Fitting Methods** — Direct Differential, Coats–Redfern against 20+ solid-state models
- **Model-Based Analysis** — ODE integration for multi-step reaction schemes (A→B→C), global optimization via Differential Evolution
- **Peak Deconvolution** — Gaussian, Fraser-Suzuki, Asymmetric Double Sigmoid
- **Interactive GUI** — draggable parameter anchors, real-time curve updates, multi-heating-rate support
- **Multi-Series Experiments** — group and compare experiments at different heating rates

---

## 🖥️ Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  Open ThermoKinetics v0.3.0                              [─][□][×]│
├──────────┬──────────────┬───────────────────────┬───────────────┤
│          │              │                       │               │
│ Files    │  Analysis    │    Plot Canvas        │    Console    │
│          │  Panel       │                       │               │
│ ▾ exp1   │              │   ╭──────────────╮    │ [INFO] Calc   │
│   series1│  ○ Model-    │   │  ~~~~~       │    │ started...    │
│   series2│    Free      │   │       ~~~    │    │               │
│ ▾ exp2   │  ● Model-    │   │          ~~ │    │ [OK] E_a =    │
│   series1│    Fitting   │   ╰──────────────╯    │ 142.3 kJ/mol │
│          │  ○ Model-    │   α  0.0 ──── 1.0     │               │
│          │    Based     │                       │               │
│          │  ○ Deconv.   │   [Anchor ●]          │               │
│          │              │   drag to adjust      │               │
└──────────┴──────────────┴───────────────────────┴───────────────┘
```

---

## 📦 Installation

### Option 1: Download Release (Recommended for Windows users)

Download the latest `OTK.exe` from the [Releases page](https://github.com/davjdk/Open_ThermoKinetics/releases) — no Python required.

### Option 2: Install with uv (Recommended for developers)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone https://github.com/davjdk/Open_ThermoKinetics.git
cd Open_ThermoKinetics
uv sync
uv run python -m src.gui
```

### Option 3: Install with pip

```bash
git clone https://github.com/davjdk/Open_ThermoKinetics.git
cd Open_ThermoKinetics
pip install -e .
python -m src.gui
```

---

## 🚀 Quick Start

1. **Launch** the application: `uv run python -m src.gui`
2. **Load data** — click "Load File" and select your TGA/DSC `.txt` or `.csv` file
3. **Organize** experiments into series by heating rate
4. **Choose analysis** from the Analysis Panel:
   - *Model-Free* → select method (Friedman, KAS, OFW, etc.) → Calculate
   - *Model-Fitting* → select model family → Fit
   - *Model-Based* → define reaction scheme → Optimize
5. **Export** results via the Console panel

### Supported Data Format

```
# Temperature [°C or K], Conversion [0-1] or Mass fraction
300.0  0.000
350.5  0.023
401.2  0.187
...
```

---

## 📊 Implemented Methods

### Model-Free (Isoconversional)

| Method | Type | Description |
|--------|------|-------------|
| Friedman (FR) | Differential | Direct rate-based isoconversional |
| Kissinger (KSG) | Differential | Peak-temperature method |
| Ozawa–Flynn–Wall (OFW) | Integral (approximate) | Log β vs 1/T |
| Kissinger–Akahira–Sunose (KAS) | Integral (approximate) | ln(β/T²) vs 1/T |
| Starink (STR) | Integral (approximate) | Improved KAS |
| Vyazovkin Advanced (AIC) | Integral (numerical) | Nonlinear minimization |

### Model-Fitting

| Method | Description |
|--------|-------------|
| Direct Differential (DD) | Rate fitting to f(α) models |
| Coats–Redfern (CR) | Integral linearization |

Models: F1, F2, F3, R2, R3, D1–D4, A2–A4, P2, P3, and more.

### Model-Based

- Multi-step reaction schemes: A→B, A→B→C, A→B+C
- ODE integration via `scipy.solve_ivp`
- Global optimization: Differential Evolution
- JIT acceleration via Numba

### Deconvolution

- Gaussian
- Fraser-Suzuki (asymmetric)
- Asymmetric Double Sigmoid (ADS)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow the project coding style (ruff + black)
4. Run tests: `uv run pytest`
5. Submit a Pull Request

### Development Setup

```bash
git clone https://github.com/davjdk/Open_ThermoKinetics.git
cd Open_ThermoKinetics
uv sync
uv run pre-commit install
uv run pytest
```

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [SciPy](https://scipy.org/) — optimization and ODE integration
- [NumPy](https://numpy.org/) — numerical computing
- [Numba](https://numba.pydata.org/) — JIT compilation
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — desktop GUI framework
- [Matplotlib](https://matplotlib.org/) — scientific visualization
- [uv](https://github.com/astral-sh/uv) — fast Python package manager
