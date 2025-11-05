"""
Real-Time Photon Animation Demo - Multi-Layer Version
Complete 2-Stream RT simulation with all features:
- Sequential vs Parallel mode
- Multi-layer atmosphere support
- Layer presets (clouds, aerosols, etc.)
- Per-layer optical properties
- Scatter and absorption line plots
- Large animation window
"""

import pygame
import pygame_gui
import numpy as np

from config import *
from photon_animation import PhotonSimulation, PhotonState, Direction, AtmosphericLayer


class FinalPhotonDemo:
    """Complete photon demo with full 2-stream RT physics"""

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2-Stream RT Photon Animation - Complete")

        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Multi-layer parameters
        self.layers = [
            AtmosphericLayer(
                tau_top=0.0,
                tau_bottom=DEFAULT_TAU_MAX,
                omega_0=DEFAULT_OMEGA_0,
                g=DEFAULT_G,
                preset_name="Custom",
                color=LAYER_PRESETS["Custom"]["color"],
            )
        ]
        self.current_layer_index = 0  # Which layer is being edited
        self.surface_albedo = DEFAULT_SURFACE_ALBEDO
        self.num_photons = DEFAULT_NUM_PHOTONS
        self.animation_speed = PHOTON_SPEED
        self.mode = DEFAULT_MODE

        # Simulation
        self.simulation = PhotonSimulation(
            layers=self.layers,
            surface_albedo=self.surface_albedo,
            num_photons=self.num_photons,
            scene_width=ANIM_WIDTH,
            mode=self.mode,
        )

        # Fonts
        self.font_huge = pygame.font.Font(None, COUNTER_FONT_SIZE)
        self.font_flux = pygame.font.Font(None, FLUX_FONT_SIZE)
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)

        # Create UI
        self._create_ui()

        self.sim_running = False

    def _create_ui(self):
        """Create multi-layer control panel"""
        px = SCENE_WIDTH + 20
        y = 20
        w = PANEL_WIDTH - 60

        # Title
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 30),
            text="<b>2-Stream RT Multi-Layer</b>",
            manager=self.ui_manager,
        )
        y += 40

        # Mode toggle
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text="<b>Propagation Mode:</b>",
            manager=self.ui_manager,
        )
        y += 25

        self.mode_sequential = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(px, y, w // 2 - 5, 30),
            text="Sequential",
            manager=self.ui_manager,
        )

        self.mode_parallel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(px + w // 2 + 5, y, w // 2 - 5, 30),
            text="Parallel",
            manager=self.ui_manager,
        )
        y += 45

        # Layer Management Section
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text="<b>Atmospheric Layers</b>",
            manager=self.ui_manager,
        )
        y += 25

        # Layer selection dropdown
        layer_options = [f"Layer {i + 1}" for i in range(len(self.layers))]
        self.layer_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=layer_options,
            starting_option=layer_options[self.current_layer_index],
            relative_rect=pygame.Rect(px, y, w, 30),
            manager=self.ui_manager,
        )
        y += 35

        # Add/Remove layer buttons
        button_width = (w - 5) // 2
        self.add_layer_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(px, y, button_width, 30),
            text="Add Layer",
            manager=self.ui_manager,
        )

        self.remove_layer_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(px + button_width + 5, y, button_width, 30),
            text="Remove Layer",
            manager=self.ui_manager,
        )
        y += 45

        # Current Layer Properties Section
        self.layer_properties_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"<b>Layer {self.current_layer_index + 1} Properties</b>",
            manager=self.ui_manager,
        )
        y += 25

        # Preset dropdown
        preset_options = list(LAYER_PRESETS.keys())
        current_preset = self.layers[self.current_layer_index].preset_name
        self.preset_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=preset_options,
            starting_option=current_preset,
            relative_rect=pygame.Rect(px, y, w, 30),
            manager=self.ui_manager,
        )
        y += 35

        # Layer top tau
        current_layer = self.layers[self.current_layer_index]
        self.tau_top_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"Layer Top (τ): {current_layer.tau_top:.1f}",
            manager=self.ui_manager,
        )
        y += 25

        self.tau_top_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(px, y, w, 20),
            start_value=current_layer.tau_top,
            value_range=(0.0, 50.0),
            manager=self.ui_manager,
        )
        y += 30

        # Layer bottom tau
        self.tau_bottom_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"Layer Bottom (τ): {current_layer.tau_bottom:.1f}",
            manager=self.ui_manager,
        )
        y += 25

        self.tau_bottom_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(px, y, w, 20),
            start_value=current_layer.tau_bottom,
            value_range=(current_layer.tau_top + 0.1, 50.0),
            manager=self.ui_manager,
        )
        y += 30

        # Single scattering albedo
        self.omega_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"SSA (ω₀): {current_layer.omega_0:.2f}",
            manager=self.ui_manager,
        )
        y += 25

        self.omega_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(px, y, w, 20),
            start_value=current_layer.omega_0,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
        )
        y += 30

        # Asymmetry parameter
        self.g_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"Asymmetry (g): {current_layer.g:.2f}",
            manager=self.ui_manager,
        )
        y += 25

        self.g_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(px, y, w, 20),
            start_value=current_layer.g,
            value_range=(-1.0, 1.0),
            manager=self.ui_manager,
        )
        y += 35

        # Global Parameters Section
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text="<b>Global Parameters</b>",
            manager=self.ui_manager,
        )
        y += 25

        # Surface albedo
        self.albedo_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"Surface Albedo: {self.surface_albedo:.2f}",
            manager=self.ui_manager,
        )
        y += 25

        self.albedo_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(px, y, w, 20),
            start_value=self.surface_albedo,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
        )
        y += 30

        # Number of photons
        self.nphotons_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"Photons: {int(self.num_photons)}",
            manager=self.ui_manager,
        )
        y += 25

        self.nphotons_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(px, y, w, 20),
            start_value=self.num_photons,
            value_range=(MIN_PHOTONS, MAX_PHOTONS),
            manager=self.ui_manager,
        )
        y += 30

        # Animation speed
        self.speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(px, y, w, 20),
            text=f"Speed: {self.animation_speed:.1f}x",
            manager=self.ui_manager,
        )
        y += 25

        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(px, y, w, 20),
            start_value=self.animation_speed,
            value_range=(0.5, 10.0),
            manager=self.ui_manager,
        )
        y += 40

        # Control Buttons
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(px, y, w, 35),
            text="Start Animation",
            manager=self.ui_manager,
        )
        y += 45

        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(px, y, w, 35),
            text="Reset",
            manager=self.ui_manager,
        )
        y += 50

        # Info box
        self.info_box = pygame_gui.elements.UITextBox(
            html_text=self._get_info_html(),
            relative_rect=pygame.Rect(px, y, w, WINDOW_HEIGHT - y - 20),
            manager=self.ui_manager,
        )

        # Set initial button states
        self._update_mode_buttons()
        self._update_layer_buttons()

    def _update_mode_buttons(self):
        """Update mode button appearance"""
        if self.mode == SEQUENTIAL_MODE:
            self.mode_sequential.disable()
            self.mode_parallel.enable()
        else:
            self.mode_sequential.enable()
            self.mode_parallel.disable()

    def _update_layer_buttons(self):
        """Enable/disable add/remove layer buttons based on constraints"""
        if len(self.layers) >= MAX_LAYERS:
            self.add_layer_button.disable()
        else:
            self.add_layer_button.enable()

        if len(self.layers) <= MIN_LAYERS:
            self.remove_layer_button.disable()
        else:
            self.remove_layer_button.enable()

    def _update_layer_controls(self):
        """Update all layer property controls to reflect current layer"""
        current_layer = self.layers[self.current_layer_index]

        # Update property label
        self.layer_properties_label.set_text(
            f"<b>Layer {self.current_layer_index + 1} Properties</b>"
        )

        # Update preset dropdown (if the preset exists in options)
        if current_layer.preset_name in LAYER_PRESETS:
            self.preset_dropdown.selected_option = current_layer.preset_name

        # Update tau sliders - IMPORTANT: set value_range BEFORE set_current_value
        self.tau_top_slider.set_current_value(current_layer.tau_top)

        # Update tau_bottom range and value
        new_bottom_range = (current_layer.tau_top + 0.1, 50.0)
        if self.tau_bottom_slider.value_range != new_bottom_range:
            self.tau_bottom_slider.value_range = new_bottom_range
            self.tau_bottom_slider.rebuild()
        self.tau_bottom_slider.set_current_value(current_layer.tau_bottom)

        # Update omega and g sliders
        self.omega_slider.set_current_value(current_layer.omega_0)
        self.g_slider.set_current_value(current_layer.g)

        # Update labels
        self.tau_top_label.set_text(f"Layer Top (τ): {current_layer.tau_top:.1f}")
        self.tau_bottom_label.set_text(
            f"Layer Bottom (τ): {current_layer.tau_bottom:.1f}"
        )
        self.omega_label.set_text(f"SSA (ω₀): {current_layer.omega_0:.2f}")
        self.g_label.set_text(f"Asymmetry (g): {current_layer.g:.2f}")

    def _on_layer_selected(self, selected_option: str):
        """Handle layer selection from dropdown"""
        # Extract layer index from "Layer N" string
        layer_num = int(selected_option.split()[1])
        self.current_layer_index = layer_num - 1

        # Update all controls to reflect the newly selected layer
        self._update_layer_controls()

    def _on_preset_selected(self, preset_name: str):
        """Handle preset selection - update current layer properties"""
        if preset_name not in LAYER_PRESETS:
            return

        preset = LAYER_PRESETS[preset_name]
        current_layer = self.layers[self.current_layer_index]

        # Update layer properties from preset
        # Note: We keep the current tau boundaries, only update optical properties
        current_layer.omega_0 = preset["omega_0"]
        current_layer.g = preset["g"]
        current_layer.preset_name = preset_name
        current_layer.color = preset["color"]

        # Update UI controls
        self._update_layer_controls()

    def _add_layer(self):
        """Add a new atmospheric layer"""
        if len(self.layers) >= MAX_LAYERS:
            return

        # New layer starts where the last layer ended
        last_layer = self.layers[-1]
        new_tau_top = last_layer.tau_bottom
        new_tau_bottom = new_tau_top + 1.0  # Default 1.0 optical depth thickness

        # Create new layer with default properties
        new_layer = AtmosphericLayer(
            tau_top=new_tau_top,
            tau_bottom=new_tau_bottom,
            omega_0=DEFAULT_OMEGA_0,
            g=DEFAULT_G,
            preset_name="Custom",
            color=LAYER_PRESETS["Custom"]["color"],
        )

        self.layers.append(new_layer)

        # Select the new layer BEFORE updating dropdown
        self.current_layer_index = len(self.layers) - 1

        # Update layer dropdown - rebuild it completely
        layer_options = [f"Layer {i + 1}" for i in range(len(self.layers))]
        self.layer_dropdown.kill()
        self.layer_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=layer_options,
            starting_option=layer_options[-1],
            relative_rect=pygame.Rect(
                SCENE_WIDTH + 20,
                90,  # Same position as original
                PANEL_WIDTH - 60,
                30,
            ),
            manager=self.ui_manager,
        )

        self._update_layer_controls()
        self._update_layer_buttons()

    def _remove_layer(self):
        """Remove the current atmospheric layer"""
        if len(self.layers) <= MIN_LAYERS:
            return

        # Remove current layer
        del self.layers[self.current_layer_index]

        # Adjust current layer index if needed
        if self.current_layer_index >= len(self.layers):
            self.current_layer_index = len(self.layers) - 1

        # Rebuild layer boundaries
        self._rebuild_layers()

        # Update layer dropdown - rebuild it completely
        layer_options = [f"Layer {i + 1}" for i in range(len(self.layers))]
        self.layer_dropdown.kill()
        self.layer_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=layer_options,
            starting_option=layer_options[self.current_layer_index],
            relative_rect=pygame.Rect(
                SCENE_WIDTH + 20,
                90,  # Same position as original
                PANEL_WIDTH - 60,
                30,
            ),
            manager=self.ui_manager,
        )

        # Update controls
        self._update_layer_controls()
        self._update_layer_buttons()

    def _rebuild_layers(self):
        """Reorganize layer boundaries to ensure they're contiguous"""
        if not self.layers:
            return

        # Ensure first layer starts at 0
        self.layers[0].tau_top = 0.0

        # Make each subsequent layer start where the previous one ended
        for i in range(1, len(self.layers)):
            self.layers[i].tau_top = self.layers[i - 1].tau_bottom

        # Update controls to reflect changes
        if hasattr(self, "tau_top_slider"):
            self._update_layer_controls()

    def _get_info_html(self):
        """Info text"""
        stats = self.simulation.stats

        if stats.total_launched == 0:
            return f"""
            <b>Mode: {self.mode.upper()}</b><br>
            <br>
            Click Start to begin
            """

        return f"""
        <b>Mode: {self.mode.upper()}</b><br>
        <br>
        Launched: {stats.total_launched}<br>
        Active: {stats.currently_moving}<br>
        Scatters: {stats.total_scatters}<br>
        <br>
        <b>Energy Budget:</b><br>
        R: {stats.reflectance:.1%}<br>
        T: {stats.transmittance:.1%}<br>
        A: {stats.absorptance:.1%}<br>
        Σ: {(stats.reflectance + stats.transmittance + stats.absorptance):.1%}
        """

    def _update_labels(self):
        """Update labels for current layer and global parameters"""
        current_layer = self.layers[self.current_layer_index]

        self.tau_top_label.set_text(f"Layer Top (τ): {current_layer.tau_top:.1f}")
        self.tau_bottom_label.set_text(
            f"Layer Bottom (τ): {current_layer.tau_bottom:.1f}"
        )
        self.omega_label.set_text(f"SSA (ω₀): {current_layer.omega_0:.2f}")
        self.g_label.set_text(f"Asymmetry (g): {current_layer.g:.2f}")
        self.albedo_label.set_text(f"Surface Albedo: {self.surface_albedo:.2f}")
        self.nphotons_label.set_text(f"Photons: {int(self.num_photons)}")
        self.speed_label.set_text(f"Speed: {self.animation_speed:.1f}x")

    def _draw_scene(self):
        """Draw main visualization"""
        self.screen.fill(COLOR_BG)

        # Draw animation area (left side, full height)
        self._draw_animation_area()

        # Draw profile plots (right side)
        self._draw_profile_plots()

        # Draw flux displays (bottom of animation area)
        self._draw_flux_displays()

        # Draw counters (bottom)
        self._draw_counters()

    def _draw_animation_area(self):
        """Draw photon animation with layer boundaries"""
        x = ANIM_MARGIN
        y = ANIM_MARGIN
        w = ANIM_WIDTH
        h = ANIM_HEIGHT
        tau_max = self.simulation.tau_max

        # Draw each layer with its specific color
        for layer in self.layers:
            layer_y_top = y + (layer.tau_top / tau_max) * h
            layer_y_bottom = y + (layer.tau_bottom / tau_max) * h
            layer_height = layer_y_bottom - layer_y_top

            # Draw layer background with its color
            s = pygame.Surface((w, int(layer_height)), pygame.SRCALPHA)
            s.fill(layer.color)
            self.screen.blit(s, (x, int(layer_y_top)))

        # Draw layer boundaries (except TOA and surface which are drawn separately)
        for i, layer in enumerate(self.layers):
            if i > 0:  # Don't draw TOA boundary here
                boundary_y = y + (layer.tau_top / tau_max) * h
                # Draw dashed line manually
                dash_length = 10
                gap_length = 5
                current_x = x
                while current_x < x + w:
                    end_x = min(current_x + dash_length, x + w)
                    pygame.draw.line(
                        self.screen,
                        (100, 100, 100),
                        (int(current_x), int(boundary_y)),
                        (int(end_x), int(boundary_y)),
                        2,
                    )
                    current_x += dash_length + gap_length
                # Layer boundary label
                boundary_text = self.font_small.render(
                    f"τ={layer.tau_top:.1f}", True, (80, 80, 80)
                )
                self.screen.blit(boundary_text, (x + w - 60, int(boundary_y) - 15))

        # TOA (top boundary)
        pygame.draw.line(self.screen, COLOR_TOA, (x, y), (x + w, y), 3)
        text = self.font_medium.render("τ=0 (TOA)", True, COLOR_TOA)
        self.screen.blit(text, (x + 10, y - 30))

        # Surface (bottom boundary)
        surf_y = y + h
        pygame.draw.line(self.screen, COLOR_SURFACE, (x, surf_y), (x + w, surf_y), 3)
        text = self.font_medium.render(
            f"τ={tau_max:.1f} (Surface, A={self.surface_albedo:.2f})",
            True,
            COLOR_SURFACE,
        )
        self.screen.blit(text, (x + 10, surf_y + 5))

        # Draw photons
        for photon in self.simulation.get_active_photons():
            py = y + (photon.tau / self.simulation.tau_max) * h
            px = x + photon.x_position

            if photon.state == PhotonState.SCATTERING:
                color = COLOR_SCATTER_EVENT
                radius = PHOTON_RADIUS + 2
            elif photon.state == PhotonState.ABSORBING:
                alpha = int(255 * (photon.absorption_timer / 15))
                color = (*COLOR_PHOTON_ABSORBED, alpha)
                radius = PHOTON_RADIUS
            elif photon.state == PhotonState.MOVING:
                color = (
                    COLOR_PHOTON_DOWN
                    if photon.direction == Direction.DOWN
                    else COLOR_PHOTON_UP
                )
                radius = PHOTON_RADIUS
            else:
                continue

            # Draw photon
            if len(color) == 4:
                surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (radius + 1, radius + 1), radius)
                self.screen.blit(surf, (int(px) - radius - 1, int(py) - radius - 1))
            else:
                pygame.draw.circle(self.screen, color, (int(px), int(py)), radius)

            # Arrow
            if photon.state == PhotonState.MOVING:
                anim_len = 6
                if photon.direction == Direction.DOWN:
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (int(px), int(py) - anim_len // 2),
                        (int(px), int(py) + anim_len // 2),
                        1,
                    )
                    pygame.draw.polygon(
                        self.screen,
                        (255, 255, 255),
                        [
                            (int(px), int(py) + anim_len // 2 + 2),
                            (int(px) - 2, int(py) + anim_len // 2 - 1),
                            (int(px) + 2, int(py) + anim_len // 2 - 1),
                        ],
                    )
                else:
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (int(px), int(py) - anim_len // 2),
                        (int(px), int(py) + anim_len // 2),
                        1,
                    )
                    pygame.draw.polygon(
                        self.screen,
                        (255, 255, 255),
                        [
                            (int(px), int(py) - anim_len // 2 - 2),
                            (int(px) - 2, int(py) - anim_len // 2 + 1),
                            (int(px) + 2, int(py) - anim_len // 2 + 1),
                        ],
                    )

    def _draw_profile_plots(self):
        """Draw scattering and absorption line plots"""
        stats = self.simulation.stats

        # Scattering plot (upper right)
        self._draw_line_plot(
            x=PLOT_X,
            y=SCATTER_PLOT_Y,
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT,
            data=stats.scattering_profile,
            color=(255, 100, 255),
            title="Scattering Events vs Depth",
            ylabel="Scatters",
        )

        # Absorption plot (lower right)
        self._draw_line_plot(
            x=PLOT_X,
            y=ABSORB_PLOT_Y,
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT,
            data=stats.absorption_profile,
            color=(220, 50, 50),
            title="Absorption Events vs Depth",
            ylabel="Absorptions",
        )

    def _draw_line_plot(self, x, y, width, height, data, color, title, ylabel):
        """Draw a line plot with axes"""
        # Background
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height))
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, width, height), 2)

        # Title
        text = self.font_medium.render(title, True, (50, 50, 50))
        text_rect = text.get_rect(center=(x + width // 2, y - 20))
        self.screen.blit(text, text_rect)

        if sum(data) == 0:
            # No data
            no_data = self.font_small.render("No data yet", True, (150, 150, 150))
            text_rect = no_data.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(no_data, text_rect)
            return

        # Plot data
        max_val = max(data) if data else 1
        bin_height = height / len(data)

        # Draw line
        points = []
        for i, count in enumerate(data):
            plot_y = y + i * bin_height + bin_height / 2
            plot_x = x + (count / max_val) * (width - 40) + 20
            points.append((plot_x, plot_y))

        if len(points) > 1:
            pygame.draw.lines(self.screen, color, False, points, 2)

        # Draw points
        for pt in points:
            pygame.draw.circle(self.screen, color, (int(pt[0]), int(pt[1])), 3)

        # Y-axis label (depth)
        depth_labels = [0, self.simulation.tau_max / 2, self.simulation.tau_max]
        for i, depth in enumerate(depth_labels):
            label_y = y + i * (height / 2)
            text = self.font_small.render(f"τ={depth:.1f}", True, (100, 100, 100))
            self.screen.blit(text, (x - 35, label_y - 8))

        # X-axis label (max value)
        max_text = self.font_small.render(f"max: {max(data)}", True, (100, 100, 100))
        self.screen.blit(max_text, (x + width - 60, y + height + 5))

    def _draw_flux_displays(self):
        """Draw incident, reflected, and transmitted flux values"""
        stats = self.simulation.stats

        # Calculate fluxes based on photon fractions
        incident_flux = SOLAR_CONSTANT
        reflected_flux = incident_flux * stats.reflectance
        transmitted_flux = incident_flux * stats.transmittance

        # Position below animation area
        y_pos = ANIM_MARGIN + ANIM_HEIGHT + 50
        x_start = ANIM_MARGIN
        spacing = ANIM_WIDTH // 3

        # Incident flux (TOA)
        self._draw_flux_value(
            x_start + spacing // 2, y_pos, incident_flux, "Incident F↓", (255, 200, 0)
        )

        # Reflected flux
        self._draw_flux_value(
            x_start + spacing + spacing // 2,
            y_pos,
            reflected_flux,
            "Reflected F↑",
            (0, 150, 255),
        )

        # Transmitted flux
        self._draw_flux_value(
            x_start + 2 * spacing + spacing // 2,
            y_pos,
            transmitted_flux,
            "Transmitted F↓",
            (255, 150, 0),
        )

    def _draw_flux_value(self, x, y, flux, label, color):
        """Draw a single flux value with label"""
        # Value
        flux_text = self.font_flux.render(f"{flux:.0f}", True, color)
        flux_rect = flux_text.get_rect(center=(x, y))
        self.screen.blit(flux_text, flux_rect)

        # Label
        label_text = self.font_small.render(label, True, (100, 100, 100))
        label_rect = label_text.get_rect(center=(x, y + 30))
        self.screen.blit(label_text, label_rect)

        # Units
        units_text = self.font_small.render("W/m²", True, (150, 150, 150))
        units_rect = units_text.get_rect(center=(x, y + 48))
        self.screen.blit(units_text, units_rect)

    def _draw_counters(self):
        """Draw large counters"""
        stats = self.simulation.stats

        cy = WINDOW_HEIGHT - 60
        spacing = SCENE_WIDTH // 3

        # Reflected
        self._draw_counter(
            spacing // 2, cy, stats.reflected, "REFLECTED", (0, 120, 255)
        )

        # Transmitted
        self._draw_counter(
            SCENE_WIDTH // 2, cy, stats.transmitted, "TRANSMITTED", (255, 150, 0)
        )

        # Absorbed
        self._draw_counter(
            SCENE_WIDTH - spacing // 2, cy, stats.absorbed, "ABSORBED", (220, 50, 50)
        )

    def _draw_counter(self, x, y, value, label, color):
        """Draw counter"""
        val_text = self.font_huge.render(str(value), True, color)
        val_rect = val_text.get_rect(center=(x, y - 10))
        self.screen.blit(val_text, val_rect)

        lab_text = self.font_small.render(label, True, (100, 100, 100))
        lab_rect = lab_text.get_rect(center=(x, y + 25))
        self.screen.blit(lab_text, lab_rect)

    def _draw_panel(self):
        """Draw control panel"""
        pygame.draw.rect(
            self.screen, COLOR_PANEL, (SCENE_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        )
        pygame.draw.line(
            self.screen,
            (200, 200, 200),
            (SCENE_WIDTH, 0),
            (SCENE_WIDTH, WINDOW_HEIGHT),
            2,
        )

    def _handle_events(self):
        """Handle events"""
        time_delta = self.clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                current_layer = self.layers[self.current_layer_index]

                if event.ui_element == self.tau_top_slider:
                    current_layer.tau_top = event.value
                    # Ensure bottom is always > top
                    if current_layer.tau_bottom <= current_layer.tau_top:
                        current_layer.tau_bottom = current_layer.tau_top + 0.1
                        self.tau_bottom_slider.set_current_value(
                            current_layer.tau_bottom
                        )
                    # Update tau_bottom slider range
                    self.tau_bottom_slider.value_range = (
                        current_layer.tau_top + 0.1,
                        50.0,
                    )
                    self._rebuild_layers()
                elif event.ui_element == self.tau_bottom_slider:
                    current_layer.tau_bottom = event.value
                    self._rebuild_layers()
                elif event.ui_element == self.omega_slider:
                    current_layer.omega_0 = event.value
                    current_layer.preset_name = "Custom"  # Mark as custom
                elif event.ui_element == self.g_slider:
                    current_layer.g = event.value
                    current_layer.preset_name = "Custom"  # Mark as custom
                elif event.ui_element == self.albedo_slider:
                    self.surface_albedo = event.value
                elif event.ui_element == self.nphotons_slider:
                    self.num_photons = int(event.value)
                elif event.ui_element == self.speed_slider:
                    self.animation_speed = event.value

                self._update_labels()

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.start_button:
                    self._start_simulation()
                elif event.ui_element == self.reset_button:
                    self._reset_simulation()
                elif event.ui_element == self.mode_sequential:
                    self.mode = SEQUENTIAL_MODE
                    self._update_mode_buttons()
                elif event.ui_element == self.mode_parallel:
                    self.mode = PARALLEL_MODE
                    self._update_mode_buttons()
                elif event.ui_element == self.add_layer_button:
                    self._add_layer()
                elif event.ui_element == self.remove_layer_button:
                    self._remove_layer()

            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.layer_dropdown:
                    self._on_layer_selected(event.text)
                elif event.ui_element == self.preset_dropdown:
                    self._on_preset_selected(event.text)

            self.ui_manager.process_events(event)

        self.ui_manager.update(time_delta)

    def _start_simulation(self):
        """Start simulation with current multi-layer configuration"""
        self.simulation.reset(
            layers=self.layers,
            surface_albedo=self.surface_albedo,
            num_photons=int(self.num_photons),
            mode=self.mode,
        )
        self.sim_running = True
        self.start_button.set_text("Running...")
        self.start_button.disable()

    def _reset_simulation(self):
        """Reset simulation with current multi-layer configuration"""
        self.simulation.reset(
            layers=self.layers,
            surface_albedo=self.surface_albedo,
            num_photons=int(self.num_photons),
            mode=self.mode,
        )
        self.sim_running = False
        self.start_button.set_text("Start Animation")
        self.start_button.enable()
        self.info_box.html_text = self._get_info_html()
        self.info_box.rebuild()

    def run(self):
        """Main loop"""
        while self.running:
            self._handle_events()

            if self.sim_running:
                self.simulation.update(self.animation_speed)

                # Update info periodically
                if pygame.time.get_ticks() % 500 < 20:
                    self.info_box.html_text = self._get_info_html()
                    self.info_box.rebuild()

                # Check completion
                if (
                    self.simulation.is_complete()
                    and self.simulation.stats.currently_moving == 0
                ):
                    self.sim_running = False
                    self.start_button.set_text("Start Animation")
                    self.start_button.enable()

            # Draw
            self._draw_scene()
            self._draw_panel()
            self.ui_manager.draw_ui(self.screen)

            pygame.display.flip()

        pygame.quit()


def main():
    app = FinalPhotonDemo()
    app.run()


if __name__ == "__main__":
    main()
