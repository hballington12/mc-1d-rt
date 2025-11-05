"""
Two-Stream Monte Carlo Radiative Transfer Simulator
====================================================

A teaching implementation combining Monte Carlo methods with two-stream
radiative transfer approximation for atmospheric physics students.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class Photon:
    """
    Represents a photon packet traveling through the atmosphere.

    Attributes:
        position: Current optical depth position [0, tau_max]
        direction: Direction of travel (+1 = downward into atmosphere, -1 = upward to space)
        weight: Current weight of photon packet (starts at 1.0)
        active: Whether photon is still propagating

    Note:
        In optical depth coordinates, τ increases downward into the atmosphere.
        Therefore: direction = +1 means moving toward surface (τ increases)
                  direction = -1 means moving toward TOA (τ decreases)
    """

    position: float  # optical depth coordinate
    direction: int  # +1 (toward surface) or -1 (toward space)
    weight: float = 1.0
    active: bool = True

    def __post_init__(self):
        """Validate photon initialization."""
        if self.direction not in [-1, 1]:
            raise ValueError(
                "Direction must be +1 (toward surface) or -1 (toward space)"
            )
        if self.weight < 0 or self.weight > 1:
            raise ValueError("Weight must be between 0 and 1")


@dataclass
class Atmosphere:
    """
    Defines atmospheric optical properties.

    Attributes:
        tau_max: Total optical depth of atmosphere
        omega_0: Single scattering albedo (probability of scattering vs absorption)
        g: Asymmetry parameter (-1 = backscatter, 0 = isotropic, +1 = forward)
        surface_albedo: Bottom boundary reflectance [0, 1]
    """

    tau_max: float
    omega_0: float  # single scattering albedo
    g: float = 0.0  # asymmetry parameter (default: isotropic)
    surface_albedo: float = 0.0

    def __post_init__(self):
        """Validate atmospheric parameters."""
        if self.tau_max <= 0:
            raise ValueError("Optical depth must be positive")
        if not 0 <= self.omega_0 <= 1:
            raise ValueError("Single scattering albedo must be in [0, 1]")
        if not -1 <= self.g <= 1:
            raise ValueError("Asymmetry parameter must be in [-1, 1]")
        if not 0 <= self.surface_albedo <= 1:
            raise ValueError("Surface albedo must be in [0, 1]")

    @property
    def is_pure_absorption(self) -> bool:
        """Check if atmosphere is purely absorbing (no scattering)."""
        return self.omega_0 == 0.0

    @property
    def is_conservative(self) -> bool:
        """Check if scattering is conservative (no absorption)."""
        return self.omega_0 == 1.0


def sample_optical_depth() -> float:
    """
    Sample optical depth to next interaction using Beer-Lambert law.

    Distance to next interaction follows exponential distribution:
        s = -ln(ξ)

    where ξ is a uniform random number in (0, 1].

    Returns:
        Optical depth to next interaction (always positive)
    """
    xi = np.random.random()
    return -np.log(xi)


def propagate_to_interaction(
    photon: Photon, atmosphere: Atmosphere
) -> Tuple[bool, str]:
    """
    Move photon to next interaction or boundary.

    Args:
        photon: Photon packet to propagate
        atmosphere: Atmospheric properties

    Returns:
        Tuple of (boundary_reached, boundary_type)
        - boundary_reached: True if photon exits atmosphere
        - boundary_type: 'top', 'bottom', or 'none'
    """
    # Sample distance to next interaction
    delta_tau = sample_optical_depth()

    # Calculate new position based on direction
    new_position = photon.position + photon.direction * delta_tau

    # Check boundaries
    if new_position <= 0:
        # Hit top boundary
        photon.position = 0.0
        return True, "top"
    elif new_position >= atmosphere.tau_max:
        # Hit bottom boundary
        photon.position = atmosphere.tau_max
        return True, "bottom"
    else:
        # Interaction occurs within atmosphere
        photon.position = new_position
        return False, "none"


def scatter_isotropic(photon: Photon) -> None:
    """
    Scatter photon isotropically in two-stream approximation.

    In the two-stream model, we only have upward and downward directions.
    Isotropic scattering means equal probability of scattering into either hemisphere.

    Args:
        photon: Photon to scatter (modified in place)
    """
    # For two-stream: 50% chance of scattering toward surface, 50% toward space
    if np.random.random() < 0.5:
        photon.direction = 1  # toward surface (τ increases)
    else:
        photon.direction = -1  # toward space (τ decreases)


def scatter_henyey_greenstein(photon: Photon, g: float) -> None:
    """
    Scatter photon using Henyey-Greenstein phase function in two-stream.

    The Henyey-Greenstein phase function describes anisotropic scattering.
    In two-stream, this reduces to a simple forward/backward choice.

    Theory:
        P(forward) = (1 + g) / 2
        P(backward) = (1 - g) / 2

    where "forward" means continuing in the same hemisphere (same direction)
    and "backward" means scattering to opposite hemisphere (reverse direction).

    Args:
        photon: Photon to scatter (modified in place)
        g: Asymmetry parameter
           g > 0: forward scattering (prefers to continue same direction)
           g < 0: backward scattering (prefers to reverse direction)
           g = 0: isotropic (equal probability)

    Examples:
        g = 0.85 (water clouds): 92.5% forward, 7.5% backward
        g = 0.0 (isotropic): 50% forward, 50% backward
        g = -0.5 (backscatter): 25% forward, 75% backward
    """
    # Probability of forward scattering (continuing in same direction)
    p_forward = (1 + g) / 2

    if np.random.random() < p_forward:
        # Forward scatter: maintain current direction
        pass  # photon.direction unchanged
    else:
        # Backward scatter: reverse direction
        photon.direction *= -1


def interact(photon: Photon, atmosphere: Atmosphere) -> str:
    """
    Process interaction at current photon position.

    Determines whether photon scatters or is absorbed based on single
    scattering albedo. If scattered, applies scattering direction change.

    Args:
        photon: Photon undergoing interaction
        atmosphere: Atmospheric properties

    Returns:
        Interaction type: 'scatter' or 'absorb'
    """
    # Decide: scatter or absorb?
    if np.random.random() < atmosphere.omega_0:
        # Scattering event - choose direction based on phase function
        if atmosphere.g == 0.0:
            # Isotropic scattering
            scatter_isotropic(photon)
        else:
            # Anisotropic scattering using Henyey-Greenstein
            scatter_henyey_greenstein(photon, atmosphere.g)

        return "scatter"
    else:
        # Absorption event
        photon.active = False
        return "absorb"


def visualize_atmosphere(
    atmosphere: Atmosphere, filename: str = "atmosphere_structure.png"
):
    """
    Visualize the atmospheric structure and optical properties.

    Args:
        atmosphere: Atmosphere object to visualize
        filename: Output filename for the plot
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    # Panel 1: Atmospheric structure
    ax1 = axes[0]
    ax1.axhline(y=0, color="navy", linewidth=3, label="Top of Atmosphere (τ = 0)")
    ax1.axhline(
        y=atmosphere.tau_max,
        color="saddlebrown",
        linewidth=3,
        label=f"Surface (τ = {atmosphere.tau_max})",
    )
    ax1.fill_between(
        [0, 1], 0, atmosphere.tau_max, alpha=0.3, color="skyblue", label="Atmosphere"
    )
    ax1.set_ylim(-0.1, atmosphere.tau_max + 0.1)
    ax1.set_xlim(0, 1)
    ax1.set_ylabel("Optical Depth (τ)", fontsize=12)
    ax1.set_title("Atmospheric Structure", fontsize=13, fontweight="bold")
    ax1.legend(loc="center", fontsize=10)
    ax1.set_xticks([])
    ax1.grid(True, alpha=0.3, axis="y")
    ax1.invert_yaxis()  # Convention: TOA at top

    # Panel 2: Optical properties
    ax2 = axes[1]
    properties = ["ω₀\n(SSA)", "g\n(asym)", "Aₛ\n(albedo)"]
    values = [atmosphere.omega_0, (atmosphere.g + 1) / 2, atmosphere.surface_albedo]
    colors = ["steelblue", "coral", "forestgreen"]

    bars = ax2.barh(properties, values, color=colors, alpha=0.7, edgecolor="black")
    ax2.set_xlim(0, 1)
    ax2.set_xlabel("Value", fontsize=12)
    ax2.set_title("Optical Properties", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="x")

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        actual_val = atmosphere.g if i == 1 else val
        ax2.text(
            val + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{actual_val:.2f}",
            va="center",
            fontsize=11,
            fontweight="bold",
        )

    # Panel 3: Interaction probabilities
    ax3 = axes[2]

    # Calculate probabilities
    prob_scatter = atmosphere.omega_0
    prob_absorb = 1 - atmosphere.omega_0

    sizes = [prob_scatter, prob_absorb]
    labels = [f"Scattering\n{prob_scatter:.1%}", f"Absorption\n{prob_absorb:.1%}"]
    colors_pie = ["gold", "crimson"]

    wedges, texts, autotexts = ax3.pie(
        sizes,
        labels=labels,
        colors=colors_pie,
        autopct="",
        startangle=90,
        wedgeprops={"edgecolor": "black", "linewidth": 2},
    )

    for text in texts:
        text.set_fontsize(11)
        text.set_fontweight("bold")

    ax3.set_title("Interaction Type", fontsize=13, fontweight="bold")

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


