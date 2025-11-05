"""
Monte Carlo 2-Stream Radiative Transfer Physics
Based on monte_carlo_2stream.py
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List
from enum import Enum


class Direction(Enum):
    """Photon direction in two-stream approximation"""

    UP = -1  # Toward space (τ decreases)
    DOWN = 1  # Toward surface (τ increases)


class Outcome(Enum):
    """Photon final outcome"""

    REFLECTED = 1  # Exited at TOA
    TRANSMITTED = 2  # Exited at BOA
    ABSORBED = 3  # Weight below threshold


@dataclass
class Photon:
    """
    Photon packet in optical depth coordinates

    Attributes:
        position: Current optical depth [0, tau_max]
        direction: UP (-1) or DOWN (+1)
        weight: Current weight [0, 1]
        active: Whether photon is still propagating
    """

    position: float = 0.0
    direction: Direction = Direction.DOWN
    weight: float = 1.0
    active: bool = True
    path: List[float] = None  # Store trajectory for visualization

    def __post_init__(self):
        if self.path is None:
            self.path = [self.position]


@dataclass
class Atmosphere:
    """
    Atmospheric optical properties

    Attributes:
        tau_max: Total optical depth
        omega_0: Single scattering albedo [0, 1]
        g: Asymmetry parameter [-1, 1]
        surface_albedo: Bottom boundary reflectance [0, 1]
    """

    tau_max: float
    omega_0: float
    g: float = 0.0
    surface_albedo: float = 0.0

    @property
    def is_pure_absorption(self) -> bool:
        return self.omega_0 == 0.0

    @property
    def is_conservative(self) -> bool:
        return self.omega_0 == 1.0


def sample_optical_depth() -> float:
    """Sample optical depth to next interaction from exponential distribution"""
    return -np.log(np.random.random())


def propagate_to_interaction(
    photon: Photon, atmosphere: Atmosphere
) -> Tuple[bool, str]:
    """
    Move photon to next interaction or boundary

    Returns:
        (boundary_reached, boundary_type)
    """
    delta_tau = sample_optical_depth()
    new_position = photon.position + photon.direction.value * delta_tau

    # Check boundaries
    if new_position <= 0.0:
        photon.position = 0.0
        photon.path.append(photon.position)
        return True, "top"
    elif new_position >= atmosphere.tau_max:
        photon.position = atmosphere.tau_max
        photon.path.append(photon.position)
        return True, "bottom"
    else:
        photon.position = new_position
        photon.path.append(photon.position)
        return False, "none"


def scatter_isotropic(photon: Photon) -> None:
    """Scatter photon isotropically in two-stream (50/50 up/down)"""
    if np.random.random() < 0.5:
        photon.direction = Direction.DOWN
    else:
        photon.direction = Direction.UP


def scatter_henyey_greenstein(photon: Photon, g: float) -> None:
    """
    Scatter photon using Henyey-Greenstein phase function

    In two-stream:
        P(forward) = (1 + g) / 2
        P(backward) = (1 - g) / 2
    """
    p_forward = (1 + g) / 2

    if np.random.random() < p_forward:
        # Forward scatter: maintain direction
        pass
    else:
        # Backward scatter: reverse direction
        photon.direction = (
            Direction.UP if photon.direction == Direction.DOWN else Direction.DOWN
        )


def interact(photon: Photon, atmosphere: Atmosphere) -> str:
    """
    Process interaction: scatter or absorb

    Returns:
        'scatter' or 'absorb'
    """
    if np.random.random() < atmosphere.omega_0:
        # Scattering event
        if atmosphere.g == 0.0:
            scatter_isotropic(photon)
        else:
            scatter_henyey_greenstein(photon, atmosphere.g)
        return "scatter"
    else:
        # Absorption event
        photon.active = False
        return "absorb"


def simulate_photon(
    atmosphere: Atmosphere, weight_threshold: float = 0.01
) -> Tuple[Outcome, float, List[float]]:
    """
    Simulate a single photon through atmosphere

    Returns:
        (outcome, final_weight, trajectory)
    """
    photon = Photon(position=0.0, direction=Direction.DOWN, weight=1.0)

    while photon.active:
        boundary, boundary_type = propagate_to_interaction(photon, atmosphere)

        if boundary:
            if boundary_type == "top":
                return Outcome.REFLECTED, photon.weight, photon.path
            else:  # bottom
                # Check surface reflection
                if np.random.random() < atmosphere.surface_albedo:
                    photon.direction = Direction.UP
                    continue
                else:
                    return Outcome.TRANSMITTED, photon.weight, photon.path

        # Check weight threshold
        if photon.weight < weight_threshold:
            return Outcome.ABSORBED, photon.weight, photon.path

        # Interaction
        photon.weight *= atmosphere.omega_0
        interaction = interact(photon, atmosphere)

        if interaction == "absorb":
            return Outcome.ABSORBED, photon.weight, photon.path

    return Outcome.ABSORBED, photon.weight, photon.path


def run_simulation(
    atmosphere: Atmosphere, num_photons: int, weight_threshold: float = 0.01
) -> dict:
    """
    Run Monte Carlo simulation with multiple photons

    Returns:
        Dictionary with statistics and sample paths
    """
    energy_reflected = 0.0
    energy_transmitted = 0.0
    energy_absorbed = 0.0

    sample_paths = []
    max_sample_paths = 50

    for i in range(num_photons):
        outcome, final_weight, path = simulate_photon(atmosphere, weight_threshold)

        if outcome == Outcome.REFLECTED:
            energy_reflected += final_weight
        elif outcome == Outcome.TRANSMITTED:
            energy_transmitted += final_weight
        elif outcome == Outcome.ABSORBED:
            energy_absorbed += 1.0 - final_weight

        # Store sample paths for visualization
        if i < max_sample_paths:
            sample_paths.append(
                {"outcome": outcome, "path": path, "weight": final_weight}
            )

    total_energy = num_photons

    return {
        "reflectance": energy_reflected / total_energy,
        "transmittance": energy_transmitted / total_energy,
        "absorptance": energy_absorbed / total_energy,
        "energy_reflected": energy_reflected,
        "energy_transmitted": energy_transmitted,
        "energy_absorbed": energy_absorbed,
        "total_energy": total_energy,
        "sample_paths": sample_paths,
        "num_photons": num_photons,
    }
