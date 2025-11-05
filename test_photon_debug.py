"""Debug script to see what the photon paths look like"""

import numpy as np
import sys

sys.path.insert(0, "/Users/ixguard/Documents/work/post-doc/other/2s-rt-exercise")

from monte_carlo_2stream import Photon, Atmosphere, propagate_to_interaction, interact

# Create test atmosphere
atm = Atmosphere(tau_max=1.0, omega_0=0.8, g=0.0, surface_albedo=0.2)

np.random.seed(42)

# Simulate one photon and print its trajectory
photon = Photon(position=0.0, direction=1)  # Start at TOA, going toward surface
print("Step 0: position=0.0, direction=+1 (toward surface)")

max_steps = 50
for step in range(1, max_steps + 1):
    boundary, boundary_type = propagate_to_interaction(photon, atm)

    print(
        f"Step {step}: position={photon.position:.4f}, boundary={boundary}, type={boundary_type}"
    )

    if boundary:
        print(f"  -> Photon exited at boundary: {boundary_type}")
        break

    # Interaction: scatter or absorb
    interaction = interact(photon, atm)

    if interaction == "absorb":
        print(f"  -> Photon absorbed")
        break
    else:
        print(
            f"  -> Scattered, new direction={photon.direction} ({'→ surface' if photon.direction == 1 else '← space'})"
        )

print(f"\nTotal steps: {step}")
