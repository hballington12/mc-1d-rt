"""
Configuration and constants for Monte Carlo 2-Stream RT Demo
"""

from enum import Enum
from dataclasses import dataclass


# Window dimensions
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
SCENE_WIDTH = 900  # Left side for visualization
PANEL_WIDTH = WINDOW_WIDTH - SCENE_WIDTH  # Right side for controls

# Colors
COLOR_BG = (240, 240, 240)
COLOR_PANEL = (255, 255, 255)
COLOR_TOA = (30, 60, 120)
COLOR_SURFACE = (139, 90, 43)
COLOR_ATMOSPHERE = (135, 206, 235, 100)  # Sky blue with alpha


# Atmospheric presets
class AtmospherePreset(Enum):
    CLEAR_SKY = "Clear Sky"
    THIN_CLOUD = "Thin Cloud"
    THICK_CLOUD = "Thick Cloud"
    AEROSOL_LAYER = "Aerosol Layer"
    CUSTOM = "Custom"


# Scattering types
class ScatteringType(Enum):
    ISOTROPIC = "Isotropic (g=0)"
    FORWARD = "Forward (g=0.85)"
    MODERATE = "Moderate (g=0.5)"
    BACKWARD = "Backward (g=-0.3)"


@dataclass
class AtmosphereConfig:
    """Configuration for atmospheric optical properties"""

    tau_max: float = 1.0  # Total optical depth
    omega_0: float = 0.9  # Single scattering albedo
    g: float = 0.5  # Asymmetry parameter
    surface_albedo: float = 0.2  # Bottom boundary reflectance
    solar_zenith: float = 0.0  # Solar zenith angle (degrees)

    @property
    def is_pure_absorption(self) -> bool:
        return self.omega_0 == 0.0

    @property
    def is_conservative(self) -> bool:
        return self.omega_0 == 1.0


# Preset configurations
ATMOSPHERE_PRESETS = {
    AtmospherePreset.CLEAR_SKY: AtmosphereConfig(
        tau_max=0.1, omega_0=0.95, g=0.0, surface_albedo=0.15, solar_zenith=30.0
    ),
    AtmospherePreset.THIN_CLOUD: AtmosphereConfig(
        tau_max=5.0, omega_0=0.9999, g=0.85, surface_albedo=0.2, solar_zenith=30.0
    ),
    AtmospherePreset.THICK_CLOUD: AtmosphereConfig(
        tau_max=30.0, omega_0=0.9999, g=0.85, surface_albedo=0.2, solar_zenith=30.0
    ),
    AtmospherePreset.AEROSOL_LAYER: AtmosphereConfig(
        tau_max=1.0, omega_0=0.85, g=0.7, surface_albedo=0.1, solar_zenith=60.0
    ),
}

# Simulation parameters
DEFAULT_NUM_PHOTONS = 5000
MAX_PHOTONS = 50000
WEIGHT_THRESHOLD = 0.01
FPS = 60

# Visualization parameters
MAX_PHOTON_PATHS_DISPLAY = 50  # Max photon trajectories to show
FLUX_LEVELS = 20  # Number of vertical levels for flux calculation
