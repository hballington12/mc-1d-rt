# Pygame GUI Application Architecture Summary

## Overview
This is a **pygame + pygame_gui** based interactive 2D ray tracing visualization application. It demonstrates optics simulations with real-time interactive controls for scene parameters, physics calculations, and live scattering analysis.

---

## 1. GUI Framework & Dependencies

### Framework Stack:
- **pygame**: Core graphics and windowing
- **pygame_gui**: High-level UI controls (sliders, buttons, dropdowns, labels)
- **numpy**: Numerical computations
- **Custom modules**: Scene geometry, ray tracing, optics physics

### Why pygame_gui over raw pygame:
- Built-in widgets with event handling
- Clean separation between UI logic and rendering
- Event-driven architecture (`UI_HORIZONTAL_SLIDER_MOVED`, `UI_BUTTON_PRESSED`, etc.)
- Automatic layout management and state handling

---

## 2. Main Application Structure (`integrated_gui.py`)

### Class: `IntegratedRayTracingApp`

#### Initialization Phase:
```python
__init__():
    - Setup pygame window (1200 x 700)
    - Create rendering area (800px wide for visualization)
    - Setup pygame_gui UIManager for control panel (right side)
    - Initialize scene_params dictionary (centralized state)
    - Create GUI controls via _create_gui_controls()
    - Call _update_scene() for initial computation
```

#### Key Architecture Pattern:
```
Window Layout:
┌─────────────────────────────────────────┬──────────────────┐
│                                         │                  │
│  Rendering Area (800px)                 │  Control Panel   │
│  - Ray tracing visualization            │  (400px)         │
│  - Shapes, rays, colorscale             │  - Sliders       │
│                                         │  - Buttons       │
│                                         │  - Dropdown      │
│                                         │  - Scattering    │
│                                         │    Plot          │
└─────────────────────────────────────────┴──────────────────┘
```

---

## 3. Config File (`config.py`)

### Purpose:
Centralized configuration storage using Python enums and dataclasses.

### Key Components:

```python
# Enums for type safety
class Polarization(Enum):
    PARALLEL = "parallel"          # E-field in x-y plane
    PERPENDICULAR = "perpendicular" # E-field in z direction

class ShapeType(Enum):
    SQUARE, TRIANGLE, HEXAGON, OCTAGON, CIRCLE

# Configuration dataclass
@dataclass
class ShapeConfig:
    shape_type: ShapeType
    center: Tuple[float, float]
    size: float
    rotation: float
    refractive_index: complex

# Global parameters
NUM_RAYS = 100
POLARIZATION = Polarization.PERPENDICULAR
MAX_RECURSION = 3
VACUUM_REFRACTIVE_INDEX = 1.0 + 0j
```

### Design Pattern:
- Use enums to prevent string typos
- Dataclasses for structured configuration
- All magic numbers in one place for easy tuning

---

## 4. Scene Management

### Class: `Scene` (from `scene.py`)

#### Purpose:
Manage geometric shapes and ray tracing logic.

#### Key Methods:

**Shape Creation & Geometry:**
```python
class Shape:
    - __init__(center, size, rotation, refractive_index)
    - _get_base_vertices()      # Unit shape definition
    - _compute_transformed_vertices()  # Apply scale, rotation, translation
    - get_edges()               # Return edge segments
    - get_edge_normals()        # Calculate outward-pointing normals
    - get_bounds()              # Bounding box for intersection testing
```

**Concrete Shape Classes:**
```python
Square, Triangle, Hexagon, Octagon, Circle
(All inherit from Shape, define _get_base_vertices())
```

#### Ray Tracing Algorithm:
1. **Ray-Edge Intersection Detection**: Check ray against all shape edges + scene boundaries
2. **Find Closest Intersection**: Track minimum t value
3. **Handle Interaction**: If not at boundary, calculate reflection/refraction
4. **Recursive Tracing**: Generate new rays up to max recursion depth
5. **Store Path**: All segments stored in RayPath

---

## 5. Control System (`integrated_gui.py` - detailed)