def visualize_optical_depth_distribution(
    n_samples: int = 10000, filename: str = "optical_depth_distribution.png"
):
    """
    Visualize the exponential distribution of optical depths.

    Args:
        n_samples: Number of samples to generate
        filename: Output filename for the plot
    """
    # Sample optical depths
    samples = [sample_optical_depth() for _ in range(n_samples)]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Histogram with theoretical curve
    ax1 = axes[0]
    counts, bins, patches = ax1.hist(
        samples,
        bins=50,
        density=True,
        alpha=0.7,
        color="steelblue",
        edgecolor="black",
        label="MC samples",
    )

    # Theoretical exponential distribution
    tau_theory = np.linspace(0, max(samples), 200)
    pdf_theory = np.exp(-tau_theory)
    ax1.plot(tau_theory, pdf_theory, "r-", linewidth=2.5, label="Theory: exp(-τ)")

    ax1.set_xlabel("Optical Depth (τ)", fontsize=12)
    ax1.set_ylabel("Probability Density", fontsize=12)
    ax1.set_title("Optical Depth Sampling Distribution", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Cumulative distribution
    ax2 = axes[1]
    sorted_samples = np.sort(samples)
    cumulative = np.arange(1, len(sorted_samples) + 1) / len(sorted_samples)

    ax2.plot(
        sorted_samples, cumulative, "b-", linewidth=2, alpha=0.7, label="MC cumulative"
    )

    # Theoretical CDF: 1 - exp(-tau)
    tau_theory = np.linspace(0, max(samples), 200)
    cdf_theory = 1 - np.exp(-tau_theory)
    ax2.plot(tau_theory, cdf_theory, "r--", linewidth=2.5, label="Theory: 1-exp(-τ)")

    ax2.set_xlabel("Optical Depth (τ)", fontsize=12)
    ax2.set_ylabel("Cumulative Probability", fontsize=12)
    ax2.set_title("Cumulative Distribution Function", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


def visualize_photon_paths(
    atmosphere: Atmosphere, n_photons: int = 3, filename: str = "photon_paths.png"
):
    """
    Visualize individual photon trajectories step-by-step through the atmosphere.

    Args:
        atmosphere: Atmosphere object
        n_photons: Number of photon paths to simulate (default 3)
        filename: Output filename for the plot
    """
    fig, axes = plt.subplots(1, n_photons, figsize=(5 * n_photons, 6), squeeze=False)
    axes = axes.flatten()

    # Find interesting photon trajectories (ones with multiple scattering events)
    interesting_seeds = []
    for seed in range(1000):  # Try up to 1000 seeds
        np.random.seed(seed)
        test_photon = Photon(position=0.0, direction=1)
        scatter_count = 0

        for step in range(50):
            boundary, _ = propagate_to_interaction(test_photon, atmosphere)
            if boundary:
                break
            interaction = interact(test_photon, atmosphere)
            if interaction == "absorb":
                break
            scatter_count += 1

        # Keep trajectories with at least 3 scattering events
        if scatter_count >= 3:
            interesting_seeds.append(seed)
            if len(interesting_seeds) >= n_photons:
                break

    # If we didn't find enough interesting ones, just use sequential seeds
    if len(interesting_seeds) < n_photons:
        interesting_seeds = list(range(n_photons))

    # Simulate photon paths using selected seeds
    for photon_id in range(n_photons):
        np.random.seed(interesting_seeds[photon_id])
        ax = axes[photon_id]

        photon = Photon(position=0.0, direction=1)  # Start at TOA, going toward surface
        positions = [photon.position]
        steps = [0]

        # Track events
        events = []
        event_positions = []
        event_steps = []

        # Simulate up to 50 interactions per photon
        max_steps = 50
        for step in range(1, max_steps + 1):
            boundary, boundary_type = propagate_to_interaction(photon, atmosphere)

            positions.append(photon.position)
            steps.append(step)

            if boundary:
                event_type = "escape_top" if boundary_type == "top" else "hit_surface"
                events.append(event_type)
                event_positions.append(photon.position)
                event_steps.append(step)
                break

            # Interaction: scatter or absorb
            interaction = interact(photon, atmosphere)

            if interaction == "absorb":
                events.append("absorbed")
                event_positions.append(photon.position)
                event_steps.append(step)
                break
            else:
                # Scattering event - mark it
                events.append("scatter")
                event_positions.append(photon.position)
                event_steps.append(step)

        # Draw atmosphere boundaries
        ax.axhline(
            y=0, color="navy", linewidth=2, linestyle="-", label="TOA", alpha=0.7
        )
        ax.axhline(
            y=atmosphere.tau_max,
            color="saddlebrown",
            linewidth=2,
            linestyle="-",
            label="Surface",
            alpha=0.7,
        )
        ax.fill_betweenx(
            [0, atmosphere.tau_max], 0, max(steps), alpha=0.1, color="skyblue"
        )

        # Plot photon path
        ax.plot(
            steps,
            positions,
            "o-",
            color="darkblue",
            linewidth=2,
            markersize=4,
            alpha=0.6,
            label="Path",
        )

        # Mark scattering events
        scatter_steps = [event_steps[i] for i, e in enumerate(events) if e == "scatter"]
        scatter_positions = [
            event_positions[i] for i, e in enumerate(events) if e == "scatter"
        ]
        if scatter_steps:
            ax.scatter(
                scatter_steps,
                scatter_positions,
                s=80,
                color="gold",
                marker="*",
                edgecolor="black",
                linewidth=0.5,
                label="Scatter",
                zorder=5,
            )

        # Mark final outcome
        final_event = events[-1] if events else None
        final_step = event_steps[-1] if event_steps else 0
        final_pos = event_positions[-1] if event_positions else positions[-1]

        if final_event == "escape_top":
            ax.scatter(
                final_step,
                final_pos,
                s=150,
                color="green",
                marker="^",
                edgecolor="black",
                linewidth=1.5,
                label="Escaped",
                zorder=6,
            )
        elif final_event == "hit_surface":
            ax.scatter(
                final_step,
                final_pos,
                s=150,
                color="red",
                marker="v",
                edgecolor="black",
                linewidth=1.5,
                label="Surface",
                zorder=6,
            )
        elif final_event == "absorbed":
            ax.scatter(
                final_step,
                final_pos,
                s=150,
                color="crimson",
                marker="X",
                edgecolor="black",
                linewidth=1.5,
                label="Absorbed",
                zorder=6,
            )

        ax.set_xlabel("Step Number", fontsize=11)
        ax.set_ylabel("Optical Depth (τ)", fontsize=11)
        ax.set_title(f"Photon #{photon_id + 1}", fontsize=12, fontweight="bold")
        ax.set_ylim(-0.1, atmosphere.tau_max + 0.1)
        ax.invert_yaxis()
        ax.legend(fontsize=8, loc="best")
        ax.grid(True, alpha=0.3)

    plt.suptitle(
        f"Photon Trajectories (ω₀={atmosphere.omega_0}, τ={atmosphere.tau_max})",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {filename}")


if __name__ == "__main__":
    # Example setup for testing
    print("Two-Stream Monte Carlo RT Simulator")
    print("=" * 40)

    # Create test atmosphere (high scattering for interesting photon paths)
    atm = Atmosphere(tau_max=2.0, omega_0=0.95, g=0.0, surface_albedo=0.3)

    print(f"\nAtmosphere properties:")
    print(f"  Optical depth: {atm.tau_max}")
    print(f"  Single scatter albedo: {atm.omega_0}")
    print(f"  Asymmetry parameter: {atm.g}")
    print(f"  Surface albedo: {atm.surface_albedo}")
    print(f"  Pure absorption: {atm.is_pure_absorption}")
    print(f"  Conservative scattering: {atm.is_conservative}")

    # Create test photon (starting at TOA, going toward surface)
    photon = Photon(position=0.0, direction=1)

    print(f"\nInitial photon state:")
    print(f"  Position (τ): {photon.position}")
    print(
        f"  Direction: {photon.direction} ({'→ surface' if photon.direction == 1 else '← space'})"
    )
    print(f"  Weight: {photon.weight}")
    print(f"  Active: {photon.active}")

    # Test optical depth sampling
    print(f"\n{'Optical Depth Sampling Test':=^40}")
    print("Sampling 5 random optical depths:")
    for i in range(5):
        tau = sample_optical_depth()
        print(f"  Sample {i + 1}: τ = {tau:.4f}")

    # Test photon propagation
    print(f"\n{'Photon Propagation Test':=^40}")
    test_photon = Photon(
        position=0.0, direction=1
    )  # Start at TOA, going toward surface
    print(
        f"Starting at τ = {test_photon.position:.4f}, direction = {test_photon.direction} ({'→ surface' if test_photon.direction == 1 else '← space'})"
    )

    boundary, boundary_type = propagate_to_interaction(test_photon, atm)
    print(f"After propagation: τ = {test_photon.position:.4f}")
    print(f"Boundary reached: {boundary}, type: {boundary_type}")

    # Test upward propagation (toward space)
    test_photon2 = Photon(
        position=0.5, direction=-1
    )  # Middle of atmosphere, going toward space
    print(
        f"\nStarting at τ = {test_photon2.position:.4f}, direction = {test_photon2.direction} ({'→ surface' if test_photon2.direction == 1 else '← space'})"
    )
    boundary, boundary_type = propagate_to_interaction(test_photon2, atm)
    print(f"After propagation: τ = {test_photon2.position:.4f}")
    print(f"Boundary reached: {boundary}, type: {boundary_type}")

    # Test scattering
    print(f"\n{'Isotropic Scattering Test':=^40}")
    scatter_photon = Photon(position=0.5, direction=1)
    print(
        f"Before scattering: direction = {scatter_photon.direction} ({'→ surface' if scatter_photon.direction == 1 else '← space'})"
    )

    # Test multiple scattering events
    directions = []
    for _ in range(10):
        test_p = Photon(position=0.5, direction=1)
        scatter_isotropic(test_p)
        directions.append(test_p.direction)

    n_toward_surface = sum(1 for d in directions if d == 1)
    n_toward_space = sum(1 for d in directions if d == -1)
    print(
        f"After 10 scattering events: {n_toward_surface} toward surface, {n_toward_space} toward space"
    )

    # Test interaction
    print(f"\n{'Interaction Test':=^40}")
    print(f"Atmosphere: ω₀ = {atm.omega_0} (scattering probability)")

    results = {"scatter": 0, "absorb": 0}
    for _ in range(1000):
        test_p = Photon(position=0.5, direction=1)
        interaction_type = interact(test_p, atm)
        results[interaction_type] += 1

    print(f"After 1000 interactions:")
    print(f"  Scattered: {results['scatter']} ({results['scatter'] / 10:.1f}%)")
    print(f"  Absorbed: {results['absorb']} ({results['absorb'] / 10:.1f}%)")
    print(f"  Expected scatter rate: {atm.omega_0 * 100:.1f}%")

    # Test Henyey-Greenstein scattering
    print(f"\n{'Henyey-Greenstein Scattering Test':=^40}")

    test_g_values = [0.0, 0.5, 0.85, -0.3]
    for g_test in test_g_values:
        forward_count = 0
        n_trials = 1000

        for _ in range(n_trials):
            test_p = Photon(position=0.5, direction=1)  # Start going toward surface
            scatter_henyey_greenstein(test_p, g_test)
            if test_p.direction == 1:  # Still going toward surface (forward)
                forward_count += 1

        p_forward_observed = forward_count / n_trials
        p_forward_expected = (1 + g_test) / 2

        print(
            f"  g = {g_test:+.2f}: forward={p_forward_observed:.3f}, expected={p_forward_expected:.3f}"
        )

    # Generate visualizations
    print(f"\n{'Generating Visualizations':=^40}")
    visualize_atmosphere(atm)
    visualize_optical_depth_distribution(n_samples=10000)
    visualize_photon_paths(atm, n_photons=3)
    print("\nAll visualizations complete!")
