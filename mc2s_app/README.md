# Monte Carlo 2-Stream Radiative Transfer Demo

An interactive educational GUI application for teaching atmospheric radiative transfer using Monte Carlo photon-tracing methods combined with two-stream approximations.

## 🦎 Overview

This application provides students with a hands-on way to explore how radiation propagates through Earth's atmosphere. By simulating individual photon trajectories, students can visualize the effects of:

- **Optical depth** - How opaque the atmosphere is
- **Single scattering albedo** - Probability of scattering vs absorption
- **Asymmetry parameter** - Forward vs backward scattering preference
- **Surface albedo** - Ground reflectance
- **Solar geometry** - Impact of sun angle

## 🐊 Features

### Interactive Controls
- Real-time parameter adjustment via sliders
- Preset atmospheric profiles (Clear Sky, Thin/Thick Clouds, Aerosols)
- Adjustable number of photons (100 to 50,000)

### Visualizations
- **Photon trajectories** - See individual photon paths through atmosphere
- **Energy budget bars** - Visual breakdown of reflected/transmitted/absorbed energy
- **Real-time statistics** - Reflectance, transmittance, absorptance percentages

### Educational Value
- Demonstrates energy conservation in radiative transfer
- Shows effect of cloud optical depth on solar radiation
- Illustrates role of aerosols in atmospheric heating
- Connects microscopic (photon) to macroscopic (flux) descriptions

## 🦊 Installation

### Quick Start (Development)

```bash
# Navigate to the app directory
cd mc2s_app

# Run setup script (creates venv and installs dependencies)
./setup.sh

# Activate virtual environment
source .venv/bin/activate

# Run the app
python src/mc2s_gui.py
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/mc2s_gui.py
```

### Building Standalone Executable

For distribution to students without Python installed:

```bash
# Activate venv and build
source .venv/bin/activate
./build.sh

# On macOS, this creates: dist/MC2S_Demo.app
# On Linux/Windows: dist/MC2S_Demo executable

# Compress for distribution
cd dist
zip -r MC2S_Demo.zip MC2S_Demo.app
```

## 🐸 Usage Guide

### Interface Layout

The application window is divided into two sections:

1. **Left Panel (Visualization)**
   - Atmosphere diagram with TOA and surface boundaries
   - Photon trajectory paths (colored by outcome)
   - Energy budget bar chart

2. **Right Panel (Controls)**
   - Atmospheric parameter sliders
   - Preset dropdown menu
   - Run simulation button
   - Results statistics display

### Atmospheric Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| **Optical Depth (τ)** | 0.1 - 30 | Total atmospheric opacity. Higher = more opaque |
| **Single Scatter Albedo (ω₀)** | 0 - 1 | Scattering probability. 0 = pure absorption, 1 = no absorption |
| **Asymmetry (g)** | -1 to +1 | Scattering direction preference. +1 = forward, -1 = backward, 0 = isotropic |
| **Surface Albedo** | 0 - 1 | Ground reflectance. 0 = black, 1 = perfect reflector |
| **Solar Zenith Angle** | 0° - 85° | Sun position. 0° = overhead, 90° = horizon |
| **Number of Photons** | 100 - 50,000 | More photons = better statistics but slower |

### Preset Scenarios

- **Clear Sky** (τ=0.1): Minimal atmospheric scattering
- **Thin Cloud** (τ=5): Typical cumulus cloud
- **Thick Cloud** (τ=30): Dense storm cloud
- **Aerosol Layer** (τ=1, ω₀=0.85): Polluted atmosphere

### Interpreting Results

The results panel shows:

- **Reflectance**: Fraction of energy reflected back to space
- **Transmittance**: Fraction reaching the surface
- **Absorptance**: Fraction absorbed by atmosphere
- **Total**: Should always be ≈100% (energy conservation)

Color coding for photon paths:
- 🔵 **Blue**: Reflected (exited at TOA)
- 🟠 **Orange**: Transmitted (reached surface)
- ⚫ **Gray**: Absorbed (weight dropped below threshold)

