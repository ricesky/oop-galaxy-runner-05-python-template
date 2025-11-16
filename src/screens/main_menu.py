import pygame
from .base import BaseScreen
from ..ui.button import Button


class MainMenuScreen(BaseScreen):
    def __init__(self, manager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)

        self.background_color = (10, 10, 40)

        self.title_font = pygame.font.SysFont(None, 64)
        self.button_font = pygame.font.SysFont(None, 32)

        # Posisi tombol
        button_width = 220
        button_height = 50
        center_x = screen_width // 2
        start_y = screen_height // 2 - 40

        self.start_button = Button(
            pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            "Start Game",
            self.button_font,
        )

        self.highscore_button = Button(
            pygame.Rect(center_x - button_width // 2, start_y + 70, button_width, button_height),
            "High Score",
            self.button_font,
        )

        self.quit_button = Button(
            pygame.Rect(center_x - button_width // 2, start_y + 140, button_width, button_height),
            "Quit",
            self.button_font,
        )

    def handle_event(self, event: pygame.event.Event):
        if self.start_button.handle_event(event):
            from .game_screen import GameScreen
            new_screen = GameScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

        if self.highscore_button.handle_event(event):
            from .high_score import HighScoreScreen
            new_screen = HighScoreScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

        if self.quit_button.handle_event(event):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float):
        # Main menu tidak punya animasi khusus, boleh dikosongkan.
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(self.background_color)

        # Judul
        title_surf = self.title_font.render("Galaxy Runner", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 120))
        surface.blit(title_surf, title_rect)

        # Tombol
        self.start_button.draw(surface)
        self.highscore_button.draw(surface)
        self.quit_button.draw(surface)
