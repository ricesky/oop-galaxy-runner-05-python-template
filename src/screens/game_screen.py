import pygame
from .base import BaseScreen
from ..core.game import Game
from ..ui.button import Button


class GameScreen(BaseScreen):
    def __init__(self, manager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)

        self.game = Game(screen_width, screen_height)

        # Tombol Back to Menu (misal di pojok kanan atas)
        self.button_font = pygame.font.SysFont(None, 24)
        self.back_button = Button(
            pygame.Rect(screen_width - 150, 10, 140, 40),
            "Back to Menu",
            self.button_font,
            bg_color=(80, 80, 80),
            hover_color=(120, 120, 120),
        )

    def handle_event(self, event: pygame.event.Event):
        # Forward event ke Game jika suatu saat perlu (misal pause dsb.)
        self.game.handle_event(event)

        if self.back_button.handle_event(event):
            from .main_menu import MainMenuScreen
            new_screen = MainMenuScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

    def update(self, dt: float):
        self.game.update(dt)

    def draw(self, surface: pygame.Surface):
        self.game.draw(surface)
        self.back_button.draw(surface)
