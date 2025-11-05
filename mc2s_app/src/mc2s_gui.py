"""
Monte Carlo 2-Stream Radiative Transfer GUI Application
Interactive educational demo for atmospheric physics students
"""

import pygame
import pygame_gui
import numpy as np
from typing import List, Dict
import threading

from config import *
from physics import Atmosphere, run_simulation, Outcome


class MC2SApp:
    """Main application class for Monte Carlo 2-Stream RT Demo"""

    def __init__(self):
        pygame.init()

        # Create window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Monte Carlo 2-Stream Radiative Transfer Demo")

        # Create UI manager
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize parameters
        self.atm_params = {
            "tau_max": 2.0,
            "omega_0": 0.9,
            "g": 0.5,
            "surface_albedo": 0.2,
            "solar_zenith": 30.0,
            "num_photons": 5000,
            "preset": AtmospherePreset.CUSTOM,
        }

        # Simulation results
        self.results = None
        self.simulation_running = False

        # Create UI elements
        self._create_ui()

        # Run initial simulation
        self._run_simulation()

    def _create_ui(self):
        """Create all UI controls in the right panel"""
        panel_x = SCENE_WIDTH + 20
        y_offset = 20
        slider_width = PANEL_WIDTH - 60

        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, PANEL_WIDTH - 40, 40),
            text="Atmospheric Parameters",
            manager=self.ui_manager,
        )
        y_offset += 50

        # Preset dropdown
        self.preset_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 150, 25),
            text="Preset:",
            manager=self.ui_manager,
        )

        preset_options = [preset.value for preset in AtmospherePreset]
        self.preset_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=preset_options,
            starting_option=AtmospherePreset.CUSTOM.value,
            relative_rect=pygame.Rect(panel_x + 160, y_offset, 200, 30),
            manager=self.ui_manager,
        )
        y_offset += 50

        # Optical Depth slider
        self.tau_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Optical Depth (τ): {self.atm_params['tau_max']:.2f}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.tau_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.atm_params["tau_max"],
            value_range=(0.1, 30.0),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Single Scattering Albedo slider
        self.omega_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Single Scatter Albedo (ω₀): {self.atm_params['omega_0']:.3f}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.omega_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.atm_params["omega_0"],
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Asymmetry parameter slider
        self.g_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Asymmetry (g): {self.atm_params['g']:.2f}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.g_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.atm_params["g"],
            value_range=(-1.0, 1.0),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Surface albedo slider
        self.albedo_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Surface Albedo: {self.atm_params['surface_albedo']:.2f}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.albedo_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.atm_params["surface_albedo"],
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Solar zenith angle slider
        self.zenith_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Solar Zenith Angle: {self.atm_params['solar_zenith']:.1f}°",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.zenith_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.atm_params["solar_zenith"],
            value_range=(0.0, 85.0),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Number of photons slider
        self.nphotons_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Number of Photons: {self.atm_params['num_photons']}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.nphotons_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.atm_params["num_photons"],
            value_range=(100, MAX_PHOTONS),
            manager=self.ui_manager,
        )
        y_offset += 60

        # Run button
        self.run_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 40),
            text="Run Simulation",
            manager=self.ui_manager,
        )
        y_offset += 60

        # Results display
        self.results_label = pygame_gui.elements.UITextBox(
            html_text="<font size=4><b>Results:</b></font><br>Run simulation to see results",
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 200),
            manager=self.ui_manager,
        )

    def _update_labels(self):
        """Update all label texts with current parameter values"""
        self.tau_label.set_text(f"Optical Depth (τ): {self.atm_params['tau_max']:.2f}")
        self.omega_label.set_text(
            f"Single Scatter Albedo (ω₀): {self.atm_params['omega_0']:.3f}"
        )
        self.g_label.set_text(f"Asymmetry (g): {self.atm_params['g']:.2f}")
        self.albedo_label.set_text(
            f"Surface Albedo: {self.atm_params['surface_albedo']:.2f}"
        )
        self.zenith_label.set_text(
            f"Solar Zenith Angle: {self.atm_params['solar_zenith']:.1f}°"
        )
        self.nphotons_label.set_text(
            f"Number of Photons: {int(self.atm_params['num_photons'])}"
        )

    def _apply_preset(self, preset: AtmospherePreset):
        """Apply a preset atmospheric configuration"""
        if preset == AtmospherePreset.CUSTOM:
            return

        config = ATMOSPHERE_PRESETS[preset]
        self.atm_params["tau_max"] = config.tau_max
        self.atm_params["omega_0"] = config.omega_0
        self.atm_params["g"] = config.g
        self.atm_params["surface_albedo"] = config.surface_albedo
        self.atm_params["solar_zenith"] = config.solar_zenith

        # Update sliders
        self.tau_slider.set_current_value(config.tau_max)
        self.omega_slider.set_current_value(config.omega_0)
        self.g_slider.set_current_value(config.g)
        self.albedo_slider.set_current_value(config.surface_albedo)
        self.zenith_slider.set_current_value(config.solar_zenith)

        self._update_labels()
        self._run_simulation()

    def _run_simulation(self):
        """Run Monte Carlo simulation in background thread"""
        if self.simulation_running:
            return

        self.simulation_running = True
        self.run_button.set_text("Running...")
        self.run_button.disable()

        # Create atmosphere
        atmosphere = Atmosphere(
            tau_max=self.atm_params["tau_max"],
            omega_0=self.atm_params["omega_0"],
            g=self.atm_params["g"],
            surface_albedo=self.atm_params["surface_albedo"],
        )

        # Run simulation in thread
        def run():
            self.results = run_simulation(
                atmosphere, int(self.atm_params["num_photons"]), WEIGHT_THRESHOLD
            )
            self.simulation_running = False
            self.run_button.set_text("Run Simulation")
            self.run_button.enable()
            self._update_results_display()

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def _update_results_display(self):
        """Update results text box with simulation outcomes"""
        if self.results is None:
            return

        r = self.results
        html = f"""
        <font size=4><b>Results:</b></font><br>
        <font size=3>
        Photons simulated: {r["num_photons"]}<br>
        <br>
        <b>Energy Budget:</b><br>
        Reflectance: {r["reflectance"]:.1%}<br>
        Transmittance: {r["transmittance"]:.1%}<br>
        Absorptance: {r["absorptance"]:.1%}<br>
        <br>
        Total: {(r["reflectance"] + r["transmittance"] + r["absorptance"]):.1%}<br>
        <br>
        <b>Absolute Energy:</b><br>
        Reflected: {r["energy_reflected"]:.1f}<br>
        Transmitted: {r["energy_transmitted"]:.1f}<br>
        Absorbed: {r["energy_absorbed"]:.1f}<br>
        </font>
        """
        self.results_label.html_text = html
        self.results_label.rebuild()

    def _draw_scene(self):
        """Draw the main visualization area"""
        # Clear scene area
        pygame.draw.rect(self.screen, COLOR_BG, (0, 0, SCENE_WIDTH, WINDOW_HEIGHT))

        # Draw atmosphere bounds
        margin = 50
        viz_width = SCENE_WIDTH - 2 * margin
        viz_height = WINDOW_HEIGHT - 2 * margin

        # TOA line
        toa_y = margin
        pygame.draw.line(
            self.screen, COLOR_TOA, (margin, toa_y), (SCENE_WIDTH - margin, toa_y), 3
        )

        # Surface line
        surface_y = margin + viz_height
        pygame.draw.line(
            self.screen,
            COLOR_SURFACE,
            (margin, surface_y),
            (SCENE_WIDTH - margin, surface_y),
            3,
        )

        # Atmosphere background
        atm_rect = pygame.Rect(margin, toa_y, viz_width, viz_height)
        s = pygame.Surface((viz_width, viz_height), pygame.SRCALPHA)
        s.fill(COLOR_ATMOSPHERE)
        self.screen.blit(s, (margin, toa_y))

        # Labels
        font = pygame.font.Font(None, 24)
        toa_text = font.render("Top of Atmosphere (τ=0)", True, COLOR_TOA)
        self.screen.blit(toa_text, (margin + 10, toa_y - 30))

        tau_text = f"τ = {self.atm_params['tau_max']:.1f}"
        surface_text = font.render(f"Surface ({tau_text})", True, COLOR_SURFACE)
        self.screen.blit(surface_text, (margin + 10, surface_y + 10))

        # Draw photon paths if available
        if self.results and "sample_paths" in self.results:
            self._draw_photon_paths(margin, toa_y, viz_width, viz_height)

        # Draw energy bars
        if self.results:
            self._draw_energy_bars(margin, toa_y, viz_width, viz_height)

    def _draw_photon_paths(self, x_offset, y_offset, width, height):
        """Draw sample photon trajectories"""
        if (
            not self.results
            or "sample_paths" in self.results
            and len(self.results["sample_paths"]) == 0
        ):
            return

        tau_max = self.atm_params["tau_max"]

        for i, path_data in enumerate(
            self.results["sample_paths"][:MAX_PHOTON_PATHS_DISPLAY]
        ):
            path = path_data["path"]
            outcome = path_data["outcome"]

            # Color based on outcome
            if outcome == Outcome.REFLECTED:
                color = (0, 150, 255, 100)  # Blue
            elif outcome == Outcome.TRANSMITTED:
                color = (255, 150, 0, 100)  # Orange
            else:
                color = (150, 150, 150, 80)  # Gray

            # Draw path
            if len(path) > 1:
                points = []
                for j, tau in enumerate(path):
                    # Convert optical depth to y-coordinate
                    y = y_offset + (tau / tau_max) * height
                    # Stagger x positions slightly for visibility
                    x = x_offset + (i % 10) * (width / 10) + width / 20
                    points.append((x, y))

                # Draw semi-transparent line
                if len(points) >= 2:
                    pygame.draw.lines(self.screen, color[:3], False, points, 1)

    def _draw_energy_bars(self, x_offset, y_offset, width, height):
        """Draw energy budget bars on the side"""
        if not self.results:
            return

        bar_width = 40
        bar_x = x_offset + width + 20
        bar_height = height

        r = self.results

        # Reflected (top)
        refl_height = int(r["reflectance"] * bar_height)
        pygame.draw.rect(
            self.screen, (0, 120, 255), (bar_x, y_offset, bar_width, refl_height)
        )

        # Absorbed (middle)
        abs_height = int(r["absorptance"] * bar_height)
        pygame.draw.rect(
            self.screen,
            (200, 0, 0),
            (bar_x, y_offset + refl_height, bar_width, abs_height),
        )

        # Transmitted (bottom)
        trans_height = int(r["transmittance"] * bar_height)
        pygame.draw.rect(
            self.screen,
            (255, 150, 0),
            (bar_x, y_offset + refl_height + abs_height, bar_width, trans_height),
        )

        # Labels
        font = pygame.font.Font(None, 18)

        if refl_height > 20:
            refl_text = font.render(f"{r['reflectance']:.0%}", True, (255, 255, 255))
            self.screen.blit(refl_text, (bar_x + 5, y_offset + refl_height // 2 - 10))

        if abs_height > 20:
            abs_text = font.render(f"{r['absorptance']:.0%}", True, (255, 255, 255))
            self.screen.blit(
                abs_text, (bar_x + 5, y_offset + refl_height + abs_height // 2 - 10)
            )

        if trans_height > 20:
            trans_text = font.render(f"{r['transmittance']:.0%}", True, (0, 0, 0))
            self.screen.blit(
                trans_text,
                (
                    bar_x + 5,
                    y_offset + refl_height + abs_height + trans_height // 2 - 10,
                ),
            )

    def _draw_panel(self):
        """Draw the control panel background"""
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
        """Handle pygame and UI events"""
        time_delta = self.clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Handle UI events
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.tau_slider:
                    self.atm_params["tau_max"] = event.value
                    self.atm_params["preset"] = AtmospherePreset.CUSTOM
                elif event.ui_element == self.omega_slider:
                    self.atm_params["omega_0"] = event.value
                    self.atm_params["preset"] = AtmospherePreset.CUSTOM
                elif event.ui_element == self.g_slider:
                    self.atm_params["g"] = event.value
                    self.atm_params["preset"] = AtmospherePreset.CUSTOM
                elif event.ui_element == self.albedo_slider:
                    self.atm_params["surface_albedo"] = event.value
                    self.atm_params["preset"] = AtmospherePreset.CUSTOM
                elif event.ui_element == self.zenith_slider:
                    self.atm_params["solar_zenith"] = event.value
                    self.atm_params["preset"] = AtmospherePreset.CUSTOM
                elif event.ui_element == self.nphotons_slider:
                    self.atm_params["num_photons"] = int(event.value)

                self._update_labels()

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.run_button:
                    self._run_simulation()

            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.preset_dropdown:
                    # Find matching preset
                    for preset in AtmospherePreset:
                        if preset.value == event.text:
                            self._apply_preset(preset)
                            break

            self.ui_manager.process_events(event)

        self.ui_manager.update(time_delta)

    def run(self):
        """Main application loop"""
        while self.running:
            self._handle_events()

            # Draw everything
            self._draw_scene()
            self._draw_panel()
            self.ui_manager.draw_ui(self.screen)

            pygame.display.flip()

        pygame.quit()


def main():
    """Entry point for the application"""
    app = MC2SApp()
    app.run()


if __name__ == "__main__":
    main()
