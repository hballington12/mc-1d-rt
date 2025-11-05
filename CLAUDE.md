# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Two-Stream Monte Carlo Radiative Transfer** teaching implementation for atmospheric physics students. It combines Monte Carlo photon-tracing methods with two-stream approximations to simulate how radiation propagates through a scattering-absorbing atmosphere.

## Core Architecture

### Main Components

1. **monte_carlo_2stream.py** - Production implementation with:
   - `Photon` dataclass: Tracks position (optical depth), direction (+1 toward surface, -1 toward space), weight, and active status
   - `Atmosphere` dataclass: Defines optical properties (tau_max, omega_0, g, surface_albedo)
   - Monte Carlo simulation functions: `sample_optical_depth()`, `propagate_to_interaction()`, `scatter_isotropic()`, `scatter_henyey_greenstein()`, `interact()`
   - Visualization functions for atmosphere structure, optical depth distributions, and photon trajectories

2. **rt2s.ipynb** - Jupyter notebook with:
   - Alternative implementation using Enum-based Direction system
   - Energy tracking across multiple photons
   - Interactive visualizations of photon paths
   - Monte Carlo simulations with outcome statistics

3. **test_photon_debug.py** - Simple debug script to trace single photon trajectories

## Key Physics Concepts

### Coordinate System
- **Optical depth (τ)**: Vertical coordinate where τ=0 is top-of-atmosphere (TOA) and τ=tau_max is bottom-of-atmosphere (BOA/surface)
- **Direction convention**: +1 = downward (toward surface, τ increases), -1 = upward (toward space, τ decreases)

### Optical Parameters
- **Single scattering albedo (ω₀)**: Probability of scattering vs absorption [0,1]
  - ω₀=0: Pure absorption
  - ω₀=1: Conservative scattering (no absorption)
- **Asymmetry parameter (g)**: Phase function asymmetry [-1,1]
  - g>0: Forward scattering preference
  - g<0: Backward scattering preference
  - g=0: Isotropic scattering
- **Surface albedo**: Bottom boundary reflectance

### Monte Carlo Process
1. Photon starts at TOA (τ=0) moving downward (direction=+1)
2. Sample optical depth to next interaction: τ = -ln(ξ) where ξ~U(0,1)
3. Move photon: new_position = position + direction × τ
4. Check boundaries (escape at TOA/BOA) or interact
5. Interaction: reduce weight by ω₀, scatter using phase function
6. Repeat until photon escapes or weight drops below threshold

## Running the Code

### Execute main script
```bash
python monte_carlo_2stream.py
```
This runs test cases and generates three visualization PNG files:
- `atmosphere_structure.png` - Atmospheric layers and optical properties
- `optical_depth_distribution.png` - Exponential sampling validation
- `photon_paths.png` - Individual photon trajectories

### Run Jupyter notebook
```bash
jupyter notebook rt2s.ipynb
```

### Debug single photon
```bash
python test_photon_debug.py
```

## Development Notes

### Code Style
- Uses dataclasses for clean data structures (`@dataclass` decorator)
- Validates parameters in `__post_init__` methods
- Type hints for function signatures
- Matplotlib set to non-interactive backend ("Agg") for PNG generation

### Physics Validation
The implementation follows Beer-Lambert law for absorption and Henyey-Greenstein phase function for anisotropic scattering. Results should match analytical two-stream solutions for standard benchmark cases (see 2stream_monte_carlo_guide.md section 6).

### Random Number Generation
Uses numpy's `np.random.random()` for uniform random numbers. No fixed seeds in production code (only in visualization functions to ensure reproducible example trajectories).

### Two-Stream Simplification
In full 3D Monte Carlo, photons scatter into arbitrary directions. This code simplifies to two-stream by only tracking upward/downward hemispheres - scattering changes direction to +1 or -1 based on phase function probabilities.

## File Dependencies

- **numpy**: Array operations and random number generation
- **matplotlib**: Plotting (imports `matplotlib.pyplot` and sets backend)
- **dataclasses**: Python's built-in dataclass decorator (Python 3.7+)