### Scene Parameters Dictionary:
```python
scene_params = {
    "position_x": float,           # Shape X position
    "position_y": float,           # Shape Y position
    "rotation_deg": float,         # Rotation in degrees
    "scale": float,                # Size scaling
    "refractive_index_real": float,   # n (real part)
    "refractive_index_imag": float,   # k (absorption)
    "wavelength_nm": float,        # Wavelength in nanometers
    "num_rays": int,               # Number of incident rays
    "plane_wave_offset": float,    # Y-offset of incident plane wave
    "polarization": Polarization,  # PARALLEL or PERPENDICULAR
    "max_recursion": int,          # Recursion depth
    "shape_type": ShapeType,       # Shape selection
}
```

### Control Types & Event Handling:

#### 1. Horizontal Sliders:
```python
self.pos_x_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(panel_x, y_pos, control_width, height),
    start_value=self.scene_params["position_x"],
    value_range=(-3.0, 3.0),
    manager=self.ui_manager,
)

# Event handling:
if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
    if event.ui_element == self.pos_x_slider:
        self.scene_params["position_x"] = event.value
        self.pos_x_label.set_text(f"Position X: {event.value:.2f}")
        self._update_scene()  # Recompute rays
```

#### 2. Buttons (Toggle):
```python
self.pol_parallel_button = pygame_gui.elements.UIButton(...)
self.pol_perp_button = pygame_gui.elements.UIButton(...)

# Event handling:
if event.type == pygame_gui.UI_BUTTON_PRESSED:
    if event.ui_element == self.pol_parallel_button:
        self.pol_parallel_button.disable()
        self.pol_perp_button.enable()
        self._update_scene()
```

#### 3. Dropdown Menu:
```python
self.shape_dropdown = pygame_gui.elements.UIDropDownMenu(
    options_list=["Square", "Triangle", "Hexagon", "Octagon", "Circle"],
    starting_option="Square",
    ...
)

# Event handling:
if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
    shape_map = {"Square": ShapeType.SQUARE, ...}
    self.scene_params["shape_type"] = shape_map.get(event.text)
    self._update_scene()
```

#### 4. Labels (Read-only Display):
```python
self.pos_x_label = pygame_gui.elements.UILabel(...)
# Updated dynamically via:
self.pos_x_label.set_text(f"Position X: {value:.2f}")
```

---

## 6. Real-Time Visualization & Rendering

### Rendering Pipeline:

```
Main Loop (60 FPS):
    1. Process all pygame events
    2. Handle UI events → update scene_params
    3. If params changed → call _update_scene()
    4. Render rays to render_surface
    5. Blit render_surface to screen
    6. Draw UI on top
    7. Display scattering plot
    8. Flip display
```

### render_scene() Method:

```python
def render_scene(self):
    # 1. Clear background
    self.render_surface.fill((0, 0, 0))
    
    # 2. Draw reference axes
    pygame.draw.line(...)  # x and y axes
    
    # 3. Draw scene boundary
    for edge in boundary_edges:
        pygame.draw.line(...)
    
    # 4. Draw incident plane wave (blue line)
    pygame.draw.line(...)
    
    # 5. Draw shapes (white polygons)
    for shape in self.shapes:
        vertices = [world_to_screen(v) for v in shape.transformed_vertices]
        pygame.draw.polygon(self.render_surface, (255, 255, 255), vertices, 2)
    
    # 6. Draw rays with intensity-based coloring
    for ray_path in self.ray_paths:
        for ray in ray_path.segments:
            intensity = calculate_intensity(ray.electric_field)
            color = intensity_to_heat_color(intensity, self.max_intensity)
            thickness = clamp(1 + 2*intensity/max, 1, 3)
            pygame.draw.line(..., color, ..., thickness)
    
    # 7. Draw colorscale legend
    draw_colorscale(...)
```

### Coordinate Transformation:

```python
def world_to_screen(self, point):
    """Convert world coordinates to screen coordinates"""
    screen_point = point * np.array([1, -1]) * self.scale + self.offset
    return tuple(screen_point.astype(int))
```

---

## 7. Physics & Visualization (`optics.py`, `colormap.py`)

### Ray Physics Calculations:

