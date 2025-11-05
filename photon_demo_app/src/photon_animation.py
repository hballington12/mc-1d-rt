"""
Real-time animated photon simulation
Shows photons moving vertically through atmosphere with scattering/absorption events
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class PhotonState(Enum):
    """Current state of animated photon"""

    MOVING = 1
    SCATTERING = 2  # Flash animation
    ABSORBING = 3  # Fade animation
    REFLECTED = 4  # Exited top
    TRANSMITTED = 5  # Exited bottom
    ABSORBED = 6  # Fully absorbed


class Direction(Enum):
    """Movement direction"""

    DOWN = 1
    UP = -1


@dataclass
class AnimatedPhoton:
    """
    A photon with animation state for real-time visualization

    Attributes:
        tau: Current optical depth position [0, tau_max]
        direction: Direction.DOWN or Direction.UP
        weight: Current weight [0, 1]
        state: Current animation state
        x_position: Horizontal position for display (fixed, just for spreading out visually)
        next_interaction_tau: Optical depth where next interaction occurs
        scatter_flash_timer: Frames remaining for scatter flash
        absorption_timer: Frames remaining for absorption fade
    """

    tau: float = 0.0
    direction: Direction = Direction.DOWN
    weight: float = 1.0
    state: PhotonState = PhotonState.MOVING
    x_position: float = 0.0
    next_interaction_tau: float = 0.0
    scatter_flash_timer: int = 0
    absorption_timer: int = 0

    def __post_init__(self):
        """Sample first interaction on creation"""
        if self.next_interaction_tau == 0.0:
            self.next_interaction_tau = self._sample_next_interaction()

    def _sample_next_interaction(self) -> float:
        """Sample optical depth to next interaction"""
        return -np.log(np.random.random())


@dataclass
class SimulationStats:
    """Statistics tracker for the simulation"""

    total_launched: int = 0
    reflected: int = 0
    transmitted: int = 0
    absorbed: int = 0

    # Where photons get absorbed (depth bins)
    absorption_profile: List[int] = field(default_factory=lambda: [0] * 30)

    # Where photons scatter (depth bins)
    scattering_profile: List[int] = field(default_factory=lambda: [0] * 30)

    # Running counts of photons in each state
    currently_moving: int = 0

    # Total scattering events
    total_scatters: int = 0

    def reset(self):
        """Reset all statistics"""
        self.total_launched = 0
        self.reflected = 0
        self.transmitted = 0
        self.absorbed = 0
        self.absorption_profile = [0] * len(self.absorption_profile)
        self.scattering_profile = [0] * len(self.scattering_profile)
        self.currently_moving = 0
        self.total_scatters = 0

    @property
    def completed(self) -> int:
        """Total completed photons"""
        return self.reflected + self.transmitted + self.absorbed

    @property
    def reflectance(self) -> float:
        """Fraction reflected"""
        return self.reflected / self.total_launched if self.total_launched > 0 else 0.0

    @property
    def transmittance(self) -> float:
        """Fraction transmitted"""
        return (
            self.transmitted / self.total_launched if self.total_launched > 0 else 0.0
        )

    @property
    def absorptance(self) -> float:
        """Fraction absorbed"""
        return self.absorbed / self.total_launched if self.total_launched > 0 else 0.0


class PhotonSimulation:
    """
    Manages real-time animated photon simulation
    Photons move step-by-step through atmosphere
    """

    def __init__(
        self,
        tau_max: float,
        omega_0: float,
        g: float,
        surface_albedo: float,
        num_photons: int,
        scene_width: float,
        mode: str = "sequential",
        weight_threshold: float = 0.01,
    ):
        self.tau_max = tau_max
        self.omega_0 = omega_0  # Single scattering albedo
        self.g = g  # Asymmetry parameter
        self.surface_albedo = surface_albedo
        self.num_photons = num_photons
        self.scene_width = scene_width
        self.mode = mode  # "sequential" or "parallel"
        self.weight_threshold = weight_threshold

        self.photons: List[AnimatedPhoton] = []
        self.stats = SimulationStats()

        self.launch_counter = 0
        self.launch_interval = 2  # Frames between photon launches (sequential mode)
        self.frames_since_launch = 0

    def reset(
        self,
        tau_max: float,
        omega_0: float,
        g: float,
        surface_albedo: float,
        num_photons: int,
        mode: str = "sequential",
    ):
        """Reset simulation with new parameters"""
        self.tau_max = tau_max
        self.omega_0 = omega_0
        self.g = g
        self.surface_albedo = surface_albedo
        self.num_photons = num_photons
        self.mode = mode

        self.photons.clear()
        self.stats.reset()
        self.launch_counter = 0
        self.frames_since_launch = 0

        # In parallel mode, launch all photons at once
        if self.mode == "parallel":
            for i in range(self.num_photons):
                self._launch_photon()

    def update(self, speed: float = 2.0):
        """
        Update simulation by one time step

        Args:
            speed: Movement speed in optical depth units per frame
        """
        # Launch new photons if needed (sequential mode only)
        if self.mode == "sequential" and self.launch_counter < self.num_photons:
            self.frames_since_launch += 1
            if self.frames_since_launch >= self.launch_interval:
                self._launch_photon()
                self.frames_since_launch = 0

        # Update all active photons
        for photon in self.photons:
            self._update_photon(photon, speed)

        # Remove completed photons (keep for a bit for visualization)
        self.photons = [
            p
            for p in self.photons
            if p.state not in [PhotonState.REFLECTED, PhotonState.TRANSMITTED]
            or p.absorption_timer > 0
        ]

        # Update currently moving count
        self.stats.currently_moving = sum(
            1 for p in self.photons if p.state == PhotonState.MOVING
        )

    def _launch_photon(self):
        """Launch a new photon from TOA"""
        # Spread photons across scene width
        x_pos = (self.launch_counter / max(self.num_photons - 1, 1)) * self.scene_width

        photon = AnimatedPhoton(
            tau=0.0,
            direction=Direction.DOWN,
            weight=1.0,
            state=PhotonState.MOVING,
            x_position=x_pos,
        )

        self.photons.append(photon)
        self.launch_counter += 1
        self.stats.total_launched += 1

    def _update_photon(self, photon: AnimatedPhoton, speed: float):
        """Update single photon state"""

        # Handle special animation states
        if photon.state == PhotonState.ABSORBING:
            photon.absorption_timer -= 1
            if photon.absorption_timer <= 0:
                photon.state = PhotonState.ABSORBED
                self.stats.absorbed += 1
                # Record absorption depth
                bin_idx = int(
                    (photon.tau / self.tau_max) * len(self.stats.absorption_profile)
                )
                bin_idx = min(bin_idx, len(self.stats.absorption_profile) - 1)
                self.stats.absorption_profile[bin_idx] += 1
            return

        # Skip if already completed
        if photon.state in [
            PhotonState.REFLECTED,
            PhotonState.TRANSMITTED,
            PhotonState.ABSORBED,
        ]:
            return

        # Move photon
        delta_tau = speed * 0.01  # Convert pixels to optical depth units
        photon.tau += photon.direction.value * delta_tau

        # Check boundaries
        if photon.tau <= 0.0:
            photon.tau = 0.0
            photon.state = PhotonState.REFLECTED
            self.stats.reflected += 1
            return

        if photon.tau >= self.tau_max:
            photon.tau = self.tau_max
            # Check surface reflection
            if np.random.random() < self.surface_albedo:
                photon.direction = Direction.UP
                photon.next_interaction_tau = photon.tau + Direction.UP.value * (
                    -np.log(np.random.random())
                )
            else:
                photon.state = PhotonState.TRANSMITTED
                self.stats.transmitted += 1
            return

        # Check if reached interaction point
        if (
            photon.direction == Direction.DOWN
            and photon.tau >= photon.next_interaction_tau
        ) or (
            photon.direction == Direction.UP
            and photon.tau <= photon.next_interaction_tau
        ):
            # Interaction!
            self._process_interaction(photon)

    def _process_interaction(self, photon: AnimatedPhoton):
        """Process scattering or absorption event"""

        # Decide: scatter or absorb?
        if np.random.random() < self.omega_0:
            # Scattering event - no animation delay, just instant direction change
            # Record scattering event location
            self.stats.total_scatters += 1
            bin_idx = int(
                (photon.tau / self.tau_max) * len(self.stats.scattering_profile)
            )
            bin_idx = min(bin_idx, len(self.stats.scattering_profile) - 1)
            self.stats.scattering_profile[bin_idx] += 1

            # Henyey-Greenstein scattering in 2-stream
            # P(forward) = (1 + g) / 2, P(backward) = (1 - g) / 2
            p_forward = (1 + self.g) / 2

            if np.random.random() < p_forward:
                # Forward scatter: maintain current direction
                pass
            else:
                # Backward scatter: reverse direction
                photon.direction = (
                    Direction.UP
                    if photon.direction == Direction.DOWN
                    else Direction.DOWN
                )

            # Sample next interaction and continue moving
            photon.next_interaction_tau = photon.tau + photon.direction.value * (
                -np.log(np.random.random())
            )
            photon.state = PhotonState.MOVING
        else:
            # Absorption event
            photon.state = PhotonState.ABSORBING
            photon.absorption_timer = 15  # Fade for 15 frames

        # Check weight threshold
        photon.weight *= self.omega_0
        if photon.weight < self.weight_threshold:
            photon.state = PhotonState.ABSORBING
            photon.absorption_timer = 15

    def is_complete(self) -> bool:
        """Check if simulation is complete"""
        return self.stats.completed >= self.num_photons

    def get_active_photons(self) -> List[AnimatedPhoton]:
        """Get all photons for rendering"""
        return self.photons