## Common Modifications

### Change atmospheric properties
Modify the test atmosphere in `__main__` block:
```python
atm = Atmosphere(tau_max=2.0, omega_0=0.95, g=0.0, surface_albedo=0.3)
```

### Add multiple layers
The `Atmosphere` class accepts a list of layers (see notebook implementation for multi-layer example).

### Adjust photon count for better statistics
Convergence goes as 1/√N. Use 10,000+ photons for smooth results.

### Modify visualization
All plotting functions accept `filename` parameter. Adjust DPI or figure size in function calls.

## GUI Application (mc2s_app/)

An interactive educational demo application has been created in the `mc2s_app/` directory:

### Quick Start
```bash
cd mc2s_app
./setup.sh
source .venv/bin/activate
python src/mc2s_gui.py
```

### Features
- Real-time Monte Carlo simulation with interactive parameter sliders
- Visual photon trajectory display (up to 50 paths)
- Energy budget visualization (reflectance/transmittance/absorptance)
- 4 preset atmospheric scenarios (Clear Sky, Thin/Thick Cloud, Aerosols)
- Background threading for non-blocking simulation
- Build scripts for standalone distribution to students

### Architecture
- **mc2s_gui.py** (460 lines): Main pygame-based GUI application
  - `MC2SApp` class handles all UI events, drawing, and simulation coordination
  - Event-driven architecture with pygame_gui widgets (sliders, buttons, dropdowns)
  - 1400×800 window: 900px scene + 500px control panel
- **physics.py** (210 lines): Monte Carlo RT simulation engine
  - Direct port of `monte_carlo_2stream.py` with path tracking
  - `simulate_photon()` and `run_simulation()` functions
- **config.py** (90 lines): Configuration, constants, and presets
  - `AtmospherePreset` enum and `AtmosphereConfig` dataclass
  - `ATMOSPHERE_PRESETS` dictionary with 4 teaching scenarios

### Distribution
```bash
./build.sh  # Creates standalone executable
# macOS: dist/MC2S_Demo.app
# Linux/Win: dist/MC2S_Demo
```

See `mc2s_app/README.md` for detailed usage and `mc2s_app/QUICKSTART.md` for student-friendly guide.

## Real-Time Photon Animation Demo (photon_demo_app/)

A **highly visual, simplified demo** for first-time learners has been created in `photon_demo_app/`:

### Quick Start
```bash
cd photon_demo_app
./setup.sh
source .venv/bin/activate
python src/photon_demo.py
```

### What Makes It Special
- **Real-time animation**: Watch photons move vertically through atmosphere step-by-step
- **Visual feedback**: Yellow (down), blue (up), magenta flash (scatter), red fade (absorption)
- **Simplified physics**: Isotropic scattering only, 1-100 photons, perfect for visualization
- **Live statistics**: Reflectance/transmittance/absorptance update as photons move
- **Absorption profile**: Histogram shows WHERE in atmosphere photons get absorbed
- **Intuitive controls**: 4 sliders (optical depth, scattering probability, photon count, animation speed)

### Key Differences from mc2s_app
- **photon_demo_app**: Animated visualization, 1-100 photons, simplified for teaching first concepts
- **mc2s_app**: Full simulation, 100-50k photons, complete physics, research-grade statistics

### Use Cases
- First exposure to Monte Carlo RT (start here!)
- Live classroom demonstrations (engaging animation)
- Building physical intuition (see scatter/absorption happen)
- Then progress to `mc2s_app` for quantitative analysis

See `photon_demo_app/README.md` for educational demos and `photon_demo_app/QUICKSTART.md` to get started in 30 seconds.

## Reference Documentation

See **2stream_monte_carlo_guide.md** for comprehensive theoretical background covering:
- Two-stream radiative transfer equations
- Monte Carlo fundamentals
- Implementation strategy
- Validation approaches
- Learning objectives for students
- Expected results and test cases
