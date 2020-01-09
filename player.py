from constants import *
from colors import *
import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # Set player coords
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE_WIDTH
        self.height = PLAYER_SIZE_HEIGHT

        #
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        # Draw the car (a rectangle!)
        pygame.draw.rect(self.image, WHITE, [0, 0, self.width, self.height])

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

        # Update coordinates for draw
        self._update_coords()

    def _update_coords(self):
        self.rect.x = self.x - self.width / 2
        self.rect.y = self.y

    def move_right(self, pixels):
        # Check if we can move to right then move
        if self.x + self.width / 2 + pixels <= WIDTH:
            self.x = self.x + pixels
        # Update draw coordinates
        self._update_coords()

    def move_left(self, pixels):
        # Check if we can move to right then move
        if self.x - self.width / 2 - pixels >= 0:
            self.x -= pixels
        # Update draw coordinates
        self._update_coords()