## 🦁 Physics Background

### Two-Stream Approximation

Instead of tracking photons in full 3D, this model simplifies to:
- **Upward flux (F⁺)**: Radiation moving toward space (τ decreases)
- **Downward flux (F⁻)**: Radiation moving toward surface (τ increases)

This captures essential physics while remaining computationally tractable.

### Monte Carlo Method

Each photon:
1. Starts at top-of-atmosphere (τ=0) moving downward
2. Samples exponentially-distributed path length to next interaction
3. Scatters or absorbs based on single scattering albedo
4. Continues until exiting atmosphere or weight drops too low

Statistical averaging over many photons recovers macroscopic radiation field.

### Key Physics Concepts

- **Optical depth**: ∫(absorption + scattering) dz
- **Beer-Lambert Law**: Direct beam attenuation = exp(-τ)
- **Henyey-Greenstein**: Phase function for anisotropic scattering
- **Energy conservation**: R + T + A = 1

## 🐻 File Structure

```
mc2s_app/
├── src/
│   ├── mc2s_gui.py      # Main GUI application
│   ├── physics.py       # Monte Carlo RT simulation
│   └── config.py        # Configuration and constants
├── requirements.txt     # Python dependencies
├── setup.sh            # Setup script
├── build.sh            # Build script for distribution
├── mc2s_app.spec       # PyInstaller configuration
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🦜 Educational Applications

### Classroom Demonstrations

1. **Cloud radiative effects**: Compare thin vs thick cloud presets
2. **Greenhouse effect**: Show absorption with low ω₀
3. **Aerosol cooling**: Demonstrate increased reflectance with aerosols
4. **Solar geometry**: Impact of zenith angle on energy budget

### Student Exercises

1. Find τ where reflectance = transmittance
2. Determine surface albedo needed to match satellite observations
3. Calculate atmospheric heating rate from absorptance
4. Compare isotropic vs forward scattering impacts

### Research Applications

- Validate against analytical two-stream solutions
- Explore parameter sensitivities
- Test cloud radiative forcing scenarios
- Demonstrate variance reduction techniques

## 🐺 Troubleshooting

### App won't start
- Ensure Python 3.8+ is installed: `python3 --version`
- Check all dependencies installed: `pip list`
- Try running with console output: change `console=True` in .spec file

### Slow performance
- Reduce number of photons (< 5000 for interactive use)
- Simulation runs in background thread - UI remains responsive
- Consider upgrading numpy (uses optimized BLAS/LAPACK)

### Incorrect results
- Check energy conservation: R+T+A should equal 100%
- Increase photon count for better statistics (convergence ~ 1/√N)
- Verify atmospheric parameters are physical (0 ≤ ω₀ ≤ 1, etc.)

## 🐉 Extending the App

### Adding Features

1. **Spectral calculations**: Loop over wavelengths
2. **Multiple layers**: Extend `Atmosphere` class
3. **Thermal emission**: Add upward surface radiation
4. **3D visualization**: Use matplotlib for flux profiles

### Customizing Presets

Edit `ATMOSPHERE_PRESETS` in `config.py`:

```python
ATMOSPHERE_PRESETS[AtmospherePreset.MY_CASE] = AtmosphereConfig(
    tau_max=2.0,
    omega_0=0.95,
    g=0.6,
    surface_albedo=0.3,
    solar_zenith=45.0
)
```

## 🐾 References

- **Theoretical Guide**: See `2stream_monte_carlo_guide.md` in parent directory
- **Original Code**: Based on `monte_carlo_2stream.py`
- **Textbook**: Thomas & Stamnes, *Radiative Transfer in the Atmosphere and Ocean*

## 📚 Credits

Developed for undergraduate atmospheric physics education.

Based on Monte Carlo radiative transfer methods and two-stream approximations commonly used in climate models and remote sensing applications.

## 📝 License

Educational use. Feel free to modify and distribute for teaching purposes.

---

**For questions or issues, check the CLAUDE.md file in the parent directory.**