```python
# Snell's law refraction angle
snells_law_refraction_angle(theta_i, n1, n2) -> Optional[float]

# Vector math for reflection/refraction
get_reflection_vector(incident_dir, normal) -> np.ndarray
get_refraction_vector(incident_dir, normal, theta_i, theta_t) -> np.ndarray

# Fresnel coefficients (frequency-dependent)
fresnel_reflection_coefficient(n1, n2, theta_i, theta_t, polarization) -> complex
fresnel_transmission_coefficient(n1, n2, theta_i, theta_t, polarization) -> complex

# Material absorption
calculate_absorption_factor(distance, n_imag, wavelength_nm) -> float
# Uses Beer-Lambert law: exp(-2*k*2π*distance/λ)
```

### Visualization Functions:

```python
# Convert field amplitude to RGB color
intensity_to_heat_color(intensity, max_intensity, log_scale=True) -> (R, G, B)
# Colormap: Black → Red → Orange → Yellow → White

# Calculate intensity from electric field
calculate_intensity(electric_field) -> float
# Returns: E²/2

# Draw colorscale legend
draw_colorscale(screen, font, x, y, width, height, max_intensity, log_scale)
# Includes logarithmic scaling (4 orders of magnitude)
```

---

## 8. Advanced Features: Scattering Analysis

### _calculate_scattering_distribution() Method:

```python
1. Iterate through all ray_path.segments
2. For rays with recursion_level > 0 that hit boundary:
   - Calculate scattering angle from initial direction
   - Accumulate intensity in angular bins (0-180°)
   - Handle singularities at θ = 0° and θ = 180°

3. Convert to differential cross-section:
   - Divide by sin(θ) for solid angle normalization
   - Normalize by total intensity

4. Store in self.scattering_intensity array
```

### _draw_scattering_plot() Method:

```python
1. Draw plot background and border
2. Draw grid (5 horizontal, vertical at 30° intervals)
3. Plot scattering data with logarithmic y-axis
4. Connect points with lines (green color)
5. Add axis labels (angles 0-180°, log intensity scale)
```

---

## 9. Key Design Patterns

### Pattern 1: Event-Driven Updates
```python
# UI event → Parameter update → Scene recompute → Render
for event in pygame.event.get():
    handle_ui_event(event)  # Updates scene_params
    
if update_needed:
    _update_scene()  # Recomputes all rays
    
render_scene()  # Draws visualization
```

### Pattern 2: Centralized Parameter State
```python
# Single source of truth for all simulation parameters
self.scene_params = {key: value, ...}

# All controls read/write to this dictionary
# All scene computation reads from this dictionary
# Makes GUI interactive and state-consistent
```

### Pattern 3: Lazy Computation
```python
# Rays only recomputed when parameters change
# Not on every frame
# Expensive physics calculations cached until user changes slider
```

### Pattern 4: Composition Over Inheritance
```python
# IntegratedRayTracingApp manages:
#   - pygame initialization
#   - pygame_gui UIManager
#   - Scene parameters
#   - Rendering pipeline
#   
# Doesn't inherit from Scene, instead uses composition
# More flexible for UI-specific logic
```

### Pattern 5: Separation of Concerns
```
config.py       → Configuration and enums
ray.py          → Ray data structure
scene.py        → Geometry and shape classes
optics.py       → Physics calculations
colormap.py     → Visualization/coloring logic
scene_gui.py    → Alternative GUI (not used in integrated version)
integrated_gui.py → Main application and pygame_gui integration
```

---

## 10. Architecture for Your Monte Carlo 2-Stream RT Demo

### Recommended Structure:

```
app/
├── src/
│   ├── config.py              # Enums, dataclasses for params
│   ├── radiative_transfer.py  # Physics (two-stream equations)
│   ├── monte_carlo.py         # MC ray tracing
│   ├── atmosphere.py          # Atmospheric layers/scattering
│   ├── colormap.py            # Visualization colormaps
│   ├── integrated_gui.py       # pygame_gui main app
│   └── run.py                 # Entry point
├── requirements.txt
└── README.md
```

### Key Adaptations:

1. **Config Module**:
   ```python
   class AtmosphereProfile(Enum):
       CLEAR, CLOUD, AEROSOL, ...
   
   @dataclass
   class RTConfig:
       - solar_zenith_angle
       - surface_albedo
       - optical_depth
       - wavelength
       - num_photons
       - num_layers
   ```

