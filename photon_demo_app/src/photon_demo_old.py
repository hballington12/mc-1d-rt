"""
Real-Time Photon Animation Demo
Educational visualization of atmospheric radiative transfer
Students watch photons move, scatter, and absorb in real-time!
"""

import pygame
import pygame_gui
import numpy as np

from config import *
from photon_animation import PhotonSimulation, PhotonState, Direction


class PhotonDemoApp:
    """Main application for real-time photon animation"""

    def __init__(self):
        pygame.init()

        # Create window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Real-Time Photon Animation - 2-Stream RT Demo")

        # UI manager
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Clock
        self.clock = pygame.time.Clock()
        self.running = True

        # Parameters
        self.tau_max = DEFAULT_TAU_MAX
        self.omega_0 = DEFAULT_OMEGA_0
        self.num_photons = DEFAULT_NUM_PHOTONS
        self.animation_speed = PHOTON_SPEED

        # Simulation
        self.simulation = PhotonSimulation(
            tau_max=self.tau_max,
            omega_0=self.omega_0,
            num_photons=self.num_photons,
            scene_width=ANIM_WIDTH,
        )

        # Animation area coordinates
        self.anim_x = ANIM_MARGIN
        self.anim_y = ANIM_MARGIN

        # Fonts
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        # Create UI
        self._create_ui()

        # Simulation running
        self.sim_running = False

    def _create_ui(self):
        """Create control panel UI"""
        panel_x = SCENE_WIDTH + 20
        y_offset = 20
        slider_width = PANEL_WIDTH - 60

        # Title
        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 40),
            text="<b>Photon Animation Demo</b>",
            manager=self.ui_manager,
        )
        y_offset += 50

        # Optical depth slider
        self.tau_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Optical Depth (τ): {self.tau_max:.1f}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.tau_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.tau_max,
            value_range=(0.5, 10.0),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Single scattering albedo slider
        self.omega_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Scattering Prob (ω₀): {self.omega_0:.2f}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.omega_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.omega_0,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Number of photons slider
        self.nphotons_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Number of Photons: {self.num_photons}",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.nphotons_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.num_photons,
            value_range=(MIN_PHOTONS, MAX_PHOTONS),
            manager=self.ui_manager,
        )
        y_offset += 45

        # Animation speed slider
        self.speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            text=f"Animation Speed: {self.animation_speed:.1f}x",
            manager=self.ui_manager,
        )
        y_offset += 30

        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 25),
            start_value=self.animation_speed,
            value_range=(0.5, 10.0),
            manager=self.ui_manager,
        )
        y_offset += 50

        # Start button
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 40),
            text="Start Animation",
            manager=self.ui_manager,
        )
        y_offset += 50

        # Reset button
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 40),
            text="Reset",
            manager=self.ui_manager,
        )
        y_offset += 60

        # Statistics text box
        self.stats_box = pygame_gui.elements.UITextBox(
            html_text="<b>Statistics:</b><br>Press Start to begin",
            relative_rect=pygame.Rect(panel_x, y_offset, slider_width, 300),
            manager=self.ui_manager,
        )

    def _update_labels(self):
        """Update slider labels"""
        self.tau_label.set_text(f"Optical Depth (τ): {self.tau_max:.1f}")
        self.omega_label.set_text(f"Scattering Prob (ω₀): {self.omega_0:.2f}")
        self.nphotons_label.set_text(f"Number of Photons: {int(self.num_photons)}")
        self.speed_label.set_text(f"Animation Speed: {self.animation_speed:.1f}x")

    def _update_stats_display(self):
        """Update statistics display"""
        stats = self.simulation.stats

        if stats.total_launched == 0:
            html = "<b>Statistics:</b><br>No photons launched yet"
        else:
            html = f"""
            <b>Statistics:</b><br>
            <br>
            Launched: {stats.total_launched}<br>
            Completed: {stats.completed}<br>
            Moving: {stats.currently_moving}<br>
            <br>
            <b>Outcomes:</b><br>
            Reflected: {stats.reflected} ({stats.reflectance:.1%})<br>
            Transmitted: {stats.transmitted} ({stats.transmittance:.1%})<br>
            Absorbed: {stats.absorbed} ({stats.absorptance:.1%})<br>
            <br>
            <b>Total: {(stats.reflectance + stats.transmittance + stats.absorptance):.1%}</b>
            """

        self.stats_box.html_text = html
        self.stats_box.rebuild()

    def _draw_scene(self):
        """Draw main animation area"""
        # Background
        self.screen.fill(COLOR_BG)

        # Animation area background
        anim_rect = pygame.Rect(self.anim_x, self.anim_y, ANIM_WIDTH, ANIM_HEIGHT)
        s = pygame.Surface((ANIM_WIDTH, ANIM_HEIGHT), pygame.SRCALPHA)
        s.fill(COLOR_ATMOSPHERE)
        self.screen.blit(s, (self.anim_x, self.anim_y))

        # TOA line
        pygame.draw.line(
            self.screen,
            COLOR_TOA,
            (self.anim_x, self.anim_y),
            (self.anim_x + ANIM_WIDTH, self.anim_y),
            3,
        )

        # Surface line
        surface_y = self.anim_y + ANIM_HEIGHT
        pygame.draw.line(
            self.screen,
            COLOR_SURFACE,
            (self.anim_x, surface_y),
            (self.anim_x + ANIM_WIDTH, surface_y),
            3,
        )

        # Labels
        toa_text = self.font_medium.render("Top of Atmosphere (τ=0)", True, COLOR_TOA)
        self.screen.blit(toa_text, (self.anim_x + 10, self.anim_y - 30))

        surface_text = self.font_medium.render(
            f"Surface (τ={self.tau_max:.1f})", True, COLOR_SURFACE
        )
        self.screen.blit(surface_text, (self.anim_x + 10, surface_y + 5))

        # Draw photons
        self._draw_photons()

        # Draw absorption profile
        self._draw_absorption_profile()

    def _draw_photons(self):
        """Draw all animated photons"""
        for photon in self.simulation.get_active_photons():
            # Convert optical depth to y-coordinate
            y = self.anim_y + (photon.tau / self.tau_max) * ANIM_HEIGHT
            x = self.anim_x + photon.x_position

            # Choose color based on state
            if photon.state == PhotonState.SCATTERING:
                # Flashing magenta for scatter event
                color = COLOR_SCATTER_EVENT
                radius = PHOTON_RADIUS + 2
            elif photon.state == PhotonState.ABSORBING:
                # Fading red for absorption
                alpha = int(255 * (photon.absorption_timer / 15))
                color = (*COLOR_PHOTON_ABSORBED, alpha)
                radius = PHOTON_RADIUS
            elif photon.state == PhotonState.MOVING:
                # Color by direction
                if photon.direction == Direction.DOWN:
                    color = COLOR_PHOTON_DOWN
                else:
                    color = COLOR_PHOTON_UP
                radius = PHOTON_RADIUS
            else:
                continue  # Skip completed photons

            # Draw photon
            if len(color) == 4:  # Has alpha
                s = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (radius + 1, radius + 1), radius)
                self.screen.blit(s, (int(x) - radius - 1, int(y) - radius - 1))
            else:
                pygame.draw.circle(self.screen, color, (int(x), int(y)), radius)

            # Draw small arrow for direction
            if photon.state == PhotonState.MOVING:
                arrow_len = 8
                if photon.direction == Direction.DOWN:
                    # Downward arrow
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (int(x), int(y) - arrow_len // 2),
                        (int(x), int(y) + arrow_len // 2),
                        2,
                    )
                    pygame.draw.polygon(
                        self.screen,
                        (255, 255, 255),
                        [
                            (int(x), int(y) + arrow_len // 2 + 3),
                            (int(x) - 3, int(y) + arrow_len // 2 - 2),
                            (int(x) + 3, int(y) + arrow_len // 2 - 2),
                        ],
                    )
                else:
                    # Upward arrow
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (int(x), int(y) - arrow_len // 2),
                        (int(x), int(y) + arrow_len // 2),
                        2,
                    )
                    pygame.draw.polygon(
                        self.screen,
                        (255, 255, 255),
                        [
                            (int(x), int(y) - arrow_len // 2 - 3),
                            (int(x) - 3, int(y) - arrow_len // 2 + 2),
                            (int(x) + 3, int(y) - arrow_len // 2 + 2),
                        ],
                    )

    def _draw_absorption_profile(self):
        """Draw histogram of where photons are absorbed"""
        stats = self.simulation.stats

        if sum(stats.absorption_profile) == 0:
            return

        # Draw on right side of animation area
        profile_x = self.anim_x + ANIM_WIDTH + 10
        profile_width = 30
        bin_height = ANIM_HEIGHT / len(stats.absorption_profile)

        max_count = max(stats.absorption_profile) if stats.absorption_profile else 1

        for i, count in enumerate(stats.absorption_profile):
            if count > 0:
                y = self.anim_y + i * bin_height
                bar_width = (count / max_count) * profile_width

                pygame.draw.rect(
                    self.screen,
                    (200, 50, 50, 180),
                    (profile_x, y, bar_width, bin_height - 1),
                )

        # Label
        label = self.font_small.render("Absorption", True, (100, 100, 100))
        self.screen.blit(label, (profile_x, self.anim_y - 20))

    def _draw_panel(self):
        """Draw control panel background"""
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
                if event.ui_element == self.tau_slider:
                    self.tau_max = event.value
                elif event.ui_element == self.omega_slider:
                    self.omega_0 = event.value
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

            self.ui_manager.process_events(event)

        self.ui_manager.update(time_delta)

    def _start_simulation(self):
        """Start the animation"""
        self.simulation.reset(self.tau_max, self.omega_0, int(self.num_photons))
        self.sim_running = True
        self.start_button.set_text("Running...")
        self.start_button.disable()

    def _reset_simulation(self):
        """Reset the simulation"""
        self.simulation.reset(self.tau_max, self.omega_0, int(self.num_photons))
        self.sim_running = False
        self.start_button.set_text("Start Animation")
        self.start_button.enable()
        self._update_stats_display()

    def run(self):
        """Main application loop"""
        while self.running:
            self._handle_events()

            # Update simulation if running
            if self.sim_running:
                self.simulation.update(self.animation_speed)
                self._update_stats_display()

                # Check if complete
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
    """Entry point"""
    app = PhotonDemoApp()
    app.run()


if __name__ == "__main__":
    main()
