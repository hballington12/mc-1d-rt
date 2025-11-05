"""
Configuration for Real-Time Photon Animation Demo
Simple, educational visualization of photon propagation
"""

# Window dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
SCENE_WIDTH = 950  # Left side for animation and plots
PANEL_WIDTH = WINDOW_WIDTH - SCENE_WIDTH  # Right side for controls

# Layout: Animation | Scattering | Absorption | Control Panel
ANIM_MARGIN = 40

# Animation area (left third)
ANIM_WIDTH = int(SCENE_WIDTH * 0.5) - ANIM_MARGIN
ANIM_HEIGHT = (
    WINDOW_HEIGHT - ANIM_MARGIN * 2 - 180
)  # Leave space for flux displays and counters

# Scattering plot (middle third, same height as animation)
SCATTER_PLOT_X = ANIM_MARGIN + ANIM_WIDTH + 20
SCATTER_PLOT_Y = ANIM_MARGIN
SCATTER_PLOT_WIDTH = int(SCENE_WIDTH * 0.25) - 30
SCATTER_PLOT_HEIGHT = ANIM_HEIGHT

# Absorption plot (right third, same height as animation)
ABSORB_PLOT_X = SCATTER_PLOT_X + SCATTER_PLOT_WIDTH + 20
ABSORB_PLOT_Y = ANIM_MARGIN
ABSORB_PLOT_WIDTH = SCENE_WIDTH - ABSORB_PLOT_X - 20
ABSORB_PLOT_HEIGHT = ANIM_HEIGHT

# Colors
COLOR_BG = (240, 245, 250)
COLOR_PANEL = (255, 255, 255)
COLOR_TOA = (30, 60, 120)
COLOR_SURFACE = (139, 90, 43)
COLOR_ATMOSPHERE = (135, 206, 235, 80)  # Sky blue with alpha

# Photon colors
COLOR_PHOTON_DOWN = (255, 200, 0)  # Yellow-orange (downward moving)
COLOR_PHOTON_UP = (0, 150, 255)  # Blue (upward moving)
COLOR_PHOTON_ABSORBED = (200, 50, 50)  # Red (absorbed)
COLOR_SCATTER_EVENT = (255, 100, 255)  # Magenta flash for scattering

# Photon animation
PHOTON_RADIUS = 3
PHOTON_SPEED = 2.0  # Pixels per frame (in optical depth units)
SCATTER_FLASH_DURATION = 20  # Frames to show scatter event flash
ABSORPTION_FADE_DURATION = 25  # Frames for absorption animation

# Simulation parameters
DEFAULT_TAU_MAX = 3.0
DEFAULT_OMEGA_0 = 0.9  # Single scattering albedo
DEFAULT_G = 0.75  # Asymmetry parameter
DEFAULT_SURFACE_ALBEDO = 0.2
DEFAULT_NUM_PHOTONS = 100
MIN_PHOTONS = 1
MAX_PHOTONS = 10000

# Propagation modes
SEQUENTIAL_MODE = "sequential"  # Launch photons one by one
PARALLEL_MODE = "parallel"  # All photons move simultaneously
DEFAULT_MODE = PARALLEL_MODE  # Start in parallel mode by default

# Physics
WEIGHT_THRESHOLD = 0.01

# Frame rate
FPS = 60

# Statistics bins
NUM_DEPTH_BINS = 30  # For showing where photons are absorbed/scattered

# Counter display
COUNTER_FONT_SIZE = 48
COUNTER_LABEL_SIZE = 20

# Solar flux parameters
SOLAR_CONSTANT = 1361.0  # W/m^2 - Solar irradiance at TOA (typical value)
FLUX_FONT_SIZE = 36
FLUX_LABEL_SIZE = 18

# Multi-layer parameters
MAX_LAYERS = 5
MIN_LAYERS = 1

# Layer presets with literature-based optical properties
# References:
# - Rayleigh: g=0 (symmetric), ω=1.0 (pure scattering), τ~0.08 at 500nm
# - Cirrus: τ~0.3-1.4 (95%), ω~0.84-0.99, g~0.75 for ice crystals
# - Water clouds: τ~5-10, ω~0.9995-0.9999, g~0.85 (Mie theory)
# - Urban aerosol: τ~0.1-0.2, ω~0.835 (measured mean), g~0.39
# - Volcanic sulfate: τ~0.0-0.3, ω~0.98 (highly reflective)
# - Biomass smoke: τ~0.23, ω~0.87, g~0.60
LAYER_PRESETS = {
    "Rayleigh (Clear Sky)": {
        "tau_thickness": 0.08,
        "omega_0": 1.0,
        "g": 0.0,
        "description": "Molecular scattering only",
        "color": (135, 206, 250, 60),  # Light blue
    },
    "Cirrus (Ice Cloud)": {
        "tau_thickness": 0.8,
        "omega_0": 0.92,
        "g": 0.75,
        "description": "High-altitude ice crystals",
        "color": (240, 248, 255, 90),  # Alice blue
    },
    "Stratocumulus (Water)": {
        "tau_thickness": 10.0,
        "omega_0": 0.9999,
        "g": 0.85,
        "description": "Low-level water cloud",
        "color": (220, 220, 220, 130),  # Light gray
    },
    "Altostratus (Water)": {
        "tau_thickness": 5.0,
        "omega_0": 0.9995,
        "g": 0.85,
        "description": "Mid-level water cloud",
        "color": (200, 200, 210, 110),  # Light gray-blue
    },
    "Urban Aerosol": {
        "tau_thickness": 0.15,
        "omega_0": 0.835,
        "g": 0.39,
        "description": "Pollution and urban haze",
        "color": (205, 170, 125, 110),  # Tan/brown
    },
    "Volcanic Sulfate": {
        "tau_thickness": 0.10,
        "omega_0": 0.98,
        "g": 0.65,
        "description": "Stratospheric sulfate layer",
        "color": (190, 190, 200, 100),  # Light gray-white
    },
    "Biomass Smoke": {
        "tau_thickness": 0.23,
        "omega_0": 0.87,
        "g": 0.60,
        "description": "Wildfire/agricultural smoke",
        "color": (139, 137, 137, 140),  # Dark gray
    },
    "Custom": {
        "tau_thickness": 1.0,
        "omega_0": 0.9,
        "g": 0.0,
        "description": "User-defined properties",
        "color": (135, 206, 235, 80),  # Sky blue
    },
}
