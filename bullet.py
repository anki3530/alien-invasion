import pygame

from pygame.sprite import Sprite


class Bullet(Sprite):
    """class to manage bullets from ship"""
    def __init__(self, ai_game):
        """creating bullet at ship's current position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # create the bullet at (0, 0) then set it on current position.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
                                self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # stores the position as decimal
        self.y = float(self.rect.y)

    def update(self):
        """moves the bullet up the screen"""
        self.y -= self.settings.bullet_speed
        # updates the rectangle position
        self.rect.y = self.y

    def draw_bullet(self):
        """draw the bullet on the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)