2. **Physics Module** (Instead of optics.py):
   ```python
   - two_stream_equations(tau, omega, g)
   - rayleigh_scattering()
   - mie_scattering()
   - absorption_coefficient()
   - phase_function()
   ```

3. **Scene Parameters**:
   ```python
   scene_params = {
       "solar_zenith": 30.0,
       "surface_albedo": 0.15,
       "cloud_optical_depth": 5.0,
       "wavelength_nm": 500.0,
       "num_photons": 1000,
       "num_layers": 10,
       "scattering_type": "rayleigh",  # or "mie"
   }
   ```

4. **Visualization Enhancements**:
   - Instead of scattering plot, show:
     - Upwelling/downwelling flux vs height
     - Reflectance/transmittance spectrum
     - Phase function visualization
   - Modify colorscale for radiance/flux (not field amplitude)

5. **Control Panel**:
   ```python
   # Keep pygame_gui structure, adapt for RT parameters
   - Solar angle slider (0-90°)
   - Surface albedo slider (0-1)
   - Cloud optical depth slider
   - Wavelength selector (slider or dropdown)
   - Photon count slider
   - Output selector (flux, reflectance, transmittance)
   ```

---

## 11. Performance Considerations

### Current Implementation:
- 60 FPS target
- Ray computation happens off-screen (not blocking rendering)
- Lazy evaluation: rays only recomputed when parameters change
- Max recursion depth limits computation cost

### For Monte Carlo RT:
- **Challenge**: 10,000+ photons × multiple scatterings = expensive
- **Solution**: 
  1. Use background thread for computation
  2. Show progress indicator while computing
  3. Cache results for frequently-used parameter combinations
  4. Implement early stopping (convergence check)
  5. Use batch processing for photons

---

## 12. File Locations & Key Code Snippets

### File: `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/integrated_gui.py`
- **Lines 1-90**: Class initialization and GUI control creation
- **Lines 250-450**: Scene update and ray generation
- **Lines 800-900**: Event handling (slider, button, dropdown)
- **Lines 900+**: Main render loop and display

### File: `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/config.py`
- **Enums**: Polarization, ShapeType
- **Dataclass**: ShapeConfig
- **Global Constants**: NUM_RAYS, MAX_RECURSION, etc.

### File: `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/optics.py`
- **Line 5-30**: Snell's law refraction
- **Line 35-60**: Fresnel reflection/transmission coefficients
- **Line 100+**: Absorption calculations

---

## Summary of Architecture Strengths

1. **Modular Design**: Clear separation between physics, geometry, UI, and visualization
2. **Real-Time Interactivity**: Event-driven updates enable smooth user interaction
3. **Extensible**: Easy to add new shapes, new physics calculations, new visualizations
4. **Readable**: Well-documented with clear naming conventions
5. **Efficient**: Lazy computation, caching, only recalculate when needed
6. **Visualizations**: Multiple ways to display data (rays, colors, plots, analysis)

---

## Quick Reference: Common Patterns to Copy

```python
# 1. Create a slider
self.my_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect(x, y, width, height),
    start_value=initial_value,
    value_range=(min_val, max_val),
    manager=self.ui_manager,
)

# 2. Update label dynamically
self.my_label.set_text(f"Value: {self.scene_params['key']:.2f}")

# 3. Handle slider event
if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
    if event.ui_element == self.my_slider:
        self.scene_params['key'] = event.value
        update_needed = True

# 4. Trigger recomputation on change
if update_needed:
    self._update_scene()

# 5. Draw colored line based on intensity
color = intensity_to_heat_color(intensity, max_intensity)
pygame.draw.line(surface, color, start, end, thickness)

# 6. Convert world to screen coordinates
screen_pos = self.world_to_screen(world_pos)
```

---

## Files Analyzed

- `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/integrated_gui.py` (35,958 bytes)
- `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/config.py` (1,439 bytes)
- `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/scene_gui.py` (8,669 bytes)
- `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/scene.py` (19,861 bytes)
- `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/ray.py` (1,539 bytes)
- `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/optics.py` (7,501 bytes)
- `/Users/ixguard/Documents/work/post-doc/seminars/ss-lecture-2025/app/src/colormap.py` (5,573 bytes)

