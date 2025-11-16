import pygame
from .base import BaseScreen
from ..ui.button import Button


class HighScoreScreen(BaseScreen):
    def __init__(self, manager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)

        self.background_color = (20, 10, 40)
        self.title_font = pygame.font.SysFont(None, 48)
        self.text_font = pygame.font.SysFont(None, 28)

        self.back_button = Button(
            pygame.Rect(20, screen_height - 70, 160, 40),
            "Back to Menu",
            self.text_font,
        )

        # Untuk sementara, high score masih dummy text
        self.dummy_scores = ["1. AAA - 1230", "2. BBB - 900", "3. CCC - 750"]

    def handle_event(self, event: pygame.event.Event):
        if self.back_button.handle_event(event):
            from .main_menu import MainMenuScreen
            new_screen = MainMenuScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(self.background_color)

        title_surf = self.title_font.render("High Scores", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surf, title_rect)

        y = 150
        for line in self.dummy_scores:
            text_surf = self.text_font.render(line, True, (230, 230, 230))
            text_rect = text_surf.get_rect(center=(self.screen_width // 2, y))
            surface.blit(text_surf, text_rect)
            y += 40

        self.back_button.draw(surface)
