"""
Real-Time Photon Animation Demo - Enhanced Version
Beautiful visualization with scattering/absorption profiles and live counters
"""

import pygame
import pygame_gui
import numpy as np

from config import *
from photon_animation import PhotonSimulation, PhotonState, Direction


class EnhancedPhotonDemo:
    """Enhanced photon demo with improved layout and visualizations"""

    def __init__(self):
        pygame.init()

        # Window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Real-Time Photon Animation - Enhanced")

        # UI
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
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
            scene_width=PHOTON_AREA_WIDTH,
        )

        # Layout coordinates
        self.photon_area_x = ANIM_MARGIN_LEFT + PROFILE_WIDTH + 20
        self.scatter_profile_x = ANIM_MARGIN_LEFT
        self.absorb_profile_x = self.photon_area_x + PHOTON_AREA_WIDTH + 20
        self.anim_y = ANIM_MARGIN_TOP

        # Fonts
        self.font_huge = pygame.font.Font(None, COUNTER_FONT_SIZE)
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        # Create UI
        self._create_ui()

        # State
        self.sim_running = False

    def _create_ui(self):
        """Create control panel"""
        panel_x = SCENE_WIDTH + 20
        y = 20
        w = PANEL_WIDTH - 60

        # Title
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y, w, 30),
            text="<b>Enhanced Photon Demo</b>",
            manager=self.ui_manager,
        )
        y += 40

        # Optical depth
        self.tau_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            text=f"Optical Depth (τ): {self.tau_max:.1f}",
            manager=self.ui_manager,
        )
        y += 30

        self.tau_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            start_value=self.tau_max,
            value_range=(0.5, 10.0),
            manager=self.ui_manager,
        )
        y += 40

        # Scattering probability
        self.omega_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            text=f"Scattering Prob (ω₀): {self.omega_0:.2f}",
            manager=self.ui_manager,
        )
        y += 30

        self.omega_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            start_value=self.omega_0,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
        )
        y += 40

        # Number of photons
        self.nphotons_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            text=f"Photons: {int(self.num_photons)}",
            manager=self.ui_manager,
        )
        y += 30

        self.nphotons_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            start_value=self.num_photons,
            value_range=(MIN_PHOTONS, MAX_PHOTONS),
            manager=self.ui_manager,
        )
        y += 40

        # Animation speed
        self.speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            text=f"Speed: {self.animation_speed:.1f}x",
            manager=self.ui_manager,
        )
        y += 30

        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y, w, 25),
            start_value=self.animation_speed,
            value_range=(0.5, 10.0),
            manager=self.ui_manager,
        )
        y += 50

        # Buttons
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y, w, 40),
            text="Start Animation",
            manager=self.ui_manager,
        )
        y += 50

        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y, w, 40),
            text="Reset",
            manager=self.ui_manager,
        )
        y += 60

        # Info box
        self.info_box = pygame_gui.elements.UITextBox(
            html_text=self._get_info_html(),
            relative_rect=pygame.Rect(panel_x, y, w, WINDOW_HEIGHT - y - 20),
            manager=self.ui_manager,
        )

    def _get_info_html(self):
        """Generate info HTML"""
        stats = self.simulation.stats

        if stats.total_launched == 0:
            return "<b>Instructions:</b><br>Click Start to begin animation"

        return f"""
        <b>Statistics:</b><br>
        Launched: {stats.total_launched}<br>
        Active: {stats.currently_moving}<br>
        Scatters: {stats.total_scatters}<br>
        <br>
        <b>Energy:</b><br>
        R: {stats.reflectance:.1%}<br>
        T: {stats.transmittance:.1%}<br>
        A: {stats.absorptance:.1%}<br>
        Σ: {(stats.reflectance + stats.transmittance + stats.absorptance):.1%}
        """

    def _update_labels(self):
        """Update labels"""
        self.tau_label.set_text(f"Optical Depth (τ): {self.tau_max:.1f}")
        self.omega_label.set_text(f"Scattering Prob (ω₀): {self.omega_0:.2f}")
        self.nphotons_label.set_text(f"Photons: {int(self.num_photons)}")
        self.speed_label.set_text(f"Speed: {self.animation_speed:.1f}x")

    def _draw_scene(self):
        """Draw main visualization"""
        self.screen.fill(COLOR_BG)

        # Draw three columns: scatter profile | photon area | absorption profile
        self._draw_profiles()
        self._draw_photon_area()
        self._draw_counters()

    def _draw_profiles(self):
        """Draw scattering and absorption profile histograms"""
        stats = self.simulation.stats

        # Scattering profile (left)
        self._draw_profile_histogram(
            x=self.scatter_profile_x,
            y=self.anim_y,
            width=PROFILE_WIDTH,
            height=ANIM_HEIGHT,
            data=stats.scattering_profile,
            color=(255, 150, 255, 180),  # Magenta
            title="Scattering Events",
            side="left",
        )

        # Absorption profile (right)
        self._draw_profile_histogram(
            x=self.absorb_profile_x,
            y=self.anim_y,
            width=PROFILE_WIDTH,
            height=ANIM_HEIGHT,
            data=stats.absorption_profile,
            color=(220, 80, 80, 180),  # Red
            title="Absorption Events",
            side="right",
        )

    def _draw_profile_histogram(self, x, y, width, height, data, color, title, side):
        """Draw a vertical histogram"""
        if sum(data) == 0:
            # No data yet - just draw frame
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y, width, height), 2)

            # Title
            text = self.font_medium.render(title, True, (100, 100, 100))
            text_rect = text.get_rect(center=(x + width // 2, y - 20))
            self.screen.blit(text, text_rect)
            return

        # Background
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 50))
        self.screen.blit(s, (x, y))

        # Draw bars
        bin_height = height / len(data)
        max_count = max(data) if data else 1

        for i, count in enumerate(data):
            if count > 0:
                bin_y = y + i * bin_height

                # Bar extends from center
                if side == "left":
                    bar_width = (count / max_count) * (width - 10)
                    bar_x = x + width - bar_width - 5
                else:  # right
                    bar_width = (count / max_count) * (width - 10)
                    bar_x = x + 5

                pygame.draw.rect(
                    self.screen, color, (bar_x, bin_y, bar_width, bin_height - 1)
                )

        # Frame
        pygame.draw.rect(self.screen, (150, 150, 150), (x, y, width, height), 2)

        # Title
        text = self.font_medium.render(title, True, (60, 60, 60))
        text_rect = text.get_rect(center=(x + width // 2, y - 20))
        self.screen.blit(text, text_rect)

        # Max value
        max_text = self.font_small.render(f"max: {max(data)}", True, (100, 100, 100))
        self.screen.blit(max_text, (x + 5, y + height + 5))

    def _draw_photon_area(self):
        """Draw central area with photons"""
        x = self.photon_area_x
        y = self.anim_y
        width = PHOTON_AREA_WIDTH
        height = ANIM_HEIGHT

        # Background atmosphere
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        s.fill(COLOR_ATMOSPHERE)
        self.screen.blit(s, (x, y))

        # TOA line
        pygame.draw.line(self.screen, COLOR_TOA, (x, y), (x + width, y), 3)
        toa_text = self.font_medium.render("τ=0 (TOA)", True, COLOR_TOA)
        self.screen.blit(toa_text, (x + 10, y - 30))

        # Surface line
        surface_y = y + height
        pygame.draw.line(
            self.screen, COLOR_SURFACE, (x, surface_y), (x + width, surface_y), 3
        )
        surface_text = self.font_medium.render(
            f"τ={self.tau_max:.1f} (Surface)", True, COLOR_SURFACE
        )
        self.screen.blit(surface_text, (x + 10, surface_y + 5))

        # Draw photons
        for photon in self.simulation.get_active_photons():
            photon_y = y + (photon.tau / self.tau_max) * height
            photon_x = x + photon.x_position

            # Choose appearance
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
                self.screen.blit(
                    surf, (int(photon_x) - radius - 1, int(photon_y) - radius - 1)
                )
            else:
                pygame.draw.circle(
                    self.screen, color, (int(photon_x), int(photon_y)), radius
                )

            # Direction arrow for moving photons
            if photon.state == PhotonState.MOVING:
                arrow_len = 6
                if photon.direction == Direction.DOWN:
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (int(photon_x), int(photon_y) - arrow_len // 2),
                        (int(photon_x), int(photon_y) + arrow_len // 2),
                        1,
                    )
                    pygame.draw.polygon(
                        self.screen,
                        (255, 255, 255),
                        [
                            (int(photon_x), int(photon_y) + arrow_len // 2 + 2),
                            (int(photon_x) - 2, int(photon_y) + arrow_len // 2 - 1),
                            (int(photon_x) + 2, int(photon_y) + arrow_len // 2 - 1),
                        ],
                    )
                else:
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (int(photon_x), int(photon_y) - arrow_len // 2),
                        (int(photon_x), int(photon_y) + arrow_len // 2),
                        1,
                    )
                    pygame.draw.polygon(
                        self.screen,
                        (255, 255, 255),
                        [
                            (int(photon_x), int(photon_y) - arrow_len // 2 - 2),
                            (int(photon_x) - 2, int(photon_y) - arrow_len // 2 + 1),
                            (int(photon_x) + 2, int(photon_y) - arrow_len // 2 + 1),
                        ],
                    )

    def _draw_counters(self):
        """Draw large counters at bottom of screen"""
        stats = self.simulation.stats

        # Bottom section for counters
        counter_y = WINDOW_HEIGHT - 60
        counter_spacing = SCENE_WIDTH // 3

        # Reflected counter (left)
        self._draw_counter(
            x=counter_spacing // 2,
            y=counter_y,
            value=stats.reflected,
            label="REFLECTED",
            color=(0, 120, 255),
        )

        # Transmitted counter (center)
        self._draw_counter(
            x=SCENE_WIDTH // 2,
            y=counter_y,
            value=stats.transmitted,
            label="TRANSMITTED",
            color=(255, 150, 0),
        )

        # Absorbed counter (right)
        self._draw_counter(
            x=SCENE_WIDTH - counter_spacing // 2,
            y=counter_y,
            value=stats.absorbed,
            label="ABSORBED",
            color=(220, 50, 50),
        )

    def _draw_counter(self, x, y, value, label, color):
        """Draw a large counter with label"""
        # Value
        value_text = self.font_huge.render(str(value), True, color)
        value_rect = value_text.get_rect(center=(x, y - 10))
        self.screen.blit(value_text, value_rect)

        # Label
        label_text = self.font_small.render(label, True, (100, 100, 100))
        label_rect = label_text.get_rect(center=(x, y + 25))
        self.screen.blit(label_text, label_rect)

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
        """Start animation"""
        self.simulation.reset(self.tau_max, self.omega_0, int(self.num_photons))
        self.sim_running = True
        self.start_button.set_text("Running...")
        self.start_button.disable()

    def _reset_simulation(self):
        """Reset"""
        self.simulation.reset(self.tau_max, self.omega_0, int(self.num_photons))
        self.sim_running = False
        self.start_button.set_text("Start Animation")
        self.start_button.enable()
        self.info_box.html_text = self._get_info_html()
        self.info_box.rebuild()

    def run(self):
        """Main loop"""
        while self.running:
            self._handle_events()

            # Update simulation
            if self.sim_running:
                self.simulation.update(self.animation_speed)

                # Update info every few frames
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
    app = EnhancedPhotonDemo()
    app.run()


if __name__ == "__main__":
    main()
