"""
Configuration for Real-Time Photon Animation Demo
Simple, educational visualization of photon propagation
"""

# Window dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
SCENE_WIDTH = 950  # Left side for animation and plots
PANEL_WIDTH = WINDOW_WIDTH - SCENE_WIDTH  # Right side for controls

# Animation area (full left side)
ANIM_MARGIN = 40
ANIM_WIDTH = int(SCENE_WIDTH * 0.7) - ANIM_MARGIN * 2
ANIM_HEIGHT = (
    WINDOW_HEIGHT - ANIM_MARGIN * 2 - 180
)  # Leave space for flux displays and counters at bottom

# Profile plot area (right side of scene)
PLOT_X = int(SCENE_WIDTH * 0.7) + 20
PLOT_WIDTH = SCENE_WIDTH - PLOT_X - 20
PLOT_HEIGHT = 300
SCATTER_PLOT_Y = 50
ABSORB_PLOT_Y = SCATTER_PLOT_Y + PLOT_HEIGHT + 50

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
PHOTON_RADIUS = 4
PHOTON_SPEED = 2.0  # Pixels per frame (in optical depth units)
SCATTER_FLASH_DURATION = 10  # Frames to show scatter event flash
ABSORPTION_FADE_DURATION = 15  # Frames for absorption animation

# Simulation parameters
DEFAULT_TAU_MAX = 3.0
DEFAULT_OMEGA_0 = 0.9  # Single scattering albedo
DEFAULT_G = 0.0  # Asymmetry parameter
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

# Layer presets (name: {tau_thickness, omega_0, g, description})
LAYER_PRESETS = {
    "Clear Atmosphere": {
        "tau_thickness": 0.1,
        "omega_0": 0.99,
        "g": 0.1,
        "description": "Rayleigh scattering only",
        "color": (135, 206, 250, 80),  # Light blue
    },
    "Thin Cirrus": {
        "tau_thickness": 1.0,
        "omega_0": 0.999,
        "g": 0.85,
        "description": "Ice crystals, high altitude",
        "color": (240, 248, 255, 100),  # Alice blue
    },
    "Water Cloud": {
        "tau_thickness": 10.0,
        "omega_0": 0.99,
        "g": 0.85,
        "description": "Liquid water droplets",
        "color": (220, 220, 220, 120),  # Light gray
    },
    "Thick Cloud": {
        "tau_thickness": 30.0,
        "omega_0": 0.999,
        "g": 0.85,
        "description": "Dense water cloud",
        "color": (180, 180, 180, 150),  # Gray
    },
    "Aerosol Layer": {
        "tau_thickness": 0.5,
        "omega_0": 0.9,
        "g": 0.7,
        "description": "Dust or pollution",
        "color": (205, 170, 125, 100),  # Tan
    },
    "Smoke/Soot": {
        "tau_thickness": 2.0,
        "omega_0": 0.85,
        "g": 0.6,
        "description": "Absorbing particles",
        "color": (139, 137, 137, 130),  # Dark gray
    },
    "Custom": {
        "tau_thickness": 3.0,
        "omega_0": 0.9,
        "g": 0.0,
        "description": "User-defined properties",
        "color": (135, 206, 235, 80),  # Sky blue
    },
}
